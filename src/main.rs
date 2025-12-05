use clap::{CommandFactory, Parser};
use clap_complete;
use rpassword;
use std::path::PathBuf;

use torc::cli::{Cli, Commands};
use torc::client::apis::configuration::Configuration;
use torc::client::apis::default_api;
use torc::client::commands::compute_nodes::handle_compute_node_commands;
use torc::client::commands::events::handle_event_commands;
use torc::client::commands::files::handle_file_commands;
use torc::client::commands::job_dependencies::handle_job_dependency_commands;
use torc::client::commands::jobs::handle_job_commands;
use torc::client::commands::reports::handle_report_commands;
use torc::client::commands::resource_requirements::handle_resource_requirements_commands;
use torc::client::commands::results::handle_result_commands;
use torc::client::commands::slurm::handle_slurm_commands;
use torc::client::commands::user_data::handle_user_data_commands;
use torc::client::commands::workflows::handle_workflow_commands;
use torc::client::workflow_manager::WorkflowManager;
use torc::client::workflow_spec::WorkflowSpec;

// Import the binary command modules from the library
use torc::plot_resources_cmd;
use torc::run_jobs_cmd;
use torc::tui_runner;

/// Helper function to determine if a string is a file path or workflow ID
fn is_spec_file(arg: &str) -> bool {
    arg.ends_with(".yaml")
        || arg.ends_with(".yml")
        || arg.ends_with(".json")
        || arg.ends_with(".json5")
        || std::path::Path::new(arg).is_file()
}

fn main() {
    let cli = Cli::parse();

    // Resolve log level with priority: CLI arg > env var > default
    let log_level = cli.log_level.unwrap_or_else(|| "info".to_string());

    // Initialize logger with CLI argument or RUST_LOG env var
    // Skip initialization for commands that set up their own logging (e.g., Run, Tui)
    // or output to stdout (e.g., Completions)
    let skip_logger_init = matches!(
        cli.command,
        Commands::Run { .. } | Commands::Tui(..) | Commands::Completions { .. }
    );

    if !skip_logger_init {
        env_logger::Builder::new().parse_filters(&log_level).init();
    }

    // Validate format option for API commands
    if !matches!(cli.format.as_str(), "table" | "json") {
        eprintln!("Error: format must be either 'table' or 'json'");
        std::process::exit(1);
    }

    // Resolve URL with priority: CLI arg > env var > default
    let url = cli
        .url
        .unwrap_or_else(|| "http://localhost:8080/torc-service/v1".to_string());

    // Create configuration for API commands
    let mut config = Configuration::new();
    config.base_path = url.clone();

    // Handle authentication
    if let Some(username) = cli.username.clone() {
        let password = match cli.password.clone() {
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
        Commands::Run {
            workflow_spec_or_id,
            max_parallel_jobs,
            num_cpus,
            memory_gb,
            num_gpus,
            poll_interval,
            output_dir,
        } => {
            let workflow_id = if is_spec_file(workflow_spec_or_id) {
                // Create workflow from spec file
                let user = std::env::var("USER")
                    .or_else(|_| std::env::var("USERNAME"))
                    .unwrap_or_else(|_| "unknown".to_string());
                match WorkflowSpec::create_workflow_from_spec(
                    &config,
                    workflow_spec_or_id,
                    &user,
                    true,
                ) {
                    Ok(id) => {
                        println!("Created workflow {}", id);
                        id
                    }
                    Err(e) => {
                        eprintln!("Error creating workflow from spec: {}", e);
                        std::process::exit(1);
                    }
                }
            } else {
                // Parse as workflow ID
                match workflow_spec_or_id.parse::<i64>() {
                    Ok(id) => id,
                    Err(_) => {
                        eprintln!(
                            "Error: '{}' is neither a valid workflow spec file nor a workflow ID",
                            workflow_spec_or_id
                        );
                        std::process::exit(1);
                    }
                }
            };

            // Build args for run_jobs_cmd
            let args = run_jobs_cmd::Args {
                workflow_id: Some(workflow_id),
                url: url.clone(),
                output_dir: output_dir
                    .clone()
                    .unwrap_or_else(|| PathBuf::from("output")),
                poll_interval: poll_interval.unwrap_or(5.0),
                max_parallel_jobs: *max_parallel_jobs,
                database_poll_interval: 30,
                time_limit: None,
                end_time: None,
                num_cpus: *num_cpus,
                memory_gb: *memory_gb,
                num_gpus: *num_gpus,
                num_nodes: None,
                scheduler_config_id: None,
                log_prefix: None,
                cpu_affinity_cpus_per_job: None,
                log_level: log_level.clone(),
            };

            run_jobs_cmd::run(&args);
        }
        Commands::Submit {
            workflow_spec_or_id,
            ignore_missing_data,
        } => {
            let workflow_id = if is_spec_file(workflow_spec_or_id) {
                // Load and validate spec file
                let spec = match WorkflowSpec::from_spec_file(workflow_spec_or_id) {
                    Ok(spec) => spec,
                    Err(e) => {
                        eprintln!("Error loading workflow spec: {}", e);
                        std::process::exit(1);
                    }
                };

                // Check if spec has schedule_nodes action
                if !spec.has_schedule_nodes_action() {
                    eprintln!("Error: Cannot submit workflow");
                    eprintln!();
                    eprintln!(
                        "The spec does not define an on_workflow_start action with schedule_nodes."
                    );
                    eprintln!("To submit to a scheduler, add a workflow action like:");
                    eprintln!();
                    eprintln!("  actions:");
                    eprintln!("    - trigger_type: on_workflow_start");
                    eprintln!("      action_type: schedule_nodes");
                    eprintln!("      scheduler_type: slurm");
                    eprintln!("      scheduler: \"my-cluster\"");
                    eprintln!();
                    eprintln!("Or run locally instead:");
                    eprintln!("  torc run {}", workflow_spec_or_id);
                    std::process::exit(1);
                }

                // Create workflow from spec
                let user = std::env::var("USER")
                    .or_else(|_| std::env::var("USERNAME"))
                    .unwrap_or_else(|_| "unknown".to_string());
                match WorkflowSpec::create_workflow_from_spec(
                    &config,
                    workflow_spec_or_id,
                    &user,
                    true,
                ) {
                    Ok(id) => {
                        println!("Created workflow {}", id);
                        id
                    }
                    Err(e) => {
                        eprintln!("Error creating workflow from spec: {}", e);
                        std::process::exit(1);
                    }
                }
            } else {
                // Parse as workflow ID
                match workflow_spec_or_id.parse::<i64>() {
                    Ok(id) => id,
                    Err(_) => {
                        eprintln!(
                            "Error: '{}' is neither a valid workflow spec file nor a workflow ID",
                            workflow_spec_or_id
                        );
                        std::process::exit(1);
                    }
                }
            };

            // Check if workflow has schedule_nodes actions (for existing workflows)
            if !is_spec_file(workflow_spec_or_id) {
                match default_api::get_workflow_actions(&config, workflow_id) {
                    Ok(actions) => {
                        let has_schedule_nodes = actions.iter().any(|action| {
                            action.trigger_type == "on_workflow_start"
                                && action.action_type == "schedule_nodes"
                        });

                        if !has_schedule_nodes {
                            eprintln!("Error: Cannot submit workflow {}", workflow_id);
                            eprintln!();
                            eprintln!(
                                "The workflow does not define an on_workflow_start action with schedule_nodes."
                            );
                            eprintln!(
                                "To submit to a scheduler, the workflow must have an action configured."
                            );
                            eprintln!();
                            eprintln!("Or run locally instead:");
                            eprintln!("  torc run {}", workflow_id);
                            std::process::exit(1);
                        }
                    }
                    Err(e) => {
                        eprintln!("Error getting workflow actions: {}", e);
                        std::process::exit(1);
                    }
                }
            }

            // Submit the workflow
            match default_api::get_workflow(&config, workflow_id) {
                Ok(workflow) => {
                    let workflow_manager = WorkflowManager::new(config.clone(), workflow);
                    match workflow_manager.start(*ignore_missing_data) {
                        Ok(()) => {
                            println!("Successfully submitted workflow {}", workflow_id);
                        }
                        Err(e) => {
                            eprintln!("Error submitting workflow {}: {}", workflow_id, e);
                            std::process::exit(1);
                        }
                    }
                }
                Err(e) => {
                    eprintln!("Error getting workflow {}: {}", workflow_id, e);
                    std::process::exit(1);
                }
            }
        }
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
        Commands::JobDependencies { command } => {
            handle_job_dependency_commands(command, &config, &cli.format);
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
        Commands::Completions { shell } => {
            let mut cmd = Cli::command();
            clap_complete::generate(*shell, &mut cmd, "torc", &mut std::io::stdout());
        }
    }
}
