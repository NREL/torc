//! Client implementation for the Torc workflow orchestration system
//!
//! This module contains all client-side functionality including API wrappers,
//! CLI command handlers, workflow management, and job execution.

pub mod apis;
pub mod async_cli_command;
pub mod commands;
pub mod errors;
pub mod execution_plan;
pub mod hpc;
pub mod job_runner;
pub mod log_paths;
pub mod parameter_expansion;
pub mod resource_monitor;
pub mod utils;
pub mod workflow_manager;
pub mod workflow_spec;

// Re-exports for convenience
pub use apis::configuration::Configuration;
pub use apis::default_api;
pub use hpc::{
    HpcInterface, HpcJobInfo, HpcJobStats, HpcJobStatus, HpcManager, HpcType, SlurmInterface,
    create_hpc_interface,
};
pub use job_runner::JobRunner;
// JobModel is re-exported from models (which re-exports from crate::models)
pub use utils::send_with_retries;
pub use workflow_manager::WorkflowManager;
pub use workflow_spec::{
    FileSpec, JobSpec, ResourceRequirementsSpec, SlurmSchedulerSpec, UserDataSpec, WorkflowSpec,
};
