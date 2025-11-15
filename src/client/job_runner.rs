use chrono::{DateTime, Utc};
use log::{self, debug, error, info};
use std::cell::RefCell;
use std::collections::HashMap;
use std::path::PathBuf;
use std::thread;
use std::time::Duration;

use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::async_cli_command::AsyncCliCommand;
use crate::client::resource_monitor::{ResourceMonitor, ResourceMonitorConfig};
use crate::client::utils;
use crate::models::{
    ClaimJobsSortMethod, ComputeNodesResources, ResourceRequirementsModel, ResultModel,
    WorkflowModel,
};

const GB: i64 = 1024 * 1024 * 1024;

// Cache for memory string to GB conversions
thread_local! {
    static MEMORY_CACHE: RefCell<HashMap<String, f64>> = RefCell::new(HashMap::new());
}

#[allow(dead_code)]
pub struct JobRunner {
    config: Configuration,
    workflow: WorkflowModel,
    pub workflow_id: i64,
    pub run_id: i64,
    compute_node_id: i64,
    output_dir: PathBuf,
    job_completion_poll_interval: f64,
    max_parallel_jobs: Option<i64>,
    database_poll_interval: i64,
    time_limit: Option<String>,
    end_time: Option<DateTime<Utc>>,
    resources: ComputeNodesResources,
    orig_resources: ComputeNodesResources,
    scheduler_config_id: Option<i64>,
    log_prefix: Option<String>,
    cpu_affinity_cpus_per_job: Option<i64>,
    is_subtask: bool,
    running_jobs: HashMap<i64, AsyncCliCommand>,
    job_resources: HashMap<i64, ResourceRequirementsModel>,
    rules: ComputeNodeRules,
    resource_monitor: Option<ResourceMonitor>,
}

impl JobRunner {
    pub fn new(
        config: Configuration,
        workflow: WorkflowModel,
        run_id: i64,
        compute_node_id: i64,
        output_dir: PathBuf,
        job_completion_poll_interval: f64,
        max_parallel_jobs: Option<i64>,
        database_poll_interval: i64,
        time_limit: Option<String>,
        end_time: Option<DateTime<Utc>>,
        resources: ComputeNodesResources,
        scheduler_config_id: Option<i64>,
        log_prefix: Option<String>,
        cpu_affinity_cpus_per_job: Option<i64>,
        is_subtask: bool,
        unique_label: String,
    ) -> Self {
        let workflow_id = workflow.id.expect("Workflow ID must be present");
        let running_jobs: HashMap<i64, AsyncCliCommand> = HashMap::new();
        let rules = ComputeNodeRules::new(
            workflow.compute_node_expiration_buffer_seconds,
            // TODO
            // workflow.compute_node_wait_for_new_jobs_seconds,
            workflow.compute_node_ignore_workflow_completion,
            workflow.compute_node_wait_for_healthy_database_minutes,
            workflow.jobs_sort_method,
        );
        let job_resources: HashMap<i64, ResourceRequirementsModel> = HashMap::new();
        let orig_resources = ComputeNodesResources {
            id: resources.id,
            num_cpus: resources.num_cpus,
            memory_gb: resources.memory_gb,
            num_gpus: resources.num_gpus,
            num_nodes: resources.num_nodes,
            time_limit: resources.time_limit.clone(),
            scheduler_config_id: resources.scheduler_config_id,
        };

        // Initialize resource monitoring if configured
        let resource_monitor = if let Some(ref monitor_config_json) =
            workflow.resource_monitor_config
        {
            match serde_json::from_str::<ResourceMonitorConfig>(monitor_config_json) {
                Ok(monitor_config) if monitor_config.enabled => {
                    match ResourceMonitor::new(monitor_config, output_dir.clone(), unique_label) {
                        Ok(monitor) => {
                            info!("Resource monitoring enabled");
                            Some(monitor)
                        }
                        Err(e) => {
                            error!("Failed to initialize resource monitor: {}", e);
                            None
                        }
                    }
                }
                Ok(_) => None,
                Err(e) => {
                    error!("Failed to parse resource monitor config: {}", e);
                    None
                }
            }
        } else {
            None
        };

        JobRunner {
            config,
            workflow,
            workflow_id,
            run_id,
            compute_node_id,
            output_dir,
            job_completion_poll_interval,
            max_parallel_jobs,
            database_poll_interval,
            time_limit,
            end_time,
            resources,
            orig_resources,
            scheduler_config_id,
            log_prefix,
            cpu_affinity_cpus_per_job,
            is_subtask,
            running_jobs,
            job_resources,
            rules,
            resource_monitor,
        }
    }

    pub fn run_worker(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        let version = env!("CARGO_PKG_VERSION");
        let hostname = hostname::get()
            .expect("Failed to get hostname")
            .into_string()
            .expect("Hostname is not valid UTF-8");
        let end_time = if let Some(end_time) = self.end_time {
            end_time.timestamp() - self.rules.compute_node_expiration_buffer_seconds
        } else {
            i64::MAX
        };

        // Create output directory if it doesn't exist
        if !self.output_dir.exists() {
            std::fs::create_dir_all(&self.output_dir)?;
            info!("Created output directory: {}", self.output_dir.display());
        }

        info!("Starting torc job runner version={} workflow_id={} hostname={} output_dir={} resources={:?} rules={:?}
            job_completion_poll_interval={}s",
            version, self.workflow_id, hostname, self.output_dir.display(), self.resources, self.rules, self.job_completion_poll_interval);

        // Check for and execute on_workflow_start and on_worker_start actions before entering main loop
        self.execute_workflow_start_actions();
        self.execute_worker_start_actions();

        loop {
            match utils::send_with_retries(
                &self.config,
                || default_api::is_workflow_complete(&self.config, self.workflow_id),
                self.rules.compute_node_wait_for_healthy_database_minutes,
            ) {
                Ok(response) => {
                    if response.is_canceled {
                        info!(
                            "Workflow {} is canceled. Cancel all jobs.",
                            self.workflow_id
                        );
                        self.cancel_jobs();
                        break;
                    }
                    if response.is_complete {
                        if self.rules.compute_node_ignore_workflow_completion {
                            info!(
                                "Workflow {} is complete, but compute node is ignoring completion.",
                                self.workflow_id
                            );
                        } else {
                            info!(
                                "Workflow {} is complete. Exiting job runner.",
                                self.workflow_id
                            );
                            break;
                        }
                    }
                }
                Err(_) => {
                    match utils::send_with_retries(
                        &self.config,
                        || default_api::is_workflow_complete(&self.config, self.workflow_id),
                        self.rules.compute_node_wait_for_healthy_database_minutes,
                    ) {
                        Ok(is_complete) => {
                            if is_complete.is_complete {
                                info!(
                                    "Workflow {} is complete. Exiting job runner.",
                                    self.workflow_id
                                );
                                break;
                            }
                        }
                        Err(retry_err) => {
                            error!(
                                "Failed to check workflow completion after retries: {}",
                                retry_err
                            );
                            return Err(format!(
                                "Unable to check workflow completion: {}",
                                retry_err
                            )
                            .into());
                        }
                    }
                }
            }

            self.check_job_status();
            self.check_and_execute_actions();

            debug!("Check for new jobs");
            if self.max_parallel_jobs.is_none() {
                self.run_ready_jobs_based_on_resources()
            } else {
                self.run_ready_jobs_based_on_user_parallelism()
            };

            thread::sleep(Duration::from_secs_f64(self.job_completion_poll_interval));

            if Utc::now().timestamp() >= end_time {
                self.terminate_jobs();
                info!("End time reached. Stopping job runner.");
            }
        }

        self.execute_worker_complete_actions();

        // Shutdown resource monitor if enabled
        if let Some(monitor) = self.resource_monitor.take() {
            info!("Shutting down resource monitor");
            monitor.shutdown();
        }

        info!("Job runner completed for workflow ID: {}", self.workflow_id);
        Ok(())
    }

    /// Cancel all running jobs and handle completions.
    fn cancel_jobs(&mut self) {
        let mut results = Vec::new();
        for (job_id, async_job) in self.running_jobs.iter_mut() {
            info!("Canceling job {}", job_id);
            let _ = async_job.cancel();
        }
        for (job_id, async_job) in self.running_jobs.iter_mut() {
            let _ = match async_job.wait_for_completion() {
                Ok(_) => {
                    let result = async_job.get_result(
                        self.run_id,
                        self.compute_node_id,
                        self.resource_monitor.as_ref(),
                    );
                    results.push((*job_id, result));
                    Ok(())
                }
                Err(e) => {
                    error!("Error waiting for job {}: {}", job_id, e);
                    // TODO
                    Err(e)
                }
            };
        }
        for (job_id, result) in results {
            self.handle_job_completion(job_id, result);
        }
    }

    /// Terminate all running jobs and handle completions.
    fn terminate_jobs(&mut self) {
        let mut jobs_to_remove = Vec::new();
        // let mut jobs_that_support_termination = Vec::new();
        let mut results = Vec::new();
        for (job_id, async_job) in self.running_jobs.iter_mut() {
            info!("Terminating job {}", job_id);
            let _ = async_job.terminate();
            jobs_to_remove.push(*job_id);
            // if async_job.job.supports_termination.unwrap_or(false) {
            //     jobs_that_support_termination.push(*job_id);
            // }
        }
        for (job_id, async_job) in self.running_jobs.iter_mut() {
            let _ = match async_job.wait_for_completion() {
                Ok(_) => {
                    let result = async_job.get_result(
                        self.run_id,
                        self.compute_node_id,
                        self.resource_monitor.as_ref(),
                    );
                    results.push((*job_id, result));
                    Ok(())
                }
                Err(e) => {
                    error!("Error waiting for job {}: {}", job_id, e);
                    // TODO
                    Err(e)
                }
            };
        }
        for (job_id, result) in results {
            self.handle_job_completion(job_id, result);
        }
    }

    /// Check the status of running jobs and remove completed ones.
    fn check_job_status(&mut self) {
        let mut completed_jobs = Vec::new();
        let mut job_results = Vec::new();

        // First pass: check status and collect completed jobs
        for (job_id, async_job) in self.running_jobs.iter_mut() {
            match async_job.check_status() {
                Ok(()) => {
                    if async_job.is_complete {
                        completed_jobs.push(*job_id);

                        let result = async_job.get_result(
                            self.run_id,
                            self.compute_node_id,
                            self.resource_monitor.as_ref(),
                        );
                        job_results.push((*job_id, result));
                    }
                }
                Err(e) => {
                    error!("Error checking status for job {}: {}", job_id, e);
                    // TODO
                }
            }
        }

        // Second pass: complete jobs and update resources
        for (job_id, result) in job_results {
            self.handle_job_completion(job_id, result);
        }
    }

    fn handle_job_completion(&mut self, job_id: i64, result: ResultModel) {
        match utils::send_with_retries(
            &self.config,
            || {
                default_api::complete_job(
                    &self.config,
                    job_id,
                    result.status.clone(),
                    result.run_id,
                    result.clone(),
                )
            },
            self.rules.compute_node_wait_for_healthy_database_minutes,
        ) {
            Ok(_) => {
                info!("Successfully completed job {}", job_id);
                if let Some(job_rr) = self.job_resources.get(&job_id).cloned() {
                    self.increment_resources(&job_rr);
                }
            }
            Err(e) => {
                error!("Error completing job {}: {}", job_id, e);
                // TODO
            }
        }
        self.running_jobs.remove(&job_id);
        self.job_resources.remove(&job_id);
    }

    fn decrement_resources(&mut self, rr: &ResourceRequirementsModel) {
        let job_memory_gb = convert_memory_string_to_gb(&rr.memory);
        self.resources.memory_gb -= job_memory_gb;
        self.resources.num_cpus -= rr.num_cpus;
        self.resources.num_gpus -= rr.num_gpus;
        assert!(self.resources.memory_gb >= 0.0);
        assert!(self.resources.num_cpus >= 0);
        assert!(self.resources.num_gpus >= 0);
    }

    fn increment_resources(&mut self, rr: &ResourceRequirementsModel) {
        let job_memory_gb = convert_memory_string_to_gb(&rr.memory);
        self.resources.memory_gb += job_memory_gb;
        self.resources.num_cpus += rr.num_cpus;
        self.resources.num_gpus += rr.num_gpus;
        assert!(self.resources.memory_gb <= self.orig_resources.memory_gb);
        assert!(self.resources.num_cpus <= self.orig_resources.num_cpus);
        assert!(self.resources.num_gpus <= self.orig_resources.num_gpus);
    }

    fn run_ready_jobs_based_on_resources(&mut self) {
        let limit = self.resources.num_cpus;
        match utils::send_with_retries(
            &self.config,
            || {
                default_api::claim_jobs_based_on_resources(
                    &self.config,
                    self.workflow_id,
                    &self.resources,
                    limit,
                    Some(self.rules.jobs_sort_method),
                )
            },
            self.rules.compute_node_wait_for_healthy_database_minutes,
        ) {
            Ok(response) => {
                let jobs = response.jobs.unwrap_or_default();
                if jobs.is_empty() {
                    debug!("No ready jobs found");
                    return;
                }
                if jobs.len() > limit as usize {
                    panic!(
                        "Bug in server: too many jobs returned. limit: {}, returned: {}",
                        limit,
                        jobs.len()
                    );
                }
                debug!("Found {} ready jobs to execute", jobs.len());

                for job in jobs {
                    let job_id = job.id.expect("Job must have an ID");
                    let rr_id = job
                        .resource_requirements_id
                        .expect("Job must have a resource_requirements_id");
                    let mut async_job = AsyncCliCommand::new(job);

                    let job_rr = match utils::send_with_retries(
                        &self.config,
                        || default_api::get_resource_requirements(&self.config, rr_id),
                        self.rules.compute_node_wait_for_healthy_database_minutes,
                    ) {
                        Ok(rr) => rr,
                        Err(e) => {
                            error!(
                                "Error getting resource requirements for job {}: {}",
                                job_id, e
                            );
                            panic!("Failed to get resource requirements");
                        }
                    };

                    // Mark job as started in the database before actually starting it
                    match utils::send_with_retries(
                        &self.config,
                        || {
                            default_api::start_job(
                                &self.config,
                                job_id,
                                self.run_id,
                                self.compute_node_id,
                                None,
                            )
                        },
                        self.rules.compute_node_wait_for_healthy_database_minutes,
                    ) {
                        Ok(_) => {
                            debug!("Successfully marked job {} as started in database", job_id);
                        }
                        Err(e) => {
                            panic!(
                                "Failed to mark job {} as started in database after retries: {}",
                                job_id, e
                            );
                        }
                    }

                    match async_job.start(&self.output_dir, self.resource_monitor.as_ref()) {
                        Ok(()) => {
                            info!("Started job {}", job_id);
                            self.running_jobs.insert(job_id, async_job);
                            self.decrement_resources(&job_rr);
                            self.job_resources.insert(job_id, job_rr);
                        }
                        Err(e) => {
                            error!("Error starting job {}: {}", job_id, e);
                            continue;
                        }
                    }
                }
            }
            Err(err) => {
                error!("Failed to prepare jobs for submission: {}", err);
                match utils::send_with_retries(
                    &self.config,
                    || {
                        default_api::claim_jobs_based_on_resources(
                            &self.config,
                            self.workflow_id,
                            &self.resources,
                            limit,
                            Some(self.rules.jobs_sort_method),
                        )
                    },
                    self.rules.compute_node_wait_for_healthy_database_minutes,
                ) {
                    Ok(_) => {
                        info!("Successfully prepared jobs after retry");
                    }
                    Err(retry_err) => {
                        error!(
                            "Failed to prepare jobs for submission after retries: {}",
                            retry_err
                        );
                    }
                }
            }
        }
    }

    fn run_ready_jobs_based_on_user_parallelism(&mut self) {
        let limit = self
            .max_parallel_jobs
            .expect("max_parallel_jobs must be set")
            - self.running_jobs.len() as i64;
        match utils::send_with_retries(
            &self.config,
            || default_api::claim_next_jobs(&self.config, self.workflow_id, Some(limit), None),
            self.rules.compute_node_wait_for_healthy_database_minutes,
        ) {
            Ok(response) => {
                let jobs = response.jobs.unwrap_or_default();
                if jobs.is_empty() {
                    return;
                }
                if jobs.len() > limit as usize {
                    panic!(
                        "Bug in server: too many jobs returned. limit: {}, returned: {}",
                        limit,
                        jobs.len()
                    );
                }
                info!("Found {} ready jobs to execute", jobs.len());

                // Start each job asynchronously
                for job in jobs {
                    let job_id = job.id.expect("Job must have an ID");
                    let mut async_job = AsyncCliCommand::new(job);

                    // Mark job as started in the database before actually starting it
                    match utils::send_with_retries(
                        &self.config,
                        || {
                            default_api::start_job(
                                &self.config,
                                job_id,
                                self.run_id,
                                self.compute_node_id,
                                None,
                            )
                        },
                        self.rules.compute_node_wait_for_healthy_database_minutes,
                    ) {
                        Ok(_) => {
                            debug!("Successfully marked job {} as started in database", job_id);
                        }
                        Err(e) => {
                            error!(
                                "Failed to mark job {} as started in database after retries: {}",
                                job_id, e
                            );
                            // Skip this job if we can't mark it as started
                            continue;
                        }
                    }

                    match async_job.start(&self.output_dir, self.resource_monitor.as_ref()) {
                        Ok(()) => {
                            info!("Started job {}", job_id);
                            self.running_jobs.insert(job_id, async_job);
                        }
                        Err(e) => {
                            error!("Error starting job {}: {}", job_id, e);
                            continue;
                        }
                    }
                }
            }
            Err(err) => {
                error!(
                    "Failed to prepare jobs for submission after retries: {}",
                    err
                );
                panic!("Failed to prepare jobs for submission after retries");
            }
        }
    }

    /// Execute all on_workflow_start actions before the main loop begins
    fn execute_workflow_start_actions(&mut self) {
        info!("Checking for on_workflow_start actions");

        // Get pending on_workflow_start actions
        let pending_actions = match utils::send_with_retries(
            &self.config,
            || -> Result<Vec<crate::models::WorkflowActionModel>, Box<dyn std::error::Error>> {
                let actions = default_api::get_pending_actions(
                    &self.config,
                    self.workflow_id,
                    Some(vec!["on_workflow_start".to_string()]),
                )?;
                Ok(actions)
            },
            self.rules.compute_node_wait_for_healthy_database_minutes,
        ) {
            Ok(actions) => actions,
            Err(e) => {
                error!("Failed to get pending actions: {}", e);
                return;
            }
        };

        // Execute all on_workflow_start actions
        for action in pending_actions {
            let action_id = match action.id {
                Some(id) => id,
                None => {
                    error!("Action missing id field");
                    continue;
                }
            };

            // Check if this job runner can handle this action before claiming
            if !self.can_handle_action(&action) {
                debug!(
                    "on_workflow_start action {} cannot be handled by this job runner, skipping",
                    action_id
                );
                continue;
            }

            // Try to atomically claim this action
            let claimed = match utils::claim_action(
                &self.config,
                self.workflow_id,
                action_id,
                self.compute_node_id,
                self.rules.compute_node_wait_for_healthy_database_minutes,
            ) {
                Ok(claimed) => claimed,
                Err(e) => {
                    error!(
                        "Error claiming on_workflow_start action {}: {}",
                        action_id, e
                    );
                    continue;
                }
            };

            if !claimed {
                debug!(
                    "on_workflow_start action {} already claimed by another runner",
                    action_id
                );
                continue;
            }

            // We claimed it! Execute the action
            info!("Executing on_workflow_start action {}", action_id);
            if let Err(e) = self.execute_action(&action) {
                error!(
                    "Failed to execute on_workflow_start action {}: {}",
                    action_id, e
                );
            }
        }
    }

    /// Execute all on_worker_start actions before the main loop begins
    fn execute_worker_start_actions(&mut self) {
        info!("Checking for on_worker_start actions");

        // Get pending on_worker_start actions
        let pending_actions = match utils::send_with_retries(
            &self.config,
            || -> Result<Vec<crate::models::WorkflowActionModel>, Box<dyn std::error::Error>> {
                let actions = default_api::get_pending_actions(
                    &self.config,
                    self.workflow_id,
                    Some(vec!["on_worker_start".to_string()]),
                )?;
                Ok(actions)
            },
            self.rules.compute_node_wait_for_healthy_database_minutes,
        ) {
            Ok(actions) => actions,
            Err(e) => {
                error!("Failed to get pending actions: {}", e);
                return;
            }
        };

        // Execute all on_worker_start actions
        for action in pending_actions {
            let action_id = match action.id {
                Some(id) => id,
                None => {
                    error!("Action missing id field");
                    continue;
                }
            };

            // Check if this job runner can handle this action before claiming
            if !self.can_handle_action(&action) {
                debug!(
                    "on_worker_start action {} cannot be handled by this job runner, skipping",
                    action_id
                );
                continue;
            }

            // Try to atomically claim this action
            let claimed = match utils::claim_action(
                &self.config,
                self.workflow_id,
                action_id,
                self.compute_node_id,
                self.rules.compute_node_wait_for_healthy_database_minutes,
            ) {
                Ok(claimed) => claimed,
                Err(e) => {
                    // Not fatal - just log and continue
                    error!("Error claiming on_worker_start action {}: {}", action_id, e);
                    continue;
                }
            };

            if !claimed {
                debug!(
                    "on_worker_start action {} already claimed by another runner",
                    action_id
                );
                continue;
            }

            // We claimed it! Execute the action
            info!("Executing on_worker_start action {}", action_id);
            if let Err(e) = self.execute_action(&action) {
                // Not fatal - just log and continue
                error!(
                    "Failed to execute on_worker_start action {}: {}",
                    action_id, e
                );
            }
        }
    }

    /// Execute all on_worker_complete actions after the main loop ends
    fn execute_worker_complete_actions(&mut self) {
        info!("Checking for on_worker_complete actions");

        // Get pending on_worker_complete actions
        let pending_actions = match utils::send_with_retries(
            &self.config,
            || -> Result<Vec<crate::models::WorkflowActionModel>, Box<dyn std::error::Error>> {
                let actions = default_api::get_pending_actions(
                    &self.config,
                    self.workflow_id,
                    Some(vec!["on_worker_complete".to_string()]),
                )?;
                Ok(actions)
            },
            self.rules.compute_node_wait_for_healthy_database_minutes,
        ) {
            Ok(actions) => actions,
            Err(e) => {
                error!("Failed to get pending actions: {}", e);
                return;
            }
        };

        // Execute all on_worker_complete actions
        for action in pending_actions {
            let action_id = match action.id {
                Some(id) => id,
                None => {
                    error!("Action missing id field");
                    continue;
                }
            };

            // Check if this job runner can handle this action before claiming
            if !self.can_handle_action(&action) {
                debug!(
                    "on_worker_complete action {} cannot be handled by this job runner, skipping",
                    action_id
                );
                continue;
            }

            // Try to atomically claim this action
            let claimed = match utils::claim_action(
                &self.config,
                self.workflow_id,
                action_id,
                self.compute_node_id,
                self.rules.compute_node_wait_for_healthy_database_minutes,
            ) {
                Ok(claimed) => claimed,
                Err(e) => {
                    // Not fatal - just log and continue
                    error!(
                        "Error claiming on_worker_complete action {}: {}",
                        action_id, e
                    );
                    continue;
                }
            };

            if !claimed {
                debug!(
                    "on_worker_complete action {} already claimed by another runner",
                    action_id
                );
                continue;
            }

            // We claimed it! Execute the action
            info!("Executing on_worker_complete action {}", action_id);
            if let Err(e) = self.execute_action(&action) {
                // Not fatal - just log and continue
                error!(
                    "Failed to execute on_worker_complete action {}: {}",
                    action_id, e
                );
            }
        }
    }

    /// Check for pending workflow actions and execute them if their trigger conditions are met
    fn check_and_execute_actions(&mut self) {
        // Get pending on_jobs_ready and on_jobs_complete actions
        let pending_actions = match utils::send_with_retries(
            &self.config,
            || -> Result<Vec<crate::models::WorkflowActionModel>, Box<dyn std::error::Error>> {
                let actions = default_api::get_pending_actions(
                    &self.config,
                    self.workflow_id,
                    Some(vec![
                        "on_jobs_ready".to_string(),
                        "on_jobs_complete".to_string(),
                    ]),
                )?;
                Ok(actions)
            },
            self.rules.compute_node_wait_for_healthy_database_minutes,
        ) {
            Ok(actions) => {
                if !actions.is_empty() {
                    debug!(
                        "Found {} pending action(s) (trigger_types: on_jobs_ready, on_jobs_complete)",
                        actions.len()
                    );
                }
                actions
            }
            Err(e) => {
                error!("Failed to get pending actions: {}", e);
                return;
            }
        };

        // Execute triggered actions
        // Note: The server now handles trigger detection server-side by setting triggered=1
        // when conditions are met, so we only need to claim and execute actions that are already triggered
        for action in pending_actions {
            let action_id = match action.id {
                Some(id) => id,
                None => {
                    error!("Action missing id field");
                    continue;
                }
            };

            let trigger_type = &action.trigger_type;

            // Check if this job runner can handle this action before claiming
            if !self.can_handle_action(&action) {
                debug!(
                    "Action {} cannot be handled by this job runner, skipping",
                    action_id
                );
                continue;
            }

            // Try to atomically claim this action
            let claimed = match utils::claim_action(
                &self.config,
                self.workflow_id,
                action_id,
                self.compute_node_id,
                self.rules.compute_node_wait_for_healthy_database_minutes,
            ) {
                Ok(claimed) => claimed,
                Err(e) => {
                    error!("Error claiming action {}: {}", action_id, e);
                    continue;
                }
            };

            if !claimed {
                debug!("Action {} already claimed by another runner", action_id);
                continue;
            }

            info!("Executing action {} (trigger: {})", action_id, trigger_type);
            if let Err(e) = self.execute_action(&action) {
                error!("Failed to execute action {}: {}", action_id, e);
            }
        }
    }

    /// Check if this job runner can handle the given action
    /// Job runners can handle:
    /// - run_commands actions (always)
    /// - schedule_nodes actions (including slurm)
    fn can_handle_action(&self, action: &crate::models::WorkflowActionModel) -> bool {
        let action_type = &action.action_type;

        match action_type.as_str() {
            "run_commands" => true,
            "schedule_nodes" => {
                // Check scheduler_type in action_config
                let scheduler_type = action
                    .action_config
                    .get("scheduler_type")
                    .and_then(|v| v.as_str())
                    .unwrap_or("");

                // Job runners can handle slurm schedule_nodes using schedule_slurm_nodes_for_action
                scheduler_type == "slurm"
            }
            _ => false,
        }
    }

    /// Execute a workflow action
    fn execute_action(
        &self,
        action: &crate::models::WorkflowActionModel,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let action_type = &action.action_type;
        let action_config = &action.action_config;

        match action_type.as_str() {
            "run_commands" => {
                let commands = action_config
                    .get("commands")
                    .and_then(|v| v.as_array())
                    .ok_or("run_commands action missing commands array")?;

                for command_value in commands {
                    let command = command_value.as_str().ok_or("Command must be a string")?;

                    info!("Executing command: {}", command);

                    // Execute the command using std::process::Command
                    let output = if cfg!(target_os = "windows") {
                        std::process::Command::new("cmd")
                            .arg("/C")
                            .arg(command)
                            .current_dir(&self.output_dir)
                            .output()?
                    } else {
                        std::process::Command::new("sh")
                            .arg("-c")
                            .arg(command)
                            .current_dir(&self.output_dir)
                            .output()?
                    };

                    if output.status.success() {
                        let stdout = String::from_utf8_lossy(&output.stdout);
                        if !stdout.is_empty() {
                            info!("Command output: {}", stdout.trim());
                        }
                    } else {
                        let stderr = String::from_utf8_lossy(&output.stderr);
                        error!("Command failed: {}", stderr);
                        return Err(format!(
                            "Command failed with exit code: {:?}",
                            output.status.code()
                        )
                        .into());
                    }
                }

                Ok(())
            }
            "schedule_nodes" => {
                info!("schedule_nodes action triggered");

                // Extract configuration
                let scheduler_type = action_config
                    .get("scheduler_type")
                    .and_then(|v| v.as_str())
                    .ok_or("schedule_nodes action missing scheduler_type")?;

                let scheduler_id = action_config
                    .get("scheduler_id")
                    .and_then(|v| v.as_i64())
                    .ok_or("schedule_nodes action missing scheduler_id")?;

                let num_allocations = action_config
                    .get("num_allocations")
                    .and_then(|v| v.as_i64())
                    .unwrap_or(1) as i32;

                let start_one_worker_per_node = action_config
                    .get("start_one_worker_per_node")
                    .and_then(|v| v.as_bool())
                    .unwrap_or(false);

                let start_server_on_head_node = action_config
                    .get("start_server_on_head_node")
                    .and_then(|v| v.as_bool())
                    .unwrap_or(false);

                let max_parallel_jobs = action_config
                    .get("max_parallel_jobs")
                    .and_then(|v| v.as_i64())
                    .map(|v| v as i32);

                info!(
                    "Scheduling {} compute nodes (scheduler_type={}, scheduler_id={})",
                    num_allocations, scheduler_type, scheduler_id
                );

                if scheduler_type == "slurm" {
                    // Use the same function as WorkflowManager for Slurm scheduling
                    match crate::client::commands::slurm::schedule_slurm_nodes_for_action(
                        &self.config,
                        self.workflow_id,
                        scheduler_id,
                        num_allocations,
                        "worker",
                        "output",
                        60, // poll_interval
                        max_parallel_jobs,
                        start_one_worker_per_node,
                        start_server_on_head_node,
                        false, // keep_submission_scripts
                    ) {
                        Ok(()) => {
                            info!("Successfully scheduled {} Slurm job(s)", num_allocations);
                            Ok(())
                        }
                        Err(err) => {
                            error!("Failed to schedule Slurm nodes: {}", err);
                            Err(format!("Failed to schedule Slurm nodes: {}", err).into())
                        }
                    }
                } else {
                    error!("scheduler_type = {} is not supported", scheduler_type);
                    Err(format!("Unsupported scheduler_type: {}", scheduler_type).into())
                }
            }
            _ => Err(format!("Unknown action type: {}", action_type).into()),
        }
    }
}

#[derive(Debug)]
struct ComputeNodeRules {
    /// Inform all compute nodes to shut down this number of seconds before the expiration time. This allows torc to send SIGTERM to all job processes and set all statuses to terminated. Increase the time in cases where the job processes handle SIGTERM and need more time to gracefully shut down. Set the value to 0 to maximize the time given to jobs. If not set, take the database's default value of 60 seconds.
    pub compute_node_expiration_buffer_seconds: i64,
    /// Inform all compute nodes to wait for new jobs for this time period before exiting. Does not apply if the workflow is complete.
    // pub compute_node_wait_for_new_jobs_seconds: u64,
    /// Inform all compute nodes to ignore workflow completions and hold onto allocations indefinitely. Useful for debugging failed jobs and possibly dynamic workflows where jobs get added after starting.
    pub compute_node_ignore_workflow_completion: bool,
    /// Inform all compute nodes to wait this number of minutes if the database becomes unresponsive.
    pub compute_node_wait_for_healthy_database_minutes: u64,
    pub jobs_sort_method: ClaimJobsSortMethod,
}

impl ComputeNodeRules {
    pub fn new(
        compute_node_expiration_buffer_seconds: Option<i64>,
        // compute_node_wait_for_new_jobs_seconds: Option<i64>,
        compute_node_ignore_workflow_completion: Option<bool>,
        compute_node_wait_for_healthy_database_minutes: Option<i64>,
        jobs_sort_method: Option<ClaimJobsSortMethod>,
    ) -> Self {
        ComputeNodeRules {
            compute_node_expiration_buffer_seconds: compute_node_expiration_buffer_seconds
                .unwrap_or(60) as i64,
            // compute_node_wait_for_new_jobs_seconds: compute_node_wait_for_new_jobs_seconds
            //     .unwrap_or(0) as u64,
            compute_node_ignore_workflow_completion: compute_node_ignore_workflow_completion
                .unwrap_or(false),
            compute_node_wait_for_healthy_database_minutes:
                compute_node_wait_for_healthy_database_minutes.unwrap_or(20) as u64,
            jobs_sort_method: jobs_sort_method.unwrap_or(ClaimJobsSortMethod::GpusRuntimeMemory),
        }
    }
}

/// Convert memory string to bytes
/// Supports formats like "1024", "1k", "2M", "3g", "4T" (case insensitive)
/// k/K = KiB (1024 bytes), m/M = MiB, g/G = GiB, t/T = TiB
fn convert_memory_string_to_gb(memory_str: &str) -> f64 {
    // Check cache first
    let cached_result = MEMORY_CACHE.with(|cache| cache.borrow().get(memory_str).copied());

    if let Some(cached_value) = cached_result {
        return cached_value;
    }

    // Calculate the value if not in cache
    let result = match convert_memory_string_to_bytes(memory_str) {
        Ok(bytes) => bytes as f64 / GB as f64,
        Err(e) => {
            panic!("Error converting memory string to bytes: {}", e);
        }
    };

    // Store in cache
    MEMORY_CACHE.with(|cache| {
        cache.borrow_mut().insert(memory_str.to_string(), result);
    });

    result
}

/// Convert memory string to bytes
/// Supports formats like "1024", "1k", "2M", "3g", "4T" (case insensitive)
/// k/K = KiB (1024 bytes), m/M = MiB, g/G = GiB, t/T = TiB
fn convert_memory_string_to_bytes(memory_str: &str) -> Result<i64, String> {
    // TODO: This is repeated on the server. Remove duplication.
    let memory_str = memory_str.trim();

    if memory_str.is_empty() {
        return Err("Memory string cannot be empty".to_string());
    }

    // Check if the last character is a unit
    let (number_part, multiplier) = if let Some(last_char) = memory_str.chars().last() {
        if last_char.is_alphabetic() {
            let number_part = &memory_str[..memory_str.len() - 1];
            let multiplier = match last_char.to_ascii_lowercase() {
                'k' => 1024_i64,
                'm' => 1024_i64.pow(2),
                'g' => 1024_i64.pow(3),
                't' => 1024_i64.pow(4),
                _ => return Err(format!("Invalid memory unit: {}", last_char)),
            };
            (number_part, multiplier)
        } else {
            (memory_str, 1_i64)
        }
    } else {
        return Err("Memory string cannot be empty".to_string());
    };

    // Parse the number part
    let number: i64 = number_part
        .parse()
        .map_err(|_| format!("Invalid number in memory string: {}", number_part))?;

    if number < 0 {
        return Err("Memory size cannot be negative".to_string());
    }

    // Calculate total bytes, checking for overflow
    number
        .checked_mul(multiplier)
        .ok_or_else(|| "Memory size too large, would cause overflow".to_string())
}
