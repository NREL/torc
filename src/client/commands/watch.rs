//! Watch command for monitoring workflows with automatic failure recovery

use chrono::Utc;
use env_logger::Builder;
use log::{LevelFilter, debug, error, info, warn};
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use std::process::Command;
use std::time::Duration;

use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::hpc::common::HpcJobStatus;
use crate::client::hpc::hpc_interface::HpcInterface;
use crate::client::hpc::slurm_interface::SlurmInterface;
use crate::client::log_paths::get_watch_log_file;
use crate::models;
use crate::time_utils::duration_string_to_seconds;

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
    pub auto_recover: bool,
    pub max_retries: u32,
    pub memory_multiplier: f64,
    pub runtime_multiplier: f64,
    pub retry_unknown: bool,
    pub output_dir: PathBuf,
    pub show_job_counts: bool,
    pub log_level: String,
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

/// Get job counts by status for a workflow
fn get_job_counts(
    config: &Configuration,
    workflow_id: i64,
) -> Result<HashMap<String, i64>, String> {
    let jobs_response = default_api::list_jobs(
        config,
        workflow_id,
        None,        // status filter
        None,        // needs_file_id
        None,        // upstream_job_id
        None,        // offset
        Some(10000), // limit
        None,        // sort_by
        None,        // reverse_sort
        None,        // include_relationships
        None,        // active_compute_node_id
    )
    .map_err(|e| format!("Failed to list jobs: {}", e))?;

    let jobs = jobs_response.items.unwrap_or_default();
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
/// This is more accurate than the old fail_orphaned_running_jobs because it uses Slurm
/// as the authoritative source for whether jobs are still running.
///
/// Returns the number of jobs that were failed.
fn fail_orphaned_slurm_jobs(config: &Configuration, workflow_id: i64) -> Result<usize, String> {
    // Get workflow status to retrieve run_id
    let workflow_status = default_api::get_workflow_status(config, workflow_id)
        .map_err(|e| format!("Failed to get workflow status: {}", e))?;
    let run_id = workflow_status.run_id;

    // Get all scheduled compute nodes with status="active" and scheduler_type="slurm"
    let scheduled_nodes_response = default_api::list_scheduled_compute_nodes(
        config,
        workflow_id,
        None,           // offset
        Some(1000),     // limit
        None,           // sort_by
        None,           // reverse_sort
        None,           // scheduler_id
        None,           // scheduler_config_id
        Some("active"), // status
    )
    .map_err(|e| format!("Failed to list scheduled compute nodes: {}", e))?;

    let scheduled_nodes = scheduled_nodes_response.items.unwrap_or_default();

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
        let compute_nodes_response = default_api::list_compute_nodes(
            config,
            workflow_id,
            None,                            // offset
            Some(1000),                      // limit
            None,                            // sort_by
            None,                            // reverse_sort
            None,                            // hostname
            None,                            // is_active - any status
            Some(scheduled_compute_node_id), // scheduled_compute_node_id
        )
        .map_err(|e| format!("Failed to list compute nodes: {}", e))?;

        let compute_nodes = compute_nodes_response.items.unwrap_or_default();

        for compute_node in &compute_nodes {
            let compute_node_id = match compute_node.id {
                Some(id) => id,
                None => continue,
            };

            // Find all jobs with this active_compute_node_id
            let jobs_response = default_api::list_jobs(
                config,
                workflow_id,
                None,                  // status - we want any status (should be Running)
                None,                  // needs_file_id
                None,                  // upstream_job_id
                None,                  // offset
                Some(10000),           // limit
                None,                  // sort_by
                None,                  // reverse_sort
                None,                  // include_relationships
                Some(compute_node_id), // active_compute_node_id
            )
            .map_err(|e| format!("Failed to list jobs for compute node: {}", e))?;

            let orphaned_jobs = jobs_response.items.unwrap_or_default();

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
    let scheduled_nodes_response = default_api::list_scheduled_compute_nodes(
        config,
        workflow_id,
        None,            // offset
        Some(1000),      // limit
        None,            // sort_by
        None,            // reverse_sort
        None,            // scheduler_id
        None,            // scheduler_config_id
        Some("pending"), // status
    )
    .map_err(|e| format!("Failed to list pending scheduled compute nodes: {}", e))?;

    let scheduled_nodes = scheduled_nodes_response.items.unwrap_or_default();

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
    let active_nodes = default_api::list_scheduled_compute_nodes(
        config,
        workflow_id,
        None,           // offset
        Some(1),        // limit - just need one
        None,           // sort_by
        None,           // reverse_sort
        None,           // scheduler_id
        None,           // scheduler_config_id
        Some("active"), // status
    );

    if let Ok(response) = active_nodes {
        if let Some(nodes) = response.items {
            for node in nodes {
                if node.scheduler_type.to_lowercase() == "slurm" {
                    // Check if this Slurm job is still running
                    if let Ok(slurm) = SlurmInterface::new() {
                        let slurm_job_id = node.scheduler_id.to_string();
                        if let Ok(info) = slurm.get_status(&slurm_job_id) {
                            if info.status == HpcJobStatus::Running
                                || info.status == HpcJobStatus::Queued
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
        }
    }

    // Check for pending allocations
    let pending_nodes = default_api::list_scheduled_compute_nodes(
        config,
        workflow_id,
        None,            // offset
        Some(1),         // limit - just need one
        None,            // sort_by
        None,            // reverse_sort
        None,            // scheduler_id
        None,            // scheduler_config_id
        Some("pending"), // status
    );

    if let Ok(response) = pending_nodes {
        if let Some(nodes) = response.items {
            for node in nodes {
                if node.scheduler_type.to_lowercase() == "slurm" {
                    // Check if this Slurm job is still queued
                    if let Ok(slurm) = SlurmInterface::new() {
                        let slurm_job_id = node.scheduler_id.to_string();
                        if let Ok(info) = slurm.get_status(&slurm_job_id) {
                            if info.status == HpcJobStatus::Running
                                || info.status == HpcJobStatus::Queued
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
    let running_jobs_response = default_api::list_jobs(
        config,
        workflow_id,
        Some(models::JobStatus::Running),
        None,        // needs_file_id
        None,        // upstream_job_id
        None,        // offset
        Some(10000), // limit
        None,        // sort_by
        None,        // reverse_sort
        None,        // include_relationships
        None,        // active_compute_node_id
    )
    .map_err(|e| format!("Failed to list running jobs: {}", e))?;

    let running_jobs = running_jobs_response.items.unwrap_or_default();

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

/// Poll until workflow is complete, optionally printing status updates
fn poll_until_complete(
    config: &Configuration,
    workflow_id: i64,
    poll_interval: u64,
    show_job_counts: bool,
) -> Result<HashMap<String, i64>, String> {
    loop {
        // Check if workflow is complete
        match default_api::is_workflow_complete(config, workflow_id) {
            Ok(response) => {
                if response.is_complete {
                    info!("Workflow {} is complete", workflow_id);
                    break;
                }
            }
            Err(e) => {
                return Err(format!("Error checking workflow status: {}", e));
            }
        }

        // Print current status if requested
        if show_job_counts {
            match get_job_counts(config, workflow_id) {
                Ok(counts) => {
                    let completed = counts.get("Completed").unwrap_or(&0);
                    let running = counts.get("Running").unwrap_or(&0);
                    let pending = counts.get("Pending").unwrap_or(&0);
                    let failed = counts.get("Failed").unwrap_or(&0);
                    let blocked = counts.get("Blocked").unwrap_or(&0);
                    info!(
                        "  completed={}, running={}, pending={}, failed={}, blocked={}",
                        completed, running, pending, failed, blocked
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

        std::thread::sleep(Duration::from_secs(poll_interval));
    }

    get_job_counts(config, workflow_id)
}

/// Diagnose failures and return job IDs that need resource adjustments
fn diagnose_failures(workflow_id: i64, _output_dir: &PathBuf) -> Result<serde_json::Value, String> {
    // Run check-resource-utilization command
    // Note: This command doesn't take an output_dir argument - it reads from the database
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
fn get_slurm_log_info(workflow_id: i64, output_dir: &PathBuf) -> Result<serde_json::Value, String> {
    // Run reports results command to get log paths
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
    diagnosis: &serde_json::Value,
    slurm_info: &serde_json::Value,
) -> HashMap<i64, SlurmLogInfo> {
    let mut log_map = HashMap::new();

    // Build map from job_id to slurm log paths
    if let Some(jobs) = slurm_info.get("jobs").and_then(|v| v.as_array()) {
        for job in jobs {
            if let Some(job_id) = job.get("job_id").and_then(|v| v.as_i64()) {
                let slurm_stdout = job
                    .get("slurm_stdout")
                    .and_then(|v| v.as_str())
                    .map(String::from);
                let slurm_stderr = job
                    .get("slurm_stderr")
                    .and_then(|v| v.as_str())
                    .map(String::from);
                let slurm_job_id = job
                    .get("slurm_job_id")
                    .and_then(|v| v.as_str())
                    .map(String::from);

                if slurm_stdout.is_some() || slurm_stderr.is_some() {
                    log_map.insert(
                        job_id,
                        SlurmLogInfo {
                            slurm_job_id,
                            slurm_stdout,
                            slurm_stderr,
                        },
                    );
                }
            }
        }
    }

    // Filter to only failed jobs
    let mut failed_log_map = HashMap::new();
    if let Some(failed_jobs) = diagnosis.get("failed_jobs").and_then(|v| v.as_array()) {
        for job_info in failed_jobs {
            if let Some(job_id) = job_info.get("job_id").and_then(|v| v.as_i64()) {
                if let Some(log_info) = log_map.remove(&job_id) {
                    failed_log_map.insert(job_id, log_info);
                }
            }
        }
    }

    failed_log_map
}

/// Information about Slurm logs for a job
#[derive(Debug)]
pub struct SlurmLogInfo {
    pub slurm_job_id: Option<String>,
    pub slurm_stdout: Option<String>,
    pub slurm_stderr: Option<String>,
}

/// Result of applying recovery heuristics
pub struct RecoveryResult {
    pub oom_fixed: usize,
    pub timeout_fixed: usize,
    pub other_failures: usize,
    pub jobs_to_retry: Vec<i64>,
}

/// Apply recovery heuristics and update job resources
fn apply_recovery_heuristics(
    config: &Configuration,
    workflow_id: i64,
    diagnosis: &serde_json::Value,
    memory_multiplier: f64,
    runtime_multiplier: f64,
    retry_unknown: bool,
    output_dir: &PathBuf,
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
            log::debug!("Could not get Slurm log info: {}", e);
            HashMap::new()
        }
    };

    // Get failed jobs info from diagnosis
    let failed_jobs = diagnosis
        .get("failed_jobs")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default();

    for job_info in &failed_jobs {
        let job_id = job_info.get("job_id").and_then(|v| v.as_i64()).unwrap_or(0);
        let likely_oom = job_info
            .get("likely_oom")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);
        let likely_timeout = job_info
            .get("likely_timeout")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);

        if job_id == 0 {
            continue;
        }

        // Log Slurm info if available
        if let Some(slurm_info) = slurm_log_map.get(&job_id) {
            if let Some(slurm_job_id) = &slurm_info.slurm_job_id {
                log::debug!("  Job {} ran in Slurm allocation {}", job_id, slurm_job_id);
            }
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

        // Get current resource requirements
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

        let mut updated = false;
        let mut new_rr = rr.clone();

        // Apply OOM heuristic
        if likely_oom {
            if let Some(current_bytes) = parse_memory_bytes(&rr.memory) {
                let new_bytes = (current_bytes as f64 * memory_multiplier) as u64;
                let new_memory = format_memory_bytes_short(new_bytes);
                info!(
                    "  Job {} ({}): OOM detected, increasing memory {} -> {}",
                    job_id, job.name, rr.memory, new_memory
                );
                new_rr.memory = new_memory;
                updated = true;
                oom_fixed += 1;
            }
        }

        // Apply timeout heuristic
        if likely_timeout {
            // Use duration_string_to_seconds from time_utils
            if let Ok(current_secs) = duration_string_to_seconds(&rr.runtime) {
                let new_secs = (current_secs as f64 * runtime_multiplier) as u64;
                let new_runtime = format_duration_iso8601(new_secs);
                info!(
                    "  Job {} ({}): Timeout detected, increasing runtime {} -> {}",
                    job_id, job.name, rr.runtime, new_runtime
                );
                new_rr.runtime = new_runtime;
                updated = true;
                timeout_fixed += 1;
            }
        }

        // Update resource requirements if changed
        if updated {
            if let Err(e) = default_api::update_resource_requirements(config, rr_id, new_rr) {
                warn!(
                    "  Warning: failed to update resource requirements for job {}: {}",
                    job_id, e
                );
            }
            // Job had OOM or timeout - always retry
            jobs_to_retry.push(job_id);
        } else if !likely_oom && !likely_timeout {
            // Unknown failure - only retry if retry_unknown is enabled
            other_failures += 1;
            if retry_unknown {
                jobs_to_retry.push(job_id);
            }
        }
    }

    Ok(RecoveryResult {
        oom_fixed,
        timeout_fixed,
        other_failures,
        jobs_to_retry,
    })
}

/// Reset specific failed jobs for retry
fn reset_failed_jobs(
    _config: &Configuration,
    workflow_id: i64,
    job_ids: &[i64],
) -> Result<usize, String> {
    if job_ids.is_empty() {
        return Ok(0);
    }

    let job_count = job_ids.len();

    // Use reset-status --failed-only --restart to reset failed jobs and trigger unblocking
    let output = Command::new("torc")
        .args([
            "workflows",
            "reset-status",
            &workflow_id.to_string(),
            "--failed-only",
            "--restart",
            "--no-prompts",
        ])
        .output()
        .map_err(|e| format!("Failed to run workflow reset-status: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("workflow reset-status failed: {}", stderr));
    }

    Ok(job_count)
}

/// Regenerate Slurm schedulers and submit allocations
fn regenerate_and_submit(workflow_id: i64, output_dir: &PathBuf) -> Result<(), String> {
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

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("slurm regenerate failed: {}", stderr));
    }

    Ok(())
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

    info!(
        "Watching workflow {} (poll interval: {}s{}{})",
        args.workflow_id,
        args.poll_interval,
        if args.auto_recover {
            format!(", auto-recover enabled, max retries: {}", args.max_retries)
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
        // Poll until workflow is complete
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
            error!("\n✓ Workflow completed successfully ({} jobs)", completed);
            break;
        }

        error!("\nWorkflow completed with failures:");
        error!("  - Failed: {}", failed);
        error!("  - Canceled: {}", canceled);
        error!("  - Terminated: {}", terminated);
        error!("  - Completed: {}", completed);

        // Check if we should attempt recovery
        if !args.auto_recover {
            info!("\nAuto-recovery disabled. To enable, use --auto-recover flag.");
            info!("Or use the Torc MCP server with your AI assistant for manual recovery.");
            std::process::exit(1);
        }

        if retry_count >= args.max_retries {
            error!(
                "\nMax retries ({}) exceeded. Manual intervention required.",
                args.max_retries
            );
            info!("Use the Torc MCP server with your AI assistant to investigate.");
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
                serde_json::json!({"failed_jobs": []})
            }
        };

        // Step 2: Apply heuristics to adjust resources
        info!("\nApplying recovery heuristics...");
        let recovery_result = match apply_recovery_heuristics(
            config,
            args.workflow_id,
            &diagnosis,
            args.memory_multiplier,
            args.runtime_multiplier,
            args.retry_unknown,
            &args.output_dir,
        ) {
            Ok(result) => {
                if result.oom_fixed > 0 || result.timeout_fixed > 0 {
                    info!(
                        "  Applied fixes: {} OOM, {} timeout",
                        result.oom_fixed, result.timeout_fixed
                    );
                }
                if result.other_failures > 0 {
                    if args.retry_unknown {
                        info!(
                            "  {} job(s) with unknown failure cause (will retry)",
                            result.other_failures
                        );
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
                    other_failures: 0,
                    jobs_to_retry: Vec::new(),
                }
            }
        };

        // Check if there are any jobs to retry
        if recovery_result.jobs_to_retry.is_empty() {
            error!(
                "\nNo recoverable jobs found. {} job(s) failed with unknown causes.",
                recovery_result.other_failures
            );
            error!("Use --retry-unknown to retry jobs with unknown failure causes.");
            error!("Or use the Torc MCP server with your AI assistant to investigate.");
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

        // Step 4: Regenerate Slurm schedulers and submit
        info!("Regenerating Slurm schedulers and submitting...");
        if let Err(e) = regenerate_and_submit(args.workflow_id, &args.output_dir) {
            error!("Error regenerating schedulers: {}", e);
            std::process::exit(1);
        }

        info!("\nRecovery initiated. Resuming monitoring...\n");
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_memory_bytes() {
        assert_eq!(parse_memory_bytes("1g"), Some(1024 * 1024 * 1024));
        assert_eq!(parse_memory_bytes("2gb"), Some(2 * 1024 * 1024 * 1024));
        assert_eq!(parse_memory_bytes("512m"), Some(512 * 1024 * 1024));
        assert_eq!(parse_memory_bytes("512mb"), Some(512 * 1024 * 1024));
        assert_eq!(parse_memory_bytes("1024k"), Some(1024 * 1024));
        assert_eq!(parse_memory_bytes("1024kb"), Some(1024 * 1024));
        assert_eq!(parse_memory_bytes("1024"), Some(1024));
        assert_eq!(parse_memory_bytes("invalid"), None);
    }

    #[test]
    fn test_format_memory_bytes_short() {
        assert_eq!(format_memory_bytes_short(1024 * 1024 * 1024), "1g");
        assert_eq!(format_memory_bytes_short(2 * 1024 * 1024 * 1024), "2g");
        assert_eq!(format_memory_bytes_short(512 * 1024 * 1024), "512m");
        assert_eq!(format_memory_bytes_short(1024 * 1024), "1m");
        assert_eq!(format_memory_bytes_short(1024), "1k");
        assert_eq!(format_memory_bytes_short(512), "512b");
    }

    #[test]
    fn test_format_duration_iso8601() {
        assert_eq!(format_duration_iso8601(3600), "PT1H");
        assert_eq!(format_duration_iso8601(7200), "PT2H");
        assert_eq!(format_duration_iso8601(5400), "PT1H30M");
        assert_eq!(format_duration_iso8601(1800), "PT30M");
        assert_eq!(format_duration_iso8601(60), "PT1M");
        assert_eq!(format_duration_iso8601(30), "PT1M"); // rounds up to minimum 1 minute
    }
}
