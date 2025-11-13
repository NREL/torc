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

// Re-export commonly used types
pub use models::*;

// Re-export client types when client feature is enabled
#[cfg(feature = "client")]
pub use client::apis::configuration::Configuration;
