//! Recovery action execution.

use log::{debug, info};
use serde::{Deserialize, Serialize};

use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::models::{JobStatus, ResourceRequirementsModel};

/// Recovery actions that can be taken for failed jobs.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum RecoveryAction {
    /// Restart the job with no changes (for transient failures)
    Restart,

    /// Restart with modified resource requirements
    RestartWithResources {
        /// New memory requirement (e.g., "8g")
        memory: Option<String>,
        /// New runtime limit (e.g., "PT2H")
        runtime: Option<String>,
        /// New CPU count
        num_cpus: Option<i64>,
    },

    /// Cancel the job and its dependents
    Cancel,

    /// Mark as completed and continue (skip the job)
    Skip,
}

/// Execute a recovery action for a job.
pub fn execute_recovery(
    config: &Configuration,
    job_id: i64,
    action: &RecoveryAction,
) -> Result<(), String> {
    match action {
        RecoveryAction::Restart => restart_job(config, job_id),
        RecoveryAction::RestartWithResources {
            memory,
            runtime,
            num_cpus,
        } => restart_with_resources(config, job_id, memory, runtime, num_cpus),
        RecoveryAction::Cancel => cancel_job(config, job_id),
        RecoveryAction::Skip => skip_job(config, job_id),
    }
}

/// Restart a job by resetting its status to uninitialized.
fn restart_job(config: &Configuration, job_id: i64) -> Result<(), String> {
    info!("Restarting job {}", job_id);

    // Reset job status to uninitialized
    default_api::manage_status_change(
        config,
        job_id,
        JobStatus::Uninitialized,
        0, // run_id
        None,
    )
    .map_err(|e| format!("Failed to reset job status: {}", e))?;

    // Get workflow ID to reinitialize
    let job =
        default_api::get_job(config, job_id).map_err(|e| format!("Failed to get job: {}", e))?;

    // Reinitialize the workflow to process the reset job
    default_api::initialize_jobs(config, job.workflow_id, None, None, None)
        .map_err(|e| format!("Failed to reinitialize jobs: {}", e))?;

    debug!("Job {} reset and workflow reinitialized", job_id);
    Ok(())
}

/// Restart a job with updated resource requirements.
fn restart_with_resources(
    config: &Configuration,
    job_id: i64,
    memory: &Option<String>,
    runtime: &Option<String>,
    num_cpus: &Option<i64>,
) -> Result<(), String> {
    info!(
        "Restarting job {} with updated resources (memory: {:?}, runtime: {:?}, cpus: {:?})",
        job_id, memory, runtime, num_cpus
    );

    // Get the job to find resource requirements
    let job =
        default_api::get_job(config, job_id).map_err(|e| format!("Failed to get job: {}", e))?;

    // Update resource requirements if the job has them
    if let Some(req_id) = job.resource_requirements_id {
        let mut reqs = default_api::get_resource_requirements(config, req_id)
            .map_err(|e| format!("Failed to get resource requirements: {}", e))?;

        // Update fields if provided
        if let Some(mem) = memory {
            info!("Updating memory from {} to {}", reqs.memory, mem);
            reqs.memory = mem.clone();
        }
        if let Some(rt) = runtime {
            info!("Updating runtime from {} to {}", reqs.runtime, rt);
            reqs.runtime = rt.clone();
        }
        if let Some(cpus) = num_cpus {
            info!("Updating num_cpus from {} to {}", reqs.num_cpus, cpus);
            reqs.num_cpus = *cpus;
        }

        // Update the resource requirements
        default_api::update_resource_requirements(
            config,
            req_id,
            ResourceRequirementsModel {
                id: reqs.id,
                workflow_id: reqs.workflow_id,
                name: reqs.name,
                num_cpus: reqs.num_cpus,
                num_gpus: reqs.num_gpus,
                num_nodes: reqs.num_nodes,
                memory: reqs.memory,
                runtime: reqs.runtime,
            },
        )
        .map_err(|e| format!("Failed to update resource requirements: {}", e))?;
    } else {
        debug!("Job {} has no resource requirements to update", job_id);
    }

    // Now restart the job
    restart_job(config, job_id)
}

/// Cancel a job.
fn cancel_job(config: &Configuration, job_id: i64) -> Result<(), String> {
    info!("Canceling job {}", job_id);

    default_api::manage_status_change(
        config,
        job_id,
        JobStatus::Canceled,
        0, // run_id
        None,
    )
    .map_err(|e| format!("Failed to cancel job: {}", e))?;

    debug!("Job {} canceled", job_id);
    Ok(())
}

/// Skip a job by marking it as completed.
fn skip_job(config: &Configuration, job_id: i64) -> Result<(), String> {
    info!("Skipping job {} (marking as completed)", job_id);

    // Get the job to find workflow_id
    let job =
        default_api::get_job(config, job_id).map_err(|e| format!("Failed to get job: {}", e))?;

    // Get the workflow status to find run_id
    let workflow_status = default_api::get_workflow_status(config, job.workflow_id)
        .map_err(|e| format!("Failed to get workflow status: {}", e))?;

    // Create a minimal result for the skipped job
    let result = crate::models::ResultModel {
        id: None,
        job_id,
        workflow_id: job.workflow_id,
        run_id: workflow_status.run_id,
        compute_node_id: 0, // No compute node for skipped job
        return_code: 0,     // Success
        exec_time_minutes: 0.0,
        completion_time: chrono::Utc::now().to_rfc3339(),
        peak_memory_bytes: None,
        avg_memory_bytes: None,
        peak_cpu_percent: None,
        avg_cpu_percent: None,
        status: JobStatus::Completed,
    };

    // Use complete_job to properly handle completion
    default_api::complete_job(
        config,
        job_id,
        JobStatus::Completed,
        workflow_status.run_id,
        result,
    )
    .map_err(|e| format!("Failed to complete job: {}", e))?;

    debug!("Job {} marked as completed (skipped)", job_id);
    Ok(())
}
