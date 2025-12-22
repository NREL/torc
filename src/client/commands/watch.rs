//! Watch command for monitoring workflows with automatic failure recovery

use std::collections::HashMap;
use std::path::PathBuf;
use std::process::Command;
use std::time::Duration;

use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::time_utils::duration_string_to_seconds;

/// Arguments for the watch command
pub struct WatchArgs {
    pub workflow_id: i64,
    pub poll_interval: u64,
    pub auto_recover: bool,
    pub max_retries: u32,
    pub memory_multiplier: f64,
    pub runtime_multiplier: f64,
    pub output_dir: PathBuf,
    pub show_job_counts: bool,
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
        None,         // status filter
        None,         // needs_file_id
        None,         // upstream_job_id
        None,         // offset
        Some(100000), // limit
        None,         // sort_by
        None,         // reverse_sort
        None,         // include_relationships
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
                    eprintln!("Workflow {} is complete", workflow_id);
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
                    eprintln!(
                        "  completed={}, running={}, pending={}, failed={}, blocked={}",
                        completed, running, pending, failed, blocked
                    );
                }
                Err(e) => {
                    eprintln!("Error getting job counts: {}", e);
                }
            }
        }

        std::thread::sleep(Duration::from_secs(poll_interval));
    }

    get_job_counts(config, workflow_id)
}

/// Diagnose failures and return job IDs that need resource adjustments
fn diagnose_failures(workflow_id: i64, output_dir: &PathBuf) -> Result<serde_json::Value, String> {
    // Run check-resource-utilization command
    let output = Command::new("torc")
        .args([
            "-f",
            "json",
            "reports",
            "check-resource-utilization",
            &workflow_id.to_string(),
            "--include-failed",
            "-o",
            output_dir.to_str().unwrap_or("output"),
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

/// Apply recovery heuristics and update job resources
fn apply_recovery_heuristics(
    config: &Configuration,
    workflow_id: i64,
    diagnosis: &serde_json::Value,
    memory_multiplier: f64,
    runtime_multiplier: f64,
    output_dir: &PathBuf,
) -> Result<(usize, usize, usize), String> {
    let mut oom_fixed = 0;
    let mut timeout_fixed = 0;
    let mut other_failures = 0;

    // Try to get Slurm log info for correlation
    let slurm_log_map = match get_slurm_log_info(workflow_id, output_dir) {
        Ok(slurm_info) => {
            let log_map = correlate_slurm_logs(diagnosis, &slurm_info);
            if !log_map.is_empty() {
                eprintln!("  Found Slurm logs for {} failed job(s)", log_map.len());
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
                eprintln!("  Warning: couldn't get job {}: {}", job_id, e);
                continue;
            }
        };

        let rr_id = match job.resource_requirements_id {
            Some(id) => id,
            None => {
                eprintln!("  Warning: job {} has no resource requirements", job_id);
                other_failures += 1;
                continue;
            }
        };

        // Get current resource requirements
        let rr = match default_api::get_resource_requirements(config, rr_id) {
            Ok(r) => r,
            Err(e) => {
                eprintln!(
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
                eprintln!(
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
                eprintln!(
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
                eprintln!(
                    "  Warning: failed to update resource requirements for job {}: {}",
                    job_id, e
                );
            }
        } else if !likely_oom && !likely_timeout {
            // Unknown failure - will retry without changes
            other_failures += 1;
        }
    }

    Ok((oom_fixed, timeout_fixed, other_failures))
}

/// Reset failed jobs and restart workflow
fn reset_failed_jobs(workflow_id: i64) -> Result<(), String> {
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
        .map_err(|e| format!("Failed to run reset-status: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("reset-status failed: {}", stderr));
    }

    Ok(())
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
    let mut retry_count = 0u32;

    eprintln!(
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
        eprintln!("  (use --show-job-counts to display per-status counts during polling)");
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
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
        };

        let completed = *counts.get("Completed").unwrap_or(&0);
        let failed = *counts.get("Failed").unwrap_or(&0);
        let canceled = *counts.get("Canceled").unwrap_or(&0);
        let terminated = *counts.get("Terminated").unwrap_or(&0);

        let needs_recovery = failed > 0 || canceled > 0 || terminated > 0;

        if !needs_recovery {
            eprintln!("\n✓ Workflow completed successfully ({} jobs)", completed);
            break;
        }

        eprintln!("\nWorkflow completed with failures:");
        eprintln!("  - Failed: {}", failed);
        eprintln!("  - Canceled: {}", canceled);
        eprintln!("  - Terminated: {}", terminated);
        eprintln!("  - Completed: {}", completed);

        // Check if we should attempt recovery
        if !args.auto_recover {
            eprintln!("\nAuto-recovery disabled. To enable, use --auto-recover flag.");
            eprintln!("Or use the Torc MCP server with your AI assistant for manual recovery.");
            std::process::exit(1);
        }

        if retry_count >= args.max_retries {
            eprintln!(
                "\nMax retries ({}) exceeded. Manual intervention required.",
                args.max_retries
            );
            eprintln!("Use the Torc MCP server with your AI assistant to investigate.");
            std::process::exit(1);
        }

        retry_count += 1;
        eprintln!(
            "\nAttempting automatic recovery (attempt {}/{})",
            retry_count, args.max_retries
        );

        // Step 1: Diagnose failures
        eprintln!("\nDiagnosing failures...");
        let diagnosis = match diagnose_failures(args.workflow_id, &args.output_dir) {
            Ok(d) => d,
            Err(e) => {
                eprintln!("Warning: Could not diagnose failures: {}", e);
                eprintln!("Attempting retry without resource adjustments...");
                serde_json::json!({"failed_jobs": []})
            }
        };

        // Step 2: Apply heuristics to adjust resources
        eprintln!("\nApplying recovery heuristics...");
        match apply_recovery_heuristics(
            config,
            args.workflow_id,
            &diagnosis,
            args.memory_multiplier,
            args.runtime_multiplier,
            &args.output_dir,
        ) {
            Ok((oom, timeout, other)) => {
                if oom > 0 || timeout > 0 {
                    eprintln!("  Applied fixes: {} OOM, {} timeout", oom, timeout);
                }
                if other > 0 {
                    eprintln!("  {} job(s) with unknown failure cause (will retry)", other);
                }
            }
            Err(e) => {
                eprintln!("Warning: Error applying heuristics: {}", e);
            }
        }

        // Step 3: Reset failed jobs
        eprintln!("\nResetting failed jobs...");
        if let Err(e) = reset_failed_jobs(args.workflow_id) {
            eprintln!("Error resetting jobs: {}", e);
            std::process::exit(1);
        }

        // Step 4: Regenerate Slurm schedulers and submit
        eprintln!("Regenerating Slurm schedulers and submitting...");
        if let Err(e) = regenerate_and_submit(args.workflow_id, &args.output_dir) {
            eprintln!("Error regenerating schedulers: {}", e);
            std::process::exit(1);
        }

        eprintln!("\nRecovery initiated. Resuming monitoring...\n");
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
