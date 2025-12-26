use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::commands::get_env_user_name;
use crate::client::commands::output::{print_if_json, print_json};
use crate::client::commands::{
    print_error, select_workflow_interactively, table_format::display_table_with_count,
};
use crate::models;
use tabled::Tabled;

#[derive(Tabled)]
struct ComputeNodeTableRow {
    #[tabled(rename = "ID")]
    id: i64,
    #[tabled(rename = "Hostname")]
    hostname: String,
    #[tabled(rename = "PID")]
    pid: i64,
    #[tabled(rename = "CPUs")]
    num_cpus: i64,
    #[tabled(rename = "Memory (GB)")]
    memory_gb: String,
    #[tabled(rename = "GPUs")]
    num_gpus: i64,
    #[tabled(rename = "Active")]
    is_active: String,
    #[tabled(rename = "Start Time")]
    start_time: String,
    #[tabled(rename = "Duration")]
    duration: String,
}

impl From<&models::ComputeNodeModel> for ComputeNodeTableRow {
    fn from(node: &models::ComputeNodeModel) -> Self {
        let duration = match node.duration_seconds {
            Some(d) => format!("{:.1}s", d),
            None => "-".to_string(),
        };

        let is_active = match node.is_active {
            Some(true) => "Yes".to_string(),
            Some(false) => "No".to_string(),
            None => "-".to_string(),
        };

        ComputeNodeTableRow {
            id: node.id.unwrap_or(-1),
            hostname: node.hostname.clone(),
            pid: node.pid,
            num_cpus: node.num_cpus,
            memory_gb: format!("{:.2}", node.memory_gb),
            num_gpus: node.num_gpus,
            is_active,
            start_time: node.start_time.clone(),
            duration,
        }
    }
}

#[derive(clap::Subcommand)]
pub enum ComputeNodeCommands {
    /// Get a specific compute node by ID
    Get {
        /// ID of the compute node
        #[arg()]
        id: i64,
    },
    /// List compute nodes for a workflow
    List {
        /// List compute nodes for this workflow (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// Maximum number of compute nodes to return
        #[arg(short, long, default_value = "10000")]
        limit: i64,
        /// Offset for pagination (0-based)
        #[arg(short, long, default_value = "0")]
        offset: i64,
        /// Field to sort by
        #[arg(short, long)]
        sort_by: Option<String>,
        /// Reverse sort order
        #[arg(short, long, default_value = "false")]
        reverse_sort: bool,
        /// Filter by scheduled compute node ID
        #[arg(long)]
        scheduled_compute_node: Option<i64>,
    },
}

pub fn handle_compute_node_commands(
    config: &Configuration,
    command: &ComputeNodeCommands,
    format: &str,
) {
    match command {
        ComputeNodeCommands::Get { id } => match default_api::get_compute_node(config, *id) {
            Ok(node) => {
                if print_if_json(format, &node, "compute node") {
                    // JSON was printed
                } else {
                    println!("Compute Node Details:");
                    println!("  ID: {}", node.id.unwrap_or(-1));
                    println!("  Workflow ID: {}", node.workflow_id);
                    println!("  Hostname: {}", node.hostname);
                    println!("  PID: {}", node.pid);
                    println!("  CPUs: {}", node.num_cpus);
                    println!("  Memory: {:.2} GB", node.memory_gb);
                    println!("  GPUs: {}", node.num_gpus);
                    println!(
                        "  Active: {}",
                        match node.is_active {
                            Some(true) => "Yes",
                            Some(false) => "No",
                            None => "Unknown",
                        }
                    );
                    println!("  Start Time: {}", node.start_time);
                    if let Some(duration) = node.duration_seconds {
                        println!("  Duration: {:.2} seconds", duration);
                    }
                }
            }
            Err(e) => {
                print_error("getting compute node", &e);
                std::process::exit(1);
            }
        },
        ComputeNodeCommands::List {
            workflow_id,
            limit,
            offset,
            sort_by,
            reverse_sort,
            scheduled_compute_node,
        } => {
            let user_name = get_env_user_name();
            let selected_workflow_id = match workflow_id {
                Some(id) => *id,
                None => match select_workflow_interactively(config, &user_name) {
                    Ok(id) => id,
                    Err(e) => {
                        eprintln!("Error selecting workflow: {}", e);
                        std::process::exit(1);
                    }
                },
            };

            match default_api::list_compute_nodes(
                config,
                selected_workflow_id,
                Some(*offset),
                Some(*limit),
                sort_by.as_deref(),
                Some(*reverse_sort),
                None, // hostname filter
                None, // is_active filter
                *scheduled_compute_node,
            ) {
                Ok(response) => {
                    let nodes = response.items.unwrap_or_default();

                    if format == "json" {
                        let json_output = serde_json::json!({
                            "items": nodes,
                            "total_count": response.total_count,
                        });
                        print_json(&json_output, "compute nodes");
                    } else if nodes.is_empty() {
                        println!(
                            "No compute nodes found for workflow {}",
                            selected_workflow_id
                        );
                    } else {
                        let rows: Vec<ComputeNodeTableRow> =
                            nodes.iter().map(|n| n.into()).collect();
                        display_table_with_count(&rows, "compute nodes");
                        if response.total_count as usize > nodes.len() {
                            println!(
                                "\nShowing {} of {} total compute nodes",
                                nodes.len(),
                                response.total_count
                            );
                        }
                    }
                }
                Err(e) => {
                    print_error("listing compute nodes", &e);
                    std::process::exit(1);
                }
            }
        }
    }
}
