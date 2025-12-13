//! Common utilities for the Torc client
//!
//! This module contains utility functions that are used across multiple
//! client modules.
//!
//! # Example
//!
//! ```rust
//! use torc::client::{Configuration, utils::send_with_retries, default_api};
//!
//! # fn example(config: &Configuration) -> Result<(), Box<dyn std::error::Error>> {
//! // Retry API calls with automatic network error handling
//! let response = send_with_retries(
//!     config,
//!     || default_api::ping(config),
//!     5, // Wait up to 5 minutes for server recovery
//! )?;
//! # Ok(())
//! # }
//! ```

use log::{debug, error, info, warn};
use std::fs::File;
use std::io::Write;
use std::path::Path;
use std::process::Command;
use std::thread;
use std::time::{Duration, Instant};

use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;

const PING_INTERVAL_SECONDS: u64 = 30;

/// Execute an API call with automatic retries for network errors
///
/// This function will immediately return non-network errors, but will retry
/// network-related errors by periodically pinging the server until it comes
/// back online or the timeout is reached.
///
/// # Arguments
/// * `config` - The API configuration to use for server pings
/// * `api_call` - The API call function to execute and potentially retry
/// * `wait_for_healthy_database_minutes` - Maximum time to wait for the server to recover
///
/// # Returns
/// The result of the API call, or the original error if retries are exhausted
pub fn send_with_retries<T, E, F>(
    config: &Configuration,
    mut api_call: F,
    wait_for_healthy_database_minutes: u64,
) -> Result<T, E>
where
    F: FnMut() -> Result<T, E>,
    E: std::fmt::Display,
{
    match api_call() {
        Ok(result) => Ok(result),
        Err(e) => {
            // Check if this is a network-related error
            let error_str = e.to_string().to_lowercase();
            let is_network_error = error_str.contains("connection")
                || error_str.contains("timeout")
                || error_str.contains("network")
                || error_str.contains("dns")
                || error_str.contains("resolve")
                || error_str.contains("unreachable");

            if !is_network_error {
                // Not a network error, return immediately
                return Err(e);
            }

            warn!(
                "Network error detected: {}. Entering retry loop for up to {} minutes.",
                e, wait_for_healthy_database_minutes
            );

            let start_time = Instant::now();
            let timeout_duration = Duration::from_secs(wait_for_healthy_database_minutes * 60);

            loop {
                if start_time.elapsed() >= timeout_duration {
                    error!(
                        "Retry timeout exceeded ({} minutes). Giving up.",
                        wait_for_healthy_database_minutes
                    );
                    return Err(e);
                }

                thread::sleep(Duration::from_secs(PING_INTERVAL_SECONDS));

                // Try to ping the server
                match default_api::ping(config) {
                    Ok(_) => {
                        info!("Server is back online. Retrying original API call.");
                        // Server is back, retry the original call
                        return api_call();
                    }
                    Err(ping_error) => {
                        debug!(
                            "Server still unreachable: {}. Continuing to wait...",
                            ping_error
                        );
                        continue;
                    }
                }
            }
        }
    }
}

/// Atomically claim a workflow action for execution
///
/// This function attempts to claim an action so that only one compute node
/// executes it. Uses automatic retries for network errors.
///
/// # Arguments
/// * `config` - The API configuration
/// * `workflow_id` - The workflow ID
/// * `action_id` - The action ID to claim
/// * `compute_node_id` - The compute node ID claiming the action
/// * `wait_for_healthy_database_minutes` - Maximum time to wait for server recovery
///
/// # Returns
/// * `Ok(true)` - Successfully claimed the action
/// * `Ok(false)` - Action was already claimed by another compute node
/// * `Err(_)` - An error occurred during the claim attempt
pub fn claim_action(
    config: &Configuration,
    workflow_id: i64,
    action_id: i64,
    compute_node_id: Option<i64>,
    wait_for_healthy_database_minutes: u64,
) -> Result<bool, Box<dyn std::error::Error>> {
    let claimed = send_with_retries(
        config,
        || -> Result<bool, Box<dyn std::error::Error>> {
            let body = match compute_node_id {
                Some(id) => serde_json::json!({ "compute_node_id": id }),
                None => serde_json::json!({}),
            };

            match default_api::claim_action(config, workflow_id, action_id, body) {
                Ok(result) => {
                    let claimed = result
                        .get("claimed")
                        .and_then(|v| v.as_bool())
                        .unwrap_or(false);
                    Ok(claimed)
                }
                Err(err) => {
                    // Check if it's a Conflict (already claimed by another compute node)
                    if let crate::client::apis::Error::ResponseError(ref response_content) = err {
                        if response_content.status == reqwest::StatusCode::CONFLICT {
                            return Ok(false);
                        }
                    }
                    Err(Box::new(err))
                }
            }
        },
        wait_for_healthy_database_minutes,
    )?;

    Ok(claimed)
}

/// Detect the number of NVIDIA GPUs available on the system.
///
/// Uses NVML (NVIDIA Management Library) to query the number of GPU devices.
/// Returns 0 if NVML fails to initialize (e.g., no NVIDIA drivers installed,
/// no NVIDIA GPUs present, or NVML library not available).
///
/// # Returns
/// The number of NVIDIA GPUs detected, or 0 if detection fails.
///
/// # Example
/// ```ignore
/// let num_gpus = detect_nvidia_gpus();
/// println!("Detected {} NVIDIA GPU(s)", num_gpus);
/// ```
pub fn detect_nvidia_gpus() -> i64 {
    match nvml_wrapper::Nvml::init() {
        Ok(nvml) => match nvml.device_count() {
            Ok(count) => {
                info!("Detected {} NVIDIA GPU(s)", count);
                count as i64
            }
            Err(e) => {
                debug!("Failed to get NVIDIA GPU count: {}", e);
                0
            }
        },
        Err(e) => {
            debug!(
                "NVML initialization failed (no NVIDIA GPUs or drivers): {}",
                e
            );
            0
        }
    }
}

/// Capture environment variables containing a substring and save them to a file.
///
/// This is useful for debugging job runner environment, especially for capturing
/// all SLURM-related environment variables.
///
/// # Arguments
/// * `file_path` - Path where the environment variables will be written
/// * `substring` - Only environment variables whose names contain this substring will be captured
///
/// # Note
/// Errors are logged but do not cause the function to fail, since environment capture
/// is informational and should not block process exit.
pub fn capture_env_vars(file_path: &Path, substring: &str) {
    info!(
        "Capturing environment variables containing '{}' to: {}",
        substring,
        file_path.display()
    );

    let mut env_vars: Vec<(String, String)> = std::env::vars()
        .filter(|(key, _)| key.contains(substring))
        .collect();

    // Sort for consistent output
    env_vars.sort_by(|a, b| a.0.cmp(&b.0));

    match File::create(file_path) {
        Ok(mut file) => {
            for (key, value) in &env_vars {
                if let Err(e) = writeln!(file, "{}={}", key, value) {
                    error!("Error writing environment variable to file: {}", e);
                    return;
                }
            }
            info!(
                "Successfully captured {} environment variables",
                env_vars.len()
            );
        }
        Err(e) => {
            error!(
                "Error creating environment variables file {}: {}",
                file_path.display(),
                e
            );
        }
    }
}

/// Capture dmesg output and save it to a file.
///
/// This may contain useful debug information if any job failed (e.g., OOM killer,
/// hardware errors, kernel panics).
///
/// # Arguments
/// * `file_path` - Path where the dmesg output will be written
///
/// # Note
/// Errors are logged but do not cause the function to fail, since dmesg capture
/// is informational and should not block process exit.
pub fn capture_dmesg(file_path: &Path) {
    info!("Capturing dmesg output to: {}", file_path.display());

    match Command::new("dmesg").arg("--ctime").output() {
        Ok(output) => match File::create(file_path) {
            Ok(mut file) => {
                if let Err(e) = file.write_all(&output.stdout) {
                    error!("Error writing dmesg stdout to file: {}", e);
                }
                if !output.stderr.is_empty() {
                    if let Err(e) = file.write_all(b"\n--- stderr ---\n") {
                        error!("Error writing dmesg separator: {}", e);
                    }
                    if let Err(e) = file.write_all(&output.stderr) {
                        error!("Error writing dmesg stderr to file: {}", e);
                    }
                }
                info!("Successfully captured dmesg output");
            }
            Err(e) => {
                error!("Error creating dmesg file {}: {}", file_path.display(), e);
            }
        },
        Err(e) => {
            error!("Error running dmesg command: {}", e);
        }
    }
}
