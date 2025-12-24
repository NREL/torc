//! Tool implementations for the Torc MCP server.

use rmcp::{Error as McpError, model::CallToolResult};
use std::fs;
use std::path::PathBuf;
use std::process::Command;

use torc::client::apis::configuration::Configuration;
use torc::client::apis::default_api;
use torc::client::log_paths;
use torc::models::{JobStatus, ResourceRequirementsModel};

/// Maximum number of jobs to retrieve in a single request.
/// Results may be truncated if the workflow has more jobs than this limit.
const MAX_JOBS_LIMIT: i64 = 10000;

/// Helper to create an internal error
fn internal_error(msg: String) -> McpError {
    McpError::internal_error(msg, None)
}

/// Helper to create an invalid params error
fn invalid_params(msg: &str) -> McpError {
    McpError::invalid_request(msg.to_string(), None)
}

/// Parse status string to JobStatus enum
fn parse_status(status: &str) -> Option<JobStatus> {
    match status.to_lowercase().as_str() {
        "uninitialized" => Some(JobStatus::Uninitialized),
        "blocked" => Some(JobStatus::Blocked),
        "ready" => Some(JobStatus::Ready),
        "pending" => Some(JobStatus::Pending),
        "running" => Some(JobStatus::Running),
        "completed" => Some(JobStatus::Completed),
        "failed" => Some(JobStatus::Failed),
        "canceled" => Some(JobStatus::Canceled),
        "terminated" => Some(JobStatus::Terminated),
        "disabled" => Some(JobStatus::Disabled),
        _ => None,
    }
}

/// Get workflow status with job counts.
pub fn get_workflow_status(
    config: &Configuration,
    workflow_id: i64,
) -> Result<CallToolResult, McpError> {
    // Get workflow info
    let workflow = default_api::get_workflow(config, workflow_id)
        .map_err(|e| internal_error(format!("Failed to get workflow: {}", e)))?;

    // Get job counts by status - get all jobs
    let jobs_response = default_api::list_jobs(
        config,
        workflow_id,
        None,                 // status filter
        None,                 // needs_file_id
        None,                 // upstream_job_id
        None,                 // offset
        Some(MAX_JOBS_LIMIT), // limit
        None,                 // sort_by
        None,                 // reverse_sort
        None,                 // include_relationships
    )
    .map_err(|e| internal_error(format!("Failed to list jobs: {}", e)))?;

    let jobs = jobs_response.items.unwrap_or_default();
    let truncated = jobs.len() as i64 >= MAX_JOBS_LIMIT;

    // Count jobs by status
    let mut status_counts = std::collections::HashMap::new();
    for job in &jobs {
        if let Some(status) = &job.status {
            let status_str = format!("{:?}", status);
            *status_counts.entry(status_str).or_insert(0) += 1;
        }
    }

    let mut result = serde_json::json!({
        "workflow_id": workflow.id,
        "name": workflow.name,
        "user": workflow.user,
        "description": workflow.description,
        "total_jobs": jobs.len(),
        "job_counts_by_status": status_counts,
    });

    if truncated {
        result["warning"] = serde_json::json!(format!(
            "Results truncated at {} jobs. Workflow may have more jobs.",
            MAX_JOBS_LIMIT
        ));
    }

    Ok(CallToolResult::success(vec![rmcp::model::Content::text(
        serde_json::to_string_pretty(&result).unwrap_or_default(),
    )]))
}

/// Get detailed job information.
pub fn get_job_details(config: &Configuration, job_id: i64) -> Result<CallToolResult, McpError> {
    let job = default_api::get_job(config, job_id)
        .map_err(|e| internal_error(format!("Failed to get job: {}", e)))?;

    // Get resource requirements if available
    let resource_reqs = if let Some(req_id) = job.resource_requirements_id {
        default_api::get_resource_requirements(config, req_id).ok()
    } else {
        None
    };

    // Get latest result if job has run
    let result = default_api::list_results(
        config,
        job.workflow_id,
        Some(job_id),
        None,    // run_id
        None,    // offset
        Some(1), // limit - just get latest
        None,    // sort_by
        None,    // reverse_sort
        None,    // return_code
        None,    // status
        None,    // all_runs
    )
    .ok()
    .and_then(|r| r.items)
    .and_then(|items| items.into_iter().next());

    let response = serde_json::json!({
        "job_id": job.id,
        "workflow_id": job.workflow_id,
        "name": job.name,
        "command": job.command,
        "status": format!("{:?}", job.status),
        "invocation_script": job.invocation_script,
        "supports_termination": job.supports_termination,
        "cancel_on_blocking_job_failure": job.cancel_on_blocking_job_failure,
        "depends_on_job_ids": job.depends_on_job_ids,
        "resource_requirements": resource_reqs.map(|r| serde_json::json!({
            "id": r.id,
            "num_cpus": r.num_cpus,
            "num_gpus": r.num_gpus,
            "memory": r.memory,
            "runtime": r.runtime,
        })),
        "latest_result": result.map(|r| serde_json::json!({
            "run_id": r.run_id,
            "return_code": r.return_code,
            "exec_time_minutes": r.exec_time_minutes,
            "completion_time": r.completion_time,
            "peak_memory_bytes": r.peak_memory_bytes,
            "avg_cpu_percent": r.avg_cpu_percent,
        })),
    });

    Ok(CallToolResult::success(vec![rmcp::model::Content::text(
        serde_json::to_string_pretty(&response).unwrap_or_default(),
    )]))
}

/// Read job logs.
pub fn get_job_logs(
    output_dir: &PathBuf,
    workflow_id: i64,
    job_id: i64,
    run_id: i64,
    log_type: &str,
    tail_lines: Option<usize>,
) -> Result<CallToolResult, McpError> {
    let log_path = match log_type.to_lowercase().as_str() {
        "stdout" => log_paths::get_job_stdout_path(output_dir, workflow_id, job_id, run_id),
        "stderr" => log_paths::get_job_stderr_path(output_dir, workflow_id, job_id, run_id),
        _ => return Err(invalid_params("log_type must be 'stdout' or 'stderr'")),
    };

    let content = fs::read_to_string(&log_path)
        .map_err(|e| internal_error(format!("Failed to read log file {}: {}", log_path, e)))?;

    let output = if let Some(n) = tail_lines {
        let lines: Vec<&str> = content.lines().collect();
        let start = lines.len().saturating_sub(n);
        lines[start..].join("\n")
    } else {
        content
    };

    Ok(CallToolResult::success(vec![rmcp::model::Content::text(
        output,
    )]))
}

/// List failed jobs in a workflow.
pub fn list_failed_jobs(
    config: &Configuration,
    workflow_id: i64,
) -> Result<CallToolResult, McpError> {
    let jobs_response = default_api::list_jobs(
        config,
        workflow_id,
        Some(JobStatus::Failed),
        None,                 // needs_file_id
        None,                 // upstream_job_id
        None,                 // offset
        Some(MAX_JOBS_LIMIT), // limit
        None,                 // sort_by
        None,                 // reverse_sort
        None,                 // include_relationships
    )
    .map_err(|e| internal_error(format!("Failed to list jobs: {}", e)))?;

    let jobs = jobs_response.items.unwrap_or_default();
    let truncated = jobs.len() as i64 >= MAX_JOBS_LIMIT;

    let failed_jobs: Vec<serde_json::Value> = jobs
        .iter()
        .map(|job| {
            serde_json::json!({
                "job_id": job.id,
                "name": job.name,
                "command": job.command,
            })
        })
        .collect();

    let mut result = serde_json::json!({
        "workflow_id": workflow_id,
        "failed_job_count": failed_jobs.len(),
        "failed_jobs": failed_jobs,
    });

    if truncated {
        result["warning"] = serde_json::json!(format!(
            "Results truncated at {} jobs. There may be more failed jobs.",
            MAX_JOBS_LIMIT
        ));
    }

    Ok(CallToolResult::success(vec![rmcp::model::Content::text(
        serde_json::to_string_pretty(&result).unwrap_or_default(),
    )]))
}

/// List jobs by status.
pub fn list_jobs_by_status(
    config: &Configuration,
    workflow_id: i64,
    status: &str,
) -> Result<CallToolResult, McpError> {
    let status_enum = parse_status(status).ok_or_else(|| invalid_params("Invalid status value"))?;

    let jobs_response = default_api::list_jobs(
        config,
        workflow_id,
        Some(status_enum),
        None,                 // needs_file_id
        None,                 // upstream_job_id
        None,                 // offset
        Some(MAX_JOBS_LIMIT), // limit
        None,                 // sort_by
        None,                 // reverse_sort
        None,                 // include_relationships
    )
    .map_err(|e| internal_error(format!("Failed to list jobs: {}", e)))?;

    let jobs = jobs_response.items.unwrap_or_default();
    let truncated = jobs.len() as i64 >= MAX_JOBS_LIMIT;

    let job_list: Vec<serde_json::Value> = jobs
        .iter()
        .map(|job| {
            serde_json::json!({
                "job_id": job.id,
                "name": job.name,
                "command": job.command,
            })
        })
        .collect();

    let mut result = serde_json::json!({
        "workflow_id": workflow_id,
        "status": status,
        "count": job_list.len(),
        "jobs": job_list,
    });

    if truncated {
        result["warning"] = serde_json::json!(format!(
            "Results truncated at {} jobs. There may be more jobs with status '{}'.",
            MAX_JOBS_LIMIT, status
        ));
    }

    Ok(CallToolResult::success(vec![rmcp::model::Content::text(
        serde_json::to_string_pretty(&result).unwrap_or_default(),
    )]))
}

/// Check resource utilization for a workflow by running the CLI command.
pub fn check_resource_utilization(
    workflow_id: i64,
    include_failed: bool,
) -> Result<CallToolResult, McpError> {
    let mut cmd = Command::new("torc");
    cmd.args(["-f", "json", "reports", "check-resource-utilization"]);
    cmd.arg(workflow_id.to_string());

    if include_failed {
        cmd.arg("--include-failed");
    }

    let output = cmd
        .output()
        .map_err(|e| internal_error(format!("Failed to execute torc command: {}", e)))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(internal_error(format!(
            "torc command failed: {}",
            stderr.trim()
        )));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    Ok(CallToolResult::success(vec![rmcp::model::Content::text(
        stdout.to_string(),
    )]))
}

/// Reset failed jobs and restart a workflow by running the CLI command.
pub fn reset_and_restart_workflow(workflow_id: i64) -> Result<CallToolResult, McpError> {
    let output = Command::new("torc")
        .args([
            "-f",
            "json",
            "workflows",
            "reset-status",
            &workflow_id.to_string(),
            "--failed-only",
            "--restart",
            "--no-prompts",
        ])
        .output()
        .map_err(|e| internal_error(format!("Failed to execute torc command: {}", e)))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(internal_error(format!(
            "torc command failed: {}",
            stderr.trim()
        )));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    Ok(CallToolResult::success(vec![rmcp::model::Content::text(
        stdout.to_string(),
    )]))
}

/// Update job resource requirements.
pub fn update_job_resources(
    config: &Configuration,
    job_id: i64,
    num_cpus: Option<i64>,
    memory: Option<String>,
    runtime: Option<String>,
) -> Result<CallToolResult, McpError> {
    // Get the job to find its resource requirements ID
    let job = default_api::get_job(config, job_id)
        .map_err(|e| internal_error(format!("Failed to get job: {}", e)))?;

    let req_id = job
        .resource_requirements_id
        .ok_or_else(|| invalid_params("Job does not have resource requirements to update"))?;

    // Get current requirements
    let mut reqs = default_api::get_resource_requirements(config, req_id)
        .map_err(|e| internal_error(format!("Failed to get resource requirements: {}", e)))?;

    // Update fields if provided
    if let Some(cpus) = num_cpus {
        reqs.num_cpus = cpus;
    }
    if let Some(mem) = memory {
        reqs.memory = mem;
    }
    if let Some(rt) = runtime {
        reqs.runtime = rt;
    }

    // Update the resource requirements
    let updated = default_api::update_resource_requirements(
        config,
        req_id,
        ResourceRequirementsModel {
            id: reqs.id,
            workflow_id: reqs.workflow_id,
            name: reqs.name.clone(),
            num_cpus: reqs.num_cpus,
            num_gpus: reqs.num_gpus,
            num_nodes: reqs.num_nodes,
            memory: reqs.memory.clone(),
            runtime: reqs.runtime.clone(),
        },
    )
    .map_err(|e| internal_error(format!("Failed to update resource requirements: {}", e)))?;

    let result = serde_json::json!({
        "success": true,
        "job_id": job_id,
        "resource_requirements_id": req_id,
        "updated": {
            "num_cpus": updated.num_cpus,
            "num_gpus": updated.num_gpus,
            "memory": updated.memory,
            "runtime": updated.runtime,
        },
    });

    Ok(CallToolResult::success(vec![rmcp::model::Content::text(
        serde_json::to_string_pretty(&result).unwrap_or_default(),
    )]))
}

/// Cancel jobs.
pub fn cancel_jobs(config: &Configuration, job_ids: &[i64]) -> Result<CallToolResult, McpError> {
    let mut canceled = Vec::new();
    let mut errors = Vec::new();

    for job_id in job_ids {
        match default_api::manage_status_change(
            config,
            *job_id,
            JobStatus::Canceled,
            0, // run_id
            None,
        ) {
            Ok(_) => canceled.push(*job_id),
            Err(e) => errors.push(serde_json::json!({
                "job_id": job_id,
                "error": format!("{}", e),
            })),
        }
    }

    let result = serde_json::json!({
        "canceled_jobs": canceled,
        "canceled_count": canceled.len(),
        "errors": errors,
    });

    Ok(CallToolResult::success(vec![rmcp::model::Content::text(
        serde_json::to_string_pretty(&result).unwrap_or_default(),
    )]))
}

/// Create a workflow from a JSON specification.
pub fn create_workflow_from_spec(
    config: &Configuration,
    spec_json: &str,
    user: &str,
) -> Result<CallToolResult, McpError> {
    use std::io::Write;

    // Parse the spec to get the name for the result message
    let spec: serde_json::Value = serde_json::from_str(spec_json)
        .map_err(|e| invalid_params(&format!("Invalid workflow spec JSON: {}", e)))?;

    let name = spec
        .get("name")
        .and_then(|v| v.as_str())
        .unwrap_or("unnamed");

    // Write spec to a temp file
    let mut temp_file = tempfile::NamedTempFile::new()
        .map_err(|e| internal_error(format!("Failed to create temp file: {}", e)))?;

    temp_file
        .write_all(spec_json.as_bytes())
        .map_err(|e| internal_error(format!("Failed to write spec to temp file: {}", e)))?;

    let temp_path = temp_file.path();

    // Create the workflow using the existing function
    let workflow_id = torc::client::workflow_spec::WorkflowSpec::create_workflow_from_spec(
        config, temp_path, user, false, false,
    )
    .map_err(|e| internal_error(format!("Failed to create workflow: {}", e)))?;

    let result = serde_json::json!({
        "success": true,
        "workflow_id": workflow_id,
        "message": format!("Created workflow '{}' with ID {}", name, workflow_id),
    });

    Ok(CallToolResult::success(vec![rmcp::model::Content::text(
        serde_json::to_string_pretty(&result).unwrap_or_default(),
    )]))
}

/// Restart jobs in a workflow.
pub fn restart_jobs(
    workflow_id: i64,
    failed_only: Option<bool>,
    job_ids: Option<Vec<i64>>,
) -> Result<CallToolResult, McpError> {
    let mut cmd = Command::new("torc");
    cmd.args(["-f", "json", "workflows", "reset-status"]);
    cmd.arg(workflow_id.to_string());

    if failed_only.unwrap_or(true) {
        cmd.arg("--failed-only");
    }

    cmd.args(["--restart", "--no-prompts"]);

    if let Some(ids) = &job_ids {
        for id in ids {
            cmd.args(["--job-id", &id.to_string()]);
        }
    }

    let output = cmd
        .output()
        .map_err(|e| internal_error(format!("Failed to run torc command: {}", e)))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    if !output.status.success() {
        return Ok(CallToolResult::success(vec![rmcp::model::Content::text(
            format!(
                "{{\"success\": false, \"error\": \"Command failed\", \"stderr\": {:?}}}",
                stderr.trim()
            ),
        )]));
    }

    // The CLI outputs JSON, pass it through
    let content = if stdout.trim().is_empty() {
        serde_json::json!({
            "success": true,
            "message": "Jobs restarted successfully"
        })
        .to_string()
    } else {
        stdout.to_string()
    };

    Ok(CallToolResult::success(vec![rmcp::model::Content::text(
        content,
    )]))
}

/// Resubmit a workflow by regenerating Slurm schedulers and submitting allocations.
pub fn resubmit_workflow(
    output_dir: &PathBuf,
    workflow_id: i64,
    account: Option<String>,
    profile: Option<String>,
    dry_run: bool,
) -> Result<CallToolResult, McpError> {
    let mut cmd = Command::new("torc");
    cmd.args(["-f", "json", "slurm", "regenerate"]);
    cmd.arg(workflow_id.to_string());

    if let Some(acct) = &account {
        cmd.args(["--account", acct]);
    }

    if let Some(prof) = &profile {
        cmd.args(["--profile", prof]);
    }

    cmd.args(["--output-dir", output_dir.to_str().unwrap_or("output")]);

    if !dry_run {
        cmd.arg("--submit");
    }

    let output = cmd
        .output()
        .map_err(|e| internal_error(format!("Failed to run torc command: {}", e)))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    if !output.status.success() {
        return Ok(CallToolResult::success(vec![rmcp::model::Content::text(
            format!(
                "{{\"success\": false, \"error\": \"Command failed\", \"stderr\": {:?}}}",
                stderr.trim()
            ),
        )]));
    }

    // The CLI outputs JSON, pass it through
    let content = if stdout.trim().is_empty() {
        serde_json::json!({
            "success": true,
            "workflow_id": workflow_id,
            "dry_run": dry_run,
            "message": if dry_run { "Preview complete" } else { "Allocations submitted" }
        })
        .to_string()
    } else {
        stdout.to_string()
    };

    Ok(CallToolResult::success(vec![rmcp::model::Content::text(
        content,
    )]))
}
