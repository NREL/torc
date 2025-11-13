use clap::{Parser, Subcommand};

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

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Cli {
    /// Output format (table or json)
    #[arg(short, long, default_value = "table")]
    format: String,
    /// URL of torc server
    #[arg(short, long, default_value = "http://localhost:8080/torc-service/v1")]
    url: String,
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
}

fn main() {
    env_logger::init();
    let cli = Cli::parse();

    // Validate format option
    if !matches!(cli.format.as_str(), "table" | "json") {
        eprintln!("Error: format must be either 'table' or 'json'");
        std::process::exit(1);
    }

    // Create default configuration (you may want to make this configurable)
    let mut config = Configuration::new();
    config.base_path = cli.url;

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
    }
}
