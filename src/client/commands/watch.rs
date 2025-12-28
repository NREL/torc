//! Watch command for monitoring workflows with automatic failure recovery

use chrono::Utc;
use env_logger::Builder;
use log::{LevelFilter, debug, error, info, warn};
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use std::time::Duration;

use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::utils;

// Re-export shared recovery types and functions from the recover module
use super::recover::{
    RecoveryResult, apply_recovery_heuristics, diagnose_failures, regenerate_and_submit,
    reinitialize_workflow, reset_failed_jobs, run_recovery_hook,
};
use crate::client::report_models::ResourceUtilizationReport;

/// Default wait time for database connectivity issues (in minutes)
const WAIT_FOR_HEALTHY_DATABASE_MINUTES: u64 = 20;

/// Execute an API call with automatic retries for network errors.
/// This wraps utils::send_with_retries with a default timeout.
fn send_with_retries<T, E, F>(config: &Configuration, api_call: F) -> Result<T, E>
where
    F: FnMut() -> Result<T, E>,
    E: std::fmt::Display,
{
    utils::send_with_retries(config, api_call, WAIT_FOR_HEALTHY_DATABASE_MINUTES)
}
use crate::client::commands::pagination::{
    ComputeNodeListParams, JobListParams, ScheduledComputeNodeListParams, paginate_compute_nodes,
    paginate_jobs, paginate_scheduled_compute_nodes,
};
use crate::client::hpc::common::HpcJobStatus;
use crate::client::hpc::hpc_interface::HpcInterface;
use crate::client::hpc::slurm_interface::SlurmInterface;
use crate::client::log_paths::get_watch_log_file;
use crate::models;

/// A writer that writes to both stdout and a file
struct MultiWriter {
    stdout: std::io::Stdout,
    file: File,
}

impl Write for MultiWriter {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        self.stdout.write_all(buf)?;
        self.file.write(buf)
    }

    fn flush(&mut self) -> std::io::Result<()> {
        self.stdout.flush()?;
        self.file.flush()
    }
}

/// Return code used when failing jobs orphaned by an ungraceful job runner termination.
/// This value (-128) is chosen to be:
/// - Negative, clearly distinguishing it from normal exit codes
/// - Related to signal convention (128 is the base for signal exits)
/// - Easy to identify in logs and results
pub const ORPHANED_JOB_RETURN_CODE: i64 = -128;

/// Arguments for the watch command
pub struct WatchArgs {
    pub workflow_id: i64,
    pub poll_interval: u64,
    pub recover: bool,
    pub max_retries: u32,
    pub memory_multiplier: f64,
    pub runtime_multiplier: f64,
    pub retry_unknown: bool,
    pub recovery_hook: Option<String>,
    pub output_dir: PathBuf,
    pub show_job_counts: bool,
    pub log_level: String,
}

/// Get job counts by status for a workflow
fn get_job_counts(
    config: &Configuration,
    workflow_id: i64,
) -> Result<HashMap<String, i64>, String> {
    let jobs = paginate_jobs(config, workflow_id, JobListParams::new())
        .map_err(|e| format!("Failed to list jobs: {}", e))?;
    let mut counts = HashMap::new();

    for job in &jobs {
        if let Some(status) = &job.status {
            let status_str = format!("{:?}", status);
            *counts.entry(status_str).or_insert(0) += 1;
        }
    }

    Ok(counts)
}

/// Detect and fail orphaned Slurm jobs by checking Slurm as the source of truth.
///
/// This function:
/// 1. Gets scheduled compute nodes with status="active" and scheduler_type="slurm"
/// 2. For each, uses SlurmInterface to check if the Slurm job is still running
/// 3. If not running, finds all compute nodes associated with that scheduled compute node
/// 4. Finds all jobs with active_compute_node_id matching those compute nodes
/// 5. Fails those jobs with the orphaned return code
///
/// Returns the number of jobs that were failed.
fn fail_orphaned_slurm_jobs(config: &Configuration, workflow_id: i64) -> Result<usize, String> {
    // Get workflow status to retrieve run_id
    let workflow_status = default_api::get_workflow_status(config, workflow_id)
        .map_err(|e| format!("Failed to get workflow status: {}", e))?;
    let run_id = workflow_status.run_id;

    // Get all scheduled compute nodes with status="active" and scheduler_type="slurm"
    let scheduled_nodes = paginate_scheduled_compute_nodes(
        config,
        workflow_id,
        ScheduledComputeNodeListParams::new().with_status("active".to_string()),
    )
    .map_err(|e| format!("Failed to list scheduled compute nodes: {}", e))?;

    // Filter for Slurm scheduler type
    let slurm_nodes: Vec<_> = scheduled_nodes
        .iter()
        .filter(|node| node.scheduler_type.to_lowercase() == "slurm")
        .collect();

    if slurm_nodes.is_empty() {
        return Ok(0);
    }

    // Create SlurmInterface to check job status
    let slurm = match SlurmInterface::new() {
        Ok(s) => s,
        Err(e) => {
            warn!("Could not create SlurmInterface: {}", e);
            return Ok(0);
        }
    };

    let mut total_failed = 0;

    for scheduled_node in slurm_nodes {
        let slurm_job_id = scheduled_node.scheduler_id.to_string();
        let scheduled_compute_node_id = match scheduled_node.id {
            Some(id) => id,
            None => continue,
        };

        // Check Slurm status
        let slurm_status = match slurm.get_status(&slurm_job_id) {
            Ok(info) => info.status,
            Err(e) => {
                warn!(
                    "Error checking Slurm status for job {}: {}",
                    slurm_job_id, e
                );
                continue;
            }
        };

        // If Slurm job is still running or queued, skip it
        if slurm_status == HpcJobStatus::Running || slurm_status == HpcJobStatus::Queued {
            continue;
        }

        // Slurm job is not running (Complete, Unknown, or None means it's gone)
        info!(
            "Slurm job {} is no longer running (status: {:?}), checking for orphaned jobs",
            slurm_job_id, slurm_status
        );

        // Find all compute nodes associated with this scheduled compute node
        let compute_nodes = paginate_compute_nodes(
            config,
            workflow_id,
            ComputeNodeListParams::new().with_scheduled_compute_node_id(scheduled_compute_node_id),
        )
        .map_err(|e| format!("Failed to list compute nodes: {}", e))?;

        for compute_node in &compute_nodes {
            let compute_node_id = match compute_node.id {
                Some(id) => id,
                None => continue,
            };

            // Find all jobs with this active_compute_node_id
            let orphaned_jobs = paginate_jobs(
                config,
                workflow_id,
                JobListParams::new().with_active_compute_node_id(compute_node_id),
            )
            .map_err(|e| format!("Failed to list jobs for compute node: {}", e))?;

            if orphaned_jobs.is_empty() {
                continue;
            }

            info!(
                "Found {} orphaned job(s) from Slurm job {} (compute node {})",
                orphaned_jobs.len(),
                slurm_job_id,
                compute_node_id
            );

            // Fail each orphaned job
            for job in &orphaned_jobs {
                let job_id = match job.id {
                    Some(id) => id,
                    None => continue,
                };

                // Create a result for the orphaned job
                let result = models::ResultModel::new(
                    job_id,
                    workflow_id,
                    run_id,
                    compute_node_id,
                    ORPHANED_JOB_RETURN_CODE,
                    0.0,
                    Utc::now().to_rfc3339(),
                    models::JobStatus::Failed,
                );

                // Mark the job as failed
                match default_api::complete_job(
                    config,
                    job_id,
                    models::JobStatus::Failed,
                    run_id,
                    result,
                ) {
                    Ok(_) => {
                        info!(
                            "  Marked orphaned job {} ({}) as failed (Slurm job {} no longer running)",
                            job_id, job.name, slurm_job_id
                        );
                        total_failed += 1;
                    }
                    Err(e) => {
                        warn!("  Failed to mark job {} as failed: {}", job_id, e);
                    }
                }
            }

            // Mark this compute node as inactive since its Slurm job is gone
            let mut updated_node = compute_node.clone();
            updated_node.is_active = Some(false);
            match default_api::update_compute_node(config, compute_node_id, updated_node) {
                Ok(_) => {
                    debug!(
                        "Marked compute node {} as inactive (Slurm job {} no longer running)",
                        compute_node_id, slurm_job_id
                    );
                }
                Err(e) => {
                    warn!(
                        "Failed to mark compute node {} as inactive: {}",
                        compute_node_id, e
                    );
                }
            }
        }

        // Update the scheduled compute node status to "complete" since the Slurm job is done
        match default_api::update_scheduled_compute_node(
            config,
            scheduled_compute_node_id,
            models::ScheduledComputeNodesModel::new(
                workflow_id,
                scheduled_node.scheduler_id,
                scheduled_node.scheduler_config_id,
                scheduled_node.scheduler_type.clone(),
                "complete".to_string(),
            ),
        ) {
            Ok(_) => {
                info!(
                    "Updated scheduled compute node {} status to 'complete'",
                    scheduled_compute_node_id
                );
            }
            Err(e) => {
                warn!(
                    "Failed to update scheduled compute node {} status: {}",
                    scheduled_compute_node_id, e
                );
            }
        }
    }

    if total_failed > 0 {
        info!(
            "Marked {} orphaned Slurm job(s) as failed (return code {})",
            total_failed, ORPHANED_JOB_RETURN_CODE
        );
    }

    Ok(total_failed)
}

/// Check for pending Slurm jobs that no longer exist and mark them as complete.
///
/// This handles the case where a Slurm job was submitted but cancelled or failed
/// before it ever started running. In this scenario:
/// - The ScheduledComputeNode remains in "pending" status
/// - The Slurm job no longer exists in the queue
///
/// This function:
/// 1. Gets all scheduled compute nodes with status="pending" and scheduler_type="slurm"
/// 2. Checks if the Slurm job still exists
/// 3. If the Slurm job doesn't exist, marks the ScheduledComputeNode as "complete"
///
/// Returns the number of pending nodes that were cleaned up.
fn cleanup_dead_pending_slurm_jobs(
    config: &Configuration,
    workflow_id: i64,
) -> Result<usize, String> {
    // Get all scheduled compute nodes with status="pending"
    let scheduled_nodes = paginate_scheduled_compute_nodes(
        config,
        workflow_id,
        ScheduledComputeNodeListParams::new().with_status("pending".to_string()),
    )
    .map_err(|e| format!("Failed to list pending scheduled compute nodes: {}", e))?;

    // Filter for Slurm scheduler type
    let slurm_nodes: Vec<_> = scheduled_nodes
        .iter()
        .filter(|node| node.scheduler_type.to_lowercase() == "slurm")
        .collect();

    if slurm_nodes.is_empty() {
        return Ok(0);
    }

    // Create SlurmInterface to check job status
    let slurm = match SlurmInterface::new() {
        Ok(s) => s,
        Err(e) => {
            debug!(
                "Could not create SlurmInterface for pending job check: {}",
                e
            );
            return Ok(0);
        }
    };

    let mut total_cleaned = 0;

    for scheduled_node in slurm_nodes {
        let slurm_job_id = scheduled_node.scheduler_id.to_string();
        let scheduled_compute_node_id = match scheduled_node.id {
            Some(id) => id,
            None => continue,
        };

        // Check Slurm status
        let slurm_status = match slurm.get_status(&slurm_job_id) {
            Ok(info) => info.status,
            Err(e) => {
                debug!(
                    "Error checking Slurm status for pending job {}: {}",
                    slurm_job_id, e
                );
                continue;
            }
        };

        // If Slurm job is still queued or running, skip it (it's still valid)
        if slurm_status == HpcJobStatus::Queued || slurm_status == HpcJobStatus::Running {
            continue;
        }

        // If the job completed normally, it will transition through the normal path
        // We only care about jobs that no longer exist (None/Unknown)
        if slurm_status == HpcJobStatus::Complete {
            // Job completed but never started running in our system - this is unusual
            // but we should mark it as complete so it doesn't block
            info!(
                "Slurm job {} completed but was still pending in our system, marking as complete",
                slurm_job_id
            );
        } else {
            // Job no longer exists (None/Unknown) - was cancelled or failed before starting
            info!(
                "Pending Slurm job {} no longer exists (status: {:?}), marking as complete",
                slurm_job_id, slurm_status
            );
        }

        // Update the scheduled compute node status to "complete"
        match default_api::update_scheduled_compute_node(
            config,
            scheduled_compute_node_id,
            models::ScheduledComputeNodesModel::new(
                workflow_id,
                scheduled_node.scheduler_id,
                scheduled_node.scheduler_config_id,
                scheduled_node.scheduler_type.clone(),
                "complete".to_string(),
            ),
        ) {
            Ok(_) => {
                info!(
                    "Updated pending scheduled compute node {} (Slurm job {}) status to 'complete'",
                    scheduled_compute_node_id, slurm_job_id
                );
                total_cleaned += 1;
            }
            Err(e) => {
                warn!(
                    "Failed to update scheduled compute node {} status: {}",
                    scheduled_compute_node_id, e
                );
            }
        }
    }

    if total_cleaned > 0 {
        info!("Cleaned up {} dead pending Slurm job(s)", total_cleaned);
    }

    Ok(total_cleaned)
}

/// Check if there are any active workers (compute nodes or scheduled compute nodes).
/// This is used after workflow completion to wait for all workers to exit before
/// proceeding with recovery actions. Workers need to complete their cleanup routines.
fn has_active_workers(config: &Configuration, workflow_id: i64) -> bool {
    // Check for active compute nodes (is_active=true)
    if let Ok(response) = send_with_retries(config, || {
        default_api::list_compute_nodes(
            config,
            workflow_id,
            None,       // offset
            Some(1),    // limit - just need one
            None,       // sort_by
            None,       // reverse_sort
            None,       // hostname
            Some(true), // is_active = true
            None,       // scheduled_compute_node_id
        )
    }) && let Some(nodes) = response.items
        && !nodes.is_empty()
    {
        return true;
    }

    // Also check for any scheduled compute nodes (pending or active)
    // These represent Slurm allocations that haven't fully exited yet
    has_any_scheduled_compute_nodes(config, workflow_id)
}

/// Check if there are any scheduled compute nodes with status pending or active.
/// If there are none, the workflow cannot make progress.
fn has_any_scheduled_compute_nodes(config: &Configuration, workflow_id: i64) -> bool {
    // Check for pending allocations
    if let Ok(response) = send_with_retries(config, || {
        default_api::list_scheduled_compute_nodes(
            config,
            workflow_id,
            None,            // offset
            Some(1),         // limit - just need one
            None,            // sort_by
            None,            // reverse_sort
            None,            // scheduler_id
            None,            // scheduler_config_id
            Some("pending"), // status
        )
    }) && let Some(nodes) = response.items
        && !nodes.is_empty()
    {
        return true;
    }

    // Check for active allocations
    if let Ok(response) = send_with_retries(config, || {
        default_api::list_scheduled_compute_nodes(
            config,
            workflow_id,
            None,           // offset
            Some(1),        // limit - just need one
            None,           // sort_by
            None,           // reverse_sort
            None,           // scheduler_id
            None,           // scheduler_config_id
            Some("active"), // status
        )
    }) && let Some(nodes) = response.items
        && !nodes.is_empty()
    {
        return true;
    }

    false
}

/// Check if there is at least one valid Slurm allocation (pending or running in Slurm).
///
/// This is used to optimize the poll loop: if we have valid allocations, we can skip
/// the expensive per-allocation orphan detection and just sleep.
///
/// Returns true if at least one Slurm allocation is still valid (queued or running).
fn has_valid_slurm_allocation(config: &Configuration, workflow_id: i64) -> bool {
    // Get scheduled compute nodes with status="pending" or "active"
    // We'll sample one from each category to check

    // First check for active allocations
    let active_nodes = send_with_retries(config, || {
        default_api::list_scheduled_compute_nodes(
            config,
            workflow_id,
            None,           // offset
            Some(1),        // limit - just need one
            None,           // sort_by
            None,           // reverse_sort
            None,           // scheduler_id
            None,           // scheduler_config_id
            Some("active"), // status
        )
    });

    if let Ok(response) = active_nodes
        && let Some(nodes) = response.items
    {
        for node in nodes {
            if node.scheduler_type.to_lowercase() == "slurm" {
                // Check if this Slurm job is still running
                if let Ok(slurm) = SlurmInterface::new() {
                    let slurm_job_id = node.scheduler_id.to_string();
                    if let Ok(info) = slurm.get_status(&slurm_job_id)
                        && (info.status == HpcJobStatus::Running
                            || info.status == HpcJobStatus::Queued)
                    {
                        debug!(
                            "Found valid active Slurm allocation {} (status: {:?})",
                            slurm_job_id, info.status
                        );
                        return true;
                    }
                }
            }
        }
    }

    // Check for pending allocations
    let pending_nodes = send_with_retries(config, || {
        default_api::list_scheduled_compute_nodes(
            config,
            workflow_id,
            None,            // offset
            Some(1),         // limit - just need one
            None,            // sort_by
            None,            // reverse_sort
            None,            // scheduler_id
            None,            // scheduler_config_id
            Some("pending"), // status
        )
    });

    if let Ok(response) = pending_nodes
        && let Some(nodes) = response.items
    {
        for node in nodes {
            if node.scheduler_type.to_lowercase() == "slurm" {
                // Check if this Slurm job is still queued
                if let Ok(slurm) = SlurmInterface::new() {
                    let slurm_job_id = node.scheduler_id.to_string();
                    if let Ok(info) = slurm.get_status(&slurm_job_id)
                        && (info.status == HpcJobStatus::Running
                            || info.status == HpcJobStatus::Queued)
                    {
                        debug!(
                            "Found valid pending Slurm allocation {} (status: {:?})",
                            slurm_job_id, info.status
                        );
                        return true;
                    }
                }
            }
        }
    }

    // No valid Slurm allocations found
    debug!("No valid Slurm allocations found");
    false
}

/// Detect and fail orphaned running jobs.
///
/// This handles the case where a job runner (e.g., torc-slurm-job-runner) was killed
/// ungracefully by the scheduler (e.g., Slurm). In this scenario:
/// - Jobs claimed by the runner remain in "running" status
/// - The ScheduledComputeNode remains in "active" status
/// - No active compute nodes exist to process the jobs
///
/// Returns the number of jobs that were failed.
fn fail_orphaned_running_jobs(config: &Configuration, workflow_id: i64) -> Result<usize, String> {
    // Get workflow status to retrieve run_id
    let workflow_status = default_api::get_workflow_status(config, workflow_id)
        .map_err(|e| format!("Failed to get workflow status: {}", e))?;
    let run_id = workflow_status.run_id;

    // Check for active compute nodes
    let active_nodes_response = default_api::list_compute_nodes(
        config,
        workflow_id,
        None,       // offset
        Some(1),    // limit - we only need to know if any exist
        None,       // sort_by
        None,       // reverse_sort
        None,       // hostname
        Some(true), // is_active = true
        None,       // scheduled_compute_node_id
    )
    .map_err(|e| format!("Failed to list active compute nodes: {}", e))?;

    let active_node_count = active_nodes_response.total_count;

    // If there are active compute nodes, jobs are being processed normally
    if active_node_count > 0 {
        return Ok(0);
    }

    // Get all jobs with status=Running
    let running_jobs = paginate_jobs(
        config,
        workflow_id,
        JobListParams::new().with_status(models::JobStatus::Running),
    )
    .map_err(|e| format!("Failed to list running jobs: {}", e))?;

    if running_jobs.is_empty() {
        return Ok(0);
    }

    info!(
        "Detected {} orphaned running job(s) with no active compute nodes",
        running_jobs.len()
    );

    // Get or create a compute node for recording the failure
    // First, try to find any existing compute node for this workflow
    let compute_node_id = match default_api::list_compute_nodes(
        config,
        workflow_id,
        None,    // offset
        Some(1), // limit
        None,    // sort_by
        None,    // reverse_sort
        None,    // hostname
        None,    // is_active - any status
        None,    // scheduled_compute_node_id
    ) {
        Ok(response) => {
            if let Some(nodes) = response.items {
                if let Some(node) = nodes.first() {
                    node.id.unwrap_or(0)
                } else {
                    0
                }
            } else {
                0
            }
        }
        Err(_) => 0,
    };

    // If no compute node exists, create a recovery node
    let compute_node_id = if compute_node_id == 0 {
        match default_api::create_compute_node(
            config,
            models::ComputeNodeModel::new(
                workflow_id,
                "orphan-recovery".to_string(),
                0, // pid
                Utc::now().to_rfc3339(),
                1,   // num_cpus
                1.0, // memory_gb
                0,   // num_gpus
                1,   // num_nodes
                "local".to_string(),
                None, // scheduler
            ),
        ) {
            Ok(node) => node.id.unwrap_or(0),
            Err(e) => {
                warn!("Could not create recovery compute node: {}", e);
                0
            }
        }
    } else {
        compute_node_id
    };

    let mut failed_count = 0;

    for job in &running_jobs {
        let job_id = match job.id {
            Some(id) => id,
            None => continue,
        };

        // Create a result for the orphaned job
        let result = models::ResultModel::new(
            job_id,
            workflow_id,
            run_id,
            compute_node_id,
            ORPHANED_JOB_RETURN_CODE, // Unique return code for orphaned jobs
            0.0,                      // exec_time_minutes - unknown
            Utc::now().to_rfc3339(),  // completion_time
            models::JobStatus::Failed, // status
        );

        // Mark the job as failed
        match default_api::complete_job(config, job_id, models::JobStatus::Failed, run_id, result) {
            Ok(_) => {
                info!(
                    "  Marked orphaned job {} ({}) as failed with return code {}",
                    job_id, job.name, ORPHANED_JOB_RETURN_CODE
                );
                failed_count += 1;
            }
            Err(e) => {
                warn!("  Failed to mark job {} as failed: {}", job_id, e);
            }
        }
    }

    if failed_count > 0 {
        info!(
            "Marked {} orphaned job(s) as failed (return code {})",
            failed_count, ORPHANED_JOB_RETURN_CODE
        );
    }

    Ok(failed_count)
}

/// Poll until workflow is complete, optionally printing status updates.
/// After the workflow is complete, continues to wait until all workers have exited
/// (no active compute nodes and no scheduled compute nodes). This is critical for
/// recovery scenarios to ensure workers complete their cleanup routines before
/// any recovery actions are taken.
fn poll_until_complete(
    config: &Configuration,
    workflow_id: i64,
    poll_interval: u64,
    show_job_counts: bool,
) -> Result<HashMap<String, i64>, String> {
    let mut workflow_complete = false;

    loop {
        // Check if workflow is complete
        if !workflow_complete {
            match send_with_retries(config, || {
                default_api::is_workflow_complete(config, workflow_id)
            }) {
                Ok(response) => {
                    if response.is_complete {
                        info!(
                            "Workflow {} is complete, waiting for workers to exit...",
                            workflow_id
                        );
                        workflow_complete = true;
                        // Don't break yet - wait for workers to exit
                    }
                }
                Err(e) => {
                    return Err(format!("Error checking workflow status: {}", e));
                }
            }
        }

        // If workflow is complete, wait for all workers to exit before returning
        if workflow_complete {
            let workers_active = has_active_workers(config, workflow_id);
            if !workers_active {
                info!("All workers have exited");
                break;
            }
            debug!("Waiting for workers to exit...");
            std::thread::sleep(Duration::from_secs(poll_interval));
            continue;
        }

        // Print current status if requested
        if show_job_counts {
            match get_job_counts(config, workflow_id) {
                Ok(counts) => {
                    let completed = counts.get("Completed").unwrap_or(&0);
                    let running = counts.get("Running").unwrap_or(&0);
                    let ready = counts.get("Ready").unwrap_or(&0);
                    let failed = counts.get("Failed").unwrap_or(&0);
                    let blocked = counts.get("Blocked").unwrap_or(&0);
                    info!(
                        "  ready={}, blocked={}, running={}, completed={}, failed={}",
                        ready, blocked, running, completed, failed
                    );
                }
                Err(e) => {
                    error!("Error getting job counts: {}", e);
                }
            }
        }

        // Optimization: If there's at least one valid Slurm allocation (pending or running),
        // skip the expensive per-allocation orphan detection. This reduces N squeue calls
        // to just 1-2 calls when jobs are queued or running normally.
        if has_valid_slurm_allocation(config, workflow_id) {
            std::thread::sleep(Duration::from_secs(poll_interval));
            continue;
        }

        // No valid Slurm allocations found - check for orphaned jobs
        debug!("No valid Slurm allocations, checking for orphaned jobs...");

        // Check for orphaned Slurm jobs using Slurm as the source of truth.
        // This uses the active_compute_node_id to precisely identify which jobs were
        // being run by each Slurm job, avoiding race conditions.
        match fail_orphaned_slurm_jobs(config, workflow_id) {
            Ok(count) if count > 0 => {
                info!("Orphaned Slurm jobs detected and marked as failed, continuing...");
            }
            Ok(_) => {
                // No orphaned Slurm jobs
            }
            Err(e) => {
                warn!("Error checking for orphaned Slurm jobs: {}", e);
            }
        }

        // Check for pending Slurm jobs that no longer exist (cancelled/failed before starting)
        match cleanup_dead_pending_slurm_jobs(config, workflow_id) {
            Ok(count) if count > 0 => {
                info!("Dead pending Slurm jobs cleaned up, continuing...");
            }
            Ok(_) => {
                // No dead pending Slurm jobs
            }
            Err(e) => {
                warn!("Error checking for dead pending Slurm jobs: {}", e);
            }
        }

        // Check for orphaned running jobs (jobs stuck in "running" with no active compute nodes)
        // This is a fallback for non-Slurm schedulers (local scheduler, etc.)
        match fail_orphaned_running_jobs(config, workflow_id) {
            Ok(count) if count > 0 => {
                info!("Orphaned jobs detected and marked as failed, continuing...");
            }
            Ok(_) => {
                // No orphaned jobs
            }
            Err(e) => {
                warn!("Error checking for orphaned jobs: {}", e);
            }
        }

        // Check if there are any pending or active scheduled compute nodes
        // If not, nothing can make progress and we should exit
        if !has_any_scheduled_compute_nodes(config, workflow_id) {
            warn!("No pending or active scheduled compute nodes found");
            warn!("Workflow cannot make progress without active allocations");
            break;
        }

        std::thread::sleep(Duration::from_secs(poll_interval));
    }

    get_job_counts(config, workflow_id)
}

/// Run the watch command
pub fn run_watch(config: &Configuration, args: &WatchArgs) {
    let hostname = hostname::get()
        .expect("Failed to get hostname")
        .into_string()
        .expect("Hostname is not valid UTF-8");

    // Create output directory if it doesn't exist
    if let Err(e) = std::fs::create_dir_all(&args.output_dir) {
        eprintln!(
            "Error creating output directory {}: {}",
            args.output_dir.display(),
            e
        );
        std::process::exit(1);
    }

    let log_file_path = get_watch_log_file(args.output_dir.clone(), &hostname, args.workflow_id);
    let log_file = match File::create(&log_file_path) {
        Ok(file) => file,
        Err(e) => {
            eprintln!("Error creating log file {}: {}", log_file_path, e);
            std::process::exit(1);
        }
    };

    let multi_writer = MultiWriter {
        stdout: std::io::stdout(),
        file: log_file,
    };

    // Parse log level string to LevelFilter
    let log_level_filter = match args.log_level.to_lowercase().as_str() {
        "error" => LevelFilter::Error,
        "warn" => LevelFilter::Warn,
        "info" => LevelFilter::Info,
        "debug" => LevelFilter::Debug,
        "trace" => LevelFilter::Trace,
        _ => {
            eprintln!(
                "Invalid log level '{}', defaulting to 'info'",
                args.log_level
            );
            LevelFilter::Info
        }
    };

    let mut builder = Builder::from_default_env();
    builder
        .target(env_logger::Target::Pipe(Box::new(multi_writer)))
        .filter_level(log_level_filter)
        .try_init()
        .ok(); // Ignore error if logger is already initialized

    info!("Starting watch command");
    info!("Hostname: {}", hostname);
    info!("Output directory: {}", args.output_dir.display());
    info!("Log file: {}", log_file_path);

    let mut retry_count = 0u32;

    // Early check: verify this workflow has scheduled compute nodes
    // The watch command is designed for Slurm/scheduler-based workflows.
    // For workflows run with `torc run` or `torc remote run`, use those commands directly.
    if !has_any_scheduled_compute_nodes(config, args.workflow_id) {
        error!(
            "No scheduled compute nodes found for workflow {}.",
            args.workflow_id
        );
        error!("");
        error!("The 'watch' command is designed for scheduler-based workflows (e.g., Slurm).");
        error!("For local execution, use: torc run <workflow_id>");
        error!("For remote execution, use: torc remote run <workflow_id>");
        std::process::exit(1);
    }

    info!(
        "Watching workflow {} (poll interval: {}s{}{})",
        args.workflow_id,
        args.poll_interval,
        if args.recover {
            format!(", recover enabled, max retries: {}", args.max_retries)
        } else {
            String::new()
        },
        if args.show_job_counts {
            ", job counts enabled"
        } else {
            ""
        }
    );

    if !args.show_job_counts {
        info!("  (use --show-job-counts to display per-status counts during polling)");
    }

    loop {
        let counts = match poll_until_complete(
            config,
            args.workflow_id,
            args.poll_interval,
            args.show_job_counts,
        ) {
            Ok(c) => c,
            Err(e) => {
                error!("Error: {}", e);
                std::process::exit(1);
            }
        };

        let completed = *counts.get("Completed").unwrap_or(&0);
        let failed = *counts.get("Failed").unwrap_or(&0);
        let canceled = *counts.get("Canceled").unwrap_or(&0);
        let terminated = *counts.get("Terminated").unwrap_or(&0);

        let needs_recovery = failed > 0 || canceled > 0 || terminated > 0;

        if !needs_recovery {
            info!("\n✓ Workflow completed successfully ({} jobs)", completed);
            break;
        }

        warn!("\nWorkflow completed with failures:");
        warn!("  - Failed: {}", failed);
        warn!("  - Canceled: {}", canceled);
        warn!("  - Terminated: {}", terminated);
        warn!("  - Completed: {}", completed);

        // Check if we should attempt recovery
        if !args.recover {
            info!("\nRecovery disabled. To enable, use --recover flag.");
            info!("Or use the Torc MCP server with your AI assistant for manual recovery.");
            std::process::exit(1);
        }

        if retry_count >= args.max_retries {
            warn!(
                "\nMax retries ({}) exceeded. Manual intervention required.",
                args.max_retries
            );
            warn!("Use the Torc MCP server with your AI assistant to investigate.");
            std::process::exit(1);
        }

        retry_count += 1;
        info!(
            "\nAttempting automatic recovery (attempt {}/{})",
            retry_count, args.max_retries
        );

        // Step 1: Diagnose failures
        info!("\nDiagnosing failures...");
        let diagnosis = match diagnose_failures(args.workflow_id, &args.output_dir) {
            Ok(d) => d,
            Err(e) => {
                warn!("Warning: Could not diagnose failures: {}", e);
                warn!("Attempting retry without resource adjustments...");
                ResourceUtilizationReport {
                    workflow_id: args.workflow_id,
                    run_id: None,
                    total_results: 0,
                    over_utilization_count: 0,
                    violations: Vec::new(),
                    failed_jobs_count: 0,
                    failed_jobs: Vec::new(),
                }
            }
        };

        // Step 2: Apply heuristics to adjust resources
        info!("\nApplying recovery heuristics...");
        // If a recovery hook is provided, treat unknown failures as retryable
        // (the user is explicitly saying they'll handle them with their script)
        let retry_unknown = args.retry_unknown || args.recovery_hook.is_some();
        let recovery_result = match apply_recovery_heuristics(
            config,
            args.workflow_id,
            &diagnosis,
            args.memory_multiplier,
            args.runtime_multiplier,
            retry_unknown,
            &args.output_dir,
            false, // dry_run - always execute for watch
        ) {
            Ok(result) => {
                if result.oom_fixed > 0 || result.timeout_fixed > 0 {
                    info!(
                        "  Applied fixes: {} OOM, {} timeout",
                        result.oom_fixed, result.timeout_fixed
                    );
                }
                if result.other_failures > 0 {
                    if retry_unknown {
                        if args.recovery_hook.is_some() {
                            info!(
                                "  {} job(s) with unknown failure cause (will run recovery hook)",
                                result.other_failures
                            );
                        } else {
                            info!(
                                "  {} job(s) with unknown failure cause (will retry)",
                                result.other_failures
                            );
                        }
                    } else {
                        info!(
                            "  {} job(s) with unknown failure cause (skipped, use --retry-unknown to include)",
                            result.other_failures
                        );
                    }
                }
                result
            }
            Err(e) => {
                warn!("Warning: Error applying heuristics: {}", e);
                RecoveryResult {
                    oom_fixed: 0,
                    timeout_fixed: 0,
                    unknown_retried: 0,
                    other_failures: 0,
                    jobs_to_retry: Vec::new(),
                    adjustments: Vec::new(),
                    slurm_dry_run: None,
                }
            }
        };

        // Step 2.5: Run recovery hook if there are unknown failures
        if recovery_result.other_failures > 0
            && let Some(ref hook_cmd) = args.recovery_hook
        {
            info!(
                "\n{} job(s) with unknown failure cause - running recovery hook...",
                recovery_result.other_failures
            );
            if let Err(e) = run_recovery_hook(args.workflow_id, hook_cmd) {
                error!("Recovery hook failed: {}", e);
                std::process::exit(1);
            }
        }

        // Check if there are any jobs to retry
        if recovery_result.jobs_to_retry.is_empty() {
            warn!(
                "\nNo recoverable jobs found. {} job(s) failed with unknown causes.",
                recovery_result.other_failures
            );
            warn!("Use --retry-unknown to retry jobs with unknown failure causes.");
            warn!("Or use the Torc MCP server with your AI assistant to investigate.");
            std::process::exit(1);
        }

        // Step 3: Reset failed jobs
        info!(
            "\nResetting {} job(s) for retry...",
            recovery_result.jobs_to_retry.len()
        );
        match reset_failed_jobs(config, args.workflow_id, &recovery_result.jobs_to_retry) {
            Ok(count) => {
                info!("  Reset {} job(s)", count);
            }
            Err(e) => {
                error!("Error resetting jobs: {}", e);
                std::process::exit(1);
            }
        }

        // Step 4: Reinitialize workflow first (before creating new allocations)
        // Must happen before regenerate_and_submit because reset_workflow_status
        // rejects requests when there are pending scheduled compute nodes.
        info!("Reinitializing workflow...");
        if let Err(e) = reinitialize_workflow(args.workflow_id) {
            warn!("Error reinitializing workflow: {}", e);
            std::process::exit(1);
        }

        // Step 5: Regenerate Slurm schedulers (this also marks old actions as executed)
        info!("Regenerating Slurm schedulers...");
        if let Err(e) = regenerate_and_submit(args.workflow_id, &args.output_dir) {
            warn!("Error regenerating schedulers: {}", e);
            std::process::exit(1);
        }

        info!("\nRecovery initiated. Resuming monitoring...\n");
    }
}

// Tests for parse_memory_bytes, format_memory_bytes_short, format_duration_iso8601
// are in the recover module
