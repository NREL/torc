//! Watch module for AI-powered workflow monitoring and failure recovery.
//!
//! This module provides the `torc watch` command functionality, which monitors
//! a running workflow for failures and uses Claude to diagnose issues and
//! automatically apply recovery actions.

pub mod audit;
pub mod claude_client;
pub mod failure_cache;
pub mod recovery;
pub mod watcher;

pub use audit::AuditLogger;
pub use claude_client::ClaudeClient;
pub use failure_cache::FailureCache;
pub use recovery::RecoveryAction;
pub use watcher::{WatchConfig, Watcher};
