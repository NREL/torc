use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::commands::output::print_json;
use crate::client::commands::{
    get_env_user_name, pagination, print_error, select_workflow_interactively,
    table_format::display_table_with_count,
};
use crate::client::log_paths::{
    get_job_runner_log_file, get_job_stderr_path, get_job_stdout_path,
    get_slurm_job_runner_log_file, get_slurm_stderr_path, get_slurm_stdout_path,
};
use crate::models;
use crate::time_utils::duration_string_to_seconds;
use chrono::{DateTime, FixedOffset};
use std::path::Path;
use tabled::Tabled;

/// Format memory bytes into a human-readable string
fn format_memory_bytes(bytes: i64) -> String {
    let mb = bytes as f64 / (1024.0 * 1024.0);
    if mb < 1024.0 {
        format!("{:.1} MB", mb)
    } else {
        format!("{:.2} GB", mb / 1024.0)
    }
}

/// Format seconds into a human-readable duration string
fn format_duration(seconds: f64) -> String {
    let hours = (seconds / 3600.0).floor();
    let minutes = ((seconds % 3600.0) / 60.0).floor();
    let secs = (seconds % 60.0).floor();

    if hours > 0.0 {
        format!("{:.0}h {:.0}m {:.0}s", hours, minutes, secs)
    } else if minutes > 0.0 {
        format!("{:.0}m {:.0}s", minutes, secs)
    } else {
        format!("{:.1}s", seconds)
    }
}

#[derive(Tabled)]
struct ResourceUtilizationRow {
    #[tabled(rename = "Job ID")]
    job_id: i64,
    #[tabled(rename = "Job Name")]
    job_name: String,
    #[tabled(rename = "Resource")]
    resource_type: String,
    #[tabled(rename = "Specified")]
    specified: String,
    #[tabled(rename = "Peak Used")]
    peak_used: String,
    #[tabled(rename = "Over-Utilization")]
    over_utilization: String,
}

#[derive(clap::Subcommand)]
pub enum ReportCommands {
    /// Check resource utilization and report jobs that exceeded their specified requirements
    CheckResourceUtilization {
        /// Workflow ID to analyze (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// Run ID to analyze (optional - analyzes latest run if not provided)
        #[arg(short, long)]
        run_id: Option<i64>,
        /// Show all jobs (default: only show jobs that exceeded requirements)
        #[arg(short, long)]
        all: bool,
        /// Include failed and terminated jobs in the analysis (for recovery diagnostics)
        #[arg(long)]
        include_failed: bool,
    },
    /// Generate a comprehensive JSON report of job results including all log file paths
    Results {
        /// Workflow ID to analyze (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// Output directory (where job logs are stored, passed in `torc run` and `torc submit`)
        #[arg(short, long, default_value = "output")]
        output_dir: std::path::PathBuf,
        /// Include all runs for each job (default: only latest run)
        #[arg(long)]
        all_runs: bool,
    },
    /// Generate a summary of workflow results (requires workflow to be complete)
    Summary {
        /// Workflow ID to summarize (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
    },
}

pub fn handle_report_commands(config: &Configuration, command: &ReportCommands, format: &str) {
    match command {
        ReportCommands::CheckResourceUtilization {
            workflow_id,
            run_id,
            all,
            include_failed,
        } => {
            check_resource_utilization(
                config,
                *workflow_id,
                *run_id,
                *all,
                *include_failed,
                format,
            );
        }
        ReportCommands::Results {
            workflow_id,
            output_dir,
            all_runs,
        } => {
            generate_results_report(config, *workflow_id, output_dir, *all_runs);
        }
        ReportCommands::Summary { workflow_id } => {
            generate_summary(config, *workflow_id, format);
        }
    }
}

fn check_resource_utilization(
    config: &Configuration,
    workflow_id: Option<i64>,
    run_id: Option<i64>,
    show_all: bool,
    include_failed: bool,
    format: &str,
) {
    // Get or select workflow ID
    let user = get_env_user_name();
    let wf_id = match workflow_id {
        Some(id) => id,
        None => match select_workflow_interactively(config, &user) {
            Ok(id) => id,
            Err(e) => {
                eprintln!("Error selecting workflow: {}", e);
                std::process::exit(1);
            }
        },
    };

    // Fetch completed results for the workflow using pagination
    let mut params = pagination::ResultListParams::new().with_status(models::JobStatus::Completed);
    if let Some(rid) = run_id {
        params = params.with_run_id(rid);
    }
    let completed_results = match pagination::paginate_results(config, wf_id, params) {
        Ok(results) => results,
        Err(e) => {
            print_error("fetching completed results", &e);
            std::process::exit(1);
        }
    };

    // Fetch failed and terminated results if requested
    // (terminated jobs are typically killed due to walltime/OOM, so they need recovery too)
    let failed_results = if include_failed {
        let mut failed_params =
            pagination::ResultListParams::new().with_status(models::JobStatus::Failed);
        if let Some(rid) = run_id {
            failed_params = failed_params.with_run_id(rid);
        }
        match pagination::paginate_results(config, wf_id, failed_params) {
            Ok(results) => results,
            Err(e) => {
                print_error("fetching failed results", &e);
                std::process::exit(1);
            }
        }
    } else {
        Vec::new()
    };

    let terminated_results = if include_failed {
        let mut terminated_params =
            pagination::ResultListParams::new().with_status(models::JobStatus::Terminated);
        if let Some(rid) = run_id {
            terminated_params = terminated_params.with_run_id(rid);
        }
        match pagination::paginate_results(config, wf_id, terminated_params) {
            Ok(results) => results,
            Err(e) => {
                print_error("fetching terminated results", &e);
                std::process::exit(1);
            }
        }
    } else {
        Vec::new()
    };

    // Combine results
    let mut results = completed_results;
    results.extend(failed_results);
    results.extend(terminated_results);

    if results.is_empty() {
        let msg = if include_failed {
            format!(
                "No completed, failed, or terminated job results found for workflow {}",
                wf_id
            )
        } else {
            format!("No completed job results found for workflow {}", wf_id)
        };
        println!("{}", msg);
        std::process::exit(0);
    }

    // Fetch all jobs to get resource requirements using pagination
    let jobs = match pagination::paginate_jobs(config, wf_id, pagination::JobListParams::new()) {
        Ok(jobs) => jobs,
        Err(e) => {
            print_error("fetching jobs", &e);
            std::process::exit(1);
        }
    };

    // Fetch all resource requirements using pagination
    let resource_reqs = match pagination::paginate_resource_requirements(
        config,
        wf_id,
        pagination::ResourceRequirementsListParams::new(),
    ) {
        Ok(reqs) => reqs,
        Err(e) => {
            print_error("fetching resource requirements", &e);
            std::process::exit(1);
        }
    };

    // Build lookup maps
    let job_map: std::collections::HashMap<i64, &models::JobModel> =
        jobs.iter().filter_map(|j| j.id.map(|id| (id, j))).collect();

    let resource_req_map: std::collections::HashMap<i64, &models::ResourceRequirementsModel> =
        resource_reqs
            .iter()
            .filter_map(|rr| rr.id.map(|id| (id, rr)))
            .collect();

    // Analyze each result
    let mut rows = Vec::new();
    let mut over_util_count = 0;
    let mut failed_jobs_info: Vec<serde_json::Value> = Vec::new();

    for result in &results {
        let job_id = result.job_id;
        // Consider both Failed and Terminated as "failed" for recovery purposes
        // Terminated typically means killed by Slurm due to walltime/OOM
        let is_failed = result.status == models::JobStatus::Failed
            || result.status == models::JobStatus::Terminated;

        // Get job and its resource requirements
        let job = match job_map.get(&job_id) {
            Some(j) => j,
            None => {
                eprintln!("Warning: Job {} not found in job list", job_id);
                continue;
            }
        };

        let resource_req_id = match job.resource_requirements_id {
            Some(id) => id,
            None => {
                eprintln!("Warning: Job {} has no resource requirements", job_id);
                continue;
            }
        };

        let resource_req = match resource_req_map.get(&resource_req_id) {
            Some(rr) => rr,
            None => {
                eprintln!(
                    "Warning: Resource requirements {} not found",
                    resource_req_id
                );
                continue;
            }
        };

        let job_name = job.name.clone();

        // Track failed jobs separately with their resource info
        if is_failed {
            let mut failed_info = serde_json::json!({
                "job_id": job_id,
                "job_name": job_name.clone(),
                "return_code": result.return_code,
                "exec_time_minutes": result.exec_time_minutes,
                "configured_memory": resource_req.memory.clone(),
                "configured_runtime": resource_req.runtime.clone(),
                "configured_cpus": resource_req.num_cpus,
            });

            let mut likely_oom = false;

            // Add resource usage if available
            if let Some(peak_mem) = result.peak_memory_bytes {
                failed_info["peak_memory_bytes"] = serde_json::json!(peak_mem);
                failed_info["peak_memory_formatted"] =
                    serde_json::json!(format_memory_bytes(peak_mem));

                // Check if it's an OOM issue based on memory usage
                let specified_memory_bytes = parse_memory_string(&resource_req.memory);
                if peak_mem > specified_memory_bytes {
                    likely_oom = true;
                    failed_info["oom_reason"] = serde_json::json!("memory_exceeded");
                    let over_pct =
                        ((peak_mem as f64 / specified_memory_bytes as f64) - 1.0) * 100.0;
                    failed_info["memory_over_utilization"] =
                        serde_json::json!(format!("+{:.1}%", over_pct));
                }
            }

            // Check if runtime exceeded (do this before OOM detection to distinguish)
            let exec_time_seconds = result.exec_time_minutes * 60.0;
            let mut likely_timeout = false;
            if let Ok(specified_runtime_seconds) = duration_string_to_seconds(&resource_req.runtime)
            {
                let specified_runtime_seconds = specified_runtime_seconds as f64;
                let pct_of_runtime = (exec_time_seconds / specified_runtime_seconds) * 100.0;
                failed_info["runtime_utilization"] =
                    serde_json::json!(format!("{:.1}%", pct_of_runtime));

                if exec_time_seconds > specified_runtime_seconds * 0.9 {
                    // If job ran for > 90% of its runtime, it might be a timeout
                    likely_timeout = true;
                }

                // Check for explicit timeout signals
                // Return code 152 (128 + SIGXCPU) indicates CPU time limit exceeded
                if result.return_code == 152 {
                    likely_timeout = true;
                    failed_info["timeout_reason"] = serde_json::json!("sigxcpu_152");
                }
            }

            if likely_timeout {
                failed_info["likely_timeout"] = serde_json::json!(true);
            }

            // Check for OOM via return code 137 (128 + SIGKILL)
            // When Slurm OOM-kills a job, resource metrics may not be recorded
            // but return code 137 is a strong indicator - unless it's a timeout
            //
            // Heuristic: If job ran for < 80% of its runtime and got SIGKILL, likely OOM
            // If job ran for > 90% of its runtime and got SIGKILL, likely timeout
            if !likely_oom && result.return_code == 137 {
                if let Ok(specified_runtime_seconds) =
                    duration_string_to_seconds(&resource_req.runtime)
                {
                    let specified_runtime_seconds = specified_runtime_seconds as f64;
                    let pct_of_runtime = (exec_time_seconds / specified_runtime_seconds) * 100.0;

                    // If job ran for less than 80% of its runtime, likely OOM not timeout
                    if pct_of_runtime < 80.0 {
                        likely_oom = true;
                        failed_info["oom_reason"] = serde_json::json!("sigkill_137");
                    }
                } else {
                    // Can't determine runtime percentage, assume OOM if SIGKILL
                    likely_oom = true;
                    failed_info["oom_reason"] = serde_json::json!("sigkill_137");
                }
            }

            if likely_oom {
                failed_info["likely_oom"] = serde_json::json!(true);
            }

            failed_jobs_info.push(failed_info);
        }

        // Check memory over-utilization
        if let Some(peak_memory_bytes) = result.peak_memory_bytes {
            let specified_memory_bytes = parse_memory_string(&resource_req.memory);
            if peak_memory_bytes > specified_memory_bytes {
                over_util_count += 1;
                let over_pct =
                    ((peak_memory_bytes as f64 / specified_memory_bytes as f64) - 1.0) * 100.0;
                rows.push(ResourceUtilizationRow {
                    job_id,
                    job_name: job_name.clone(),
                    resource_type: "Memory".to_string(),
                    specified: format_memory_bytes(specified_memory_bytes),
                    peak_used: format_memory_bytes(peak_memory_bytes),
                    over_utilization: format!("+{:.1}%", over_pct),
                });
            } else if show_all {
                let under_pct =
                    (1.0 - (peak_memory_bytes as f64 / specified_memory_bytes as f64)) * 100.0;
                rows.push(ResourceUtilizationRow {
                    job_id,
                    job_name: job_name.clone(),
                    resource_type: "Memory".to_string(),
                    specified: format_memory_bytes(specified_memory_bytes),
                    peak_used: format_memory_bytes(peak_memory_bytes),
                    over_utilization: format!("-{:.1}%", under_pct),
                });
            }
        }

        // Check CPU over-utilization
        // Note: CPU percent is per-core, so we need to account for num_cpus
        if let Some(peak_cpu_percent) = result.peak_cpu_percent {
            let num_cpus = resource_req.num_cpus;
            let specified_cpu_percent = 100.0 * num_cpus as f64; // 100% per CPU

            if peak_cpu_percent > specified_cpu_percent {
                over_util_count += 1;
                let over_pct = ((peak_cpu_percent / specified_cpu_percent) - 1.0) * 100.0;
                rows.push(ResourceUtilizationRow {
                    job_id,
                    job_name: job_name.clone(),
                    resource_type: "CPU".to_string(),
                    specified: format!("{:.0}% ({} cores)", specified_cpu_percent, num_cpus),
                    peak_used: format!("{:.1}%", peak_cpu_percent),
                    over_utilization: format!("+{:.1}%", over_pct),
                });
            } else if show_all {
                let under_pct = (1.0 - (peak_cpu_percent / specified_cpu_percent)) * 100.0;
                rows.push(ResourceUtilizationRow {
                    job_id,
                    job_name: job_name.clone(),
                    resource_type: "CPU".to_string(),
                    specified: format!("{:.0}% ({} cores)", specified_cpu_percent, num_cpus),
                    peak_used: format!("{:.1}%", peak_cpu_percent),
                    over_utilization: format!("-{:.1}%", under_pct),
                });
            }
        }

        // Check runtime over-utilization
        let exec_time_seconds = result.exec_time_minutes * 60.0;
        let specified_runtime_seconds = match duration_string_to_seconds(&resource_req.runtime) {
            Ok(s) => s as f64,
            Err(e) => {
                eprintln!("Warning: Failed to parse runtime for job {}: {}", job_id, e);
                continue;
            }
        };

        if exec_time_seconds > specified_runtime_seconds {
            over_util_count += 1;
            let over_pct = ((exec_time_seconds / specified_runtime_seconds) - 1.0) * 100.0;
            rows.push(ResourceUtilizationRow {
                job_id,
                job_name: job_name.clone(),
                resource_type: "Runtime".to_string(),
                specified: format_duration(specified_runtime_seconds),
                peak_used: format_duration(exec_time_seconds),
                over_utilization: format!("+{:.1}%", over_pct),
            });
        } else if show_all {
            let under_pct = (1.0 - (exec_time_seconds / specified_runtime_seconds)) * 100.0;
            rows.push(ResourceUtilizationRow {
                job_id,
                job_name: job_name.clone(),
                resource_type: "Runtime".to_string(),
                specified: format_duration(specified_runtime_seconds),
                peak_used: format_duration(exec_time_seconds),
                over_utilization: format!("-{:.1}%", under_pct),
            });
        }
    }

    // Output results
    match format {
        "json" => {
            let mut json_output = serde_json::json!({
                "workflow_id": wf_id,
                "run_id": run_id,
                "total_results": results.len(),
                "over_utilization_count": over_util_count,
                "violations": rows.iter().map(|r| {
                    serde_json::json!({
                        "job_id": r.job_id,
                        "job_name": r.job_name,
                        "resource_type": r.resource_type,
                        "specified": r.specified,
                        "peak_used": r.peak_used,
                        "over_utilization": r.over_utilization,
                    })
                }).collect::<Vec<_>>(),
            });

            // Add failed jobs section if there are any
            if !failed_jobs_info.is_empty() {
                json_output["failed_jobs_count"] = serde_json::json!(failed_jobs_info.len());
                json_output["failed_jobs"] = serde_json::json!(failed_jobs_info);
            }

            print_json(&json_output, "resource utilization");
        }
        _ => {
            if rows.is_empty() {
                if show_all {
                    println!(
                        "All {} jobs stayed within their specified resource requirements",
                        results.len()
                    );
                } else {
                    println!(
                        "✓ All {} jobs stayed within their specified resource requirements",
                        results.len()
                    );
                }
            } else {
                if !show_all {
                    println!(
                        "\n⚠ Found {} resource over-utilization violations:\n",
                        over_util_count
                    );
                }
                display_table_with_count(&rows, "violations");

                if !show_all {
                    println!(
                        "\nNote: Use --all to see all jobs, including those that stayed within limits"
                    );
                }
            }
        }
    }
}

/// Parse memory string (e.g., "1g", "512m") into bytes
fn parse_memory_string(mem_str: &str) -> i64 {
    let mem_str = mem_str.trim().to_lowercase();

    // Find where the number ends and the unit begins
    let split_pos = mem_str
        .chars()
        .position(|c| c.is_alphabetic())
        .unwrap_or(mem_str.len());

    let (num_part, unit_part) = mem_str.split_at(split_pos);

    let value: f64 = num_part.trim().parse().unwrap_or(0.0);

    match unit_part {
        "k" | "kb" => (value * 1024.0) as i64,
        "m" | "mb" => (value * 1024.0 * 1024.0) as i64,
        "g" | "gb" => (value * 1024.0 * 1024.0 * 1024.0) as i64,
        "t" | "tb" => (value * 1024.0 * 1024.0 * 1024.0 * 1024.0) as i64,
        _ => value as i64, // Assume bytes if no unit
    }
}

/// Check if a log file exists and log a warning if it doesn't
fn check_log_file_exists(path: &str, log_type: &str, job_id: i64) {
    if !std::path::Path::new(path).exists() {
        eprintln!(
            "Warning: {} log file does not exist for job {}: {}",
            log_type, job_id, path
        );
    }
}

/// Generate comprehensive JSON report of job results including log file paths
fn generate_results_report(
    config: &Configuration,
    workflow_id: Option<i64>,
    output_dir: &Path,
    all_runs: bool,
) {
    // Validate that output directory exists
    if !output_dir.exists() {
        eprintln!(
            "Error: Output directory does not exist: {}",
            output_dir.display()
        );
        std::process::exit(1);
    }

    if !output_dir.is_dir() {
        eprintln!(
            "Error: Output path is not a directory: {}",
            output_dir.display()
        );
        std::process::exit(1);
    }

    // Get or select workflow ID
    let user = get_env_user_name();
    let wf_id = match workflow_id {
        Some(id) => id,
        None => match select_workflow_interactively(config, &user) {
            Ok(id) => id,
            Err(e) => {
                eprintln!("Error selecting workflow: {}", e);
                std::process::exit(1);
            }
        },
    };

    // Fetch workflow
    let workflow = match default_api::get_workflow(config, wf_id) {
        Ok(wf) => wf,
        Err(e) => {
            print_error("fetching workflow", &e);
            std::process::exit(1);
        }
    };

    // Fetch all jobs using pagination
    let jobs = match pagination::paginate_jobs(config, wf_id, pagination::JobListParams::new()) {
        Ok(jobs) => jobs,
        Err(e) => {
            print_error("fetching jobs", &e);
            std::process::exit(1);
        }
    };

    // Build job map for quick lookup
    let job_map: std::collections::HashMap<i64, &models::JobModel> =
        jobs.iter().filter_map(|j| j.id.map(|id| (id, j))).collect();

    // Fetch results (all runs or just latest) using pagination
    let params = pagination::ResultListParams::new().with_all_runs(all_runs);
    let results = match pagination::paginate_results(config, wf_id, params) {
        Ok(results) => results,
        Err(e) => {
            print_error("fetching results", &e);
            std::process::exit(1);
        }
    };

    if results.is_empty() {
        eprintln!("No results found for workflow {}", wf_id);
        std::process::exit(0);
    }

    // Build result records
    let mut result_records = Vec::new();

    for result in &results {
        let job_id = result.job_id;

        // Get job info
        let job = match job_map.get(&job_id) {
            Some(j) => j,
            None => {
                eprintln!("Warning: Job {} not found in job list", job_id);
                continue;
            }
        };

        // Build base result record
        let mut record = serde_json::json!({
            "job_id": job_id,
            "job_name": job.name,
            "status": format!("{:?}", result.status),
            "run_id": result.run_id,
            "return_code": result.return_code,
            "completion_time": result.completion_time,
            "exec_time_minutes": result.exec_time_minutes,
            "compute_node_id": result.compute_node_id,
        });

        // Add job stdio log paths
        let job_stdout = get_job_stdout_path(output_dir, wf_id, job_id, result.run_id);
        let job_stderr = get_job_stderr_path(output_dir, wf_id, job_id, result.run_id);
        check_log_file_exists(&job_stdout, "job stdout", job_id);
        check_log_file_exists(&job_stderr, "job stderr", job_id);
        record["job_stdout"] = serde_json::json!(job_stdout);
        record["job_stderr"] = serde_json::json!(job_stderr);

        // Get compute node and determine log file paths
        let compute_node_id = result.compute_node_id;
        match default_api::get_compute_node(config, compute_node_id) {
            Ok(compute_node) => {
                let compute_node_type = &compute_node.compute_node_type;
                record["compute_node_type"] = serde_json::json!(compute_node_type);

                match compute_node_type.as_str() {
                    "local" => {
                        // For local runner, we need hostname, workflow_id, and run_id
                        let log_path = get_job_runner_log_file(
                            output_dir.to_path_buf(),
                            &compute_node.hostname,
                            wf_id,
                            result.run_id,
                        );
                        check_log_file_exists(&log_path, "job runner", job_id);
                        record["job_runner_log"] = serde_json::json!(log_path);
                    }
                    "slurm" => {
                        // For slurm runner, extract slurm job ID from scheduler JSON
                        if let Some(scheduler_value) = &compute_node.scheduler
                            && let Some(slurm_job_id) = scheduler_value.get("slurm_job_id")
                            && let Some(slurm_job_id_str) = slurm_job_id.as_str()
                        {
                            // Build slurm job runner log path
                            // We need node_id and task_pid from the scheduler data
                            // The slurm job runner uses format: job_runner_slurm_{job_id}_{node_id}_{task_pid}.log
                            // We can extract node_id and task_pid from environment during slurm execution
                            // For now, we'll try to get it from the hostname or compute_node.pid

                            // Use hostname as node_id and pid as task_pid for the log path
                            let node_id = &compute_node.hostname;
                            let task_pid = compute_node.pid as usize;

                            let log_path = get_slurm_job_runner_log_file(
                                output_dir.to_path_buf(),
                                slurm_job_id_str,
                                node_id,
                                task_pid,
                            );
                            check_log_file_exists(&log_path, "slurm job runner", job_id);
                            record["job_runner_log"] = serde_json::json!(log_path);

                            // Add slurm stdout/stderr paths
                            let slurm_stdout = get_slurm_stdout_path(output_dir, slurm_job_id_str);
                            let slurm_stderr = get_slurm_stderr_path(output_dir, slurm_job_id_str);
                            check_log_file_exists(&slurm_stdout, "slurm stdout", job_id);
                            check_log_file_exists(&slurm_stderr, "slurm stderr", job_id);
                            record["slurm_stdout"] = serde_json::json!(slurm_stdout);
                            record["slurm_stderr"] = serde_json::json!(slurm_stderr);
                        }
                    }
                    _ => {
                        // Unknown compute node type
                        record["job_runner_log"] = serde_json::Value::Null;
                    }
                }
            }
            Err(e) => {
                eprintln!(
                    "Warning: Could not fetch compute node {}: {}",
                    compute_node_id, e
                );
                record["compute_node_type"] = serde_json::Value::Null;
                record["job_runner_log"] = serde_json::Value::Null;
            }
        }

        result_records.push(record);
    }

    // Build final JSON report
    let report = serde_json::json!({
        "workflow_id": wf_id,
        "workflow_name": workflow.name,
        "workflow_user": workflow.user,
        "all_runs": all_runs,
        "total_results": result_records.len(),
        "results": result_records,
    });

    // Output JSON
    print_json(&report, "results report");
}

/// Generate a summary of workflow results
fn generate_summary(config: &Configuration, workflow_id: Option<i64>, format: &str) {
    // Get or select workflow ID
    let user = get_env_user_name();
    let workflow_id = match workflow_id {
        Some(id) => id,
        None => match select_workflow_interactively(config, &user) {
            Ok(id) => id,
            Err(e) => {
                eprintln!("Error selecting workflow: {}", e);
                std::process::exit(1);
            }
        },
    };

    // Fetch workflow info
    let workflow = match default_api::get_workflow(config, workflow_id) {
        Ok(wf) => wf,
        Err(e) => {
            print_error("fetching workflow", &e);
            std::process::exit(1);
        }
    };

    // Fetch all jobs to get total count
    let jobs =
        match pagination::paginate_jobs(config, workflow_id, pagination::JobListParams::new()) {
            Ok(jobs) => jobs,
            Err(e) => {
                print_error("fetching jobs", &e);
                std::process::exit(1);
            }
        };

    let total_jobs = jobs.len();

    // Count jobs by status
    let mut uninitialized_count = 0;
    let mut blocked_count = 0;
    let mut ready_count = 0;
    let mut pending_count = 0;
    let mut running_count = 0;
    let mut completed_count = 0;
    let mut failed_count = 0;
    let mut canceled_count = 0;
    let mut terminated_count = 0;
    let mut disabled_count = 0;

    for job in &jobs {
        match job.status {
            Some(models::JobStatus::Uninitialized) => uninitialized_count += 1,
            Some(models::JobStatus::Blocked) => blocked_count += 1,
            Some(models::JobStatus::Ready) => ready_count += 1,
            Some(models::JobStatus::Pending) => pending_count += 1,
            Some(models::JobStatus::Running) => running_count += 1,
            Some(models::JobStatus::Completed) => completed_count += 1,
            Some(models::JobStatus::Failed) => failed_count += 1,
            Some(models::JobStatus::Canceled) => canceled_count += 1,
            Some(models::JobStatus::Terminated) => terminated_count += 1,
            Some(models::JobStatus::Disabled) => disabled_count += 1,
            None => {}
        }
    }

    // Fetch results to get execution time stats
    let results = match pagination::paginate_results(
        config,
        workflow_id,
        pagination::ResultListParams::new(),
    ) {
        Ok(results) => results,
        Err(e) => {
            print_error("fetching results", &e);
            std::process::exit(1);
        }
    };

    // Calculate total execution time
    let total_exec_time_minutes: f64 = results.iter().map(|r| r.exec_time_minutes).sum();

    // Calculate walltime (elapsed time from first job start to last job completion)
    let walltime_seconds: Option<f64> = {
        let mut min_start: Option<DateTime<FixedOffset>> = None;
        let mut max_end: Option<DateTime<FixedOffset>> = None;

        for result in &results {
            if let Ok(completion_time) = DateTime::parse_from_rfc3339(&result.completion_time) {
                // Calculate start time by subtracting execution time from completion time
                let exec_duration = chrono::Duration::milliseconds(
                    (result.exec_time_minutes * 60.0 * 1000.0) as i64,
                );
                let start_time = completion_time - exec_duration;

                min_start = Some(match min_start {
                    Some(current_min) if start_time < current_min => start_time,
                    Some(current_min) => current_min,
                    None => start_time,
                });

                max_end = Some(match max_end {
                    Some(current_max) if completion_time > current_max => completion_time,
                    Some(current_max) => current_max,
                    None => completion_time,
                });
            }
        }

        match (min_start, max_end) {
            (Some(start), Some(end)) => Some((end - start).num_milliseconds() as f64 / 1000.0),
            _ => None,
        }
    };

    // Output results
    if format == "json" {
        let mut report = serde_json::json!({
            "workflow_id": workflow_id,
            "workflow_name": workflow.name,
            "workflow_user": workflow.user,
            "total_jobs": total_jobs,
            "jobs_by_status": {
                "uninitialized": uninitialized_count,
                "blocked": blocked_count,
                "ready": ready_count,
                "pending": pending_count,
                "running": running_count,
                "completed": completed_count,
                "failed": failed_count,
                "canceled": canceled_count,
                "terminated": terminated_count,
                "disabled": disabled_count,
            },
            "total_exec_time_minutes": total_exec_time_minutes,
            "total_exec_time_formatted": format_duration(total_exec_time_minutes * 60.0),
        });

        if let Some(walltime) = walltime_seconds {
            report["walltime_seconds"] = serde_json::json!(walltime);
            report["walltime_formatted"] = serde_json::json!(format_duration(walltime));
        }

        print_json(&report, "workflow summary");
    } else {
        println!("Workflow Summary");
        println!("================");
        println!();
        println!("Workflow ID: {}", workflow_id);
        println!("Name: {}", workflow.name);
        println!("User: {}", workflow.user);
        println!();
        println!("Job Status (total: {}):", total_jobs);
        if uninitialized_count > 0 {
            println!("  Uninitialized: {}", uninitialized_count);
        }
        if blocked_count > 0 {
            println!("  Blocked:       {}", blocked_count);
        }
        if ready_count > 0 {
            println!("  Ready:         {}", ready_count);
        }
        if pending_count > 0 {
            println!("  Pending:       {}", pending_count);
        }
        if running_count > 0 {
            println!("  Running:       {}", running_count);
        }
        if completed_count > 0 {
            println!("  Completed:     {} ✓", completed_count);
        }
        if failed_count > 0 {
            println!("  Failed:        {} ✗", failed_count);
        }
        if canceled_count > 0 {
            println!("  Canceled:      {}", canceled_count);
        }
        if terminated_count > 0 {
            println!("  Terminated:    {} ✗", terminated_count);
        }
        if disabled_count > 0 {
            println!("  Disabled:      {}", disabled_count);
        }
        println!();
        println!(
            "Total Execution Time: {}",
            format_duration(total_exec_time_minutes * 60.0)
        );
        if let Some(walltime) = walltime_seconds {
            println!("Walltime:             {}", format_duration(walltime));
        }

        if completed_count == total_jobs {
            println!();
            println!("✓ All jobs completed successfully!");
        }
    }
}
