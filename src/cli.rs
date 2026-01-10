//! CLI types for the torc command-line interface.
//!
//! This module defines the command-line interface structure using clap.
//! It is separated from the main binary to allow documentation generation.

use clap::{Parser, Subcommand, builder::styling};
use std::path::PathBuf;

use crate::client::commands::access_groups::AccessGroupCommands;
use crate::client::commands::compute_nodes::ComputeNodeCommands;
use crate::client::commands::config::ConfigCommands;
use crate::client::commands::events::EventCommands;
use crate::client::commands::files::FileCommands;
use crate::client::commands::hpc::HpcCommands;
use crate::client::commands::job_dependencies::JobDependencyCommands;
use crate::client::commands::jobs::JobCommands;
use crate::client::commands::logs::LogCommands;
use crate::client::commands::remote::RemoteCommands;
use crate::client::commands::reports::ReportCommands;
use crate::client::commands::resource_requirements::ResourceRequirementsCommands;
use crate::client::commands::results::ResultCommands;
use crate::client::commands::scheduled_compute_nodes::ScheduledComputeNodeCommands;
use crate::client::commands::slurm::{GroupByStrategy, SlurmCommands};
use crate::client::commands::user_data::UserDataCommands;
use crate::client::commands::workflows::WorkflowCommands;
use crate::plot_resources_cmd;
use crate::tui_runner;

const STYLES: styling::Styles = styling::Styles::styled()
    .header(styling::AnsiColor::Green.on_default().bold())
    .usage(styling::AnsiColor::Green.on_default().bold())
    .literal(styling::AnsiColor::Cyan.on_default().bold())
    .placeholder(styling::AnsiColor::Cyan.on_default());

const HELP_TEMPLATE: &str = "\
{before-help}{name} {version}
{about-with-newline}
{usage-heading} {usage}

{all-args}

\x1b[1;32mWorkflow Execution:\x1b[0m
  \x1b[1;36mrun\x1b[0m                      Run a workflow locally
  \x1b[1;36msubmit\x1b[0m                   Submit a workflow to scheduler
  \x1b[1;36msubmit-slurm\x1b[0m             Submit to Slurm with auto-generated schedulers
  \x1b[1;36mwatch\x1b[0m                    Watch workflow and recover from failures
  \x1b[1;36mrecover\x1b[0m                  Recover a Slurm workflow from failures

\x1b[1;32mWorkflow Management:\x1b[0m
  \x1b[1;36mworkflows\x1b[0m                Workflow management commands
  \x1b[1;36mjobs\x1b[0m                     Job management commands
  \x1b[1;36mfiles\x1b[0m                    File management commands
  \x1b[1;36muser-data\x1b[0m                User data management commands
  \x1b[1;36mevents\x1b[0m                   Event management commands
  \x1b[1;36mresource-requirements\x1b[0m    Resource requirements management
  \x1b[1;36mresults\x1b[0m                  Result management commands
  \x1b[1;36mcompute-nodes\x1b[0m            Compute node management
  \x1b[1;36mscheduled-compute-nodes\x1b[0m  Scheduled compute node management
  \x1b[1;36mtui\x1b[0m                      Interactive terminal UI

\x1b[1;32mScheduler & Compute:\x1b[0m
  \x1b[1;36mslurm\x1b[0m                    Slurm scheduler commands
  \x1b[1;36mhpc\x1b[0m                      HPC system profiles and partitions
  \x1b[1;36mremote\x1b[0m                   Remote worker execution (SSH)

\x1b[1;32mAnalysis & Debugging:\x1b[0m
  \x1b[1;36mreports\x1b[0m                  Generate reports and analytics
  \x1b[1;36mlogs\x1b[0m                     Bundle and analyze workflow logs
  \x1b[1;36mjob-dependencies\x1b[0m         Job dependency queries

\x1b[1;32mConfiguration & Utilities:\x1b[0m
  \x1b[1;36mconfig\x1b[0m                   Manage configuration settings
  \x1b[1;36mplot-resources\x1b[0m           Generate HTML resource plots
  \x1b[1;36mcompletions\x1b[0m              Generate shell completions
  \x1b[1;36mhelp\x1b[0m                     Print help for a subcommand
{after-help}";

/// Torc workflow orchestration system
#[derive(Parser)]
#[command(author, version, about = "Torc workflow orchestration system", long_about = None)]
#[command(styles = STYLES, help_template = HELP_TEMPLATE, disable_help_subcommand = true, subcommand_help_heading = None)]
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
    /// Password for basic authentication (uses USER env var as username)
    #[arg(long, env = "TORC_PASSWORD")]
    pub password: Option<String>,
    /// Prompt for password securely (alternative to --password or TORC_PASSWORD)
    #[arg(long)]
    pub prompt_password: bool,
    /// Skip checking server version compatibility
    #[arg(long)]
    pub skip_version_check: bool,
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    // =========================================================================
    // Workflow Execution - Primary commands for running workflows
    // =========================================================================
    /// Run a workflow locally (create from spec file or run existing workflow by ID)
    #[command(
        hide = true,
        after_long_help = "\
EXAMPLES:
    # Run from spec file
    torc run workflow.yaml

    # Run existing workflow
    torc run 123

    # With resource limits
    torc run --num-cpus 8 --memory-gb 32 --num-gpus 2 workflow.yaml

    # Limit parallel jobs
    torc run --max-parallel-jobs 4 workflow.yaml

    # Custom output directory
    torc run -o /path/to/output workflow.yaml
"
    )]
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
        /// Skip validation checks (e.g., scheduler node requirements). Use with caution.
        #[arg(long, default_value = "false")]
        skip_checks: bool,
    },
    /// Submit a workflow to scheduler (create from spec file or submit existing workflow by ID)
    ///
    /// Requires workflow to have an on_workflow_start action with schedule_nodes.
    /// For Slurm workflows without pre-configured schedulers, use `submit-slurm` instead.
    #[command(
        hide = true,
        after_long_help = "\
EXAMPLES:
    # Submit from spec file (must have on_workflow_start action)
    torc submit workflow_with_actions.yaml

    # Submit existing workflow
    torc submit 123

    # Ignore missing input data
    torc submit -i workflow.yaml
"
    )]
    Submit {
        /// Path to workflow spec file (JSON/JSON5/YAML) or workflow ID
        #[arg()]
        workflow_spec_or_id: String,
        /// Ignore missing data (defaults to false)
        #[arg(short, long, default_value = "false")]
        ignore_missing_data: bool,
        /// Skip validation checks (e.g., scheduler node requirements). Use with caution.
        #[arg(long, default_value = "false")]
        skip_checks: bool,
    },
    /// Submit a workflow to Slurm with auto-generated schedulers
    ///
    /// Automatically generates Slurm schedulers based on job resource requirements
    /// and HPC profile.
    ///
    /// WARNING: This command uses heuristics to generate schedulers and workflow
    /// actions. For complex workflows with unusual dependency patterns, the
    /// generated configuration may not be optimal and could waste allocation time.
    ///
    /// RECOMMENDED: Preview the generated configuration first with:
    ///
    ///   torc slurm generate --account <account> workflow.yaml
    ///
    /// Review the schedulers and actions to ensure they are appropriate for your
    /// workflow before submitting. You can save the output and submit manually:
    ///
    ///   torc slurm generate --account <account> -o workflow_with_schedulers.yaml workflow.yaml
    ///   torc submit workflow_with_schedulers.yaml
    #[command(
        name = "submit-slurm",
        hide = true,
        after_long_help = "\
EXAMPLES:
    # Submit with auto-generated Slurm schedulers
    torc submit-slurm --account myproject workflow.yaml

    # Specify HPC profile
    torc submit-slurm --account myproject --hpc-profile kestrel workflow.yaml

    # Single allocation mode
    torc submit-slurm --account myproject --single-allocation workflow.yaml

    # Group by partition
    torc submit-slurm --account myproject --group-by partition workflow.yaml
"
    )]
    SubmitSlurm {
        /// Path to workflow spec file (JSON/JSON5/YAML/KDL)
        #[arg()]
        workflow_spec: String,
        /// Slurm account to use for allocations (can also be specified in workflow's slurm_defaults)
        #[arg(short, long)]
        account: Option<String>,
        /// HPC profile to use (auto-detected if not specified)
        #[arg(long)]
        hpc_profile: Option<String>,
        /// Bundle all nodes into a single Slurm allocation per scheduler
        ///
        /// By default, creates one Slurm allocation per node (N×1 mode), which allows
        /// jobs to start as nodes become available and provides better fault tolerance.
        ///
        /// With this flag, creates one large allocation with all nodes (1×N mode),
        /// which requires all nodes to be available simultaneously but uses a single sbatch.
        #[arg(long)]
        single_allocation: bool,
        /// Strategy for grouping jobs into schedulers
        ///
        /// - resource-requirements: Each unique resource_requirements creates a separate
        ///   scheduler. This preserves user intent and provides fine-grained control.
        /// - partition: Jobs whose resource requirements map to the same partition are
        ///   grouped together, reducing the number of schedulers.
        #[arg(long, value_enum, default_value_t = GroupByStrategy::ResourceRequirements)]
        group_by: GroupByStrategy,
        /// Ignore missing data (defaults to false)
        #[arg(short, long, default_value = "false")]
        ignore_missing_data: bool,
        /// Skip validation checks (e.g., scheduler node requirements). Use with caution.
        #[arg(long, default_value = "false")]
        skip_checks: bool,
        /// Overwrite existing slurm_schedulers and actions in the spec file.
        /// Without this flag, an error is returned if the spec already has schedulers.
        #[arg(long, default_value = "false")]
        overwrite: bool,
    },
    /// Watch a workflow and automatically recover from failures
    ///
    /// Monitors a workflow until completion. With --recover, automatically
    /// diagnoses failures, adjusts resource requirements, and resubmits jobs.
    ///
    /// Recovery heuristics:
    /// - OOM (out of memory): Increase memory by --memory-multiplier (default 1.5x)
    /// - Timeout: Increase runtime by --runtime-multiplier (default 1.5x)
    /// - Other failures: Retry without changes (transient errors)
    ///
    /// Without --recover, reports failures and exits for manual intervention
    /// or AI-assisted recovery via the MCP server.
    #[command(
        hide = true,
        after_long_help = "\
EXAMPLES:
    # Watch until completion
    torc watch 123

    # Watch with automatic recovery
    torc watch 123 --recover

    # Custom poll interval and resource multipliers
    torc watch 123 --recover -p 30 --memory-multiplier 2.0 --runtime-multiplier 1.5

    # With custom recovery hook
    torc watch 123 --recover --recovery-hook 'bash fix-cluster.sh'
"
    )]
    Watch {
        /// Workflow ID to watch
        #[arg()]
        workflow_id: i64,

        /// Poll interval in seconds
        #[arg(short, long, default_value = "60")]
        poll_interval: u64,

        /// Enable automatic failure recovery
        #[arg(short, long)]
        recover: bool,

        /// Maximum number of recovery attempts
        #[arg(short, long, default_value = "3")]
        max_retries: u32,

        /// Memory multiplier for OOM failures (default: 1.5 = 50% increase)
        #[arg(long, default_value = "1.5")]
        memory_multiplier: f64,

        /// Runtime multiplier for timeout failures (default: 1.5 = 50% increase)
        #[arg(long, default_value = "1.5")]
        runtime_multiplier: f64,

        /// Retry jobs with unknown failure causes (not OOM or timeout)
        ///
        /// By default, only jobs that failed due to OOM or timeout are retried
        /// (with increased resources). Jobs with unknown failure causes are skipped
        /// since they likely have script or data bugs that won't be fixed by retrying.
        ///
        /// Enable this flag to also retry jobs with unknown failures (e.g., to handle
        /// transient errors like network issues or filesystem glitches).
        #[arg(long)]
        retry_unknown: bool,

        /// Custom recovery hook command for unknown failures
        ///
        /// When jobs fail with unknown causes (not OOM or timeout), this command
        /// is executed before resetting jobs for retry. Use this to run custom
        /// recovery logic, such as adjusting Spark cluster sizes or fixing
        /// configuration issues.
        ///
        /// The workflow ID is passed as both an argument and environment variable:
        /// - Argument: `<command> <workflow_id>`
        /// - Environment: `TORC_WORKFLOW_ID=<workflow_id>`
        ///
        /// Example: --recovery-hook "bash fix-spark-cluster.sh"
        #[arg(long)]
        recovery_hook: Option<String>,

        /// Output directory for job files
        #[arg(short, long, default_value = "output")]
        output_dir: PathBuf,

        /// Show job counts by status during polling
        ///
        /// WARNING: This option queries all jobs on each poll, which can cause high
        /// server load for large workflows. Only use for debugging or small workflows.
        #[arg(short, long)]
        show_job_counts: bool,
    },
    /// Recover a Slurm workflow from failures
    ///
    /// Diagnoses job failures (OOM, timeout), adjusts resource requirements,
    /// and resubmits jobs. Use after a workflow has completed with failures.
    ///
    /// This command:
    /// 1. Checks preconditions (workflow complete, no active workers)
    /// 2. Diagnoses failures using resource utilization data
    /// 3. Applies recovery heuristics (increase memory/runtime)
    /// 4. Runs optional recovery hook for custom logic
    /// 5. Resets failed jobs and regenerates Slurm schedulers
    /// 6. Submits new allocations
    ///
    /// For continuous monitoring with automatic recovery, use `torc watch --recover`.
    #[command(
        hide = true,
        after_long_help = "\
EXAMPLES:
    # Basic recovery
    torc recover 123

    # Dry run to preview changes
    torc recover 123 --dry-run

    # Custom resource multipliers
    torc recover 123 --memory-multiplier 2.0 --runtime-multiplier 1.5

    # Also retry unknown failures
    torc recover 123 --retry-unknown
"
    )]
    Recover {
        /// Workflow ID to recover
        #[arg()]
        workflow_id: i64,

        /// Output directory for job files
        #[arg(short, long, default_value = "output")]
        output_dir: PathBuf,

        /// Memory multiplier for OOM failures (default: 1.5 = 50% increase)
        #[arg(long, default_value = "1.5")]
        memory_multiplier: f64,

        /// Runtime multiplier for timeout failures (default: 1.4 = 40% increase)
        #[arg(long, default_value = "1.4")]
        runtime_multiplier: f64,

        /// Retry jobs with unknown failure causes (not OOM or timeout)
        ///
        /// By default, only jobs that failed due to OOM or timeout are retried.
        /// Enable this to also retry jobs with unknown failures.
        #[arg(long)]
        retry_unknown: bool,

        /// Custom recovery hook command for unknown failures
        ///
        /// When jobs fail with unknown causes, this command is executed before
        /// resetting jobs. The workflow ID is passed as both an argument and
        /// the TORC_WORKFLOW_ID environment variable.
        ///
        /// Example: --recovery-hook "bash fix-cluster.sh"
        #[arg(long)]
        recovery_hook: Option<String>,

        /// Show what would be done without making any changes
        ///
        /// Diagnoses failures and shows proposed resource adjustments, but does
        /// not actually update resources, reset jobs, or submit allocations.
        #[arg(long)]
        dry_run: bool,
    },
    /// Interactive terminal UI for managing workflows
    #[command(
        hide = true,
        after_long_help = "\
EXAMPLES:
    # Connect to running server
    torc tui

    # Standalone mode (starts embedded server)
    torc tui --standalone

    # Standalone with custom settings
    torc tui --standalone --port 9090 --database /path/to/db.sqlite
"
    )]
    Tui(tui_runner::Args),
    // =========================================================================
    // Workflow Management - CRUD operations on workflow resources
    // =========================================================================
    /// Workflow management commands
    #[command(hide = true)]
    Workflows {
        #[command(subcommand)]
        command: WorkflowCommands,
    },
    /// Job management commands
    #[command(hide = true)]
    Jobs {
        #[command(subcommand)]
        command: JobCommands,
    },
    /// File management commands
    #[command(hide = true)]
    Files {
        #[command(subcommand)]
        command: FileCommands,
    },
    /// User data management commands
    #[command(hide = true)]
    UserData {
        #[command(subcommand)]
        command: UserDataCommands,
    },
    /// Event management commands
    #[command(hide = true)]
    Events {
        #[command(subcommand)]
        command: EventCommands,
    },
    /// Result management commands
    #[command(hide = true)]
    Results {
        #[command(subcommand)]
        command: ResultCommands,
    },

    // =========================================================================
    // Scheduler & Compute - HPC, Slurm, and distributed execution
    // =========================================================================
    /// Slurm scheduler commands
    #[command(hide = true)]
    Slurm {
        #[command(subcommand)]
        command: SlurmCommands,
    },
    /// HPC system profiles and partition information
    #[command(hide = true)]
    Hpc {
        #[command(subcommand)]
        command: HpcCommands,
    },
    /// Compute node management commands
    #[command(hide = true)]
    ComputeNodes {
        #[command(subcommand)]
        command: ComputeNodeCommands,
    },
    /// Scheduled compute node management commands
    #[command(hide = true)]
    ScheduledComputeNodes {
        #[command(subcommand)]
        command: ScheduledComputeNodeCommands,
    },
    /// Remote worker execution commands (SSH-based distributed execution)
    #[command(hide = true)]
    Remote {
        #[command(subcommand)]
        command: RemoteCommands,
    },

    // =========================================================================
    // Analysis & Debugging - Troubleshooting and insights
    // =========================================================================
    /// Generate reports and analytics
    #[command(hide = true)]
    Reports {
        #[command(subcommand)]
        command: ReportCommands,
    },
    /// Bundle and analyze workflow logs
    #[command(hide = true)]
    Logs {
        #[command(subcommand)]
        command: LogCommands,
    },
    /// Job dependency and relationship queries
    #[command(hide = true)]
    JobDependencies {
        #[command(subcommand)]
        command: JobDependencyCommands,
    },
    /// Resource requirements management commands
    #[command(hide = true)]
    ResourceRequirements {
        #[command(subcommand)]
        command: ResourceRequirementsCommands,
    },

    // =========================================================================
    // Configuration & Utilities - Setup and miscellaneous
    // =========================================================================
    /// Manage access groups for team-based access control
    #[command(hide = true)]
    AccessGroups {
        #[command(subcommand)]
        command: AccessGroupCommands,
    },
    /// Manage configuration files and settings
    #[command(hide = true)]
    Config {
        #[command(subcommand)]
        command: ConfigCommands,
    },
    /// Generate interactive HTML plots from resource monitoring data
    #[command(
        hide = true,
        after_long_help = "\
EXAMPLES:
    torc plot-resources output/resource_metrics.db
    torc plot-resources -o /reports/ resource_metrics.db
    torc plot-resources -j job1,job2,job3 resource_metrics.db
"
    )]
    PlotResources(plot_resources_cmd::Args),
    /// Check if the server is running and accessible
    Ping,
    /// Generate shell completions
    #[command(
        hide = true,
        after_long_help = "\
EXAMPLES:
    # Bash (add to ~/.bashrc)
    torc completions bash > ~/.local/share/bash-completion/completions/torc

    # Zsh (add to ~/.zshrc: fpath=(~/.zfunc $fpath))
    torc completions zsh > ~/.zfunc/_torc

    # Fish
    torc completions fish > ~/.config/fish/completions/torc.fish
"
    )]
    Completions {
        /// The shell to generate completions for
        #[arg(value_enum)]
        shell: clap_complete::Shell,
    },
}
