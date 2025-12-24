//! Tool implementations for the Torc MCP server.

use rmcp::{Error as McpError, model::CallToolResult};
use std::fs;
use std::path::PathBuf;
use std::process::Command;

use torc::client::apis::configuration::Configuration;
use torc::client::apis::default_api;
use torc::client::commands::pagination::jobs::{JobListParams, paginate_jobs};
use torc::client::commands::pagination::results::{ResultListParams, paginate_results};
use torc::client::log_paths;
use torc::models::{JobStatus, ResourceRequirementsModel};

/// Helper to create an internal error
fn internal_error(msg: String) -> McpError {
    McpError::internal_error(msg, None)
}

/// Helper to create an invalid params error
fn invalid_params(msg: &str) -> McpError {
    McpError::invalid_request(msg.to_string(), None)
}

/// Get workflow status with job counts.
pub fn get_workflow_status(
    config: &Configuration,
    workflow_id: i64,
) -> Result<CallToolResult, McpError> {
    // Get workflow info
    let workflow = default_api::get_workflow(config, workflow_id)
        .map_err(|e| internal_error(format!("Failed to get workflow: {}", e)))?;

    // Get all jobs
    let jobs = paginate_jobs(config, workflow_id, JobListParams::new())
        .map_err(|e| internal_error(format!("Failed to list jobs: {}", e)))?;

    // Count jobs by status
    let mut status_counts = std::collections::HashMap::new();
    for job in &jobs {
        if let Some(status) = &job.status {
            let status_str = format!("{:?}", status);
            *status_counts.entry(status_str).or_insert(0) += 1;
        }
    }

    let result = serde_json::json!({
        "workflow_id": workflow.id,
        "name": workflow.name,
        "user": workflow.user,
        "description": workflow.description,
        "total_jobs": jobs.len(),
        "job_counts_by_status": status_counts,
    });

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
    let result = paginate_results(
        config,
        job.workflow_id,
        ResultListParams::new().with_job_id(job_id).with_limit(1),
    )
    .ok()
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
    let jobs = paginate_jobs(
        config,
        workflow_id,
        JobListParams::new().with_status(JobStatus::Failed),
    )
    .map_err(|e| internal_error(format!("Failed to list jobs: {}", e)))?;

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

    let result = serde_json::json!({
        "workflow_id": workflow_id,
        "failed_job_count": failed_jobs.len(),
        "failed_jobs": failed_jobs,
    });

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
    let status_enum: JobStatus = status
        .to_lowercase()
        .parse()
        .map_err(|_| invalid_params("Invalid status value"))?;

    let jobs = paginate_jobs(
        config,
        workflow_id,
        JobListParams::new().with_status(status_enum),
    )
    .map_err(|e| internal_error(format!("Failed to list jobs: {}", e)))?;

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

    let result = serde_json::json!({
        "workflow_id": workflow_id,
        "status": status,
        "count": job_list.len(),
        "jobs": job_list,
    });

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

/// Create a workflow from a JSON specification.
///
/// Supports:
/// - action: "create_workflow" (create in database) or "save_spec_file" (save to filesystem)
/// - workflow_type: "local" or "slurm"
#[allow(clippy::too_many_arguments)]
pub fn create_workflow(
    config: &Configuration,
    spec_json: &str,
    user: &str,
    action: &str,
    workflow_type: &str,
    account: Option<&str>,
    hpc_profile: Option<&str>,
    output_path: Option<&str>,
) -> Result<CallToolResult, McpError> {
    use std::io::Write;

    // Validate action
    if action != "create_workflow" && action != "save_spec_file" {
        return Err(invalid_params(
            "action must be 'create_workflow' or 'save_spec_file'",
        ));
    }

    // Validate workflow_type
    if workflow_type != "local" && workflow_type != "slurm" {
        return Err(invalid_params("workflow_type must be 'local' or 'slurm'"));
    }

    // For slurm workflows, prompt user for account if not provided
    if workflow_type == "slurm" && account.is_none() {
        let prompt_msg = serde_json::json!({
            "status": "need_input",
            "message": "Slurm workflows require an account for job submission.",
            "action_required": "Please ask the user: What Slurm account should be used for this workflow? (This is typically a project or allocation name like 'myproject' or 'research-gpu')",
            "then": "Call this tool again with the account parameter set to the user's response."
        });
        return Ok(CallToolResult::success(vec![rmcp::model::Content::text(
            serde_json::to_string_pretty(&prompt_msg).unwrap_or_default(),
        )]));
    }

    // Validate save_spec_file requirements
    if action == "save_spec_file" && output_path.is_none() {
        return Err(invalid_params(
            "output_path is required for save_spec_file action",
        ));
    }

    // Parse the spec
    let spec: serde_json::Value = serde_json::from_str(spec_json)
        .map_err(|e| invalid_params(&format!("Invalid workflow spec JSON: {}", e)))?;

    let name = spec
        .get("name")
        .and_then(|v| v.as_str())
        .unwrap_or("unnamed")
        .to_string();

    // For Slurm workflows, validate resource_requirements exist
    if workflow_type == "slurm" {
        // Check if resource_requirements section exists and has entries
        let has_resource_reqs = spec
            .get("resource_requirements")
            .and_then(|v| v.as_array())
            .map(|a| !a.is_empty())
            .unwrap_or(false);

        // Find jobs missing resource_requirements
        let jobs_missing_reqs: Vec<String> = spec
            .get("jobs")
            .and_then(|v| v.as_array())
            .map(|jobs| {
                jobs.iter()
                    .filter(|job| {
                        job.get("resource_requirements").is_none()
                            || job.get("resource_requirements") == Some(&serde_json::Value::Null)
                    })
                    .filter_map(|job| job.get("name").and_then(|n| n.as_str()).map(String::from))
                    .collect()
            })
            .unwrap_or_default();

        // If missing resource_requirements section or jobs without assignments, return helpful error
        if !has_resource_reqs || !jobs_missing_reqs.is_empty() {
            let mut issues = Vec::new();

            if !has_resource_reqs {
                issues.push(
                    "The workflow spec is missing a 'resource_requirements' section.".to_string(),
                );
            }

            if !jobs_missing_reqs.is_empty() {
                issues.push(format!(
                    "The following jobs are missing resource_requirements: {}",
                    jobs_missing_reqs.join(", ")
                ));
            }

            let error_msg = serde_json::json!({
                "error": "missing_resource_requirements",
                "message": "Slurm workflows require resource requirements for all jobs.",
                "issues": issues,
                "help": "Please ask the user to specify resource requirements for their jobs. Each resource requirement needs: name, num_cpus (integer), memory (e.g., '4g', '512m'), runtime (ISO8601 duration like 'PT1H' for 1 hour, 'PT30M' for 30 minutes). Jobs can share requirements by referencing the same name. Example structure:",
                "example": {
                    "resource_requirements": [
                        {"name": "small", "num_cpus": 1, "memory": "2g", "runtime": "PT30M", "num_gpus": 0, "num_nodes": 1},
                        {"name": "large", "num_cpus": 8, "memory": "32g", "runtime": "PT4H", "num_gpus": 0, "num_nodes": 1}
                    ],
                    "jobs": [
                        {"name": "job1", "command": "...", "resource_requirements": "small"},
                        {"name": "job2", "command": "...", "resource_requirements": "large"}
                    ]
                }
            });

            return Ok(CallToolResult::success(vec![rmcp::model::Content::text(
                serde_json::to_string_pretty(&error_msg).unwrap_or_default(),
            )]));
        }
    }

    // Write spec to a temp file (needed for CLI commands)
    let mut temp_file = tempfile::NamedTempFile::new()
        .map_err(|e| internal_error(format!("Failed to create temp file: {}", e)))?;

    temp_file
        .write_all(spec_json.as_bytes())
        .map_err(|e| internal_error(format!("Failed to write spec to temp file: {}", e)))?;

    let temp_path = temp_file.path();

    match (action, workflow_type) {
        ("create_workflow", "local") => {
            // Create local workflow using the library function
            let workflow_id = torc::client::workflow_spec::WorkflowSpec::create_workflow_from_spec(
                config, temp_path, user, false, false,
            )
            .map_err(|e| internal_error(format!("Failed to create workflow: {}", e)))?;

            let result = serde_json::json!({
                "success": true,
                "workflow_id": workflow_id,
                "message": format!("Created local workflow '{}' with ID {}", name, workflow_id),
            });

            Ok(CallToolResult::success(vec![rmcp::model::Content::text(
                serde_json::to_string_pretty(&result).unwrap_or_default(),
            )]))
        }
        ("create_workflow", "slurm") => {
            // Create slurm workflow using CLI: torc workflows create-slurm
            let mut cmd = Command::new("torc");
            cmd.args(["-f", "json", "workflows", "create-slurm"]);
            cmd.args(["--account", account.unwrap()]);
            cmd.args(["--user", user]);

            if let Some(profile) = hpc_profile {
                cmd.args(["--hpc-profile", profile]);
            }

            cmd.arg(temp_path);

            let output = cmd
                .output()
                .map_err(|e| internal_error(format!("Failed to run torc command: {}", e)))?;

            if !output.status.success() {
                let stderr = String::from_utf8_lossy(&output.stderr);
                return Err(internal_error(format!(
                    "Failed to create slurm workflow: {}",
                    stderr.trim()
                )));
            }

            let stdout = String::from_utf8_lossy(&output.stdout);

            // Try to parse the workflow ID from the output
            let result = if let Ok(parsed) = serde_json::from_str::<serde_json::Value>(&stdout) {
                parsed
            } else {
                serde_json::json!({
                    "success": true,
                    "message": format!("Created slurm workflow '{}'", name),
                    "output": stdout.trim(),
                })
            };

            Ok(CallToolResult::success(vec![rmcp::model::Content::text(
                serde_json::to_string_pretty(&result).unwrap_or_default(),
            )]))
        }
        ("save_spec_file", "local") => {
            // Save the spec as JSON to the output path
            let output_path = output_path.unwrap();
            let content = serde_json::to_string_pretty(&spec)
                .map_err(|e| internal_error(format!("Failed to serialize spec: {}", e)))?;
            std::fs::write(output_path, &content)
                .map_err(|e| internal_error(format!("Failed to write spec file: {}", e)))?;

            let result = serde_json::json!({
                "success": true,
                "message": format!("Saved workflow spec '{}' to {}", name, output_path),
                "output_path": output_path,
            });

            Ok(CallToolResult::success(vec![rmcp::model::Content::text(
                serde_json::to_string_pretty(&result).unwrap_or_default(),
            )]))
        }
        ("save_spec_file", "slurm") => {
            // Generate slurm schedulers and save as JSON
            let output_path = output_path.unwrap();

            let mut cmd = Command::new("torc");
            cmd.args(["slurm", "generate"]);
            cmd.args(["--account", account.unwrap()]);
            cmd.args(["--output", output_path]);

            if let Some(profile) = hpc_profile {
                cmd.args(["--profile", profile]);
            }

            cmd.arg(temp_path);

            let output = cmd
                .output()
                .map_err(|e| internal_error(format!("Failed to run torc command: {}", e)))?;

            if !output.status.success() {
                let stderr = String::from_utf8_lossy(&output.stderr);
                return Err(internal_error(format!(
                    "Failed to generate slurm spec: {}",
                    stderr.trim()
                )));
            }

            let result = serde_json::json!({
                "success": true,
                "message": format!("Generated slurm workflow spec '{}' at {}", name, output_path),
                "output_path": output_path,
            });

            Ok(CallToolResult::success(vec![rmcp::model::Content::text(
                serde_json::to_string_pretty(&result).unwrap_or_default(),
            )]))
        }
        _ => Err(invalid_params("Invalid action/workflow_type combination")),
    }
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
