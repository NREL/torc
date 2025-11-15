//! Torc - Workflow Orchestration System
//!
//! This library provides shared functionality for the Torc workflow orchestration system.
//! It includes data models, server implementation, and client utilities.

// Shared modules (always available)
pub mod models;
pub mod time_utils;

// Server modules (behind feature flag)
#[cfg(feature = "server")]
pub mod server;

// Client modules (behind feature flag)
#[cfg(feature = "client")]
pub mod client;

// TUI module (behind feature flag)
#[cfg(feature = "tui")]
pub mod tui;

// Binary command modules (behind feature flags) - re-exported for standalone binaries
#[cfg(feature = "client")]
pub mod run_jobs_cmd;

#[cfg(feature = "tui")]
pub mod tui_runner;

#[cfg(feature = "plot_resources")]
pub mod plot_resources_cmd;

// Re-export commonly used types
pub use models::*;

// Re-export client types when client feature is enabled
#[cfg(feature = "client")]
pub use client::apis::configuration::Configuration;
