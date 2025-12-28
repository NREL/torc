//! Shared recovery functionality for Slurm workflows.
//!
//! This module provides the core recovery logic used by both:
//! - `torc recover` standalone command
//! - `torc watch --recover` automatic recovery

use log::{debug, info, warn};
use serde::Serialize;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::process::Command;

use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::report_models::{ResourceUtilizationReport, ResultsReport};
use crate::time_utils::duration_string_to_seconds;

/// Arguments for workflow recovery
pub struct RecoverArgs {
    pub workflow_id: i64,
    pub output_dir: PathBuf,
    pub memory_multiplier: f64,
    pub runtime_multiplier: f64,
    pub retry_unknown: bool,
    pub recovery_hook: Option<String>,
    pub dry_run: bool,
}

/// Result of applying recovery heuristics
#[derive(Debug, Clone, Serialize)]
pub struct RecoveryResult {
    pub oom_fixed: usize,
    pub timeout_fixed: usize,
    pub unknown_retried: usize,
    pub other_failures: usize,
    pub jobs_to_retry: Vec<i64>,
    /// Detailed resource adjustments (for JSON output)
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub adjustments: Vec<ResourceAdjustmentReport>,
}

/// Detailed report of a resource adjustment for JSON output
#[derive(Debug, Clone, Serialize)]
pub struct ResourceAdjustmentReport {
    /// The resource_requirements_id being adjusted
    pub resource_requirements_id: i64,
    /// Job IDs that share this resource requirement
    pub job_ids: Vec<i64>,
    /// Job names for reference
    pub job_names: Vec<String>,
    /// Whether memory was adjusted
    pub memory_adjusted: bool,
    /// Original memory setting
    #[serde(skip_serializing_if = "Option::is_none")]
    pub original_memory: Option<String>,
    /// New memory setting
    #[serde(skip_serializing_if = "Option::is_none")]
    pub new_memory: Option<String>,
    /// Maximum peak memory observed (bytes)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_peak_memory_bytes: Option<u64>,
    /// Whether runtime was adjusted
    pub runtime_adjusted: bool,
    /// Original runtime setting
    #[serde(skip_serializing_if = "Option::is_none")]
    pub original_runtime: Option<String>,
    /// New runtime setting
    #[serde(skip_serializing_if = "Option::is_none")]
    pub new_runtime: Option<String>,
}

/// Full recovery report for JSON output
#[derive(Debug, Clone, Serialize)]
pub struct RecoveryReport {
    pub workflow_id: i64,
    pub dry_run: bool,
    pub memory_multiplier: f64,
    pub runtime_multiplier: f64,
    pub result: RecoveryResult,
    /// The diagnosis data (failed jobs info)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub diagnosis: Option<ResourceUtilizationReport>,
}

/// Information about Slurm logs for a job
#[derive(Debug)]
pub struct SlurmLogInfo {
    pub slurm_job_id: Option<String>,
    pub slurm_stdout: Option<String>,
    pub slurm_stderr: Option<String>,
}

/// Parse memory string (e.g., "8g", "512m", "1024k") to bytes
pub fn parse_memory_bytes(mem: &str) -> Option<u64> {
    let mem = mem.trim().to_lowercase();
    let (num_str, multiplier) = if mem.ends_with("gb") {
        (mem.trim_end_matches("gb"), 1024u64 * 1024 * 1024)
    } else if mem.ends_with("g") {
        (mem.trim_end_matches("g"), 1024u64 * 1024 * 1024)
    } else if mem.ends_with("mb") {
        (mem.trim_end_matches("mb"), 1024u64 * 1024)
    } else if mem.ends_with("m") {
        (mem.trim_end_matches("m"), 1024u64 * 1024)
    } else if mem.ends_with("kb") {
        (mem.trim_end_matches("kb"), 1024u64)
    } else if mem.ends_with("k") {
        (mem.trim_end_matches("k"), 1024u64)
    } else {
        (mem.as_str(), 1u64)
    };
    num_str
        .parse::<f64>()
        .ok()
        .map(|n| (n * multiplier as f64) as u64)
}

/// Format bytes to memory string (e.g., "12g", "512m")
pub fn format_memory_bytes_short(bytes: u64) -> String {
    if bytes >= 1024 * 1024 * 1024 {
        format!("{}g", bytes / (1024 * 1024 * 1024))
    } else if bytes >= 1024 * 1024 {
        format!("{}m", bytes / (1024 * 1024))
    } else if bytes >= 1024 {
        format!("{}k", bytes / 1024)
    } else {
        format!("{}b", bytes)
    }
}

/// Format seconds to ISO8601 duration (e.g., "PT2H30M")
pub fn format_duration_iso8601(secs: u64) -> String {
    let hours = secs / 3600;
    let mins = (secs % 3600) / 60;
    if hours > 0 && mins > 0 {
        format!("PT{}H{}M", hours, mins)
    } else if hours > 0 {
        format!("PT{}H", hours)
    } else {
        format!("PT{}M", mins.max(1))
    }
}

/// Recover a Slurm workflow by:
/// 1. Checking preconditions (workflow complete, no active workers)
/// 2. Diagnosing failures (OOM, timeout, etc.)
/// 3. Applying recovery heuristics (adjusting resources)
/// 4. Running recovery hook (if provided)
/// 5. Resetting failed jobs
/// 6. Reinitializing workflow
/// 7. Regenerating and submitting Slurm schedulers
pub fn recover_workflow(
    config: &Configuration,
    args: &RecoverArgs,
) -> Result<RecoveryResult, String> {
    if args.dry_run {
        info!("[DRY RUN] Showing what would be done without making changes");
    }

    // Step 1: Check preconditions
    check_recovery_preconditions(config, args.workflow_id)?;

    // Step 2: Diagnose failures
    info!("Diagnosing failures...");
    let diagnosis = diagnose_failures(args.workflow_id, &args.output_dir)?;

    // Step 3: Apply recovery heuristics (in dry_run mode, this shows changes without applying them)
    if args.dry_run {
        info!("[DRY RUN] Proposed resource adjustments:");
    } else {
        info!("Applying recovery heuristics...");
    }
    let mut result = apply_recovery_heuristics(
        config,
        args.workflow_id,
        &diagnosis,
        args.memory_multiplier,
        args.runtime_multiplier,
        args.retry_unknown,
        &args.output_dir,
        args.dry_run,
    )?;

    if result.oom_fixed > 0 || result.timeout_fixed > 0 {
        if args.dry_run {
            info!(
                "  Would apply fixes: {} OOM, {} timeout",
                result.oom_fixed, result.timeout_fixed
            );
        } else {
            info!(
                "  Applied fixes: {} OOM, {} timeout",
                result.oom_fixed, result.timeout_fixed
            );
        }
    }

    if result.other_failures > 0 {
        if args.retry_unknown {
            if args.recovery_hook.is_some() {
                info!(
                    "  {} job(s) with unknown failure cause (would run recovery hook)",
                    result.other_failures
                );
            } else {
                info!(
                    "  {} job(s) with unknown failure cause (would retry)",
                    result.other_failures
                );
            }
            // Track unknown retried count
            result.unknown_retried = result.other_failures;
        } else {
            info!(
                "  {} job(s) with unknown failure cause (skipped, use --retry-unknown to include)",
                result.other_failures
            );
        }
    }

    // In dry_run mode, stop here
    if args.dry_run {
        if result.jobs_to_retry.is_empty() {
            info!("[DRY RUN] No recoverable jobs found.");
        } else {
            info!(
                "[DRY RUN] Would reset {} job(s) for retry",
                result.jobs_to_retry.len()
            );
            info!("[DRY RUN] Would reinitialize workflow");

            // Show scheduler preview based on jobs that would be retried
            // Group by resource requirements (each RR group becomes one scheduler)
            info!("[DRY RUN] Slurm schedulers that would be created:");
            if result.adjustments.is_empty() {
                // Jobs being retried without resource adjustments
                info!(
                    "  {} job(s) would be scheduled with existing resource requirements",
                    result.jobs_to_retry.len()
                );
            } else {
                // Show schedulers based on resource requirement groups
                for adj in &result.adjustments {
                    let mem_info = if let Some(ref new_mem) = adj.new_memory {
                        format!("memory: {}", new_mem)
                    } else if let Some(ref orig_mem) = adj.original_memory {
                        format!("memory: {}", orig_mem)
                    } else {
                        "memory: (default)".to_string()
                    };
                    let runtime_info = if let Some(ref new_rt) = adj.new_runtime {
                        format!("runtime: {}", new_rt)
                    } else if let Some(ref orig_rt) = adj.original_runtime {
                        format!("runtime: {}", orig_rt)
                    } else {
                        String::new()
                    };
                    let resource_info = if runtime_info.is_empty() {
                        mem_info
                    } else {
                        format!("{}, {}", mem_info, runtime_info)
                    };
                    info!(
                        "  RR {} - {} job(s): {}",
                        adj.resource_requirements_id,
                        adj.job_ids.len(),
                        resource_info
                    );
                    info!("    Jobs: {}", adj.job_names.join(", "));
                }
                info!(
                    "[DRY RUN] Total: {} allocation(s) would be submitted",
                    result.jobs_to_retry.len()
                );
            }
        }
        return Ok(result);
    }

    // Step 4: Run recovery hook if provided and there are unknown failures
    if result.other_failures > 0
        && let Some(ref hook_cmd) = args.recovery_hook
    {
        info!(
            "{} job(s) with unknown failure cause - running recovery hook...",
            result.other_failures
        );
        run_recovery_hook(args.workflow_id, hook_cmd)?;
    }

    // Check if there are any jobs to retry
    if result.jobs_to_retry.is_empty() {
        return Err(format!(
            "No recoverable jobs found. {} job(s) failed with unknown causes. \
             Use --retry-unknown to retry jobs with unknown failure causes.",
            result.other_failures
        ));
    }

    // Step 5: Reset failed jobs
    info!(
        "Resetting {} job(s) for retry...",
        result.jobs_to_retry.len()
    );
    let reset_count = reset_failed_jobs(config, args.workflow_id, &result.jobs_to_retry)?;
    info!("  Reset {} job(s)", reset_count);

    // Step 6: Reinitialize workflow (must happen BEFORE regenerate)
    // reset_workflow_status rejects requests when there are pending scheduled compute nodes,
    // so we must reinitialize before creating new allocations.
    info!("Reinitializing workflow...");
    reinitialize_workflow(args.workflow_id)?;

    // Step 7: Regenerate Slurm schedulers and submit
    info!("Regenerating Slurm schedulers...");
    regenerate_and_submit(args.workflow_id, &args.output_dir)?;

    Ok(result)
}

/// Check that the workflow is in a valid state for recovery:
/// - Workflow must be complete (all jobs in terminal state)
/// - No active workers (compute nodes or scheduled compute nodes)
fn check_recovery_preconditions(config: &Configuration, workflow_id: i64) -> Result<(), String> {
    // Check if workflow is complete
    let is_complete = default_api::is_workflow_complete(config, workflow_id)
        .map_err(|e| format!("Failed to check workflow completion status: {}", e))?;

    if !is_complete.is_complete && !is_complete.is_canceled {
        return Err("Cannot recover: workflow is not complete. \
             Wait for all jobs to finish or use 'torc workflows cancel' first."
            .to_string());
    }

    // Check for active compute nodes
    let active_nodes = default_api::list_compute_nodes(
        config,
        workflow_id,
        None,       // offset
        Some(1),    // limit - just need to know if any exist
        None,       // sort_by
        None,       // reverse_sort
        None,       // hostname
        Some(true), // is_active = true
        None,       // scheduled_compute_node_id
    )
    .map_err(|e| format!("Failed to check for active compute nodes: {}", e))?;

    if let Some(nodes) = active_nodes.items
        && !nodes.is_empty()
    {
        return Err("Cannot recover: there are still active compute nodes. \
             Wait for all workers to exit."
            .to_string());
    }

    // Check for pending/active scheduled compute nodes
    let pending_scn = default_api::list_scheduled_compute_nodes(
        config,
        workflow_id,
        None,            // offset
        Some(1),         // limit
        None,            // sort_by
        None,            // reverse_sort
        None,            // scheduler_id
        None,            // scheduler_config_id
        Some("pending"), // status
    )
    .map_err(|e| format!("Failed to check for pending scheduled compute nodes: {}", e))?;

    if pending_scn.total_count > 0 {
        return Err("Cannot recover: there are pending Slurm allocations. \
             Wait for them to start or cancel them with 'torc slurm cancel'."
            .to_string());
    }

    let active_scn = default_api::list_scheduled_compute_nodes(
        config,
        workflow_id,
        None,           // offset
        Some(1),        // limit
        None,           // sort_by
        None,           // reverse_sort
        None,           // scheduler_id
        None,           // scheduler_config_id
        Some("active"), // status
    )
    .map_err(|e| format!("Failed to check for active scheduled compute nodes: {}", e))?;

    if active_scn.total_count > 0 {
        return Err(
            "Cannot recover: there are active Slurm allocations still running. \
             Wait for all workers to exit."
                .to_string(),
        );
    }

    // Check that there are actually failed/terminated/canceled jobs to recover
    let failed_jobs = default_api::list_jobs(
        config,
        workflow_id,
        Some(crate::models::JobStatus::Failed), // status
        None,                                   // needs_file_id
        None,                                   // upstream_job_id
        None,                                   // offset
        Some(1),                                // limit
        None,                                   // sort_by
        None,                                   // reverse_sort
        None,                                   // include_relationships
        None,                                   // active_compute_node_id
    )
    .map_err(|e| format!("Failed to list failed jobs: {}", e))?;

    let terminated_jobs = default_api::list_jobs(
        config,
        workflow_id,
        Some(crate::models::JobStatus::Terminated), // status
        None,                                       // needs_file_id
        None,                                       // upstream_job_id
        None,                                       // offset
        Some(1),                                    // limit
        None,                                       // sort_by
        None,                                       // reverse_sort
        None,                                       // include_relationships
        None,                                       // active_compute_node_id
    )
    .map_err(|e| format!("Failed to list terminated jobs: {}", e))?;

    if failed_jobs.total_count == 0 && terminated_jobs.total_count == 0 {
        return Err("No failed or terminated jobs to recover. \
             Workflow may have completed successfully."
            .to_string());
    }

    Ok(())
}

/// Diagnose failures and return resource utilization report
pub fn diagnose_failures(
    workflow_id: i64,
    _output_dir: &Path,
) -> Result<ResourceUtilizationReport, String> {
    let output = Command::new("torc")
        .args([
            "-f",
            "json",
            "reports",
            "check-resource-utilization",
            &workflow_id.to_string(),
            "--include-failed",
        ])
        .output()
        .map_err(|e| format!("Failed to run check-resource-utilization: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("check-resource-utilization failed: {}", stderr));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    serde_json::from_str(&stdout)
        .map_err(|e| format!("Failed to parse resource utilization output: {}", e))
}

/// Get Slurm log information for failed jobs
fn get_slurm_log_info(workflow_id: i64, output_dir: &Path) -> Result<ResultsReport, String> {
    let output = Command::new("torc")
        .args([
            "-f",
            "json",
            "reports",
            "results",
            &workflow_id.to_string(),
            "-o",
            output_dir.to_str().unwrap_or("output"),
        ])
        .output()
        .map_err(|e| format!("Failed to run reports results: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("reports results failed: {}", stderr));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    serde_json::from_str(&stdout)
        .map_err(|e| format!("Failed to parse reports results output: {}", e))
}

/// Correlate failed jobs with their Slurm allocation logs
fn correlate_slurm_logs(
    diagnosis: &ResourceUtilizationReport,
    slurm_info: &ResultsReport,
) -> HashMap<i64, SlurmLogInfo> {
    let mut log_map = HashMap::new();

    // Build map from job_id to slurm log paths (using `results` field, not `jobs`)
    for result in &slurm_info.results {
        if result.slurm_stdout.is_some() || result.slurm_stderr.is_some() {
            log_map.insert(
                result.job_id,
                SlurmLogInfo {
                    slurm_job_id: result.slurm_job_id.clone(),
                    slurm_stdout: result.slurm_stdout.clone(),
                    slurm_stderr: result.slurm_stderr.clone(),
                },
            );
        }
    }

    // Filter to only failed jobs
    let mut failed_log_map = HashMap::new();
    for failed_job in &diagnosis.failed_jobs {
        if let Some(log_info) = log_map.remove(&failed_job.job_id) {
            failed_log_map.insert(failed_job.job_id, log_info);
        }
    }

    failed_log_map
}

/// Aggregated resource adjustment data for a single resource_requirements_id.
/// When multiple jobs share the same resource requirements, we take the maximum
/// peak memory and runtime to ensure all jobs can succeed on retry.
#[derive(Debug)]
struct ResourceAdjustment {
    /// The resource_requirements_id
    rr_id: i64,
    /// Job IDs that share this resource requirement and need retry
    job_ids: Vec<i64>,
    /// Job names for logging
    job_names: Vec<String>,
    /// Maximum peak memory observed across all OOM jobs (in bytes)
    max_peak_memory_bytes: Option<u64>,
    /// Whether any job had OOM without peak data (fall back to multiplier)
    has_oom_without_peak: bool,
    /// Whether any job had a timeout
    has_timeout: bool,
    /// Current memory setting (for fallback calculation)
    current_memory: String,
    /// Current runtime setting
    current_runtime: String,
}

/// Apply recovery heuristics and update job resources
///
/// If `dry_run` is true, shows what would be done without making changes.
///
/// When multiple jobs share the same `resource_requirements_id`, this function
/// finds the maximum peak memory across all OOM jobs in that group and applies
/// that (with multiplier) to the shared resource requirement. This ensures all
/// jobs in the group can succeed on retry.
#[allow(clippy::too_many_arguments)]
pub fn apply_recovery_heuristics(
    config: &Configuration,
    workflow_id: i64,
    diagnosis: &ResourceUtilizationReport,
    memory_multiplier: f64,
    runtime_multiplier: f64,
    retry_unknown: bool,
    output_dir: &Path,
    dry_run: bool,
) -> Result<RecoveryResult, String> {
    let mut oom_fixed = 0;
    let mut timeout_fixed = 0;
    let mut other_failures = 0;
    let mut jobs_to_retry = Vec::new();

    // Try to get Slurm log info for correlation
    let slurm_log_map = match get_slurm_log_info(workflow_id, output_dir) {
        Ok(slurm_info) => {
            let log_map = correlate_slurm_logs(diagnosis, &slurm_info);
            if !log_map.is_empty() {
                info!("  Found Slurm logs for {} failed job(s)", log_map.len());
            }
            log_map
        }
        Err(e) => {
            debug!("Could not get Slurm log info: {}", e);
            HashMap::new()
        }
    };

    // Phase 1: Collect and aggregate data by resource_requirements_id
    // This ensures that when multiple jobs share the same RR, we use the
    // maximum peak memory across all of them.
    let mut rr_adjustments: HashMap<i64, ResourceAdjustment> = HashMap::new();

    for job_info in &diagnosis.failed_jobs {
        let job_id = job_info.job_id;
        let likely_oom = job_info.likely_oom;
        let likely_timeout = job_info.likely_timeout;

        // Log Slurm info if available
        if let Some(slurm_info) = slurm_log_map.get(&job_id)
            && let Some(slurm_job_id) = &slurm_info.slurm_job_id
        {
            debug!("  Job {} ran in Slurm allocation {}", job_id, slurm_job_id);
        }

        // Handle unknown failures (no OOM or timeout detected)
        if !likely_oom && !likely_timeout {
            other_failures += 1;
            if retry_unknown {
                jobs_to_retry.push(job_id);
            }
            continue;
        }

        // Get current job to find resource requirements
        let job = match default_api::get_job(config, job_id) {
            Ok(j) => j,
            Err(e) => {
                warn!("  Warning: couldn't get job {}: {}", job_id, e);
                continue;
            }
        };

        let rr_id = match job.resource_requirements_id {
            Some(id) => id,
            None => {
                warn!("  Warning: job {} has no resource requirements", job_id);
                other_failures += 1;
                continue;
            }
        };

        // Get or create the adjustment entry for this resource_requirements_id
        let adjustment = rr_adjustments.entry(rr_id).or_insert_with(|| {
            // Fetch current resource requirements (only once per rr_id)
            let (current_memory, current_runtime) =
                match default_api::get_resource_requirements(config, rr_id) {
                    Ok(rr) => (rr.memory, rr.runtime),
                    Err(e) => {
                        warn!(
                            "  Warning: couldn't get resource requirements {}: {}",
                            rr_id, e
                        );
                        (String::new(), String::new())
                    }
                };
            ResourceAdjustment {
                rr_id,
                job_ids: Vec::new(),
                job_names: Vec::new(),
                max_peak_memory_bytes: None,
                has_oom_without_peak: false,
                has_timeout: false,
                current_memory,
                current_runtime,
            }
        });

        // Skip if we couldn't fetch the resource requirements
        if adjustment.current_memory.is_empty() {
            continue;
        }

        adjustment.job_ids.push(job_id);
        adjustment.job_names.push(job.name.clone());

        // Track OOM data
        if likely_oom {
            let peak_bytes = job_info
                .peak_memory_bytes
                .filter(|&v| v > 0)
                .map(|v| v as u64);

            if let Some(peak) = peak_bytes {
                // Update max if this job used more memory
                adjustment.max_peak_memory_bytes = Some(
                    adjustment
                        .max_peak_memory_bytes
                        .map_or(peak, |current_max| current_max.max(peak)),
                );
            } else {
                adjustment.has_oom_without_peak = true;
            }
        }

        // Track timeout
        if likely_timeout {
            adjustment.has_timeout = true;
        }
    }

    // Phase 2: Apply adjustments once per resource_requirements_id
    let mut adjustment_reports = Vec::new();

    for adjustment in rr_adjustments.values() {
        let rr_id = adjustment.rr_id;
        let mut updated = false;
        let mut memory_adjusted = false;
        let mut runtime_adjusted = false;
        let mut original_memory = None;
        let mut new_memory_str = None;
        let mut original_runtime = None;
        let mut new_runtime_str = None;

        // Fetch current resource requirements for update
        let rr = match default_api::get_resource_requirements(config, rr_id) {
            Ok(r) => r,
            Err(e) => {
                warn!(
                    "  Warning: couldn't get resource requirements {}: {}",
                    rr_id, e
                );
                continue;
            }
        };
        let mut new_rr = rr.clone();

        // Apply OOM fix using maximum peak memory across all jobs sharing this RR
        if adjustment.max_peak_memory_bytes.is_some() || adjustment.has_oom_without_peak {
            let new_bytes = if let Some(max_peak) = adjustment.max_peak_memory_bytes {
                // Use the maximum observed peak memory * multiplier
                (max_peak as f64 * memory_multiplier) as u64
            } else if let Some(current_bytes) = parse_memory_bytes(&adjustment.current_memory) {
                // Fall back to current specified * multiplier
                (current_bytes as f64 * memory_multiplier) as u64
            } else {
                warn!(
                    "  RR {}: OOM detected but couldn't determine new memory",
                    rr_id
                );
                continue;
            };

            let new_memory = format_memory_bytes_short(new_bytes);
            let job_count = adjustment.job_ids.len();

            if let Some(max_peak) = adjustment.max_peak_memory_bytes {
                if job_count > 1 {
                    info!(
                        "  {} job(s) with RR {}: OOM detected, max peak usage {} -> allocating {} ({}x)",
                        job_count,
                        rr_id,
                        format_memory_bytes_short(max_peak),
                        new_memory,
                        memory_multiplier
                    );
                    debug!("    Jobs: {:?}", adjustment.job_names);
                } else {
                    info!(
                        "  Job {} ({}): OOM detected, peak usage {} -> allocating {} ({}x)",
                        adjustment.job_ids[0],
                        adjustment.job_names[0],
                        format_memory_bytes_short(max_peak),
                        new_memory,
                        memory_multiplier
                    );
                }
            } else {
                info!(
                    "  {} job(s) with RR {}: OOM detected, increasing memory {} -> {} ({}x, no peak data)",
                    job_count, rr_id, adjustment.current_memory, new_memory, memory_multiplier
                );
            }

            // Track for JSON report
            original_memory = Some(adjustment.current_memory.clone());
            new_memory_str = Some(new_memory.clone());
            memory_adjusted = true;

            new_rr.memory = new_memory;
            updated = true;
            oom_fixed += adjustment.job_ids.len();
        }

        // Apply timeout fix
        if adjustment.has_timeout
            && let Ok(current_secs) = duration_string_to_seconds(&adjustment.current_runtime)
        {
            let new_secs = (current_secs as f64 * runtime_multiplier) as u64;
            let new_runtime = format_duration_iso8601(new_secs);
            let job_count = adjustment.job_ids.len();

            if job_count > 1 {
                info!(
                    "  {} job(s) with RR {}: Timeout detected, increasing runtime {} -> {}",
                    job_count, rr_id, adjustment.current_runtime, new_runtime
                );
            } else {
                info!(
                    "  Job {} ({}): Timeout detected, increasing runtime {} -> {}",
                    adjustment.job_ids[0],
                    adjustment.job_names[0],
                    adjustment.current_runtime,
                    new_runtime
                );
            }

            // Track for JSON report
            original_runtime = Some(adjustment.current_runtime.clone());
            new_runtime_str = Some(new_runtime.clone());
            runtime_adjusted = true;

            new_rr.runtime = new_runtime;
            updated = true;
            timeout_fixed += adjustment.job_ids.len();
        }

        // Update resource requirements if changed (only once per rr_id)
        if updated {
            if !dry_run
                && let Err(e) = default_api::update_resource_requirements(config, rr_id, new_rr)
            {
                warn!(
                    "  Warning: failed to update resource requirements {}: {}",
                    rr_id, e
                );
            }
            // All jobs sharing this RR should be retried
            jobs_to_retry.extend(&adjustment.job_ids);

            // Create adjustment report for JSON output
            adjustment_reports.push(ResourceAdjustmentReport {
                resource_requirements_id: rr_id,
                job_ids: adjustment.job_ids.clone(),
                job_names: adjustment.job_names.clone(),
                memory_adjusted,
                original_memory,
                new_memory: new_memory_str,
                max_peak_memory_bytes: adjustment.max_peak_memory_bytes,
                runtime_adjusted,
                original_runtime,
                new_runtime: new_runtime_str,
            });
        }
    }

    Ok(RecoveryResult {
        oom_fixed,
        timeout_fixed,
        unknown_retried: 0, // Will be set in recover_workflow if retry_unknown is true
        other_failures,
        jobs_to_retry,
        adjustments: adjustment_reports,
    })
}

/// Reset specific failed jobs for retry (without reinitializing)
pub fn reset_failed_jobs(
    _config: &Configuration,
    workflow_id: i64,
    job_ids: &[i64],
) -> Result<usize, String> {
    if job_ids.is_empty() {
        return Ok(0);
    }

    let job_count = job_ids.len();

    // Reset failed jobs WITHOUT --reinitialize (we'll reinitialize separately)
    let output = Command::new("torc")
        .args([
            "workflows",
            "reset-status",
            &workflow_id.to_string(),
            "--failed-only",
            "--no-prompts",
        ])
        .output()
        .map_err(|e| format!("Failed to run workflow reset-status: {}", e))?;

    // Print stdout so user sees what was reset
    if !output.stdout.is_empty() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        for line in stdout.lines() {
            info!("  {}", line);
        }
    }

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("workflow reset-status failed: {}", stderr));
    }

    Ok(job_count)
}

/// Reinitialize the workflow (set up dependencies and fire on_workflow_start actions)
pub fn reinitialize_workflow(workflow_id: i64) -> Result<(), String> {
    let output = Command::new("torc")
        .args(["workflows", "reinitialize", &workflow_id.to_string()])
        .output()
        .map_err(|e| format!("Failed to run workflow reinitialize: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("workflow reinitialize failed: {}", stderr));
    }

    Ok(())
}

/// Run the user's custom recovery hook command
pub fn run_recovery_hook(workflow_id: i64, hook_command: &str) -> Result<(), String> {
    info!("Running recovery hook: {}", hook_command);

    // Parse the command using shell-like quoting rules
    let parts = shlex::split(hook_command)
        .ok_or_else(|| format!("Invalid quoting in recovery hook command: {}", hook_command))?;
    if parts.is_empty() {
        return Err("Recovery hook command is empty".to_string());
    }

    // If the program doesn't contain a path separator and exists in the current directory,
    // prepend "./" so it's found (Command::new searches PATH, not CWD)
    let program = &parts[0];
    let program_path = if !program.contains('/') && std::path::Path::new(program).exists() {
        format!("./{}", program)
    } else {
        program.to_string()
    };
    let mut cmd = Command::new(&program_path);

    // Add any arguments from the hook command
    if parts.len() > 1 {
        cmd.args(&parts[1..]);
    }

    // Add workflow ID as final argument
    cmd.arg(workflow_id.to_string());

    // Also set as environment variable for convenience
    cmd.env("TORC_WORKFLOW_ID", workflow_id.to_string());

    let output = cmd
        .output()
        .map_err(|e| format!("Failed to execute recovery hook '{}': {}", hook_command, e))?;

    // Log stdout if present
    if !output.stdout.is_empty() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        for line in stdout.lines() {
            info!("  [hook] {}", line);
        }
    }

    // Log stderr if present
    if !output.stderr.is_empty() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        for line in stderr.lines() {
            warn!("  [hook] {}", line);
        }
    }

    if !output.status.success() {
        let exit_code = output.status.code().unwrap_or(-1);
        return Err(format!(
            "Recovery hook '{}' failed with exit code {}",
            hook_command, exit_code
        ));
    }

    info!("Recovery hook completed successfully");
    Ok(())
}

/// Regenerate Slurm schedulers and submit allocations
pub fn regenerate_and_submit(workflow_id: i64, output_dir: &Path) -> Result<(), String> {
    let output = Command::new("torc")
        .args([
            "slurm",
            "regenerate",
            &workflow_id.to_string(),
            "--submit",
            "-o",
            output_dir.to_str().unwrap_or("output"),
        ])
        .output()
        .map_err(|e| format!("Failed to run slurm regenerate: {}", e))?;

    // Print stdout so user sees what schedulers were created and submitted
    if !output.stdout.is_empty() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        for line in stdout.lines() {
            info!("  {}", line);
        }
    }

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("slurm regenerate failed: {}", stderr));
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_memory_bytes() {
        assert_eq!(parse_memory_bytes("1g"), Some(1024 * 1024 * 1024));
        assert_eq!(parse_memory_bytes("2gb"), Some(2 * 1024 * 1024 * 1024));
        assert_eq!(parse_memory_bytes("512m"), Some(512 * 1024 * 1024));
        assert_eq!(parse_memory_bytes("256mb"), Some(256 * 1024 * 1024));
        assert_eq!(parse_memory_bytes("1024k"), Some(1024 * 1024));
        assert_eq!(parse_memory_bytes("1024kb"), Some(1024 * 1024));
        assert_eq!(parse_memory_bytes("1024"), Some(1024));
    }

    #[test]
    fn test_format_memory_bytes_short() {
        assert_eq!(format_memory_bytes_short(1024 * 1024 * 1024), "1g");
        assert_eq!(format_memory_bytes_short(2 * 1024 * 1024 * 1024), "2g");
        assert_eq!(format_memory_bytes_short(512 * 1024 * 1024), "512m");
        assert_eq!(format_memory_bytes_short(1024 * 1024), "1m");
        assert_eq!(format_memory_bytes_short(1024), "1k");
    }

    #[test]
    fn test_format_duration_iso8601() {
        assert_eq!(format_duration_iso8601(3600), "PT1H");
        assert_eq!(format_duration_iso8601(7200), "PT2H");
        assert_eq!(format_duration_iso8601(5400), "PT1H30M");
        assert_eq!(format_duration_iso8601(1800), "PT30M");
        assert_eq!(format_duration_iso8601(60), "PT1M");
        assert_eq!(format_duration_iso8601(30), "PT1M"); // Minimum 1 minute
    }
}
