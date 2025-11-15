use clap::{Parser, Subcommand};
use rpassword;

use torc::client::apis::configuration::Configuration;
use torc::client::commands::compute_nodes::{ComputeNodeCommands, handle_compute_node_commands};
use torc::client::commands::events::{EventCommands, handle_event_commands};
use torc::client::commands::files::{FileCommands, handle_file_commands};
use torc::client::commands::jobs::{JobCommands, handle_job_commands};
use torc::client::commands::reports::{ReportCommands, handle_report_commands};
use torc::client::commands::resource_requirements::{
    ResourceRequirementsCommands, handle_resource_requirements_commands,
};
use torc::client::commands::results::{ResultCommands, handle_result_commands};
use torc::client::commands::slurm::{SlurmCommands, handle_slurm_commands};
use torc::client::commands::user_data::{UserDataCommands, handle_user_data_commands};
use torc::client::commands::workflows::{WorkflowCommands, handle_workflow_commands};

// Import the binary command modules from the library
use torc::plot_resources_cmd;
use torc::run_jobs_cmd;
use torc::tui_runner;

#[derive(Parser)]
#[command(author, version, about = "Torc workflow orchestration system", long_about = None)]
struct Cli {
    /// Log level (error, warn, info, debug, trace)
    #[arg(long, default_value = "info", global = true, env = "RUST_LOG")]
    log_level: String,
    /// Output format (table or json)
    #[arg(short, long, default_value = "table", global = true)]
    format: String,
    /// URL of torc server
    #[arg(
        long,
        default_value = "http://localhost:8080/torc-service/v1",
        global = true
    )]
    url: String,
    /// Username for basic authentication
    #[arg(long, global = true, env = "TORC_USERNAME")]
    username: Option<String>,
    /// Password for basic authentication (will prompt if username provided but password not)
    #[arg(long, global = true, env = "TORC_PASSWORD")]
    password: Option<String>,
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
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
    /// Run jobs locally on the current node
    RunJobs(run_jobs_cmd::Args),
    /// Interactive terminal UI for managing workflows
    Tui(tui_runner::Args),
    /// Generate interactive HTML plots from resource monitoring data
    PlotResources(plot_resources_cmd::Args),
}

fn main() {
    let cli = Cli::parse();

    // Initialize logger with CLI argument or RUST_LOG env var
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or(&cli.log_level))
        .init();

    // Validate format option for API commands
    if !matches!(cli.format.as_str(), "table" | "json") {
        eprintln!("Error: format must be either 'table' or 'json'");
        std::process::exit(1);
    }

    // Create configuration for API commands
    let mut config = Configuration::new();
    config.base_path = cli.url;

    // Handle authentication
    if let Some(username) = cli.username {
        let password = match cli.password {
            Some(pwd) => Some(pwd),
            None => {
                // Prompt for password if username provided but password not
                match rpassword::prompt_password("Password: ") {
                    Ok(pwd) => Some(pwd),
                    Err(e) => {
                        eprintln!("Error reading password: {}", e);
                        std::process::exit(1);
                    }
                }
            }
        };
        config.basic_auth = Some((username, password));
    }

    match &cli.command {
        Commands::Workflows { command } => {
            handle_workflow_commands(&config, command, &cli.format);
        }
        Commands::ComputeNodes { command } => {
            handle_compute_node_commands(&config, command, &cli.format);
        }
        Commands::Files { command } => {
            handle_file_commands(&config, command, &cli.format);
        }
        Commands::Jobs { command } => {
            handle_job_commands(&config, command, &cli.format);
        }
        Commands::ResourceRequirements { command } => {
            handle_resource_requirements_commands(&config, command, &cli.format);
        }
        Commands::Events { command } => {
            handle_event_commands(&config, command, &cli.format);
        }
        Commands::Results { command } => {
            handle_result_commands(&config, command, &cli.format);
        }
        Commands::UserData { command } => {
            handle_user_data_commands(&config, command, &cli.format);
        }
        Commands::Slurm { command } => {
            handle_slurm_commands(&config, command, &cli.format);
        }
        Commands::Reports { command } => {
            handle_report_commands(&config, command, &cli.format);
        }
        Commands::RunJobs(args) => {
            run_jobs_cmd::run(args);
        }
        Commands::Tui(args) => {
            if let Err(e) = tui_runner::run(args) {
                eprintln!("Error running TUI: {}", e);
                std::process::exit(1);
            }
        }
        Commands::PlotResources(args) => {
            if let Err(e) = plot_resources_cmd::run(args) {
                eprintln!("Error generating plots: {}", e);
                std::process::exit(1);
            }
        }
    }
}
