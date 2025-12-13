use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
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
use serde_json;
use std::path::PathBuf;
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
}

pub fn handle_report_commands(config: &Configuration, command: &ReportCommands, format: &str) {
    match command {
        ReportCommands::CheckResourceUtilization {
            workflow_id,
            run_id,
            all,
        } => {
            check_resource_utilization(config, *workflow_id, *run_id, *all, format);
        }
        ReportCommands::Results {
            workflow_id,
            output_dir,
            all_runs,
        } => {
            generate_results_report(config, *workflow_id, output_dir, *all_runs);
        }
    }
}

fn check_resource_utilization(
    config: &Configuration,
    workflow_id: Option<i64>,
    run_id: Option<i64>,
    show_all: bool,
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

    // Fetch results for the workflow using pagination
    let mut params = pagination::ResultListParams::new().with_status(models::JobStatus::Completed);
    if let Some(rid) = run_id {
        params = params.with_run_id(rid);
    }
    let results = match pagination::paginate_results(config, wf_id, params) {
        Ok(results) => results,
        Err(e) => {
            print_error("fetching results", &e);
            std::process::exit(1);
        }
    };

    if results.is_empty() {
        println!("No completed job results found for workflow {}", wf_id);
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

    for result in &results {
        let job_id = result.job_id;

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
            let json_output = serde_json::json!({
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
            println!("{}", serde_json::to_string_pretty(&json_output).unwrap());
        }
        "table" | _ => {
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
    output_dir: &PathBuf,
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
                            output_dir.clone(),
                            &compute_node.hostname,
                            wf_id,
                            result.run_id,
                        );
                        check_log_file_exists(&log_path, "job runner", job_id);
                        record["job_runner_log"] = serde_json::json!(log_path);
                    }
                    "slurm" => {
                        // For slurm runner, extract slurm job ID from scheduler JSON
                        if let Some(scheduler_value) = &compute_node.scheduler {
                            if let Some(slurm_job_id) = scheduler_value.get("slurm_job_id") {
                                if let Some(slurm_job_id_str) = slurm_job_id.as_str() {
                                    // Build slurm job runner log path
                                    // We need node_id and task_pid from the scheduler data
                                    // The slurm job runner uses format: job_runner_slurm_{job_id}_{node_id}_{task_pid}.log
                                    // We can extract node_id and task_pid from environment during slurm execution
                                    // For now, we'll try to get it from the hostname or compute_node.pid

                                    // Use hostname as node_id and pid as task_pid for the log path
                                    let node_id = &compute_node.hostname;
                                    let task_pid = compute_node.pid as usize;

                                    let log_path = get_slurm_job_runner_log_file(
                                        output_dir.clone(),
                                        slurm_job_id_str,
                                        node_id,
                                        task_pid,
                                    );
                                    check_log_file_exists(&log_path, "slurm job runner", job_id);
                                    record["job_runner_log"] = serde_json::json!(log_path);

                                    // Add slurm stdout/stderr paths
                                    let slurm_stdout =
                                        get_slurm_stdout_path(output_dir, slurm_job_id_str);
                                    let slurm_stderr =
                                        get_slurm_stderr_path(output_dir, slurm_job_id_str);
                                    check_log_file_exists(&slurm_stdout, "slurm stdout", job_id);
                                    check_log_file_exists(&slurm_stderr, "slurm stderr", job_id);
                                    record["slurm_stdout"] = serde_json::json!(slurm_stdout);
                                    record["slurm_stderr"] = serde_json::json!(slurm_stderr);
                                }
                            }
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
    match serde_json::to_string_pretty(&report) {
        Ok(json) => println!("{}", json),
        Err(e) => {
            eprintln!("Error serializing report to JSON: {}", e);
            std::process::exit(1);
        }
    }
}
