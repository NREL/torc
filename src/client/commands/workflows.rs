use std::io::{self, Write};

use clap::Subcommand;

use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::commands::hpc::create_registry_with_config_public;
use crate::client::commands::pagination::{
    JobListParams, ResourceRequirementsListParams, ScheduledComputeNodeListParams,
    SlurmSchedulersListParams, WorkflowListParams, paginate_jobs, paginate_resource_requirements,
    paginate_scheduled_compute_nodes, paginate_slurm_schedulers, paginate_workflows,
};
use crate::client::commands::slurm::generate_schedulers_for_workflow;
use crate::client::commands::{
    get_env_user_name, get_user_name, print_error, select_workflow_interactively,
    table_format::display_table_with_count,
};
use crate::client::hpc::hpc_interface::HpcInterface;
use crate::client::workflow_manager::WorkflowManager;
use crate::client::workflow_spec::WorkflowSpec;
use crate::config::TorcConfig;
use crate::models;
use serde_json;
use tabled::Tabled;

#[derive(Tabled)]
struct WorkflowTableRow {
    #[tabled(rename = "ID")]
    id: i64,
    #[tabled(rename = "Name")]
    name: String,
    #[tabled(rename = "Description")]
    description: String,
    #[tabled(rename = "User")]
    user: String,
    #[tabled(rename = "Timestamp")]
    timestamp: String,
}

#[derive(Tabled)]
struct WorkflowTableRowNoUser {
    #[tabled(rename = "ID")]
    id: i64,
    #[tabled(rename = "Name")]
    name: String,
    #[tabled(rename = "Description")]
    description: String,
    #[tabled(rename = "Timestamp")]
    timestamp: String,
}

#[derive(Tabled)]
struct WorkflowActionTableRow {
    #[tabled(rename = "ID")]
    id: i64,
    #[tabled(rename = "Trigger")]
    trigger_type: String,
    #[tabled(rename = "Action")]
    action_type: String,
    #[tabled(rename = "Progress")]
    progress: String,
    #[tabled(rename = "Status")]
    status: String,
    #[tabled(rename = "Executed At")]
    executed_at: String,
    #[tabled(rename = "Job IDs")]
    job_ids: String,
}

#[derive(Subcommand)]
pub enum WorkflowCommands {
    /// Create a workflow from a specification file (supports JSON, JSON5, YAML, and KDL formats)
    Create {
        /// Path to specification file containing WorkflowSpec
        ///
        /// Supported formats:
        /// - JSON (.json): Standard JSON format
        /// - JSON5 (.json5): JSON with comments and trailing commas
        /// - YAML (.yaml, .yml): Human-readable YAML format
        /// - KDL (.kdl): KDL document format
        ///
        /// Format is auto-detected from file extension, with fallback parsing attempted
        #[arg()]
        file: String,
        /// User that owns the workflow (defaults to USER environment variable)
        #[arg(short, long, env = "USER")]
        user: String,
        /// Disable resource monitoring (default: enabled with summary granularity and 5s sample rate)
        #[arg(long, default_value = "false")]
        no_resource_monitoring: bool,
        /// Skip validation checks (e.g., scheduler node requirements). Use with caution.
        #[arg(long, default_value = "false")]
        skip_checks: bool,
        /// Validate the workflow specification without creating it (dry-run mode)
        /// Returns a summary of what would be created including job count after parameter expansion
        #[arg(long)]
        dry_run: bool,
    },
    /// Create a workflow with auto-generated Slurm schedulers
    ///
    /// Automatically generates Slurm schedulers based on job resource requirements
    /// and HPC profile. For Slurm workflows without pre-configured schedulers.
    #[command(name = "create-slurm")]
    CreateSlurm {
        /// Path to specification file containing WorkflowSpec
        #[arg()]
        file: String,
        /// Slurm account to use for allocations
        #[arg(long)]
        account: String,
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
        /// User that owns the workflow (defaults to USER environment variable)
        #[arg(short, long, env = "USER")]
        user: String,
        /// Disable resource monitoring (default: enabled with summary granularity and 5s sample rate)
        #[arg(long, default_value = "false")]
        no_resource_monitoring: bool,
        /// Skip validation checks (e.g., scheduler node requirements). Use with caution.
        #[arg(long, default_value = "false")]
        skip_checks: bool,
        /// Validate the workflow specification without creating it (dry-run mode)
        #[arg(long)]
        dry_run: bool,
    },
    /// Create a new empty workflow
    New {
        /// Name of the workflow
        #[arg(short, long)]
        name: String,
        /// Description of the workflow
        #[arg(short, long)]
        description: Option<String>,
        /// User that owns the workflow (defaults to USER environment variable)
        #[arg(short, long, env = "USER")]
        user: String,
    },
    /// List workflows
    List {
        /// User to filter by (defaults to USER environment variable)
        #[arg(short, long, env = "USER", required_unless_present = "all_users")]
        user: Option<String>,
        /// List workflows for all users (overrides --user)
        #[arg(long)]
        all_users: bool,
        /// Maximum number of workflows to return
        #[arg(short, long, default_value = "10000")]
        limit: i64,
        /// Offset for pagination (0-based)
        #[arg(long, default_value = "0")]
        offset: i64,
        /// Field to sort by
        #[arg(long)]
        sort_by: Option<String>,
        /// Reverse sort order
        #[arg(long)]
        reverse_sort: bool,
        /// Show only archived workflows
        #[arg(long, default_value = "false")]
        archived_only: bool,
        /// Include both archived and non-archived workflows
        #[arg(long, default_value = "false")]
        include_archived: bool,
    },
    /// Get a specific workflow by ID
    Get {
        /// ID of the workflow to get (optional - will prompt if not provided)
        #[arg()]
        id: Option<i64>,
        /// User to filter by (defaults to USER environment variable)
        #[arg(short, long)]
        user: Option<String>,
    },
    /// Update an existing workflow
    Update {
        /// ID of the workflow to update (optional - will prompt if not provided)
        #[arg()]
        id: Option<i64>,
        /// Name of the workflow
        #[arg(short, long)]
        name: Option<String>,
        /// Description of the workflow
        #[arg(short, long)]
        description: Option<String>,
        /// User that owns the workflow
        #[arg(long)]
        owner_user: Option<String>,
    },
    /// Cancel a workflow and all associated Slurm jobs
    Cancel {
        /// ID of the workflow to cancel (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
    },
    /// Delete one or more workflows
    Delete {
        /// IDs of workflows to remove (optional - will prompt if not provided)
        #[arg()]
        ids: Vec<i64>,
        /// Skip confirmation prompt
        #[arg(long)]
        no_prompts: bool,
        /// Force deletion even if workflow belongs to a different user
        #[arg(long)]
        force: bool,
    },
    /// Archive or unarchive one or more workflows
    Archive {
        /// Set to true to archive, false to unarchive
        #[arg()]
        is_archived: String,
        /// IDs of workflows to archive/unarchive (if empty, will prompt for selection)
        #[arg()]
        workflow_ids: Vec<i64>,
    },
    /// Submit a workflow: initialize if needed and schedule nodes for on_workflow_start actions
    /// This command requires the workflow to have an on_workflow_start action with schedule_nodes
    Submit {
        /// ID of the workflow to submit (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// If false, fail the operation if missing data is present (defaults to false)
        #[arg(long, default_value = "false")]
        force: bool,
    },
    /// Run a workflow locally on the current node
    Run {
        /// ID of the workflow to run (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// Poll interval in seconds for checking job completion
        #[arg(short, long, default_value = "5.0")]
        poll_interval: f64,
        /// Maximum number of parallel jobs to run (defaults to available CPUs)
        #[arg(long)]
        max_parallel_jobs: Option<i64>,
        /// Output directory for job logs and results
        #[arg(long, default_value = "output")]
        output_dir: std::path::PathBuf,
    },
    /// Initialize a workflow, including all job statuses.
    Initialize {
        /// ID of the workflow to start (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// If false, fail the operation if missing data is present (defaults to false)
        #[arg(long, default_value = "false")]
        force: bool,
        /// Skip confirmation prompt
        #[arg(long)]
        no_prompts: bool,
        /// Perform a dry run without making changes
        #[arg(long)]
        dry_run: bool,
    },
    /// Reinitialize a workflow. This will reinitialize all jobs with a status of
    /// canceled, submitting, pending, or terminated. Jobs with a status of
    /// done will also be reinitialized if an input_file or user_data record has
    /// changed.
    Reinitialize {
        /// ID of the workflow to reinitialize (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// If false, fail the operation if missing data is present (defaults to false)
        #[arg(long, default_value = "false")]
        force: bool,
        /// Perform a dry run without making changes
        #[arg(long)]
        dry_run: bool,
    },
    /// Get workflow status
    Status {
        /// ID of the workflow to get status for (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// User to filter by (defaults to USER environment variable)
        #[arg(short, long)]
        user: Option<String>,
    },
    /// Reset workflow and job status
    ResetStatus {
        /// ID of the workflow to reset status for (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// Only reset failed jobs
        #[arg(long, default_value = "false")]
        failed_only: bool,
        /// Reinitialize the workflow after resetting status
        #[arg(short, long, default_value = "false")]
        reinitialize: bool,
        /// Force reset even if there are active jobs (ignores running/pending jobs check)
        #[arg(long, default_value = "false")]
        force: bool,
        /// Skip confirmation prompt
        #[arg(long)]
        no_prompts: bool,
    },
    /// Show the execution plan for a workflow specification or existing workflow
    ExecutionPlan {
        /// Path to specification file OR workflow ID
        #[arg()]
        spec_or_id: String,
    },
    /// List workflow actions and their statuses (useful for debugging action triggers)
    ListActions {
        /// ID of the workflow to show actions for (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// User to filter by when selecting workflow interactively (defaults to USER environment variable)
        #[arg(short, long)]
        user: Option<String>,
    },
    /// Check if a workflow is complete
    IsComplete {
        /// ID of the workflow to check (optional - will prompt if not provided)
        #[arg()]
        id: Option<i64>,
    },
}

fn show_execution_plan_from_spec(file_path: &str, format: &str) {
    // Parse the workflow spec
    let mut spec = match WorkflowSpec::from_spec_file(file_path) {
        Ok(spec) => spec,
        Err(e) => {
            eprintln!("Error parsing workflow specification: {}", e);
            std::process::exit(1);
        }
    };

    // Expand parameters
    if let Err(e) = spec.expand_parameters() {
        eprintln!("Error expanding parameters: {}", e);
        std::process::exit(1);
    }

    // Validate actions
    if let Err(e) = spec.validate_actions() {
        eprintln!("Error validating actions: {}", e);
        std::process::exit(1);
    }

    // Perform variable substitution to extract file/data dependencies
    if let Err(e) = spec.substitute_variables() {
        eprintln!("Error substituting variables: {}", e);
        std::process::exit(1);
    }

    // Build execution plan
    match crate::client::execution_plan::ExecutionPlan::from_spec(&spec) {
        Ok(plan) => {
            if format == "json" {
                // For JSON output, use the new DAG-based event structure
                let events_json: Vec<serde_json::Value> = plan.events.values().map(|event| {
                    serde_json::json!({
                        "id": event.id,
                        "trigger": event.trigger,
                        "trigger_description": event.trigger_description,
                        "scheduler_allocations": event.scheduler_allocations.iter().map(|alloc| {
                            serde_json::json!({
                                "scheduler": alloc.scheduler,
                                "scheduler_type": alloc.scheduler_type,
                                "num_allocations": alloc.num_allocations,
                                "job_names": alloc.jobs,
                            })
                        }).collect::<Vec<_>>(),
                        "jobs_becoming_ready": event.jobs_becoming_ready,
                        "depends_on_events": event.depends_on_events,
                        "unlocks_events": event.unlocks_events,
                    })
                }).collect();

                let output = serde_json::json!({
                    "status": "success",
                    "source": "spec_file",
                    "workflow_name": spec.name,
                    "total_events": plan.events.len(),
                    "total_jobs": spec.jobs.len(),
                    "root_events": plan.root_events,
                    "leaf_events": plan.leaf_events,
                    "events": events_json,
                });

                match serde_json::to_string_pretty(&output) {
                    Ok(json) => println!("{}", json),
                    Err(e) => {
                        eprintln!("Error serializing execution plan: {}", e);
                        std::process::exit(1);
                    }
                }
            } else {
                // Display in human-readable format
                println!("\nWorkflow: {}", spec.name);
                if let Some(ref desc) = spec.description {
                    println!("Description: {}", desc);
                }
                println!("Total Jobs: {}", spec.jobs.len());
                plan.display();
            }
        }
        Err(e) => {
            eprintln!("Error building execution plan: {}", e);
            std::process::exit(1);
        }
    }
}

fn show_execution_plan_from_database(config: &Configuration, workflow_id: i64, format: &str) {
    // Fetch workflow from database
    let workflow = match default_api::get_workflow(config, workflow_id) {
        Ok(wf) => wf,
        Err(e) => {
            eprintln!("Error fetching workflow {}: {}", workflow_id, e);
            std::process::exit(1);
        }
    };

    // Fetch all jobs for this workflow
    let jobs = match paginate_jobs(
        config,
        workflow_id,
        JobListParams::new().with_include_relationships(true),
    ) {
        Ok(jobs) => jobs,
        Err(e) => {
            eprintln!("Error fetching jobs for workflow {}: {}", workflow_id, e);
            std::process::exit(1);
        }
    };

    // Fetch workflow actions
    let actions = match default_api::get_workflow_actions(config, workflow_id) {
        Ok(actions) => actions,
        Err(e) => {
            eprintln!("Error fetching actions for workflow {}: {}", workflow_id, e);
            std::process::exit(1);
        }
    };

    // Fetch slurm schedulers for this workflow
    let slurm_schedulers =
        match paginate_slurm_schedulers(config, workflow_id, SlurmSchedulersListParams::new()) {
            Ok(schedulers) => schedulers,
            Err(e) => {
                eprintln!(
                    "Warning: Could not fetch slurm schedulers for workflow {}: {}",
                    workflow_id, e
                );
                vec![]
            }
        };

    // Fetch resource requirements for this workflow
    let resource_requirements = match paginate_resource_requirements(
        config,
        workflow_id,
        ResourceRequirementsListParams::new(),
    ) {
        Ok(rrs) => rrs,
        Err(e) => {
            eprintln!(
                "Warning: Could not fetch resource requirements for workflow {}: {}",
                workflow_id, e
            );
            vec![]
        }
    };

    // Build execution plan from database models
    match crate::client::execution_plan::ExecutionPlan::from_database_models(
        &workflow,
        &jobs,
        &actions,
        &slurm_schedulers,
        &resource_requirements,
    ) {
        Ok(plan) => {
            if format == "json" {
                // For JSON output, use the new DAG-based event structure
                let events_json: Vec<serde_json::Value> = plan.events.values().map(|event| {
                    serde_json::json!({
                        "id": event.id,
                        "trigger": event.trigger,
                        "trigger_description": event.trigger_description,
                        "scheduler_allocations": event.scheduler_allocations.iter().map(|alloc| {
                            serde_json::json!({
                                "scheduler": alloc.scheduler,
                                "scheduler_type": alloc.scheduler_type,
                                "num_allocations": alloc.num_allocations,
                                "job_names": alloc.jobs,
                            })
                        }).collect::<Vec<_>>(),
                        "jobs_becoming_ready": event.jobs_becoming_ready,
                        "depends_on_events": event.depends_on_events,
                        "unlocks_events": event.unlocks_events,
                    })
                }).collect();

                let output = serde_json::json!({
                    "status": "success",
                    "source": "database",
                    "workflow_id": workflow_id,
                    "workflow_name": workflow.name,
                    "total_events": plan.events.len(),
                    "total_jobs": jobs.len(),
                    "root_events": plan.root_events,
                    "leaf_events": plan.leaf_events,
                    "events": events_json,
                });

                match serde_json::to_string_pretty(&output) {
                    Ok(json) => println!("{}", json),
                    Err(e) => {
                        eprintln!("Error serializing execution plan: {}", e);
                        std::process::exit(1);
                    }
                }
            } else {
                println!("\nWorkflow ID: {}", workflow_id);
                println!("Workflow: {}", workflow.name);
                if let Some(desc) = &workflow.description {
                    println!("Description: {}", desc);
                }
                println!("Total Jobs: {}", jobs.len());
                plan.display();
            }
        }
        Err(e) => {
            eprintln!("Error building execution plan from database: {}", e);
            std::process::exit(1);
        }
    }
}

fn handle_execution_plan(config: &Configuration, spec_or_id: &str, format: &str) {
    // Try to parse as workflow ID first, otherwise treat as file path
    if let Ok(workflow_id) = spec_or_id.parse::<i64>() {
        // Show execution plan for existing workflow from database
        show_execution_plan_from_database(config, workflow_id, format);
    } else {
        // Show execution plan for workflow from spec file
        show_execution_plan_from_spec(spec_or_id, format);
    }
}

fn handle_list_actions(
    config: &Configuration,
    workflow_id: &Option<i64>,
    user: &Option<String>,
    format: &str,
) {
    let user_name = get_user_name(user);

    let selected_workflow_id = match workflow_id {
        Some(id) => *id,
        None => select_workflow_interactively(config, &user_name).unwrap(),
    };

    match default_api::get_workflow_actions(config, selected_workflow_id) {
        Ok(actions) => {
            if format == "json" {
                let output = serde_json::json!({
                    "actions": actions
                });
                match serde_json::to_string_pretty(&output) {
                    Ok(json) => println!("{}", json),
                    Err(e) => {
                        eprintln!("Error serializing actions to JSON: {}", e);
                        std::process::exit(1);
                    }
                }
            } else if actions.is_empty() {
                println!(
                    "No workflow actions found for workflow {}",
                    selected_workflow_id
                );
            } else {
                println!("Workflow Actions for workflow {}:", selected_workflow_id);
                println!();

                let rows: Vec<WorkflowActionTableRow> = actions
                    .iter()
                    .map(|action| {
                        // Determine status based on trigger_count, required_triggers, and executed
                        let status = if action.executed {
                            "Executed".to_string()
                        } else if action.trigger_count >= action.required_triggers {
                            "Pending (ready to claim)".to_string()
                        } else {
                            "Waiting".to_string()
                        };

                        // Format progress as "trigger_count/required_triggers"
                        let progress =
                            format!("{}/{}", action.trigger_count, action.required_triggers);

                        // Format job_ids for display
                        let job_ids = match &action.job_ids {
                            Some(ids) if !ids.is_empty() => {
                                if ids.len() <= 5 {
                                    ids.iter()
                                        .map(|id| id.to_string())
                                        .collect::<Vec<_>>()
                                        .join(", ")
                                } else {
                                    format!(
                                        "{}, ... (+{} more)",
                                        ids.iter()
                                            .take(3)
                                            .map(|id| id.to_string())
                                            .collect::<Vec<_>>()
                                            .join(", "),
                                        ids.len() - 3
                                    )
                                }
                            }
                            _ => "(all jobs)".to_string(),
                        };

                        WorkflowActionTableRow {
                            id: action.id.unwrap_or(-1),
                            trigger_type: action.trigger_type.clone(),
                            action_type: action.action_type.clone(),
                            progress,
                            status,
                            executed_at: action.executed_at.as_deref().unwrap_or("-").to_string(),
                            job_ids,
                        }
                    })
                    .collect();

                display_table_with_count(&rows, "actions");

                // Print a helpful legend
                println!();
                println!("Status legend:");
                println!(
                    "  Waiting  - trigger_count < required_triggers (action not yet triggered)"
                );
                println!(
                    "  Pending  - trigger_count >= required_triggers (ready to be claimed and executed)"
                );
                println!("  Executed - action has been claimed and executed");
            }
        }
        Err(e) => {
            print_error("getting workflow actions", &e);
            std::process::exit(1);
        }
    }
}

fn handle_cancel(config: &Configuration, workflow_id: &Option<i64>, format: &str) {
    let user_name = get_env_user_name();

    let selected_workflow_id = match workflow_id {
        Some(id) => *id,
        None => select_workflow_interactively(config, &user_name).unwrap(),
    };

    match default_api::cancel_workflow(config, selected_workflow_id, None) {
        Ok(_) => {
            if format != "json" {
                eprintln!("Successfully canceled workflow {}", selected_workflow_id);
            }
        }
        Err(e) => {
            if format == "json" {
                let error_response = serde_json::json!({
                    "status": "error",
                    "message": format!("Failed to cancel workflow: {}", e),
                    "workflow_id": selected_workflow_id
                });
                println!("{}", serde_json::to_string_pretty(&error_response).unwrap());
            } else {
                print_error("canceling workflow", &e);
            }
            std::process::exit(1);
        }
    }

    // Get all scheduled compute nodes for this workflow
    let nodes = match paginate_scheduled_compute_nodes(
        config,
        selected_workflow_id,
        ScheduledComputeNodeListParams::new(),
    ) {
        Ok(nodes) => nodes,
        Err(e) => {
            if format == "json" {
                let error_response = serde_json::json!({
                    "status": "error",
                    "message": format!("Failed to list scheduled compute nodes: {}", e),
                    "workflow_id": selected_workflow_id
                });
                println!("{}", serde_json::to_string_pretty(&error_response).unwrap());
            } else {
                print_error("listing scheduled compute nodes", &e);
            }
            std::process::exit(1);
        }
    };

    let mut canceled_jobs = Vec::new();
    let mut errors = Vec::new();

    for node in nodes {
        if node.scheduler_type == "slurm" {
            match crate::client::hpc::slurm_interface::SlurmInterface::new() {
                Ok(slurm_interface) => {
                    let job_id_str = node.scheduler_id.to_string();
                    match slurm_interface.cancel_job(&job_id_str) {
                        Ok(_) => {
                            canceled_jobs.push(node.scheduler_id);
                            if format != "json" {
                                println!("  Canceled Slurm job: {}", node.scheduler_id);
                            }
                        }
                        Err(e) => {
                            let error_msg =
                                format!("Failed to cancel Slurm job {}: {}", node.scheduler_id, e);
                            errors.push(error_msg.clone());
                            if format != "json" {
                                eprintln!("  {}", error_msg);
                            }
                        }
                    }
                }
                Err(e) => {
                    let error_msg = format!(
                        "Failed to create SlurmInterface for job {}: {}",
                        node.scheduler_id, e
                    );
                    errors.push(error_msg.clone());
                    if format != "json" {
                        eprintln!("  {}", error_msg);
                    }
                }
            }
        }
    }

    if format == "json" {
        let response = serde_json::json!({
            "status": if errors.is_empty() { "success" } else { "partial_success" },
            "workflow_id": selected_workflow_id,
            "canceled_slurm_jobs": canceled_jobs,
            "errors": if errors.is_empty() { None } else { Some(errors) }
        });
        println!("{}", serde_json::to_string_pretty(&response).unwrap());
    } else if !canceled_jobs.is_empty() {
        println!("Canceled {} Slurm job(s)", canceled_jobs.len());
    }
}

fn handle_reset_status(
    config: &Configuration,
    workflow_id: &Option<i64>,
    failed_only: bool,
    reinitialize: bool,
    force: bool,
    no_prompts: bool,
    format: &str,
) {
    let user_name = get_env_user_name();

    let selected_workflow_id = match workflow_id {
        Some(id) => *id,
        None => select_workflow_interactively(config, &user_name).unwrap(),
    };

    // Show confirmation prompt unless --no-prompt or format is json
    if !no_prompts && format != "json" {
        eprintln!(
            "\nWarning: You are about to reset the status for workflow {}.",
            selected_workflow_id
        );
        if failed_only {
            eprintln!("This will reset the status of all failed jobs.");
        } else {
            eprintln!("This will reset the status of all jobs.");
        }
        if reinitialize {
            eprintln!("The workflow will be reinitialized after reset.");
        }
        if force {
            eprintln!("Force mode is enabled (will ignore running/pending jobs check).");
        }
        print!("\nDo you want to continue? (y/N): ");
        io::stdout().flush().unwrap();

        let mut input = String::new();
        match io::stdin().read_line(&mut input) {
            Ok(_) => {
                let response = input.trim().to_lowercase();
                if response != "y" && response != "yes" {
                    eprintln!("Reset cancelled.");
                    std::process::exit(0);
                }
            }
            Err(e) => {
                eprintln!("Failed to read input: {}", e);
                std::process::exit(1);
            }
        }
    }

    // Track the results of each operation for JSON output
    let mut workflow_reset_success = false;
    let mut job_reset_success = false;
    let mut reinitialize_success = false;
    let mut errors = Vec::<String>::new();

    // Pass force as query parameter
    let force_param = if force { Some(true) } else { None };

    // Reset workflow status
    match default_api::reset_workflow_status(config, selected_workflow_id, force_param, None) {
        Ok(_) => {
            workflow_reset_success = true;
            if format != "json" {
                eprintln!(
                    "Successfully reset workflow status for workflow {}",
                    selected_workflow_id
                );
            }
        }
        Err(e) => {
            errors.push(format!("resetting workflow status: {}", e));
            if format != "json" {
                print_error("resetting workflow status", &e);
            }
        }
    }

    // Reset job status
    match default_api::reset_job_status(config, selected_workflow_id, Some(failed_only), None) {
        Ok(_) => {
            job_reset_success = true;
            if format != "json" {
                if failed_only {
                    eprintln!(
                        "Successfully reset failed job status for workflow {}",
                        selected_workflow_id
                    );
                } else {
                    eprintln!(
                        "Successfully reset all job status for workflow {}",
                        selected_workflow_id
                    );
                }
            }
        }
        Err(e) => {
            errors.push(format!("resetting job status: {}", e));
            if format != "json" {
                print_error("resetting job status", &e);
            }
        }
    }

    // If reinitialize is true, reinitialize the workflow
    if reinitialize {
        match default_api::get_workflow(config, selected_workflow_id) {
            Ok(workflow) => {
                let torc_config = TorcConfig::load().unwrap_or_default();
                let workflow_manager = WorkflowManager::new(config.clone(), torc_config, workflow);
                match workflow_manager.reinitialize(false, false) {
                    Ok(()) => {
                        reinitialize_success = true;
                        if format != "json" {
                            eprintln!(
                                "Successfully reinitialized workflow {}",
                                selected_workflow_id
                            );
                        }
                    }
                    Err(e) => {
                        errors.push(format!("reinitializing workflow: {}", e));
                        if format != "json" {
                            eprintln!(
                                "Error reinitializing workflow {}: {}",
                                selected_workflow_id, e
                            );
                        }
                    }
                }
            }
            Err(e) => {
                errors.push(format!("getting workflow for reinitialize: {}", e));
                if format != "json" {
                    print_error("getting workflow for reinitialize", &e);
                }
            }
        }
    }

    // Output combined JSON or exit with error if any operation failed
    if format == "json" {
        let overall_success =
            workflow_reset_success && job_reset_success && (!reinitialize || reinitialize_success);

        let mut messages = Vec::new();
        if workflow_reset_success {
            messages.push(format!(
                "Successfully reset workflow status for workflow {}",
                selected_workflow_id
            ));
        }
        if job_reset_success {
            if failed_only {
                messages.push(format!(
                    "Successfully reset failed job status for workflow {}",
                    selected_workflow_id
                ));
            } else {
                messages.push(format!(
                    "Successfully reset all job status for workflow {}",
                    selected_workflow_id
                ));
            }
        }
        if reinitialize && reinitialize_success {
            messages.push(format!(
                "Successfully reinitialized workflow {}",
                selected_workflow_id
            ));
        }

        let response = if overall_success {
            serde_json::json!({
                "status": "success",
                "workflow_id": selected_workflow_id,
                "operations": {
                    "workflow_reset": workflow_reset_success,
                    "job_reset": job_reset_success,
                    "reinitialize": if reinitialize { Some(reinitialize_success) } else { None }
                },
                "failed_only": failed_only,
                "messages": messages
            })
        } else {
            serde_json::json!({
                "status": "error",
                "workflow_id": selected_workflow_id,
                "operations": {
                    "workflow_reset": workflow_reset_success,
                    "job_reset": job_reset_success,
                    "reinitialize": if reinitialize { Some(reinitialize_success) } else { None }
                },
                "failed_only": failed_only,
                "messages": messages,
                "errors": errors
            })
        };

        println!("{}", serde_json::to_string_pretty(&response).unwrap());
    }

    // Exit with error if any operation failed
    if !errors.is_empty() {
        std::process::exit(1);
    }
}

fn handle_status(
    config: &Configuration,
    workflow_id: &Option<i64>,
    user: &Option<String>,
    format: &str,
) {
    let user_name = get_user_name(user);

    let selected_workflow_id = match workflow_id {
        Some(id) => *id,
        None => select_workflow_interactively(config, &user_name).unwrap(),
    };

    match default_api::get_workflow_status(config, selected_workflow_id) {
        Ok(status) => {
            if format == "json" {
                match serde_json::to_string_pretty(&status) {
                    Ok(json) => println!("{}", json),
                    Err(e) => {
                        eprintln!("Error serializing workflow status to JSON: {}", e);
                        std::process::exit(1);
                    }
                }
            } else {
                println!("Workflow Status for ID {}:", selected_workflow_id);
                if let Some(id) = status.id {
                    println!("  Status ID: {}", id);
                }
                println!("  Run ID: {}", status.run_id);
                println!("  Is Canceled: {}", status.is_canceled);
                if let Some(is_archived) = status.is_archived {
                    println!("  Is Archived: {}", is_archived);
                }
            }
        }
        Err(e) => {
            print_error("getting workflow status", &e);
            std::process::exit(1);
        }
    }
}

fn handle_reinitialize(
    config: &Configuration,
    workflow_id: &Option<i64>,
    force: bool,
    dry_run: bool,
    format: &str,
) {
    let user_name = get_env_user_name();

    let selected_workflow_id = match workflow_id {
        Some(id) => *id,
        None => select_workflow_interactively(config, &user_name).unwrap(),
    };
    // First get the workflow
    match default_api::get_workflow(config, selected_workflow_id) {
        Ok(workflow) => {
            let torc_config = TorcConfig::load().unwrap_or_default();
            let workflow_manager = WorkflowManager::new(config.clone(), torc_config, workflow);

            // Handle dry-run mode
            if dry_run {
                match workflow_manager.check_initialization() {
                    Ok(check_result) => {
                        if format == "json" {
                            let response = serde_json::json!({
                                "workflow_id": selected_workflow_id,
                                "safe": check_result.safe,
                                "missing_input_files": check_result.missing_input_files,
                                "missing_input_file_count": check_result.missing_input_files.len(),
                                "existing_output_files": check_result.existing_output_files,
                                "existing_output_file_count": check_result.existing_output_files.len(),
                            });
                            println!("{}", serde_json::to_string_pretty(&response).unwrap());
                        } else {
                            println!(
                                "Re-initialization check for workflow {}:",
                                selected_workflow_id
                            );
                            if !check_result.missing_input_files.is_empty() {
                                eprintln!(
                                    "\n❌ Missing {} required input file(s):",
                                    check_result.missing_input_files.len()
                                );
                                for file in &check_result.missing_input_files {
                                    eprintln!("  - {}", file);
                                }
                            }
                            if !check_result.existing_output_files.is_empty() {
                                eprintln!(
                                    "\n⚠️  Found {} existing output file(s):",
                                    check_result.existing_output_files.len()
                                );
                                for file in &check_result.existing_output_files {
                                    eprintln!("  - {}", file);
                                }
                            }
                            if check_result.safe {
                                println!("\n✅ Safe to reinitialize (no missing input files)");
                            } else {
                                eprintln!("\n❌ Cannot reinitialize: missing required input files");
                            }
                        }

                        // Exit with appropriate code
                        if !check_result.safe {
                            std::process::exit(1);
                        }
                    }
                    Err(e) => {
                        if format == "json" {
                            let error_response = serde_json::json!({
                                "status": "error",
                                "message": format!("Failed to check re-initialization: {}", e),
                                "workflow_id": selected_workflow_id
                            });
                            println!("{}", serde_json::to_string_pretty(&error_response).unwrap());
                        } else {
                            eprintln!(
                                "Error checking re-initialization for workflow {}: {}",
                                selected_workflow_id, e
                            );
                        }
                        std::process::exit(1);
                    }
                }
            } else {
                // Normal reinitialization (not dry-run)
                match workflow_manager.reinitialize(force, dry_run) {
                    Ok(()) => {
                        if format == "json" {
                            let success_response = serde_json::json!({
                                "status": "success",
                                "message": format!("Successfully reinitialized workflow {}", selected_workflow_id),
                                "workflow_id": selected_workflow_id
                            });
                            println!(
                                "{}",
                                serde_json::to_string_pretty(&success_response).unwrap()
                            );
                        } else {
                            eprintln!("Successfully reinitialized workflow:");
                            println!("  Workflow ID: {}", selected_workflow_id);
                        }
                    }
                    Err(e) => {
                        if format == "json" {
                            let error_response = serde_json::json!({
                                "status": "error",
                                "message": format!("Failed to reinitialize workflow: {}", e),
                                "workflow_id": selected_workflow_id
                            });
                            println!("{}", serde_json::to_string_pretty(&error_response).unwrap());
                        } else {
                            eprintln!(
                                "Error reinitializing workflow {}: {}",
                                selected_workflow_id, e
                            );
                        }
                        std::process::exit(1);
                    }
                }
            }
        }
        Err(e) => {
            print_error("getting workflow for reinitialize", &e);
            std::process::exit(1);
        }
    }
}

fn handle_initialize(
    config: &Configuration,
    workflow_id: &Option<i64>,
    force: bool,
    no_prompts: bool,
    dry_run: bool,
    format: &str,
) {
    let user_name = get_env_user_name();

    let selected_workflow_id = match workflow_id {
        Some(id) => *id,
        None => select_workflow_interactively(config, &user_name).unwrap(),
    };

    // First get the workflow
    match default_api::get_workflow(config, selected_workflow_id) {
        Ok(workflow) => {
            let torc_config = TorcConfig::load().unwrap_or_default();
            let workflow_manager = WorkflowManager::new(config.clone(), torc_config, workflow);

            // Handle dry-run mode
            if dry_run {
                match workflow_manager.check_initialization() {
                    Ok(check_result) => {
                        if format == "json" {
                            let response = serde_json::json!({
                                "workflow_id": selected_workflow_id,
                                "safe": check_result.safe,
                                "missing_input_files": check_result.missing_input_files,
                                "missing_input_file_count": check_result.missing_input_files.len(),
                                "existing_output_files": check_result.existing_output_files,
                                "existing_output_file_count": check_result.existing_output_files.len(),
                            });
                            println!("{}", serde_json::to_string_pretty(&response).unwrap());
                        } else {
                            println!(
                                "Initialization check for workflow {}:",
                                selected_workflow_id
                            );
                            if !check_result.missing_input_files.is_empty() {
                                eprintln!(
                                    "\n❌ Missing {} required input file(s):",
                                    check_result.missing_input_files.len()
                                );
                                for file in &check_result.missing_input_files {
                                    eprintln!("  - {}", file);
                                }
                            }
                            if !check_result.existing_output_files.is_empty() {
                                eprintln!(
                                    "\n⚠️  Found {} existing output file(s):",
                                    check_result.existing_output_files.len()
                                );
                                for file in &check_result.existing_output_files {
                                    eprintln!("  - {}", file);
                                }
                            }
                            if check_result.safe {
                                println!("\n✅ Safe to initialize (no missing input files)");
                            } else {
                                eprintln!("\n❌ Cannot initialize: missing required input files");
                            }
                        }

                        // Exit with appropriate code
                        if !check_result.safe {
                            std::process::exit(1);
                        }
                    }
                    Err(e) => {
                        if format == "json" {
                            let error_response = serde_json::json!({
                                "status": "error",
                                "message": format!("Failed to check initialization: {}", e),
                                "workflow_id": selected_workflow_id
                            });
                            println!("{}", serde_json::to_string_pretty(&error_response).unwrap());
                        } else {
                            eprintln!(
                                "Error checking initialization for workflow {}: {}",
                                selected_workflow_id, e
                            );
                        }
                        std::process::exit(1);
                    }
                }
            } else {
                // Normal initialization (not dry-run)
                match default_api::is_workflow_uninitialized(config, selected_workflow_id) {
                    Ok(is_initialized) => {
                        if is_initialized.as_bool().unwrap_or(false)
                            && !no_prompts
                            && format != "json"
                        {
                            println!("\nWarning: This workflow has already been initialized.");
                            println!("Some jobs already have initialized status.");
                            print!("\nDo you want to continue? (y/N): ");
                            io::stdout().flush().unwrap();

                            let mut input = String::new();
                            match io::stdin().read_line(&mut input) {
                                Ok(_) => {
                                    let response = input.trim().to_lowercase();
                                    if response != "y" && response != "yes" {
                                        println!("Initialization cancelled.");
                                        std::process::exit(0);
                                    }
                                }
                                Err(e) => {
                                    eprintln!("Failed to read input: {}", e);
                                    std::process::exit(1);
                                }
                            }
                        }
                    }
                    Err(e) => {
                        print_error("checking workflow initialization status", &e);
                        std::process::exit(1);
                    }
                }
                match workflow_manager.initialize(force) {
                    Ok(()) => {
                        if format == "json" {
                            let success_response = serde_json::json!({
                                "status": "success",
                                "message": format!("Successfully started workflow {}", selected_workflow_id),
                                "workflow_id": selected_workflow_id
                            });
                            println!(
                                "{}",
                                serde_json::to_string_pretty(&success_response).unwrap()
                            );
                        } else {
                            println!("Successfully started workflow:");
                            println!("  Workflow ID: {}", selected_workflow_id);
                        }
                    }
                    Err(e) => {
                        if format == "json" {
                            let error_response = serde_json::json!({
                                "status": "error",
                                "message": format!("Failed to start workflow: {}", e),
                                "workflow_id": selected_workflow_id
                            });
                            println!("{}", serde_json::to_string_pretty(&error_response).unwrap());
                        } else {
                            eprintln!("Error starting workflow {}: {}", selected_workflow_id, e);
                        }
                        std::process::exit(1);
                    }
                }
            }
        }
        Err(e) => {
            print_error("getting workflow for start", &e);
            std::process::exit(1);
        }
    }
}

fn handle_run(
    config: &Configuration,
    workflow_id: &Option<i64>,
    poll_interval: f64,
    max_parallel_jobs: Option<i64>,
    output_dir: &std::path::Path,
) {
    let user_name = get_env_user_name();

    let selected_workflow_id = match workflow_id {
        Some(id) => *id,
        None => select_workflow_interactively(config, &user_name).unwrap(),
    };

    // Build args for run_jobs_cmd with sensible defaults
    let args = crate::run_jobs_cmd::Args {
        workflow_id: Some(selected_workflow_id),
        url: config.base_path.clone(),
        output_dir: output_dir.to_path_buf(),
        poll_interval,
        max_parallel_jobs,
        database_poll_interval: 30,
        time_limit: None,
        end_time: None,
        num_cpus: None,
        memory_gb: None,
        num_gpus: None,
        num_nodes: None,
        scheduler_config_id: None,
        log_prefix: None,
        cpu_affinity_cpus_per_job: None,
        log_level: "info".to_string(),
    };

    crate::run_jobs_cmd::run(&args);
}

fn handle_submit(config: &Configuration, workflow_id: &Option<i64>, force: bool, format: &str) {
    let user_name = get_env_user_name();

    let selected_workflow_id = match workflow_id {
        Some(id) => *id,
        None => select_workflow_interactively(config, &user_name).unwrap(),
    };

    // Check if workflow has schedule_nodes actions
    match default_api::get_workflow_actions(config, selected_workflow_id) {
        Ok(actions) => {
            let has_schedule_nodes = actions.iter().any(|action| {
                action.trigger_type == "on_workflow_start" && action.action_type == "schedule_nodes"
            });

            if !has_schedule_nodes {
                if format == "json" {
                    let error_response = serde_json::json!({
                        "status": "error",
                        "message": "Cannot submit workflow: no on_workflow_start action with schedule_nodes found",
                        "workflow_id": selected_workflow_id
                    });
                    println!("{}", serde_json::to_string_pretty(&error_response).unwrap());
                } else {
                    eprintln!("Error: Cannot submit workflow {}", selected_workflow_id);
                    eprintln!();
                    eprintln!(
                        "The workflow does not define an on_workflow_start action with schedule_nodes."
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
                    eprintln!("  torc workflows run {}", selected_workflow_id);
                }
                std::process::exit(1);
            }
        }
        Err(e) => {
            print_error("getting workflow actions", &e);
            std::process::exit(1);
        }
    }

    // Get the workflow and submit it
    match default_api::get_workflow(config, selected_workflow_id) {
        Ok(workflow) => {
            let torc_config = TorcConfig::load().unwrap_or_default();
            let workflow_manager = WorkflowManager::new(config.clone(), torc_config, workflow);
            match workflow_manager.start(force) {
                Ok(()) => {
                    if format == "json" {
                        let success_response = serde_json::json!({
                            "status": "success",
                            "message": format!("Successfully submitted workflow {}", selected_workflow_id),
                            "workflow_id": selected_workflow_id
                        });
                        println!(
                            "{}",
                            serde_json::to_string_pretty(&success_response).unwrap()
                        );
                    } else {
                        println!("Successfully submitted workflow:");
                        println!("  Workflow ID: {}", selected_workflow_id);
                    }
                }
                Err(e) => {
                    if format == "json" {
                        let error_response = serde_json::json!({
                            "status": "error",
                            "message": format!("Failed to submit workflow: {}", e),
                            "workflow_id": selected_workflow_id
                        });
                        println!("{}", serde_json::to_string_pretty(&error_response).unwrap());
                    } else {
                        eprintln!("Error submitting workflow {}: {}", selected_workflow_id, e);
                    }
                    std::process::exit(1);
                }
            }
        }
        Err(e) => {
            print_error("getting workflow for submit", &e);
            std::process::exit(1);
        }
    }
}

fn handle_archive(config: &Configuration, is_archived: &str, workflow_ids: &[i64], format: &str) {
    // Parse is_archived string to bool
    let is_archived_bool = match is_archived.to_lowercase().as_str() {
        "true" | "1" | "yes" => true,
        "false" | "0" | "no" => false,
        _ => {
            eprintln!("Error: is_archived must be 'true' or 'false'");
            std::process::exit(1);
        }
    };

    let user_name = get_env_user_name();

    // If no workflow IDs provided, prompt for interactive selection
    let ids_to_update = if workflow_ids.is_empty() {
        vec![select_workflow_interactively(config, &user_name).unwrap()]
    } else {
        workflow_ids.to_vec()
    };

    let mut updated_workflows = Vec::new();
    let mut errors = Vec::new();
    let action = if is_archived_bool {
        "archive"
    } else {
        "unarchive"
    };
    let action_past = if is_archived_bool {
        "archived"
    } else {
        "unarchived"
    };

    for workflow_id in ids_to_update {
        // First, get the current workflow status
        match default_api::get_workflow_status(config, workflow_id) {
            Ok(mut status) => {
                // Set is_archived to the specified value
                status.is_archived = Some(is_archived_bool);

                // Update the workflow status
                match default_api::update_workflow_status(config, workflow_id, status) {
                    Ok(_) => {
                        updated_workflows.push(workflow_id);
                        if format != "json" {
                            println!("Successfully {} workflow {}", action_past, workflow_id);
                        }
                    }
                    Err(e) => {
                        let error_msg =
                            format!("Failed to {} workflow {}: {}", action, workflow_id, e);
                        errors.push(error_msg.clone());
                        if format != "json" {
                            eprintln!("Error: {}", error_msg);
                        }
                    }
                }
            }
            Err(e) => {
                let error_msg = format!("Failed to get status for workflow {}: {}", workflow_id, e);
                errors.push(error_msg.clone());
                if format != "json" {
                    eprintln!("Error: {}", error_msg);
                }
            }
        }
    }

    // Output JSON response if requested
    if format == "json" {
        let response = if errors.is_empty() {
            serde_json::json!({
                "status": "success",
                "updated_workflows": updated_workflows,
                "is_archived": is_archived_bool,
            })
        } else {
            serde_json::json!({
                "status": if updated_workflows.is_empty() { "error" } else { "partial_success" },
                "updated_workflows": updated_workflows,
                "is_archived": is_archived_bool,
                "errors": errors,
            })
        };
        println!("{}", serde_json::to_string_pretty(&response).unwrap());
    }

    // Exit with error if any workflow failed to update
    if !errors.is_empty() {
        std::process::exit(1);
    }
}

fn handle_delete(config: &Configuration, ids: &[i64], no_prompts: bool, force: bool, format: &str) {
    let user_name = get_env_user_name();

    // Get list of workflow IDs to delete
    let workflow_ids = if ids.is_empty() {
        // No IDs provided - select one interactively
        vec![select_workflow_interactively(config, &user_name).unwrap()]
    } else {
        ids.to_vec()
    };

    let mut deleted_workflows = Vec::new();
    let mut failed_deletions = Vec::new();

    for selected_id in workflow_ids {
        // Fetch workflow details to show what will be deleted
        let workflow = match default_api::get_workflow(config, selected_id) {
            Ok(wf) => wf,
            Err(e) => {
                failed_deletions.push((selected_id, format!("Failed to get workflow: {}", e)));
                continue;
            }
        };

        // Check if user owns the workflow
        if workflow.user != user_name && !force {
            let error_msg = format!(
                "Cannot delete workflow owned by user '{}' (you are '{}'). Use --force to override.",
                workflow.user, user_name
            );
            failed_deletions.push((selected_id, error_msg));
            continue;
        }

        // Count jobs in this workflow
        let job_count = match default_api::list_jobs(
            config,
            selected_id,
            None,    // status
            None,    // needs_file_id
            None,    // upstream_job_id
            None,    // offset
            Some(1), // limit (we just need the total count)
            None,    // sort_by
            None,    // reverse_sort
            None,    // include_relationships
            None,    // active_compute_node_id
        ) {
            Ok(response) => response.total_count,
            Err(e) => {
                failed_deletions.push((selected_id, format!("Failed to count jobs: {}", e)));
                continue;
            }
        };

        // If not skipping prompts, show what will be deleted and ask for confirmation
        if !no_prompts && format != "json" {
            println!("\nWarning: You are about to delete the following workflow:");
            println!("  ID: {}", workflow.id.unwrap_or(-1));
            println!("  Name: {}", workflow.name);
            println!("  User: {}", workflow.user);
            if let Some(desc) = &workflow.description {
                println!("  Description: {}", desc);
            }
            println!("\nThis will also delete:");
            println!("  - {} job(s)", job_count);
            println!("  - All associated files, user data, and results");
            println!("  - All job dependencies and relationships");
            println!("\nThis action cannot be undone.");
            print!("\nAre you sure you want to delete this workflow? (y/N): ");
            io::stdout().flush().unwrap();

            let mut input = String::new();
            match io::stdin().read_line(&mut input) {
                Ok(_) => {
                    let response = input.trim().to_lowercase();
                    if response != "y" && response != "yes" {
                        println!("Deletion cancelled for workflow {}.", selected_id);
                        continue;
                    }
                }
                Err(e) => {
                    failed_deletions.push((selected_id, format!("Failed to read input: {}", e)));
                    continue;
                }
            }
        }

        // Proceed with deletion
        match default_api::delete_workflow(config, selected_id, None) {
            Ok(removed_workflow) => {
                deleted_workflows.push(removed_workflow);
            }
            Err(e) => {
                failed_deletions.push((selected_id, format!("Failed to delete: {}", e)));
            }
        }
    }

    // Output results
    if format == "json" {
        // For JSON output, return array of deleted workflows
        let json_array: Vec<_> = deleted_workflows
            .iter()
            .map(|wf| {
                let mut json = serde_json::to_value(wf).unwrap();
                // Parse resource_monitor_config from JSON string to object if present
                if let Some(config_str) = &wf.resource_monitor_config
                    && let Ok(config_obj) = serde_json::from_str::<serde_json::Value>(config_str)
                {
                    json["resource_monitor_config"] = config_obj;
                }
                json
            })
            .collect();

        match serde_json::to_string_pretty(&json_array) {
            Ok(json_str) => println!("{}", json_str),
            Err(e) => {
                eprintln!("Error serializing workflows to JSON: {}", e);
                std::process::exit(1);
            }
        }
    } else {
        // For table output, show summary
        if !deleted_workflows.is_empty() {
            println!(
                "\nSuccessfully deleted {} workflow(s):",
                deleted_workflows.len()
            );
            for wf in &deleted_workflows {
                println!(
                    "  - ID: {}, Name: {}, User: {}",
                    wf.id.unwrap_or(-1),
                    wf.name,
                    wf.user
                );
            }
        }

        if !failed_deletions.is_empty() {
            eprintln!("\nFailed to delete {} workflow(s):", failed_deletions.len());
            for (id, error) in &failed_deletions {
                eprintln!("  - ID {}: {}", id, error);
            }
        }
    }

    // Exit with error if any deletions failed
    if !failed_deletions.is_empty() && deleted_workflows.is_empty() {
        std::process::exit(1);
    }
}

fn handle_update(
    config: &Configuration,
    id: &Option<i64>,
    name: &Option<String>,
    description: &Option<String>,
    owner_user: &Option<String>,
    format: &str,
) {
    let user_name = get_env_user_name();

    let selected_id = match id {
        Some(workflow_id) => *workflow_id,
        None => select_workflow_interactively(config, &user_name).unwrap(),
    };
    // First get the existing workflow
    match default_api::get_workflow(config, selected_id) {
        Ok(mut workflow) => {
            // Update fields that were provided
            if let Some(new_name) = name {
                workflow.name = new_name.clone();
            }
            if description.is_some() {
                workflow.description = description.clone();
            }
            if let Some(new_user) = owner_user {
                workflow.user = new_user.clone();
            }

            match default_api::update_workflow(config, selected_id, workflow) {
                Ok(updated_workflow) => {
                    if format == "json" {
                        // Convert workflow to JSON value, parsing resource_monitor_config if present
                        let mut json = serde_json::to_value(&updated_workflow).unwrap();

                        // Parse resource_monitor_config from JSON string to object if present
                        if let Some(config_str) = &updated_workflow.resource_monitor_config
                            && let Ok(config_obj) =
                                serde_json::from_str::<serde_json::Value>(config_str)
                        {
                            json["resource_monitor_config"] = config_obj;
                        }

                        match serde_json::to_string_pretty(&json) {
                            Ok(json_str) => println!("{}", json_str),
                            Err(e) => {
                                eprintln!("Error serializing workflow to JSON: {}", e);
                                std::process::exit(1);
                            }
                        }
                    } else {
                        println!("Successfully updated workflow:");
                        println!("  ID: {}", updated_workflow.id.unwrap_or(-1));
                        println!("  Name: {}", updated_workflow.name);
                        println!("  User: {}", updated_workflow.user);
                        if let Some(desc) = &updated_workflow.description {
                            println!("  Description: {}", desc);
                        }
                    }
                }
                Err(e) => {
                    print_error("updating workflow", &e);
                    std::process::exit(1);
                }
            }
        }
        Err(e) => {
            print_error("getting workflow for update", &e);
            std::process::exit(1);
        }
    }
}

fn handle_get(config: &Configuration, id: &Option<i64>, user: &Option<String>, format: &str) {
    let user_name = get_user_name(user);

    let selected_id = match id {
        Some(workflow_id) => *workflow_id,
        None => select_workflow_interactively(config, &user_name).unwrap(),
    };

    match default_api::get_workflow(config, selected_id) {
        Ok(workflow) => {
            if format == "json" {
                // Convert workflow to JSON value, parsing resource_monitor_config if present
                let mut json = serde_json::to_value(&workflow).unwrap();

                // Parse resource_monitor_config from JSON string to object if present
                if let Some(config_str) = &workflow.resource_monitor_config
                    && let Ok(config_obj) = serde_json::from_str::<serde_json::Value>(config_str)
                {
                    json["resource_monitor_config"] = config_obj;
                }

                match serde_json::to_string_pretty(&json) {
                    Ok(json_str) => println!("{}", json_str),
                    Err(e) => {
                        eprintln!("Error serializing workflow to JSON: {}", e);
                        std::process::exit(1);
                    }
                }
            } else {
                println!("Workflow ID {}:", selected_id);
                println!("  Name: {}", workflow.name);
                println!("  User: {}", workflow.user);
                if let Some(desc) = &workflow.description {
                    println!("  Description: {}", desc);
                }
                if let Some(timestamp) = &workflow.timestamp {
                    println!("  Timestamp: {}", timestamp);
                }
            }
        }
        Err(e) => {
            print_error("getting workflow", &e);
            std::process::exit(1);
        }
    }
}

#[allow(clippy::too_many_arguments)]
fn handle_list(
    config: &Configuration,
    user: &Option<String>,
    all_users: bool,
    limit: i64,
    offset: i64,
    sort_by: &Option<String>,
    reverse_sort: bool,
    archived_only: bool,
    include_archived: bool,
    format: &str,
) {
    // Use pagination utility to get all workflows
    let mut params = WorkflowListParams::new()
        .with_offset(offset)
        .with_limit(limit)
        .with_reverse_sort(reverse_sort);

    // Handle archive filtering:
    // - include_archived: show both archived and non-archived (is_archived = None)
    // - archived_only: show only archived (is_archived = Some(true))
    // - default: show only non-archived (is_archived = Some(false))
    if !include_archived {
        params = params.with_is_archived(archived_only);
    }

    // Set user filter based on --all-users flag
    if !all_users {
        let user_filter = user
            .clone()
            .unwrap_or_else(|| std::env::var("USER").unwrap_or_else(|_| "unknown".to_string()));
        params = params.with_user(user_filter);
    }
    // If all_users is true, user filter remains None (showing all users)

    if let Some(sort_field) = sort_by {
        params = params.with_sort_by(sort_field.clone());
    }

    match paginate_workflows(config, params) {
        Ok(workflows) => {
            if format == "json" {
                // Convert workflows to JSON values, parsing resource_monitor_config if present
                let workflows_json: Vec<serde_json::Value> = workflows
                    .iter()
                    .map(|workflow| {
                        let mut json = serde_json::to_value(workflow).unwrap();

                        // Parse resource_monitor_config from JSON string to object if present
                        if let Some(config_str) = &workflow.resource_monitor_config
                            && let Ok(config_obj) =
                                serde_json::from_str::<serde_json::Value>(config_str)
                        {
                            json["resource_monitor_config"] = config_obj;
                        }

                        json
                    })
                    .collect();

                match serde_json::to_string_pretty(&workflows_json) {
                    Ok(json) => println!("{}", json),
                    Err(e) => {
                        eprintln!("Error serializing workflows to JSON: {}", e);
                        std::process::exit(1);
                    }
                }
            } else if workflows.is_empty() {
                if all_users {
                    println!("No workflows found for any user");
                } else {
                    let display_user = user.clone().unwrap_or_else(|| {
                        std::env::var("USER").unwrap_or_else(|_| "unknown".to_string())
                    });
                    println!("No workflows found for user: {}", display_user);
                }
            } else if all_users {
                println!("Workflows for all users:");
                let rows: Vec<WorkflowTableRow> = workflows
                    .iter()
                    .map(|workflow| WorkflowTableRow {
                        id: workflow.id.unwrap_or(-1),
                        name: workflow.name.clone(),
                        description: workflow.description.as_deref().unwrap_or("").to_string(),
                        user: workflow.user.clone(),
                        timestamp: workflow.timestamp.as_deref().unwrap_or("").to_string(),
                    })
                    .collect();
                display_table_with_count(&rows, "workflows");
            } else {
                let display_user = user.clone().unwrap_or_else(|| {
                    std::env::var("USER").unwrap_or_else(|_| "unknown".to_string())
                });
                println!("Workflows for user {}:", display_user);
                let rows: Vec<WorkflowTableRowNoUser> = workflows
                    .iter()
                    .map(|workflow| WorkflowTableRowNoUser {
                        id: workflow.id.unwrap_or(-1),
                        name: workflow.name.clone(),
                        description: workflow.description.as_deref().unwrap_or("").to_string(),
                        timestamp: workflow.timestamp.as_deref().unwrap_or("").to_string(),
                    })
                    .collect();
                display_table_with_count(&rows, "workflows");
            }
        }
        Err(e) => {
            print_error("listing workflows", &e);
            std::process::exit(1);
        }
    }
}

fn handle_new(
    config: &Configuration,
    name: &str,
    description: &Option<String>,
    user: &str,
    format: &str,
) {
    let mut workflow = models::WorkflowModel::new(name.to_string(), user.to_string());
    workflow.description = description.clone();

    match default_api::create_workflow(config, workflow) {
        Ok(created_workflow) => {
            if format == "json" {
                // Convert workflow to JSON value, parsing resource_monitor_config if present
                let mut json = serde_json::to_value(&created_workflow).unwrap();

                // Parse resource_monitor_config from JSON string to object if present
                if let Some(config_str) = &created_workflow.resource_monitor_config
                    && let Ok(config_obj) = serde_json::from_str::<serde_json::Value>(config_str)
                {
                    json["resource_monitor_config"] = config_obj;
                }

                match serde_json::to_string_pretty(&json) {
                    Ok(json_str) => println!("{}", json_str),
                    Err(e) => {
                        eprintln!("Error serializing workflow to JSON: {}", e);
                        std::process::exit(1);
                    }
                }
            } else {
                println!("Successfully created workflow:");
                println!("  ID: {}", created_workflow.id.unwrap_or(-1));
                println!("  Name: {}", created_workflow.name);
                println!("  User: {}", created_workflow.user);
                if let Some(desc) = created_workflow.description {
                    println!("  Description: {}", desc);
                }
            }
        }
        Err(e) => {
            print_error("creating workflow", &e);
            std::process::exit(1);
        }
    }
}

fn handle_create(
    config: &Configuration,
    file: &str,
    user: &str,
    no_resource_monitoring: bool,
    skip_checks: bool,
    dry_run: bool,
    format: &str,
) {
    // Handle dry-run mode
    if dry_run {
        let result = WorkflowSpec::validate_spec(file);

        if format == "json" {
            match serde_json::to_string_pretty(&result) {
                Ok(json) => println!("{}", json),
                Err(e) => {
                    eprintln!("Error serializing validation result: {}", e);
                    std::process::exit(1);
                }
            }
        } else {
            // Human-readable output
            println!("Workflow Validation Results");
            println!("===========================");
            println!();

            let summary = &result.summary;
            println!("Workflow: {}", summary.workflow_name);
            if let Some(ref desc) = summary.workflow_description {
                println!("Description: {}", desc);
            }
            println!();

            // Show what would be created
            println!("Components to be created:");
            if summary.job_count != summary.job_count_before_expansion {
                println!(
                    "  Jobs: {} (expanded from {} parameterized job specs)",
                    summary.job_count, summary.job_count_before_expansion
                );
            } else {
                println!("  Jobs: {}", summary.job_count);
            }
            if summary.file_count != summary.file_count_before_expansion {
                println!(
                    "  Files: {} (expanded from {} parameterized file specs)",
                    summary.file_count, summary.file_count_before_expansion
                );
            } else {
                println!("  Files: {}", summary.file_count);
            }
            println!("  User data records: {}", summary.user_data_count);
            println!(
                "  Resource requirements: {}",
                summary.resource_requirements_count
            );
            println!("  Slurm schedulers: {}", summary.slurm_scheduler_count);
            println!("  Workflow actions: {}", summary.action_count);
            println!();

            if summary.has_schedule_nodes_action {
                println!(
                    "Submission: Ready for scheduler submission (has on_workflow_start schedule_nodes action)"
                );
            } else {
                println!(
                    "Submission: Local execution only (no on_workflow_start schedule_nodes action)"
                );
            }
            println!();

            // Show errors
            if !result.errors.is_empty() {
                eprintln!("Errors ({}):", result.errors.len());
                for error in &result.errors {
                    eprintln!("  - {}", error);
                }
                eprintln!();
            }

            // Show warnings
            if !result.warnings.is_empty() {
                eprintln!("Warnings ({}):", result.warnings.len());
                for warning in &result.warnings {
                    eprintln!("  - {}", warning);
                }
                eprintln!();
            }

            // Final verdict
            if result.valid {
                if result.warnings.is_empty() {
                    println!("Validation: PASSED");
                } else {
                    println!(
                        "Validation: PASSED (with {} warning(s))",
                        result.warnings.len()
                    );
                }
            } else {
                eprintln!("Validation: FAILED");
            }
        }

        // Exit with appropriate code
        if !result.valid {
            std::process::exit(1);
        }
        return;
    }

    // Normal create mode
    match WorkflowSpec::create_workflow_from_spec(
        config,
        file,
        user,
        !no_resource_monitoring,
        skip_checks,
    ) {
        Ok(workflow_id) => {
            if format == "json" {
                let json_output = serde_json::json!({
                    "workflow_id": workflow_id,
                    "status": "success",
                    "message": format!("Workflow created successfully with ID: {}", workflow_id)
                });
                match serde_json::to_string_pretty(&json_output) {
                    Ok(json) => println!("{}", json),
                    Err(e) => {
                        eprintln!("Error serializing JSON: {}", e);
                        std::process::exit(1);
                    }
                }
            } else {
                println!("Created workflow {}", workflow_id);
            }
        }
        Err(e) => {
            eprintln!("Error creating workflow from spec: {}", e);
            std::process::exit(1);
        }
    }
}

#[allow(clippy::too_many_arguments)]
fn handle_create_slurm(
    config: &Configuration,
    file: &str,
    account: &str,
    hpc_profile: Option<&str>,
    single_allocation: bool,
    user: &str,
    no_resource_monitoring: bool,
    skip_checks: bool,
    dry_run: bool,
    format: &str,
) {
    // Handle dry-run mode first
    if dry_run {
        let result = WorkflowSpec::validate_spec(file);
        if format == "json" {
            match serde_json::to_string_pretty(&result) {
                Ok(json) => println!("{}", json),
                Err(e) => {
                    eprintln!("Error serializing validation result: {}", e);
                    std::process::exit(1);
                }
            }
        } else {
            println!("Workflow Validation Results (with Slurm scheduler generation)");
            println!("==============================================================");
            println!();
            println!("Note: Dry-run validates the spec before scheduler generation.");
            println!("Use 'torc slurm generate' to preview generated schedulers.");
            println!();

            let summary = &result.summary;
            println!("Workflow: {}", summary.workflow_name);
            println!("Jobs: {}", summary.job_count);
            println!(
                "Resource requirements: {}",
                summary.resource_requirements_count
            );
            println!();

            if !result.errors.is_empty() {
                eprintln!("Errors ({}):", result.errors.len());
                for error in &result.errors {
                    eprintln!("  - {}", error);
                }
            }

            if result.valid {
                println!("Validation: PASSED");
            } else {
                eprintln!("Validation: FAILED");
            }
        }

        if !result.valid {
            std::process::exit(1);
        }
        return;
    }

    // Load HPC config and registry
    let torc_config = TorcConfig::load().unwrap_or_default();
    let registry = create_registry_with_config_public(&torc_config.client.hpc);

    // Get the HPC profile
    let profile = if let Some(name) = hpc_profile {
        registry.get(name)
    } else {
        registry.detect()
    };

    let profile = match profile {
        Some(p) => p,
        None => {
            if hpc_profile.is_some() {
                eprintln!("Unknown HPC profile: {}", hpc_profile.unwrap());
            } else {
                eprintln!("No HPC profile specified and no system detected.");
                eprintln!("Use --hpc-profile <name> to specify a profile.");
            }
            std::process::exit(1);
        }
    };

    // Parse the workflow spec
    let mut spec = match WorkflowSpec::from_spec_file(file) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("Failed to parse workflow file: {}", e);
            std::process::exit(1);
        }
    };

    // Generate schedulers
    // Don't allow force=true - if schedulers already exist, user should use the _no_slurm variant
    match generate_schedulers_for_workflow(
        &mut spec,
        profile,
        account,
        single_allocation,
        true,
        false,
    ) {
        Ok(result) => {
            if format != "json" {
                eprintln!(
                    "Auto-generated {} scheduler(s) and {} action(s) using {} profile",
                    result.scheduler_count, result.action_count, profile.name
                );
                for warning in &result.warnings {
                    eprintln!("  Warning: {}", warning);
                }
            }
        }
        Err(e) => {
            eprintln!("Error generating schedulers: {}", e);
            std::process::exit(1);
        }
    }

    // Write modified spec to temp file
    let temp_dir = std::env::temp_dir();
    let temp_file = temp_dir.join(format!("torc_workflow_{}.yaml", std::process::id()));
    match std::fs::write(&temp_file, serde_yaml::to_string(&spec).unwrap()) {
        Ok(_) => {}
        Err(e) => {
            eprintln!("Failed to write temporary workflow file: {}", e);
            std::process::exit(1);
        }
    }

    // Create workflow from modified spec
    match WorkflowSpec::create_workflow_from_spec(
        config,
        &temp_file,
        user,
        !no_resource_monitoring,
        skip_checks,
    ) {
        Ok(workflow_id) => {
            if format == "json" {
                let json_output = serde_json::json!({
                    "workflow_id": workflow_id,
                    "status": "success",
                    "message": format!("Workflow created successfully with ID: {}", workflow_id)
                });
                match serde_json::to_string_pretty(&json_output) {
                    Ok(json) => println!("{}", json),
                    Err(e) => {
                        eprintln!("Error serializing JSON: {}", e);
                        std::process::exit(1);
                    }
                }
            } else {
                println!("Created workflow {}", workflow_id);
            }
        }
        Err(e) => {
            eprintln!("Error creating workflow from spec: {}", e);
            std::process::exit(1);
        }
    }
}

fn handle_is_complete(config: &Configuration, id: Option<i64>, format: &str) {
    // Get or select workflow ID
    let user = get_env_user_name();
    let id = match id {
        Some(id) => id,
        None => match select_workflow_interactively(config, &user) {
            Ok(id) => id,
            Err(e) => {
                eprintln!("Error selecting workflow: {}", e);
                std::process::exit(1);
            }
        },
    };

    match default_api::is_workflow_complete(config, id) {
        Ok(response) => {
            if format == "json" {
                match serde_json::to_string_pretty(&response) {
                    Ok(json) => println!("{}", json),
                    Err(e) => {
                        eprintln!("Error serializing response to JSON: {}", e);
                        std::process::exit(1);
                    }
                }
            } else {
                println!("Workflow {} completion status:", id);
                println!("  Is Complete: {}", response.is_complete);
                println!("  Is Canceled: {}", response.is_canceled);
            }
        }
        Err(e) => {
            print_error("checking workflow completion", &e);
            std::process::exit(1);
        }
    }
}

pub fn handle_workflow_commands(config: &Configuration, command: &WorkflowCommands, format: &str) {
    match command {
        WorkflowCommands::Create {
            file,
            user,
            no_resource_monitoring,
            skip_checks,
            dry_run,
        } => {
            handle_create(
                config,
                file,
                user,
                *no_resource_monitoring,
                *skip_checks,
                *dry_run,
                format,
            );
        }
        WorkflowCommands::CreateSlurm {
            file,
            account,
            hpc_profile,
            single_allocation,
            user,
            no_resource_monitoring,
            skip_checks,
            dry_run,
        } => {
            handle_create_slurm(
                config,
                file,
                account,
                hpc_profile.as_deref(),
                *single_allocation,
                user,
                *no_resource_monitoring,
                *skip_checks,
                *dry_run,
                format,
            );
        }
        WorkflowCommands::New {
            name,
            description,
            user,
        } => {
            handle_new(config, name, description, user, format);
        }
        WorkflowCommands::List {
            user,
            all_users,
            limit,
            offset,
            sort_by,
            reverse_sort,
            archived_only,
            include_archived,
        } => {
            handle_list(
                config,
                user,
                *all_users,
                *limit,
                *offset,
                sort_by,
                *reverse_sort,
                *archived_only,
                *include_archived,
                format,
            );
        }
        WorkflowCommands::Get { id, user } => {
            handle_get(config, id, user, format);
        }
        WorkflowCommands::Update {
            id,
            name,
            description,
            owner_user,
        } => {
            handle_update(config, id, name, description, owner_user, format);
        }
        WorkflowCommands::Delete {
            ids,
            no_prompts,
            force,
        } => {
            handle_delete(config, ids, *no_prompts, *force, format);
        }
        WorkflowCommands::Archive {
            is_archived,
            workflow_ids,
        } => {
            handle_archive(config, is_archived, workflow_ids, format);
        }
        WorkflowCommands::Submit { workflow_id, force } => {
            handle_submit(config, workflow_id, *force, format);
        }
        WorkflowCommands::Run {
            workflow_id,
            poll_interval,
            max_parallel_jobs,
            output_dir,
        } => {
            handle_run(
                config,
                workflow_id,
                *poll_interval,
                *max_parallel_jobs,
                output_dir,
            );
        }
        WorkflowCommands::Initialize {
            workflow_id,
            force,
            no_prompts,
            dry_run,
        } => {
            handle_initialize(config, workflow_id, *force, *no_prompts, *dry_run, format);
        }
        WorkflowCommands::Reinitialize {
            workflow_id,
            force,
            dry_run,
        } => {
            handle_reinitialize(config, workflow_id, *force, *dry_run, format);
        }
        WorkflowCommands::Status { workflow_id, user } => {
            handle_status(config, workflow_id, user, format);
        }
        WorkflowCommands::ResetStatus {
            workflow_id,
            failed_only,
            reinitialize,
            force,
            no_prompts,
        } => {
            handle_reset_status(
                config,
                workflow_id,
                *failed_only,
                *reinitialize,
                *force,
                *no_prompts,
                format,
            );
        }
        WorkflowCommands::Cancel { workflow_id } => {
            handle_cancel(config, workflow_id, format);
        }
        WorkflowCommands::ExecutionPlan { spec_or_id } => {
            handle_execution_plan(config, spec_or_id, format);
        }
        WorkflowCommands::ListActions { workflow_id, user } => {
            handle_list_actions(config, workflow_id, user, format);
        }
        WorkflowCommands::IsComplete { id } => {
            handle_is_complete(config, *id, format);
        }
    }
}
