use chrono::Utc;
use clap::Subcommand;
use log::{error, info, warn};
use serde_json;
use std::collections::HashMap;
use std::path::Path;

use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::commands::get_env_user_name;
use crate::client::commands::{
    print_error, select_workflow_interactively, table_format::display_table_with_count,
};
use crate::client::hpc::hpc_interface::HpcInterface;
use crate::client::workflow_manager::WorkflowManager;
use crate::models;
use tabled::Tabled;

#[derive(Tabled)]
struct SlurmSchedulerTableRow {
    #[tabled(rename = "ID")]
    id: i64,
    #[tabled(rename = "Name")]
    name: String,
    #[tabled(rename = "Account")]
    account: String,
    #[tabled(rename = "Nodes")]
    nodes: i64,
    #[tabled(rename = "Walltime")]
    walltime: String,
    #[tabled(rename = "Partition")]
    partition: String,
    #[tabled(rename = "QOS")]
    qos: String,
}

/// Select a Slurm scheduler interactively from available schedulers for a workflow
fn select_slurm_scheduler_interactively(
    config: &Configuration,
    workflow_id: i64,
) -> Result<i64, Box<dyn std::error::Error>> {
    match default_api::list_slurm_schedulers(
        config,
        workflow_id,
        Some(0),  // offset
        Some(50), // limit
        None,     // sort_by
        None,     // reverse_sort
        None,     // name filter
        None,     // account filter
        None,     // gres filter
        None,     // mem filter
        None,     // nodes filter
        None,     // partition filter
        None,     // qos filter
        None,     // tmp filter
        None,     // walltime filter
    ) {
        Ok(response) => {
            let schedulers = response.items.unwrap_or_default();
            if schedulers.is_empty() {
                eprintln!("No Slurm schedulers found for workflow: {}", workflow_id);
                std::process::exit(1);
            }

            if schedulers.len() == 1 {
                let scheduler_id = schedulers[0].id.unwrap_or(-1);
                return Ok(scheduler_id);
            }

            eprintln!("Available Slurm schedulers:");
            eprintln!(
                "{:<5} {:<20} {:<15} {:<8} {:<12}",
                "ID", "Name", "Account", "Nodes", "Walltime"
            );
            eprintln!("{}", "-".repeat(70));
            for scheduler in schedulers.iter() {
                eprintln!(
                    "{:<5} {:<20} {:<15} {:<8} {:<12}",
                    scheduler.id.unwrap_or(-1),
                    scheduler.name.as_deref().unwrap_or(""),
                    &scheduler.account,
                    scheduler.nodes,
                    &scheduler.walltime
                );
            }

            eprintln!("\nEnter scheduler ID: ");
            use std::io::{self, Write};
            io::stdout().flush().unwrap();
            let mut input = String::new();
            match io::stdin().read_line(&mut input) {
                Ok(_) => match input.trim().parse::<i64>() {
                    Ok(id) => {
                        if schedulers.iter().any(|s| s.id == Some(id)) {
                            Ok(id)
                        } else {
                            eprintln!("Invalid scheduler ID: {}", id);
                            std::process::exit(1);
                        }
                    }
                    Err(_) => {
                        eprintln!("Invalid input. Please enter a numeric scheduler ID.");
                        std::process::exit(1);
                    }
                },
                Err(e) => {
                    eprintln!("Failed to read input: {}", e);
                    std::process::exit(1);
                }
            }
        }
        Err(e) => {
            print_error("listing Slurm schedulers", &e);
            std::process::exit(1);
        }
    }
}

#[derive(Subcommand)]
pub enum SlurmCommands {
    /// Add a Slurm config to the database
    Create {
        /// Workflow ID
        #[arg()]
        workflow_id: Option<i64>,
        /// Name of config
        #[arg(short, long, required = true)]
        name: String,
        /// HPC account
        #[arg(short, long, required = true)]
        account: String,
        /// Request nodes that have at least this number of GPUs. Ex: 'gpu:2'
        #[arg(short, long)]
        gres: Option<String>,
        /// Request nodes that have at least this amount of memory. Ex: '180G'
        #[arg(short, long)]
        mem: Option<String>,
        /// Number of nodes to use for each job
        #[arg(short = 'N', long, default_value = "1")]
        nodes: i64,
        /// HPC partition. Default is determined by the scheduler
        #[arg(short, long)]
        partition: Option<String>,
        /// Controls priority of the jobs
        #[arg(short, long, default_value = "normal")]
        qos: String,
        /// Request nodes that have at least this amount of storage scratch space
        #[arg(short, long)]
        tmp: Option<String>,
        /// Slurm job walltime
        #[arg(short = 'W', long, default_value = "04:00:00")]
        walltime: String,
        /// Add extra Slurm parameters, for example --extra='--reservation=my-reservation'
        #[arg(short, long)]
        extra: Option<String>,
    },
    /// Modify a Slurm config in the database
    Update {
        #[arg()]
        scheduler_id: i64,
        /// Name of config
        #[arg(short = 'N', long)]
        name: Option<String>,
        /// HPC account
        #[arg(short, long)]
        account: Option<String>,
        /// Request nodes that have at least this number of GPUs. Ex: 'gpu:2'
        #[arg(short, long)]
        gres: Option<String>,
        /// Request nodes that have at least this amount of memory. Ex: '180G'
        #[arg(short, long)]
        mem: Option<String>,
        /// Number of nodes to use for each job
        #[arg(short, long)]
        nodes: Option<i64>,
        /// HPC partition
        #[arg(short, long)]
        partition: Option<String>,
        /// Controls priority of the jobs
        #[arg(short, long)]
        qos: Option<String>,
        /// Request nodes that have at least this amount of storage scratch space
        #[arg(short, long)]
        tmp: Option<String>,
        /// Slurm job walltime
        #[arg(long)]
        walltime: Option<String>,
        /// Add extra Slurm parameters
        #[arg(short, long)]
        extra: Option<String>,
    },
    /// Show the current Slurm configs in the database
    List {
        /// Workflow ID
        #[arg()]
        workflow_id: Option<i64>,
        /// Maximum number of configs to return
        #[arg(short, long, default_value = "10000")]
        limit: i64,
        /// Offset for pagination (0-based)
        #[arg(long, default_value = "0")]
        offset: i64,
    },
    /// Get a specific Slurm config by ID
    Get {
        /// ID of the Slurm config to get
        #[arg()]
        id: i64,
    },
    /// Delete a Slurm config by ID
    Delete {
        /// ID of the Slurm config to delete
        #[arg()]
        id: i64,
    },
    /// Schedule compute nodes using Slurm
    ScheduleNodes {
        /// Workflow ID
        #[arg()]
        workflow_id: Option<i64>,
        /// Job prefix for the Slurm job names
        #[arg(short, long, default_value = "worker")]
        job_prefix: String,
        /// Keep submission scripts after job submission
        #[arg(long, default_value = "false")]
        keep_submission_scripts: bool,
        /// Maximum number of parallel jobs
        #[arg(short, long)]
        max_parallel_jobs: Option<i32>,
        /// Number of HPC jobs to submit
        #[arg(short, long, default_value = "1")]
        num_hpc_jobs: i32,
        /// Output directory for job output files
        #[arg(short, long, default_value = "output")]
        output: String,
        /// Poll interval in seconds
        #[arg(short, long, default_value = "60")]
        poll_interval: i32,
        /// Scheduler config ID
        #[arg(long)]
        scheduler_config_id: Option<i64>,
        /// Start one worker per node
        #[arg(long, default_value = "false")]
        start_one_worker_per_node: bool,
        /// Start torc-server on the head node of the allocation
        #[arg(long, default_value = "false")]
        start_server_on_head_node: bool,
    },
}

pub fn handle_slurm_commands(config: &Configuration, command: &SlurmCommands, format: &str) {
    match command {
        SlurmCommands::Create {
            workflow_id,
            name,
            account,
            gres,
            mem,
            nodes,
            partition,
            qos,
            tmp,
            walltime,
            extra,
        } => {
            let user_name = get_env_user_name();
            let wf_id = workflow_id.unwrap_or_else(|| {
                select_workflow_interactively(config, &user_name).unwrap_or_else(|e| {
                    eprintln!("Error selecting workflow: {}", e);
                    std::process::exit(1);
                })
            });

            let scheduler = models::SlurmSchedulerModel {
                id: None,
                workflow_id: wf_id,
                name: Some(name.clone()),
                account: account.clone(),
                gres: gres.clone(),
                mem: mem.clone(),
                nodes: *nodes,
                ntasks_per_node: None,
                partition: partition.clone(),
                qos: Some(qos.clone()),
                tmp: tmp.clone(),
                walltime: walltime.clone(),
                extra: extra.clone(),
            };

            match default_api::create_slurm_scheduler(config, scheduler) {
                Ok(created) => {
                    if format == "json" {
                        println!("{}", serde_json::to_string_pretty(&created).unwrap());
                    } else {
                        eprintln!(
                            "Added Slurm configuration '{}' (ID: {}) to workflow {}",
                            name,
                            created.id.unwrap_or(-1),
                            wf_id
                        );
                    }
                }
                Err(e) => {
                    print_error("creating Slurm scheduler", &e);
                    std::process::exit(1);
                }
            }
        }
        SlurmCommands::Update {
            scheduler_id,
            name,
            account,
            gres,
            mem,
            nodes,
            partition,
            qos,
            tmp,
            walltime,
            extra,
        } => {
            let mut scheduler = match default_api::get_slurm_scheduler(config, *scheduler_id) {
                Ok(s) => s,
                Err(e) => {
                    print_error("getting Slurm scheduler", &e);
                    std::process::exit(1);
                }
            };

            // Update fields if provided
            let mut changed = false;
            if let Some(n) = name {
                scheduler.name = Some(n.clone());
                changed = true;
            }
            if let Some(a) = account {
                scheduler.account = a.clone();
                changed = true;
            }
            if let Some(g) = gres {
                scheduler.gres = Some(g.clone());
                changed = true;
            }
            if let Some(m) = mem {
                scheduler.mem = Some(m.clone());
                changed = true;
            }
            if let Some(n) = nodes {
                scheduler.nodes = *n;
                changed = true;
            }
            if let Some(p) = partition {
                scheduler.partition = Some(p.clone());
                changed = true;
            }
            if let Some(q) = qos {
                scheduler.qos = Some(q.clone());
                changed = true;
            }
            if let Some(t) = tmp {
                scheduler.tmp = Some(t.clone());
                changed = true;
            }
            if let Some(w) = walltime {
                scheduler.walltime = w.clone();
                changed = true;
            }
            if let Some(e) = extra {
                scheduler.extra = Some(e.clone());
                changed = true;
            }

            if !changed {
                warn!("No changes requested");
                return;
            }

            match default_api::update_slurm_scheduler(config, *scheduler_id, scheduler) {
                Ok(updated) => {
                    if format == "json" {
                        println!("{}", serde_json::to_string_pretty(&updated).unwrap());
                    } else {
                        eprintln!("Updated Slurm configuration {}", scheduler_id);
                    }
                }
                Err(e) => {
                    print_error("updating Slurm scheduler", &e);
                    std::process::exit(1);
                }
            }
        }
        SlurmCommands::List {
            workflow_id,
            limit,
            offset,
        } => {
            let user_name = get_env_user_name();
            let wf_id = workflow_id.unwrap_or_else(|| {
                select_workflow_interactively(config, &user_name).unwrap_or_else(|e| {
                    eprintln!("Error selecting workflow: {}", e);
                    std::process::exit(1);
                })
            });

            match default_api::list_slurm_schedulers(
                config,
                wf_id,
                Some(*offset),
                Some(*limit),
                None, // sort_by
                None, // reverse_sort
                None, // name filter
                None, // account filter
                None, // gres filter
                None, // mem filter
                None, // nodes filter
                None, // partition filter
                None, // qos filter
                None, // tmp filter
                None, // walltime filter
            ) {
                Ok(response) => {
                    let schedulers = response.items.unwrap_or_default();
                    if format == "json" {
                        println!("{}", serde_json::to_string_pretty(&schedulers).unwrap());
                    } else {
                        let rows: Vec<SlurmSchedulerTableRow> = schedulers
                            .iter()
                            .map(|s| SlurmSchedulerTableRow {
                                id: s.id.unwrap_or(-1),
                                name: s.name.clone().unwrap_or_default(),
                                account: s.account.clone(),
                                nodes: s.nodes,
                                walltime: s.walltime.clone(),
                                partition: s.partition.clone().unwrap_or_default(),
                                qos: s.qos.clone().unwrap_or_default(),
                            })
                            .collect();

                        println!("Slurm configurations for workflow {}", wf_id);
                        display_table_with_count(&rows, "configs");
                    }
                }
                Err(e) => {
                    print_error("listing Slurm schedulers", &e);
                    std::process::exit(1);
                }
            }
        }
        SlurmCommands::Get { id } => match default_api::get_slurm_scheduler(config, *id) {
            Ok(scheduler) => {
                if format == "json" {
                    match serde_json::to_string_pretty(&scheduler) {
                        Ok(json) => println!("{}", json),
                        Err(e) => {
                            eprintln!("Error serializing Slurm config to JSON: {}", e);
                            std::process::exit(1);
                        }
                    }
                } else {
                    eprintln!("Slurm Config ID {}:", id);
                    eprintln!("  Name: {}", scheduler.name.unwrap_or_default());
                    eprintln!("  Workflow ID: {}", scheduler.workflow_id);
                    eprintln!("  Account: {}", scheduler.account);
                    eprintln!("  Nodes: {}", scheduler.nodes);
                    eprintln!("  Walltime: {}", scheduler.walltime);
                    eprintln!("  Partition: {}", scheduler.partition.unwrap_or_default());
                    eprintln!("  QOS: {}", scheduler.qos.unwrap_or_default());
                    eprintln!(
                        "  GRES: {}",
                        scheduler.gres.unwrap_or_else(|| "None".to_string())
                    );
                    eprintln!(
                        "  Memory: {}",
                        scheduler.mem.unwrap_or_else(|| "None".to_string())
                    );
                    eprintln!(
                        "  Tmp: {}",
                        scheduler.tmp.unwrap_or_else(|| "None".to_string())
                    );
                    eprintln!(
                        "  Extra: {}",
                        scheduler.extra.unwrap_or_else(|| "None".to_string())
                    );
                }
            }
            Err(e) => {
                print_error("getting Slurm scheduler", &e);
                std::process::exit(1);
            }
        },
        SlurmCommands::Delete { id } => {
            match default_api::delete_slurm_scheduler(config, *id, None) {
                Ok(deleted_scheduler) => {
                    if format == "json" {
                        match serde_json::to_string_pretty(&deleted_scheduler) {
                            Ok(json) => println!("{}", json),
                            Err(e) => {
                                eprintln!("Error serializing Slurm config to JSON: {}", e);
                                std::process::exit(1);
                            }
                        }
                    } else {
                        eprintln!("Successfully deleted Slurm config ID {}", id);
                        eprintln!("  Name: {}", deleted_scheduler.name.unwrap_or_default());
                        eprintln!("  Workflow ID: {}", deleted_scheduler.workflow_id);
                    }
                }
                Err(e) => {
                    print_error("deleting Slurm scheduler", &e);
                    std::process::exit(1);
                }
            }
        }
        SlurmCommands::ScheduleNodes {
            workflow_id,
            job_prefix,
            keep_submission_scripts,
            max_parallel_jobs,
            num_hpc_jobs,
            output,
            poll_interval,
            scheduler_config_id,
            start_one_worker_per_node,
            start_server_on_head_node,
        } => {
            let user_name = get_env_user_name();
            let wf_id = workflow_id.unwrap_or_else(|| {
                select_workflow_interactively(config, &user_name).unwrap_or_else(|e| {
                    eprintln!("Error selecting workflow: {}", e);
                    std::process::exit(1);
                })
            });

            // Get the workflow object
            let workflow = match default_api::get_workflow(config, wf_id) {
                Ok(w) => w,
                Err(e) => {
                    print_error("getting workflow", &e);
                    std::process::exit(1);
                }
            };

            // Check if all jobs are uninitialized and initialize the workflow if needed
            match default_api::is_workflow_uninitialized(config, wf_id) {
                Ok(response) => {
                    if let Some(is_uninitialized) =
                        response.get("is_uninitialized").and_then(|v| v.as_bool())
                    {
                        if is_uninitialized {
                            info!(
                                "Workflow {} has all jobs uninitialized. Initializing workflow...",
                                wf_id
                            );
                            let workflow_manager =
                                WorkflowManager::new(config.clone(), workflow.clone());
                            match workflow_manager.initialize(false) {
                                Ok(()) => {
                                    info!("Successfully initialized workflow {}", wf_id);
                                }
                                Err(e) => {
                                    error!("Error initializing workflow: {}", e);
                                    eprintln!("Error initializing workflow: {}", e);
                                    std::process::exit(1);
                                }
                            }
                        } else {
                            info!("Workflow {} already has initialized jobs", wf_id);
                        }
                    }
                }
                Err(e) => {
                    error!("Error checking if workflow is uninitialized: {}", e);
                    eprintln!("Error checking if workflow is uninitialized: {}", e);
                    std::process::exit(1);
                }
            }

            let sched_config_id = scheduler_config_id.unwrap_or_else(|| {
                select_slurm_scheduler_interactively(config, wf_id).unwrap_or_else(|e| {
                    eprintln!("Error selecting scheduler: {}", e);
                    std::process::exit(1);
                })
            });

            match schedule_slurm_nodes(
                config,
                wf_id,
                sched_config_id,
                *num_hpc_jobs,
                job_prefix,
                output,
                *poll_interval,
                *max_parallel_jobs,
                *start_one_worker_per_node,
                *start_server_on_head_node,
                *keep_submission_scripts,
                None, // torc_server_args - not available from CLI context
            ) {
                Ok(()) => {
                    eprintln!("Successfully running {} Slurm job(s)", num_hpc_jobs);
                }
                Err(e) => {
                    eprintln!("Error scheduling Slurm nodes: {}", e);
                    std::process::exit(1);
                }
            }
        }
    }
}

/// Schedule Slurm compute nodes for a workflow
///
/// # Arguments
/// * `config` - API configuration
/// * `workflow_id` - Workflow ID
/// * `scheduler_config_id` - Slurm scheduler configuration ID
/// * `num_hpc_jobs` - Number of HPC jobs to submit
/// * `job_prefix` - Prefix for job names
/// * `output` - Output directory for job output files
/// * `poll_interval` - Poll interval in seconds
/// * `max_parallel_jobs` - Maximum number of parallel jobs
/// * `start_one_worker_per_node` - Start one worker per node
/// * `start_server_on_head_node` - Start server on head node
/// * `keep_submission_scripts` - Keep submission scripts after job submission
///
/// # Returns
/// Result indicating success or failure
pub fn schedule_slurm_nodes(
    config: &Configuration,
    workflow_id: i64,
    scheduler_config_id: i64,
    num_hpc_jobs: i32,
    job_prefix: &str,
    output: &str,
    poll_interval: i32,
    max_parallel_jobs: Option<i32>,
    start_one_worker_per_node: bool,
    start_server_on_head_node: bool,
    keep_submission_scripts: bool,
    torc_server_args: Option<&serde_json::Value>,
) -> Result<(), Box<dyn std::error::Error>> {
    let scheduler = match default_api::get_slurm_scheduler(config, scheduler_config_id) {
        Ok(s) => s,
        Err(e) => {
            return Err(format!("Failed to get Slurm scheduler: {}", e).into());
        }
    };

    let slurm_interface = match crate::client::hpc::slurm_interface::SlurmInterface::new() {
        Ok(interface) => interface,
        Err(e) => {
            return Err(format!("Failed to create Slurm interface: {}", e).into());
        }
    };

    let mut config_map = HashMap::new();
    config_map.insert("account".to_string(), scheduler.account.clone());
    config_map.insert("walltime".to_string(), scheduler.walltime.clone());
    config_map.insert("nodes".to_string(), scheduler.nodes.to_string());

    if let Some(partition) = &scheduler.partition {
        config_map.insert("partition".to_string(), partition.clone());
    }
    if let Some(qos) = &scheduler.qos {
        config_map.insert("qos".to_string(), qos.clone());
    }
    if let Some(gres) = &scheduler.gres {
        config_map.insert("gres".to_string(), gres.clone());
    }
    if let Some(mem) = &scheduler.mem {
        config_map.insert("mem".to_string(), mem.clone());
    }
    if let Some(tmp) = &scheduler.tmp {
        config_map.insert("tmp".to_string(), tmp.clone());
    }
    if let Some(extra) = &scheduler.extra {
        config_map.insert("extra".to_string(), extra.clone());
    }

    std::fs::create_dir_all(output)?;

    for job_num in 0..num_hpc_jobs {
        let job_name = format!("{}_{}", job_prefix, job_num);
        let script_path = format!("{}/{}.sh", output, job_name);

        if let Err(e) = slurm_interface.create_submission_script(
            &job_name,
            &config.base_path,
            workflow_id,
            output,
            poll_interval,
            max_parallel_jobs,
            Path::new(&script_path),
            &config_map,
            start_one_worker_per_node,
            start_server_on_head_node,
            torc_server_args,
        ) {
            error!("Error creating submission script: {}", e);
            return Err(e.into());
        }

        match slurm_interface.submit(Path::new(&script_path)) {
            Ok((return_code, job_id, stderr)) => {
                if return_code != 0 {
                    error!("Error submitting job: {}", stderr);
                    return Err(format!("Job submission failed: {}", stderr).into());
                }
                let job_id_int = job_id
                    .parse()
                    .expect(&format!("Failed to parse Slurm job ID {}", job_id));
                info!("running Slurm job {} with ID: {}", job_name, job_id_int);

                let event_data = serde_json::json!({
                    "category": "scheduler",
                    "slurm_job_id": job_id,
                    "slurm_job_name": job_name,
                    "scheduler_config_id": scheduler_config_id,
                    "num_nodes": scheduler.nodes,
                });

                let scheduled_compute_node = models::ScheduledComputeNodesModel::new(
                    workflow_id,
                    job_id_int,
                    scheduler_config_id,
                    "slurm".to_string(),
                    "pending".to_string(),
                );
                if let Err(e) =
                    default_api::create_scheduled_compute_node(config, scheduled_compute_node)
                {
                    error!("Failed to create scheduled compute node: {}", e);
                }
                let event = models::EventModel::new(workflow_id, event_data);
                if let Err(e) = default_api::create_event(config, event) {
                    error!("Failed to create event: {}", e);
                }
            }
            Err(e) => {
                error!("Error submitting job: {}", e);
                return Err(e.into());
            }
        }

        if !keep_submission_scripts {
            if let Err(e) = std::fs::remove_file(&script_path) {
                error!("Failed to remove submission script: {}", e);
            }
        }
    }

    Ok(())
}

/// Create a ComputeNodesResources instance by reading information from the Slurm environment
///
/// # Arguments
/// * `interface` - SlurmInterface instance to query for system resources
/// * `scheduler_config_id` - The scheduler configuration ID to use
/// * `is_subtask` - If true, use CPUs per task instead of CPUs per node
///
/// # Returns
/// A ComputeNodesResources instance populated with Slurm environment data
pub fn create_node_resources(
    interface: &crate::client::hpc::slurm_interface::SlurmInterface,
    scheduler_config_id: Option<i64>,
    is_subtask: bool,
) -> models::ComputeNodesResources {
    let num_cpus_in_node = interface.get_num_cpus() as i64;
    let memory_gb_in_node = interface.get_memory_gb();
    let num_cpus = if is_subtask {
        interface.get_num_cpus_per_task() as i64
    } else {
        num_cpus_in_node
    };
    let memory_gb = if is_subtask {
        let num_workers = num_cpus_in_node / num_cpus;
        memory_gb_in_node / num_workers as f64
    } else {
        memory_gb_in_node
    };

    let num_gpus = interface.get_num_gpus() as i64;
    let num_nodes = interface.get_num_nodes() as i64;
    let mut resources =
        models::ComputeNodesResources::new(num_cpus, memory_gb, num_gpus, num_nodes);
    resources.scheduler_config_id = scheduler_config_id;
    resources
}

/// Create a ComputeNodeModel instance.
///
/// # Arguments
/// * `resources` - ComputeNodesResources
///
/// # Returns
/// A ComputeNodeModel instance populated with Slurm environment data
pub fn create_compute_node(
    config: &Configuration,
    workflow_id: i64,
    resources: &models::ComputeNodesResources,
    hostname: &str,
    scheduler: serde_json::Value,
) -> models::ComputeNodeModel {
    let pid = 1; // TODO
    // TODO: send_with_retries
    let compute_node = match default_api::create_compute_node(
        &config,
        models::ComputeNodeModel::new(
            workflow_id,
            hostname.to_string(),
            pid,
            Utc::now().to_rfc3339(),
            resources.num_cpus,
            resources.memory_gb,
            resources.num_gpus,
            resources.num_nodes,
            "slurm".to_string(),
            Some(scheduler),
        ),
    ) {
        Ok(node) => node,
        Err(e) => {
            error!("Error creating compute node: {}", e);
            std::process::exit(1);
        }
    };

    compute_node
}
