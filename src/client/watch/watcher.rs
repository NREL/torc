//! Main watch loop for monitoring workflows and recovering from failures.

use std::collections::HashMap;
use std::path::PathBuf;
use std::time::{Duration, Instant};

use log::{debug, error, info, warn};

use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::log_paths;
use crate::models::JobStatus;

use super::audit::AuditLogger;
use super::claude_client::ClaudeClient;
use super::failure_cache::FailureCache;
use super::recovery::execute_recovery;

/// Configuration for the watch command.
#[derive(Debug, Clone)]
pub struct WatchConfig {
    /// Poll interval in seconds
    pub poll_interval: u64,
    /// Output directory for job logs
    pub output_dir: PathBuf,
    /// Maximum recovery attempts per job
    pub max_retries: u32,
    /// Cooldown period between retries in seconds
    pub retry_cooldown: u64,
    /// Whether to only diagnose (not auto-recover)
    pub diagnose_only: bool,
    /// Claude model to use
    pub model: String,
    /// Path to failure pattern cache database
    pub cache_path: Option<PathBuf>,
    /// Rate limit: max API calls per minute
    pub rate_limit_per_minute: u32,
    /// Path to audit log file
    pub audit_log_path: Option<PathBuf>,
}

/// Tracks retry state for a job.
#[derive(Debug, Clone)]
struct JobRetryState {
    retry_count: u32,
    last_retry: Instant,
    last_failure_signature: Option<String>,
}

/// The main watcher that monitors workflows for failures.
pub struct Watcher {
    config: Configuration,
    workflow_id: i64,
    watch_config: WatchConfig,
    claude_client: ClaudeClient,
    failure_cache: Option<FailureCache>,
    audit_logger: Option<AuditLogger>,
    retry_states: HashMap<i64, JobRetryState>,
    api_calls_this_minute: u32,
    minute_start: Instant,
}

impl Watcher {
    /// Create a new Watcher instance.
    pub fn new(
        config: Configuration,
        workflow_id: i64,
        watch_config: WatchConfig,
        api_key: String,
    ) -> Result<Self, String> {
        let claude_client = ClaudeClient::new(api_key, watch_config.model.clone());

        let failure_cache = if let Some(ref path) = watch_config.cache_path {
            match FailureCache::open(path) {
                Ok(cache) => Some(cache),
                Err(e) => {
                    warn!("Failed to open failure cache at {:?}: {}", path, e);
                    None
                }
            }
        } else {
            None
        };

        let audit_logger = if let Some(ref path) = watch_config.audit_log_path {
            match AuditLogger::new(path) {
                Ok(logger) => Some(logger),
                Err(e) => {
                    warn!("Failed to create audit logger at {:?}: {}", path, e);
                    None
                }
            }
        } else {
            None
        };

        Ok(Self {
            config,
            workflow_id,
            watch_config,
            claude_client,
            failure_cache,
            audit_logger,
            retry_states: HashMap::new(),
            api_calls_this_minute: 0,
            minute_start: Instant::now(),
        })
    }

    /// Run the main watch loop.
    pub fn run(&mut self) -> Result<(), String> {
        info!("Starting watch for workflow {}", self.workflow_id);
        info!("Poll interval: {}s", self.watch_config.poll_interval);
        info!("Max retries per job: {}", self.watch_config.max_retries);
        info!("Diagnose only: {}", self.watch_config.diagnose_only);

        loop {
            // Check if workflow is complete
            if self.is_workflow_complete()? {
                info!("Workflow {} is complete", self.workflow_id);
                break;
            }

            // Get failed jobs
            let failed_jobs = self.get_failed_jobs()?;
            if !failed_jobs.is_empty() {
                info!("Found {} failed jobs", failed_jobs.len());
                for job in failed_jobs {
                    if let Err(e) = self.handle_failed_job(job) {
                        error!("Error handling failed job: {}", e);
                    }
                }
            } else {
                debug!("No failed jobs found");
            }

            // Sleep for poll interval
            std::thread::sleep(Duration::from_secs(self.watch_config.poll_interval));
        }

        Ok(())
    }

    /// Check if the workflow is complete (all jobs finished or no more work to do).
    fn is_workflow_complete(&self) -> Result<bool, String> {
        let response = default_api::is_workflow_complete(&self.config, self.workflow_id)
            .map_err(|e| format!("Failed to check workflow completion: {}", e))?;

        Ok(response.is_complete)
    }

    /// Get all failed jobs in the workflow.
    fn get_failed_jobs(&self) -> Result<Vec<crate::models::JobModel>, String> {
        let response = default_api::list_jobs(
            &self.config,
            self.workflow_id,
            Some(JobStatus::Failed),
            None,        // needs_file_id
            None,        // upstream_job_id
            None,        // offset
            Some(10000), // limit
            None,        // sort_by
            None,        // reverse_sort
            None,        // include_relationships
        )
        .map_err(|e| format!("Failed to list failed jobs: {}", e))?;

        Ok(response.items.unwrap_or_default())
    }

    /// Handle a single failed job.
    fn handle_failed_job(&mut self, job: crate::models::JobModel) -> Result<(), String> {
        let job_id = job.id.ok_or("Job has no ID")?;
        let job_name = job.name.clone();
        let max_retries = self.watch_config.max_retries;
        let retry_cooldown = self.watch_config.retry_cooldown;
        let diagnose_only = self.watch_config.diagnose_only;

        // Ensure retry state exists with initial values
        self.retry_states.entry(job_id).or_insert(JobRetryState {
            retry_count: 0,
            last_retry: Instant::now() - Duration::from_secs(retry_cooldown + 1),
            last_failure_signature: None,
        });

        // Check retry count (read state, drop borrow)
        {
            let state = self.retry_states.get(&job_id).unwrap();
            if state.retry_count >= max_retries {
                debug!(
                    "Job {} has exceeded max retries ({})",
                    job_name, max_retries
                );
                return Ok(());
            }

            // Check cooldown
            let elapsed = state.last_retry.elapsed();
            if elapsed < Duration::from_secs(retry_cooldown) {
                debug!(
                    "Job {} is in cooldown ({:.0}s remaining)",
                    job_name,
                    retry_cooldown as f64 - elapsed.as_secs_f64()
                );
                return Ok(());
            }
        }

        info!("Analyzing failed job: {} (ID: {})", job_name, job_id);

        // Get job logs
        let (stdout, stderr) = self.get_job_logs(job_id)?;

        // Compute error signature for cache lookup
        let error_signature = FailureCache::compute_signature(&stderr);

        // Check if same failure as last time (avoid retry loops)
        {
            let state = self.retry_states.get(&job_id).unwrap();
            if state.last_failure_signature.as_ref() == Some(&error_signature) {
                debug!(
                    "Job {} failed with same error signature, skipping",
                    job_name
                );
                return Ok(());
            }
        }

        // Check failure cache
        let cached_diagnosis = self
            .failure_cache
            .as_ref()
            .and_then(|cache| cache.lookup(&job_name, &error_signature).ok().flatten());

        let diagnosis = if let Some(cached) = cached_diagnosis {
            info!("Found cached diagnosis for failure pattern");
            cached
        } else {
            // Rate limit check
            if !self.check_rate_limit() {
                warn!("Rate limit exceeded, skipping Claude API call");
                return Ok(());
            }

            // Call Claude API for diagnosis
            info!("Requesting diagnosis from Claude...");
            let diagnosis = self.claude_client.diagnose_failure(
                &self.config,
                self.workflow_id,
                &job,
                &stdout,
                &stderr,
            )?;

            // Cache the diagnosis
            if let Some(ref mut cache) = self.failure_cache {
                if let Err(e) = cache.store(&job_name, &error_signature, &diagnosis) {
                    warn!("Failed to cache diagnosis: {}", e);
                }
            }

            diagnosis
        };

        // Log the diagnosis
        info!("Diagnosis: {}", diagnosis.summary);
        if let Some(ref action) = diagnosis.recommended_action {
            info!("Recommended action: {:?}", action);
        }

        // Log to audit
        if let Some(ref mut audit) = self.audit_logger {
            audit.log_diagnosis(job_id, &job_name, &diagnosis);
        }

        // Execute recovery if not in diagnose-only mode
        if !diagnose_only {
            if let Some(action) = diagnosis.recommended_action {
                info!("Executing recovery action: {:?}", action);
                match execute_recovery(&self.config, job_id, &action) {
                    Ok(()) => {
                        info!("Recovery action executed successfully");

                        // Update retry state
                        if let Some(state) = self.retry_states.get_mut(&job_id) {
                            state.retry_count += 1;
                            state.last_retry = Instant::now();
                            state.last_failure_signature = Some(error_signature.clone());
                        }

                        // Update cache success count
                        if let Some(ref mut cache) = self.failure_cache {
                            cache.record_success(&job_name, &error_signature);
                        }

                        if let Some(ref mut audit) = self.audit_logger {
                            audit.log_recovery(job_id, &job_name, &action, true);
                        }
                    }
                    Err(e) => {
                        error!("Recovery action failed: {}", e);

                        // Update retry state
                        if let Some(state) = self.retry_states.get_mut(&job_id) {
                            state.retry_count += 1;
                            state.last_retry = Instant::now();
                        }

                        // Update cache failure count
                        if let Some(ref mut cache) = self.failure_cache {
                            cache.record_failure(&job_name, &error_signature);
                        }

                        if let Some(ref mut audit) = self.audit_logger {
                            audit.log_recovery(job_id, &job_name, &action, false);
                        }
                    }
                }
            } else {
                info!("No recovery action recommended");
            }
        }

        Ok(())
    }

    /// Get stdout and stderr logs for a job.
    fn get_job_logs(&self, job_id: i64) -> Result<(String, String), String> {
        // Get the latest result to find the run_id
        let results = default_api::list_results(
            &self.config,
            self.workflow_id,
            Some(job_id),
            None,    // run_id
            None,    // offset
            Some(1), // limit
            None,    // sort_by
            None,    // reverse_sort
            None,    // return_code
            None,    // status
            None,    // all_runs
            None,    // compute_node_id
        )
        .map_err(|e| format!("Failed to get job results: {}", e))?;

        let run_id = results
            .items
            .and_then(|items| items.into_iter().next())
            .map(|r| r.run_id)
            .unwrap_or(1);

        let stdout_path = log_paths::get_job_stdout_path(
            &self.watch_config.output_dir,
            self.workflow_id,
            job_id,
            run_id,
        );
        let stderr_path = log_paths::get_job_stderr_path(
            &self.watch_config.output_dir,
            self.workflow_id,
            job_id,
            run_id,
        );

        let stdout = std::fs::read_to_string(&stdout_path).unwrap_or_else(|_| String::new());
        let stderr = std::fs::read_to_string(&stderr_path).unwrap_or_else(|_| String::new());

        // Truncate logs if too long (keep last 10KB)
        let max_len = 10 * 1024;
        let stdout = if stdout.len() > max_len {
            format!("...[truncated]...\n{}", &stdout[stdout.len() - max_len..])
        } else {
            stdout
        };
        let stderr = if stderr.len() > max_len {
            format!("...[truncated]...\n{}", &stderr[stderr.len() - max_len..])
        } else {
            stderr
        };

        Ok((stdout, stderr))
    }

    /// Check and update rate limit. Returns true if API call is allowed.
    fn check_rate_limit(&mut self) -> bool {
        let now = Instant::now();
        let elapsed = now.duration_since(self.minute_start);

        // Reset counter every minute
        if elapsed >= Duration::from_secs(60) {
            self.api_calls_this_minute = 0;
            self.minute_start = now;
        }

        if self.api_calls_this_minute >= self.watch_config.rate_limit_per_minute {
            return false;
        }

        self.api_calls_this_minute += 1;
        true
    }
}
