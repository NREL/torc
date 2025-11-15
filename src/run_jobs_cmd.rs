use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::commands::get_env_user_name;
use crate::client::commands::select_workflow_interactively;
use crate::client::job_runner::JobRunner;
use crate::client::log_paths::get_job_runner_log_file;
use crate::client::workflow_manager::WorkflowManager;
use crate::models;
use chrono::{DateTime, Utc};
use clap::Parser;
use env_logger::Builder;
use log::{LevelFilter, error, info};
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use sysinfo::{System, SystemExt};

/// A writer that writes to both stdout and a file
struct MultiWriter {
    stdout: std::io::Stdout,
    file: File,
}

impl Write for MultiWriter {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        self.stdout.write_all(buf)?;
        self.file.write(buf)
    }

    fn flush(&mut self) -> std::io::Result<()> {
        self.stdout.flush()?;
        self.file.flush()
    }
}

#[derive(Parser, Debug)]
#[command(about = "Run jobs locally on the current node", long_about = None)]
pub struct Args {
    /// Workflow ID
    #[arg()]
    pub workflow_id: Option<i64>,
    /// URL of torc server
    #[arg(short, long, default_value = "http://localhost:8080/torc-service/v1")]
    pub url: String,
    /// Output directory for jobs
    #[arg(short, long, default_value = "output")]
    pub output_dir: PathBuf,
    /// Job completion poll interval in seconds
    #[arg(short, long, default_value = "60.0")]
    pub poll_interval: f64,
    /// Maximum number of parallel jobs to run concurrently.
    /// When NOT set: Uses resource-based job allocation (considers CPU, memory, GPU requirements).
    /// When set: Uses simple queue-based allocation with this parallel limit (ignores resource requirements).
    #[arg(long)]
    pub max_parallel_jobs: Option<i64>,
    /// Database poll interval in seconds
    #[arg(long, default_value = "30")]
    pub database_poll_interval: i64,
    /// Time limit for jobs
    #[arg(long)]
    pub time_limit: Option<String>,
    /// End time for job execution
    #[arg(long)]
    pub end_time: Option<String>,
    /// Number of CPUs
    #[arg(long)]
    pub num_cpus: Option<i64>,
    /// Memory in GB
    #[arg(long)]
    pub memory_gb: Option<f64>,
    /// Number of GPUs
    #[arg(long)]
    pub num_gpus: Option<i64>,
    /// Number of nodes
    #[arg(long)]
    pub num_nodes: Option<i64>,
    /// Scheduler config ID
    #[arg(long)]
    pub scheduler_config_id: Option<i64>,
    /// Log prefix
    #[arg(long)]
    pub log_prefix: Option<String>,
    /// CPU affinity CPUs per job
    #[arg(long)]
    pub cpu_affinity_cpus_per_job: Option<i64>,
    /// Log level (error, warn, info, debug, trace)
    #[arg(long, default_value = "info")]
    pub log_level: String,
}

pub fn run(args: &Args) {
    let hostname = hostname::get()
        .expect("Failed to get hostname")
        .into_string()
        .expect("Hostname is not valid UTF-8");
    let mut config = Configuration::new();
    config.base_path = args.url.clone();
    let user = get_env_user_name();
    let workflow_id = args.workflow_id.unwrap_or_else(|| {
        select_workflow_interactively(&config, &user).unwrap_or_else(|e| {
            eprintln!("Error selecting workflow: {}", e);
            std::process::exit(1);
        })
    });
    let workflow = match default_api::get_workflow(&config, workflow_id) {
        Ok(workflow) => workflow,
        Err(e) => {
            eprintln!("Error getting workflow: {}", e);
            std::process::exit(1);
        }
    };

    // Check if all jobs are uninitialized and initialize the workflow if needed
    match default_api::is_workflow_uninitialized(&config, workflow_id) {
        Ok(response) => {
            if let Some(is_uninitialized) =
                response.get("is_uninitialized").and_then(|v| v.as_bool())
            {
                if is_uninitialized {
                    eprintln!(
                        "Workflow {} has all jobs uninitialized. Initializing workflow...",
                        workflow_id
                    );
                    let workflow_manager = WorkflowManager::new(config.clone(), workflow.clone());
                    match workflow_manager.initialize(false) {
                        Ok(()) => {
                            eprintln!("Successfully initialized workflow {}", workflow_id);
                        }
                        Err(e) => {
                            eprintln!("Error initializing workflow: {}", e);
                            std::process::exit(1);
                        }
                    }
                } else {
                    eprintln!("Workflow {} already has initialized jobs", workflow_id);
                }
            }
        }
        Err(e) => {
            eprintln!("Error checking if workflow is uninitialized: {}", e);
            std::process::exit(1);
        }
    }

    let run_id = match default_api::get_workflow_status(&config, workflow_id) {
        Ok(status) => status.run_id,
        Err(e) => {
            eprintln!("Error getting workflow status: {}", e);
            std::process::exit(1);
        }
    };

    // Create output directory if it doesn't exist
    if let Err(e) = std::fs::create_dir_all(&args.output_dir) {
        eprintln!(
            "Error creating output directory {}: {}",
            args.output_dir.display(),
            e
        );
        std::process::exit(1);
    }

    let log_file_path =
        get_job_runner_log_file(args.output_dir.clone(), &hostname, workflow_id, run_id);
    let log_file = match File::create(&log_file_path) {
        Ok(file) => file,
        Err(e) => {
            eprintln!("Error creating log file {}: {}", log_file_path, e);
            std::process::exit(1);
        }
    };

    let multi_writer = MultiWriter {
        stdout: std::io::stdout(),
        file: log_file,
    };

    // Parse log level string to LevelFilter
    let log_level_filter = match args.log_level.to_lowercase().as_str() {
        "error" => LevelFilter::Error,
        "warn" => LevelFilter::Warn,
        "info" => LevelFilter::Info,
        "debug" => LevelFilter::Debug,
        "trace" => LevelFilter::Trace,
        _ => {
            eprintln!("Invalid log level '{}', defaulting to 'info'", args.log_level);
            LevelFilter::Info
        }
    };

    let mut builder = Builder::from_default_env();
    builder
        .target(env_logger::Target::Pipe(Box::new(multi_writer)))
        .filter_level(log_level_filter)
        .init();

    info!("Starting job runner");
    info!("Hostname: {}", hostname);
    info!("Output directory: {}", args.output_dir.display());
    info!("Log file: {}", log_file_path);

    let parsed_end_time = if let Some(end_time_str) = &args.end_time {
        match end_time_str.parse::<DateTime<Utc>>() {
            Ok(dt) => Some(dt),
            Err(e) => {
                error!("Error parsing end_time: {}", e);
                std::process::exit(1);
            }
        }
    } else {
        None
    };

    let mut system = System::new_all();
    system.refresh_all();
    let system_cpus = system.cpus().len() as i64;
    let system_memory_gb = (system.total_memory() as f64) / (1024.0 * 1024.0 * 1024.0);

    let resources = models::ComputeNodesResources::new(
        args.num_cpus.unwrap_or(system_cpus),
        args.memory_gb.unwrap_or(system_memory_gb),
        args.num_gpus.unwrap_or(0),
        args.num_nodes.unwrap_or(1),
    );
    let pid = 1; // TODO
    let unique_label = format!("{}_{}_{}", hostname, workflow_id, run_id);

    let compute_node = match default_api::create_compute_node(
        &config,
        models::ComputeNodeModel::new(
            workflow_id,
            hostname.clone(),
            pid,
            Utc::now().to_rfc3339(),
            resources.num_cpus,
            resources.memory_gb,
            resources.num_gpus,
            resources.num_nodes,
            "local".to_string(),
            None,
        ),
    ) {
        Ok(node) => node,
        Err(e) => {
            error!("Error creating compute node: {}", e);
            std::process::exit(1);
        }
    };

    let mut job_runner = JobRunner::new(
        config.clone(),
        workflow,
        run_id,
        compute_node.id.expect("Compute node ID should be set"),
        args.output_dir.clone(),
        args.poll_interval,
        args.max_parallel_jobs,
        args.database_poll_interval,
        args.time_limit.clone(),
        parsed_end_time,
        resources,
        args.scheduler_config_id,
        args.log_prefix.clone(),
        args.cpu_affinity_cpus_per_job,
        false,
        unique_label,
    );

    match job_runner.run_worker() {
        Ok(()) => {
            info!("Job runner completed successfully");
        }
        Err(e) => {
            error!("Job runner failed: {}", e);
            std::process::exit(1);
        }
    }
}
