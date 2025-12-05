//! CLI types for the torc command-line interface.
//!
//! This module defines the command-line interface structure using clap.
//! It is separated from the main binary to allow documentation generation.

use clap::{Parser, Subcommand, builder::styling};
use std::path::PathBuf;

use crate::client::commands::compute_nodes::ComputeNodeCommands;
use crate::client::commands::events::EventCommands;
use crate::client::commands::files::FileCommands;
use crate::client::commands::job_dependencies::JobDependencyCommands;
use crate::client::commands::jobs::JobCommands;
use crate::client::commands::reports::ReportCommands;
use crate::client::commands::resource_requirements::ResourceRequirementsCommands;
use crate::client::commands::results::ResultCommands;
use crate::client::commands::slurm::SlurmCommands;
use crate::client::commands::user_data::UserDataCommands;
use crate::client::commands::workflows::WorkflowCommands;
use crate::plot_resources_cmd;
use crate::tui_runner;

const STYLES: styling::Styles = styling::Styles::styled()
    .header(styling::AnsiColor::Green.on_default().bold())
    .usage(styling::AnsiColor::Green.on_default().bold())
    .literal(styling::AnsiColor::Cyan.on_default().bold())
    .placeholder(styling::AnsiColor::Cyan.on_default());

/// Torc workflow orchestration system
#[derive(Parser)]
#[command(author, version, about = "Torc workflow orchestration system", long_about = None)]
#[command(styles = STYLES)]
pub struct Cli {
    /// Log level (error, warn, info, debug, trace)
    #[arg(long, env = "RUST_LOG")]
    pub log_level: Option<String>,
    /// Output format (table or json)
    #[arg(short, long, default_value = "table")]
    pub format: String,
    /// URL of torc server
    #[arg(long, env = "TORC_API_URL")]
    pub url: Option<String>,
    /// Username for basic authentication
    #[arg(long, env = "TORC_USERNAME")]
    pub username: Option<String>,
    /// Password for basic authentication (will prompt if username provided but password not)
    #[arg(long, env = "TORC_PASSWORD")]
    pub password: Option<String>,
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Run a workflow locally (create from spec file or run existing workflow by ID)
    Run {
        /// Path to workflow spec file (JSON/JSON5/YAML) or workflow ID
        #[arg()]
        workflow_spec_or_id: String,
        /// Maximum number of parallel jobs to run concurrently
        #[arg(long)]
        max_parallel_jobs: Option<i64>,
        /// Number of CPUs available
        #[arg(long)]
        num_cpus: Option<i64>,
        /// Memory in GB
        #[arg(long)]
        memory_gb: Option<f64>,
        /// Number of GPUs available
        #[arg(long)]
        num_gpus: Option<i64>,
        /// Job completion poll interval in seconds
        #[arg(short, long)]
        poll_interval: Option<f64>,
        /// Output directory for jobs
        #[arg(short, long)]
        output_dir: Option<PathBuf>,
    },
    /// Submit a workflow to scheduler (create from spec file or submit existing workflow by ID)
    ///
    /// Requires workflow to have an on_workflow_start action with schedule_nodes
    Submit {
        /// Path to workflow spec file (JSON/JSON5/YAML) or workflow ID
        #[arg()]
        workflow_spec_or_id: String,
        /// Ignore missing data (defaults to false)
        #[arg(short, long, default_value = "false")]
        ignore_missing_data: bool,
    },
    /// Workflow management commands
    Workflows {
        #[command(subcommand)]
        command: WorkflowCommands,
    },
    /// Compute node management commands
    ComputeNodes {
        #[command(subcommand)]
        command: ComputeNodeCommands,
    },
    /// File management commands
    Files {
        #[command(subcommand)]
        command: FileCommands,
    },
    /// Job management commands
    Jobs {
        #[command(subcommand)]
        command: JobCommands,
    },
    /// Job dependency and relationship queries
    JobDependencies {
        #[command(subcommand)]
        command: JobDependencyCommands,
    },
    /// Resource requirements management commands
    ResourceRequirements {
        #[command(subcommand)]
        command: ResourceRequirementsCommands,
    },
    /// Event management commands
    Events {
        #[command(subcommand)]
        command: EventCommands,
    },
    /// Result management commands
    Results {
        #[command(subcommand)]
        command: ResultCommands,
    },
    /// User data management commands
    UserData {
        #[command(subcommand)]
        command: UserDataCommands,
    },
    /// Slurm scheduler commands
    Slurm {
        #[command(subcommand)]
        command: SlurmCommands,
    },
    /// Generate reports and analytics
    Reports {
        #[command(subcommand)]
        command: ReportCommands,
    },
    /// Interactive terminal UI for managing workflows
    Tui(tui_runner::Args),
    /// Generate interactive HTML plots from resource monitoring data
    PlotResources(plot_resources_cmd::Args),
    /// Generate shell completions
    Completions {
        /// The shell to generate completions for
        #[arg(value_enum)]
        shell: clap_complete::Shell,
    },
}
