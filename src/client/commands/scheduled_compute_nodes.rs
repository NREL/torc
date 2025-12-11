use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::commands::get_env_user_name;
use crate::client::commands::{
    print_error, select_workflow_interactively, table_format::display_table_with_count,
};
use crate::models;
use serde_json;
use tabled::Tabled;

#[derive(Tabled)]
struct ScheduledComputeNodeTableRow {
    #[tabled(rename = "ID")]
    id: i64,
    #[tabled(rename = "Scheduler ID")]
    scheduler_id: i64,
    #[tabled(rename = "Config ID")]
    scheduler_config_id: i64,
    #[tabled(rename = "Type")]
    scheduler_type: String,
    #[tabled(rename = "Status")]
    status: String,
}

impl From<&models::ScheduledComputeNodesModel> for ScheduledComputeNodeTableRow {
    fn from(node: &models::ScheduledComputeNodesModel) -> Self {
        ScheduledComputeNodeTableRow {
            id: node.id.unwrap_or(-1),
            scheduler_id: node.scheduler_id,
            scheduler_config_id: node.scheduler_config_id,
            scheduler_type: node.scheduler_type.clone(),
            status: node.status.clone(),
        }
    }
}

#[derive(clap::Subcommand)]
pub enum ScheduledComputeNodeCommands {
    /// List scheduled compute nodes for a workflow
    List {
        /// List scheduled compute nodes for this workflow (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// Maximum number of scheduled compute nodes to return
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
        /// Filter by scheduler ID
        #[arg(long)]
        scheduler_id: Option<String>,
        /// Filter by scheduler config ID
        #[arg(long)]
        scheduler_config_id: Option<String>,
        /// Filter by status
        #[arg(long)]
        status: Option<String>,
    },
}

pub fn handle_scheduled_compute_node_commands(
    config: &Configuration,
    command: &ScheduledComputeNodeCommands,
    format: &str,
) {
    match command {
        ScheduledComputeNodeCommands::List {
            workflow_id,
            limit,
            offset,
            sort_by,
            reverse_sort,
            scheduler_id,
            scheduler_config_id,
            status,
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

            match default_api::list_scheduled_compute_nodes(
                config,
                selected_workflow_id,
                Some(*offset),
                Some(*limit),
                sort_by.as_deref(),
                Some(*reverse_sort),
                scheduler_id.as_deref(),
                scheduler_config_id.as_deref(),
                status.as_deref(),
            ) {
                Ok(response) => {
                    let nodes = response.items.unwrap_or_default();

                    if format == "json" {
                        let json_output = serde_json::json!({
                            "items": nodes,
                            "total_count": response.total_count,
                        });
                        match serde_json::to_string_pretty(&json_output) {
                            Ok(json) => println!("{}", json),
                            Err(e) => {
                                eprintln!(
                                    "Error serializing scheduled compute nodes to JSON: {}",
                                    e
                                );
                                std::process::exit(1);
                            }
                        }
                    } else {
                        if nodes.is_empty() {
                            println!(
                                "No scheduled compute nodes found for workflow {}",
                                selected_workflow_id
                            );
                        } else {
                            let rows: Vec<ScheduledComputeNodeTableRow> =
                                nodes.iter().map(|n| n.into()).collect();
                            display_table_with_count(&rows, "scheduled compute nodes");
                            if response.total_count as usize > nodes.len() {
                                println!(
                                    "\nShowing {} of {} total scheduled compute nodes",
                                    nodes.len(),
                                    response.total_count
                                );
                            }
                        }
                    }
                }
                Err(e) => {
                    print_error("listing scheduled compute nodes", &e);
                    std::process::exit(1);
                }
            }
        }
    }
}
