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
