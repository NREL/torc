//! HPC system profile commands
//!
//! Commands for listing, detecting, and querying HPC system profiles.

use clap::Subcommand;
use serde_json;
use tabled::Tabled;

use crate::client::hpc::{HpcDetection, HpcPartition, HpcProfile, HpcProfileRegistry};
use crate::client::workflow_graph::WorkflowGraph;
use crate::client::workflow_spec::{
    ResourceRequirementsSpec, SlurmSchedulerSpec, WorkflowActionSpec, WorkflowSpec,
};
use crate::config::{ClientHpcConfig, HpcPartitionConfig, HpcProfileConfig, TorcConfig};
use crate::time_utils::duration_string_to_seconds;

use super::table_format::display_table_with_count;

/// Create an HPC profile registry with built-in profiles and user-defined profiles from config
///
/// This is a public version for use by other modules (e.g., main.rs for submit command)
pub fn create_registry_with_config_public(hpc_config: &ClientHpcConfig) -> HpcProfileRegistry {
    create_registry_with_config(hpc_config)
}

/// Create an HPC profile registry with built-in profiles and user-defined profiles from config
fn create_registry_with_config(hpc_config: &ClientHpcConfig) -> HpcProfileRegistry {
    let mut registry = HpcProfileRegistry::with_builtin_profiles();

    // Apply profile overrides to built-in profiles
    // Note: This modifies the default_account for profiles
    // In a real implementation, we'd need mutable access to profiles

    // Add custom profiles from config
    for (name, profile_config) in &hpc_config.custom_profiles {
        let profile = config_to_profile(name, profile_config);
        registry.register(profile);
    }

    registry
}

/// Convert a config profile to an HpcProfile
fn config_to_profile(name: &str, config: &HpcProfileConfig) -> HpcProfile {
    let mut detection = Vec::new();

    // Parse detect_env_var (format: "NAME=value")
    if let Some(env_var) = &config.detect_env_var {
        if let Some((var_name, var_value)) = env_var.split_once('=') {
            detection.push(HpcDetection::EnvVar {
                name: var_name.to_string(),
                value: var_value.to_string(),
            });
        }
    }

    // Parse hostname pattern
    if let Some(pattern) = &config.detect_hostname {
        detection.push(HpcDetection::HostnamePattern {
            pattern: pattern.clone(),
        });
    }

    // Convert partitions
    let partitions: Vec<HpcPartition> = config
        .partitions
        .iter()
        .map(|p| config_to_partition(p))
        .collect();

    HpcProfile {
        name: name.to_string(),
        display_name: config.display_name.clone(),
        description: config.description.clone(),
        detection,
        default_account: config.default_account.clone(),
        partitions,
        charge_factor_cpu: config.charge_factor_cpu,
        charge_factor_gpu: config.charge_factor_gpu,
        metadata: std::collections::HashMap::new(),
    }
}

/// Convert a config partition to an HpcPartition
fn config_to_partition(config: &HpcPartitionConfig) -> HpcPartition {
    HpcPartition {
        name: config.name.clone(),
        description: config.description.clone(),
        cpus_per_node: config.cpus_per_node,
        memory_mb: config.memory_mb,
        max_walltime_secs: config.max_walltime_secs,
        max_nodes: None,
        max_nodes_per_user: None,
        min_nodes: None,
        gpus_per_node: config.gpus_per_node,
        gpu_type: config.gpu_type.clone(),
        gpu_memory_gb: config.gpu_memory_gb,
        local_disk_gb: None,
        shared: config.shared,
        requires_explicit_request: config.requires_explicit_request,
        default_qos: None,
        features: vec![],
    }
}

/// Convert seconds to Slurm walltime format (HH:MM:SS or D-HH:MM:SS)
pub fn secs_to_walltime(secs: u64) -> String {
    let hours = secs / 3600;
    let mins = (secs % 3600) / 60;
    let s = secs % 60;

    if hours >= 24 {
        let days = hours / 24;
        let h = hours % 24;
        format!("{}-{:02}:{:02}:{:02}", days, h, mins, s)
    } else {
        format!("{:02}:{:02}:{:02}", hours, mins, s)
    }
}

/// Generate a scheduler name from a resource requirements name
fn scheduler_name_from_rr(rr_name: &str) -> String {
    format!("{}_scheduler", rr_name)
}

/// Generate Slurm schedulers for a workflow spec based on resource requirements
///
/// This creates one scheduler per unique resource requirement (not per job).
/// All jobs with the same resource requirements share a scheduler.
/// Actions are generated based on whether any job using that scheduler has dependencies.
///
/// # Arguments
/// * `spec` - Workflow specification to modify
/// * `profile` - HPC profile with partition information
/// * `account` - Slurm account to use
/// * `single_allocation` - If true, create 1 allocation with N nodes (1×N mode).
///   If false (default), create N allocations with 1 node each (N×1 mode).
/// * `add_actions` - Whether to add workflow actions for scheduling
/// * `force` - Force overwrite of existing schedulers
pub fn generate_schedulers_for_workflow(
    spec: &mut WorkflowSpec,
    profile: &HpcProfile,
    account: &str,
    single_allocation: bool,
    add_actions: bool,
    force: bool,
) -> Result<GenerateResult, String> {
    // Check if workflow already has schedulers
    if !force
        && spec.slurm_schedulers.is_some()
        && !spec.slurm_schedulers.as_ref().unwrap().is_empty()
    {
        return Err(
            "Workflow already has slurm_schedulers defined. Use --force to overwrite.".to_string(),
        );
    }

    // Expand parameters before building the graph to properly detect file-based dependencies
    spec.expand_parameters()
        .map_err(|e| format!("Failed to expand parameters: {}", e))?;

    // Build a map of resource requirements by name
    let rr_map: std::collections::HashMap<String, &ResourceRequirementsSpec> = spec
        .resource_requirements
        .as_ref()
        .map(|rrs| rrs.iter().map(|rr| (rr.name.clone(), rr)).collect())
        .unwrap_or_default();

    if rr_map.is_empty() {
        return Err(
            "Workflow has no resource_requirements defined. Cannot generate schedulers."
                .to_string(),
        );
    }

    // Build workflow graph for dependency analysis and job grouping
    let graph = WorkflowGraph::from_spec(spec)
        .map_err(|e| format!("Failed to build workflow graph: {}", e))?;

    let mut schedulers: Vec<SlurmSchedulerSpec> = Vec::new();
    let mut actions: Vec<WorkflowActionSpec> = Vec::new();
    let mut warnings: Vec<String> = Vec::new();

    // Get scheduler groups from the graph
    // Groups jobs by (resource_requirements, has_dependencies)
    let scheduler_groups = graph.scheduler_groups();

    // Check for jobs without resource requirements
    for job in &spec.jobs {
        if job.resource_requirements.is_none() {
            warnings.push(format!(
                "Job '{}' has no resource_requirements, skipping scheduler generation",
                job.name
            ));
        }
    }

    // Create schedulers and actions for each group
    for group in &scheduler_groups {
        let rr_name = &group.resource_requirements;
        let has_deps = group.has_dependencies;
        let rr = match rr_map.get(rr_name) {
            Some(rr) => *rr,
            None => {
                return Err(format!("Resource requirements '{}' not found", rr_name));
            }
        };

        // Parse resource requirements
        let memory_mb = parse_memory_mb(&rr.memory)?;
        let runtime_secs = duration_string_to_seconds(&rr.runtime)? as u64;
        let gpus = if rr.num_gpus > 0 {
            Some(rr.num_gpus as u32)
        } else {
            None
        };

        // Find best partition
        let partition = match profile.find_best_partition(
            rr.num_cpus as u32,
            memory_mb,
            runtime_secs,
            gpus,
        ) {
            Some(p) => p,
            None => {
                warnings.push(format!(
                    "No partition found for resource requirements '{}' (CPUs: {}, Memory: {}, Runtime: {}, GPUs: {:?})",
                    rr_name, rr.num_cpus, rr.memory, rr.runtime, gpus
                ));
                continue;
            }
        };

        // Scheduler naming: jobs with deps get "_deferred" suffix
        let scheduler_name = if has_deps {
            format!("{}_deferred_scheduler", rr_name)
        } else {
            scheduler_name_from_rr(rr_name)
        };

        // Calculate total nodes needed based on job count and partition capacity
        // Jobs per node is based on how many jobs can fit based on CPU requirements
        let jobs_per_node = std::cmp::max(1, partition.cpus_per_node / rr.num_cpus as u32);
        // Total nodes needed to run all jobs concurrently (respecting num_nodes per job)
        let nodes_per_job = rr.num_nodes as u32;
        let total_nodes_needed =
            ((group.job_count as u32 + jobs_per_node - 1) / jobs_per_node) * nodes_per_job;
        let total_nodes_needed = std::cmp::max(1, total_nodes_needed) as i64;

        // Allocation strategy:
        // - N×1 mode (default): N separate 1-node allocations, jobs start as nodes become available
        // - 1×N mode (--single-allocation): 1 allocation with N nodes, all nodes must be available
        let (nodes_per_alloc, effective_num_allocations) = if single_allocation {
            // 1×N mode: single allocation with all nodes
            (total_nodes_needed, 1i64)
        } else {
            // N×1 mode: many single-node allocations
            (1i64, total_nodes_needed)
        };

        // Create scheduler for this group
        // Use the partition's max walltime for headroom
        let mut scheduler = SlurmSchedulerSpec {
            name: Some(scheduler_name.clone()),
            account: account.to_string(),
            partition: if partition.requires_explicit_request {
                Some(partition.name.clone())
            } else {
                None // Auto-routed
            },
            mem: Some(rr.memory.clone()),
            walltime: secs_to_walltime(partition.max_walltime_secs),
            nodes: nodes_per_alloc,
            gres: None,
            ntasks_per_node: None,
            qos: partition.default_qos.clone(),
            tmp: None,
            extra: None,
        };

        // Add GPU gres if needed
        if let Some(gpu_count) = gpus {
            scheduler.gres = Some(format!("gpu:{}", gpu_count));
        }

        schedulers.push(scheduler);

        // Create action for this scheduler
        if add_actions {
            // If requesting multiple nodes, start one worker per node
            let start_one_worker_per_node = if nodes_per_alloc > 1 {
                Some(true)
            } else {
                None
            };

            let (trigger_type, job_name_regexes) = if has_deps {
                // Jobs with dependencies: trigger on_jobs_ready when they become unblocked
                // This fires when the first job in the group becomes ready
                ("on_jobs_ready", Some(group.job_name_patterns.clone()))
            } else {
                // Jobs without dependencies: trigger on_workflow_start
                ("on_workflow_start", None)
            };

            let action = WorkflowActionSpec {
                trigger_type: trigger_type.to_string(),
                action_type: "schedule_nodes".to_string(),
                jobs: None,
                job_name_regexes,
                commands: None,
                scheduler: Some(scheduler_name.clone()),
                scheduler_type: Some("slurm".to_string()),
                num_allocations: Some(effective_num_allocations),
                start_one_worker_per_node,
                max_parallel_jobs: None,
                persistent: None,
            };
            actions.push(action);
        }
    }

    if schedulers.is_empty() {
        return Err("No schedulers could be generated. Check resource requirements.".to_string());
    }

    // Update jobs to reference their scheduler based on (resource_requirement, has_dependencies)
    for job in &mut spec.jobs {
        if let Some(rr_name) = &job.resource_requirements {
            let has_deps = graph.has_dependencies(&job.name);
            let scheduler_name = if has_deps {
                format!("{}_deferred_scheduler", rr_name)
            } else {
                scheduler_name_from_rr(rr_name)
            };
            job.scheduler = Some(scheduler_name);
        }
    }

    // Update workflow with schedulers and actions
    spec.slurm_schedulers = Some(schedulers);
    if add_actions && !actions.is_empty() {
        let mut existing_actions = spec.actions.take().unwrap_or_default();
        existing_actions.extend(actions.clone());
        spec.actions = Some(existing_actions);
    }

    Ok(GenerateResult {
        scheduler_count: spec.slurm_schedulers.as_ref().map(|s| s.len()).unwrap_or(0),
        action_count: actions.len(),
        warnings,
    })
}

/// Result of generating schedulers
pub struct GenerateResult {
    pub scheduler_count: usize,
    pub action_count: usize,
    pub warnings: Vec<String>,
}

/// Parse memory string like "100g", "512m", "1024" (MB) into MB
pub fn parse_memory_mb(s: &str) -> Result<u64, String> {
    let s = s.trim().to_lowercase();
    if s.is_empty() {
        return Err("Empty memory string".to_string());
    }

    // Check for suffix
    if let Some(num_str) = s.strip_suffix('g') {
        let num: f64 = num_str
            .parse()
            .map_err(|_| format!("Invalid number: {}", num_str))?;
        Ok((num * 1024.0) as u64)
    } else if let Some(num_str) = s.strip_suffix('m') {
        let num: u64 = num_str
            .parse()
            .map_err(|_| format!("Invalid number: {}", num_str))?;
        Ok(num)
    } else if let Some(num_str) = s.strip_suffix('k') {
        let num: f64 = num_str
            .parse()
            .map_err(|_| format!("Invalid number: {}", num_str))?;
        Ok((num / 1024.0) as u64)
    } else {
        // Assume MB
        s.parse()
            .map_err(|_| format!("Invalid memory value: {}", s))
    }
}

/// Parse walltime string like "4:00:00", "2-00:00:00" into seconds
pub fn parse_walltime_secs(s: &str) -> Result<u64, String> {
    let s = s.trim();

    // Check for day format: D-HH:MM:SS
    if let Some((days_str, rest)) = s.split_once('-') {
        let days: u64 = days_str
            .parse()
            .map_err(|_| format!("Invalid days: {}", days_str))?;
        let hms_secs = parse_hms(rest)?;
        return Ok(days * 24 * 3600 + hms_secs);
    }

    // Check for hours format: H, HH:MM, or HH:MM:SS
    parse_hms(s)
}

fn parse_hms(s: &str) -> Result<u64, String> {
    let parts: Vec<&str> = s.split(':').collect();
    match parts.len() {
        1 => {
            // Just hours
            let hours: u64 = parts[0]
                .parse()
                .map_err(|_| format!("Invalid hours: {}", parts[0]))?;
            Ok(hours * 3600)
        }
        2 => {
            // HH:MM
            let hours: u64 = parts[0]
                .parse()
                .map_err(|_| format!("Invalid hours: {}", parts[0]))?;
            let mins: u64 = parts[1]
                .parse()
                .map_err(|_| format!("Invalid minutes: {}", parts[1]))?;
            Ok(hours * 3600 + mins * 60)
        }
        3 => {
            // HH:MM:SS
            let hours: u64 = parts[0]
                .parse()
                .map_err(|_| format!("Invalid hours: {}", parts[0]))?;
            let mins: u64 = parts[1]
                .parse()
                .map_err(|_| format!("Invalid minutes: {}", parts[1]))?;
            let secs: u64 = parts[2]
                .parse()
                .map_err(|_| format!("Invalid seconds: {}", parts[2]))?;
            Ok(hours * 3600 + mins * 60 + secs)
        }
        _ => Err(format!("Invalid time format: {}", s)),
    }
}

#[derive(Subcommand)]
pub enum HpcCommands {
    /// List known HPC system profiles
    List,

    /// Detect the current HPC system
    Detect,

    /// Show details of an HPC profile
    Show {
        /// Profile name (e.g., "kestrel")
        #[arg()]
        name: String,
    },

    /// Show partitions for an HPC profile
    Partitions {
        /// Profile name (e.g., "kestrel"). If not specified, tries to detect current system.
        #[arg()]
        name: Option<String>,

        /// Filter to GPU partitions only
        #[arg(long)]
        gpu: bool,

        /// Filter to CPU-only partitions
        #[arg(long)]
        cpu: bool,

        /// Filter to shared partitions
        #[arg(long)]
        shared: bool,
    },

    /// Find partitions matching resource requirements
    Match {
        /// Number of CPUs required
        #[arg(long, default_value = "1")]
        cpus: u32,

        /// Memory required (e.g., "100g", "512m", or MB as number)
        #[arg(long, default_value = "1g")]
        memory: String,

        /// Wall time required (e.g., "4:00:00", "2-00:00:00")
        #[arg(long, default_value = "1:00:00")]
        walltime: String,

        /// Number of GPUs required
        #[arg(long)]
        gpus: Option<u32>,

        /// Profile name (if not specified, tries to detect current system)
        #[arg(long)]
        profile: Option<String>,
    },
}

#[derive(Tabled)]
struct ProfileListRow {
    #[tabled(rename = "Name")]
    name: String,
    #[tabled(rename = "Display Name")]
    display_name: String,
    #[tabled(rename = "Partitions")]
    partition_count: usize,
    #[tabled(rename = "Detected")]
    detected: String,
}

#[derive(Tabled)]
struct PartitionRow {
    #[tabled(rename = "Partition")]
    name: String,
    #[tabled(rename = "CPUs")]
    cpus: u32,
    #[tabled(rename = "Memory")]
    memory: String,
    #[tabled(rename = "Max Time")]
    max_time: String,
    #[tabled(rename = "GPUs")]
    gpus: String,
    #[tabled(rename = "Shared")]
    shared: String,
    #[tabled(rename = "Explicit")]
    explicit: String,
}

#[derive(Tabled)]
struct MatchRow {
    #[tabled(rename = "Partition")]
    name: String,
    #[tabled(rename = "CPUs")]
    cpus: u32,
    #[tabled(rename = "Memory")]
    memory: String,
    #[tabled(rename = "Max Time")]
    max_time: String,
    #[tabled(rename = "GPUs")]
    gpus: String,
    #[tabled(rename = "Notes")]
    notes: String,
}

pub fn handle_hpc_commands(command: &HpcCommands, format: &str) {
    // Load config to get user-defined profiles
    let config = TorcConfig::load().unwrap_or_default();
    let registry = create_registry_with_config(&config.client.hpc);

    match command {
        HpcCommands::List => {
            let rows: Vec<ProfileListRow> = registry
                .profiles()
                .iter()
                .map(|p| ProfileListRow {
                    name: p.name.clone(),
                    display_name: p.display_name.clone(),
                    partition_count: p.partitions.len(),
                    detected: if p.detect() { "Yes" } else { "-" }.to_string(),
                })
                .collect();

            if format == "json" {
                let json_output: Vec<_> = registry
                    .profiles()
                    .iter()
                    .map(|p| {
                        serde_json::json!({
                            "name": p.name,
                            "display_name": p.display_name,
                            "description": p.description,
                            "partition_count": p.partitions.len(),
                            "detected": p.detect(),
                        })
                    })
                    .collect();
                println!("{}", serde_json::to_string_pretty(&json_output).unwrap());
            } else {
                println!("Known HPC profiles:\n");
                display_table_with_count(&rows, "profiles");
            }
        }

        HpcCommands::Detect => {
            if let Some(profile) = registry.detect() {
                if format == "json" {
                    println!(
                        "{}",
                        serde_json::to_string_pretty(&serde_json::json!({
                            "detected": true,
                            "name": profile.name,
                            "display_name": profile.display_name,
                            "description": profile.description,
                        }))
                        .unwrap()
                    );
                } else {
                    println!(
                        "Detected HPC system: {} ({})",
                        profile.display_name, profile.name
                    );
                    if !profile.description.is_empty() {
                        println!("  {}", profile.description);
                    }
                    // Show what triggered detection
                    for detection in &profile.detection {
                        if detection.matches() {
                            match detection {
                                crate::client::hpc::HpcDetection::EnvVar { name, value } => {
                                    println!("  Detection: {}={}", name, value);
                                }
                                crate::client::hpc::HpcDetection::HostnamePattern { pattern } => {
                                    println!("  Detection: hostname matches {}", pattern);
                                }
                                crate::client::hpc::HpcDetection::FileExists { path } => {
                                    println!("  Detection: file exists {}", path);
                                }
                            }
                        }
                    }
                }
            } else {
                if format == "json" {
                    println!(
                        "{}",
                        serde_json::to_string_pretty(&serde_json::json!({
                            "detected": false,
                            "message": "No known HPC system detected",
                        }))
                        .unwrap()
                    );
                } else {
                    println!("No known HPC system detected.");
                    println!("\nKnown systems:");
                    for profile in registry.profiles() {
                        println!("  - {} ({})", profile.display_name, profile.name);
                    }
                }
            }
        }

        HpcCommands::Show { name } => {
            if let Some(profile) = registry.get(name) {
                if format == "json" {
                    println!("{}", serde_json::to_string_pretty(&profile).unwrap());
                } else {
                    println!("HPC Profile: {} ({})", profile.display_name, profile.name);
                    println!();
                    if !profile.description.is_empty() {
                        println!("Description: {}", profile.description);
                    }
                    println!("Detected: {}", if profile.detect() { "Yes" } else { "No" });
                    println!();

                    // Show detection methods
                    println!("Detection methods:");
                    for detection in &profile.detection {
                        match detection {
                            crate::client::hpc::HpcDetection::EnvVar { name, value } => {
                                println!("  - Environment variable: {}={}", name, value);
                            }
                            crate::client::hpc::HpcDetection::HostnamePattern { pattern } => {
                                println!("  - Hostname pattern: {}", pattern);
                            }
                            crate::client::hpc::HpcDetection::FileExists { path } => {
                                println!("  - File exists: {}", path);
                            }
                        }
                    }
                    println!();

                    // Show charge factors
                    println!("Charge factors:");
                    println!("  CPU: {} AU per node-hour", profile.charge_factor_cpu);
                    println!("  GPU: {} AU per node-hour", profile.charge_factor_gpu);
                    println!();

                    // Show partition summary
                    let cpu_count = profile.cpu_partitions().len();
                    let gpu_count = profile.gpu_partitions().len();
                    println!(
                        "Partitions: {} total ({} CPU, {} GPU)",
                        profile.partitions.len(),
                        cpu_count,
                        gpu_count
                    );
                    println!();
                    println!(
                        "Use 'torc hpc partitions {}' to see partition details.",
                        name
                    );

                    // Show metadata
                    if !profile.metadata.is_empty() {
                        println!();
                        println!("Additional information:");
                        for (key, value) in &profile.metadata {
                            println!("  {}: {}", key, value);
                        }
                    }
                }
            } else {
                eprintln!("Unknown HPC profile: {}", name);
                eprintln!("\nKnown profiles:");
                for p in registry.profiles() {
                    eprintln!("  - {}", p.name);
                }
                std::process::exit(1);
            }
        }

        HpcCommands::Partitions {
            name,
            gpu,
            cpu,
            shared,
        } => {
            let profile = if let Some(n) = name {
                registry.get(n)
            } else {
                registry.detect()
            };

            let profile = match profile {
                Some(p) => p,
                None => {
                    if name.is_some() {
                        eprintln!("Unknown HPC profile: {}", name.as_ref().unwrap());
                    } else {
                        eprintln!("No HPC profile specified and no system detected.");
                        eprintln!("Use 'torc hpc partitions <profile>' or run on an HPC system.");
                    }
                    std::process::exit(1);
                }
            };

            let mut partitions: Vec<_> = profile.partitions.iter().collect();

            // Apply filters
            if *gpu {
                partitions.retain(|p| p.gpus_per_node.is_some());
            }
            if *cpu {
                partitions.retain(|p| p.gpus_per_node.is_none());
            }
            if *shared {
                partitions.retain(|p| p.shared);
            }

            if format == "json" {
                println!("{}", serde_json::to_string_pretty(&partitions).unwrap());
            } else {
                println!(
                    "Partitions for {} ({}):\n",
                    profile.display_name, profile.name
                );

                let rows: Vec<PartitionRow> = partitions
                    .iter()
                    .map(|p| PartitionRow {
                        name: p.name.clone(),
                        cpus: p.cpus_per_node,
                        memory: format!("{:.0}G", p.memory_gb()),
                        max_time: p.max_walltime_str(),
                        gpus: p
                            .gpus_per_node
                            .map(|g| format!("{}x {}", g, p.gpu_type.as_deref().unwrap_or("GPU")))
                            .unwrap_or_else(|| "-".to_string()),
                        shared: if p.shared { "Yes" } else { "-" }.to_string(),
                        explicit: if p.requires_explicit_request {
                            "Yes"
                        } else {
                            "-"
                        }
                        .to_string(),
                    })
                    .collect();

                display_table_with_count(&rows, "partitions");

                println!();
                println!("Notes:");
                println!("  - 'Explicit' means partition must be requested with -p/--partition");
                println!("  - Use 'torc hpc match' to find partitions for specific requirements");
            }
        }

        HpcCommands::Match {
            cpus,
            memory,
            walltime,
            gpus,
            profile: profile_name,
        } => {
            let profile = if let Some(n) = profile_name {
                registry.get(n)
            } else {
                registry.detect()
            };

            let profile = match profile {
                Some(p) => p,
                None => {
                    if profile_name.is_some() {
                        eprintln!("Unknown HPC profile: {}", profile_name.as_ref().unwrap());
                    } else {
                        eprintln!("No HPC profile specified and no system detected.");
                        eprintln!("Use --profile <name> or run on an HPC system.");
                    }
                    std::process::exit(1);
                }
            };

            // Parse memory
            let memory_mb = match parse_memory_mb(memory) {
                Ok(m) => m,
                Err(e) => {
                    eprintln!("Invalid memory format: {}", e);
                    std::process::exit(1);
                }
            };

            // Parse walltime
            let walltime_secs = match parse_walltime_secs(walltime) {
                Ok(s) => s,
                Err(e) => {
                    eprintln!("Invalid walltime format: {}", e);
                    std::process::exit(1);
                }
            };

            let matching = profile.find_matching_partitions(*cpus, memory_mb, walltime_secs, *gpus);

            if format == "json" {
                let output = serde_json::json!({
                    "profile": profile.name,
                    "requirements": {
                        "cpus": cpus,
                        "memory_mb": memory_mb,
                        "walltime_secs": walltime_secs,
                        "gpus": gpus,
                    },
                    "matching_partitions": matching,
                    "best_partition": profile.find_best_partition(*cpus, memory_mb, walltime_secs, *gpus),
                });
                println!("{}", serde_json::to_string_pretty(&output).unwrap());
            } else {
                println!("Requirements:");
                println!("  CPUs: {}", cpus);
                println!("  Memory: {} ({} MB)", memory, memory_mb);
                println!("  Walltime: {} ({} seconds)", walltime, walltime_secs);
                if let Some(g) = gpus {
                    println!("  GPUs: {}", g);
                }
                println!();

                if matching.is_empty() {
                    println!(
                        "No partitions match these requirements on {}.",
                        profile.display_name
                    );
                    println!();
                    println!("Possible reasons:");
                    println!("  - Requested CPUs exceed maximum per node");
                    println!("  - Requested memory exceeds maximum per node");
                    println!("  - Requested walltime exceeds partition limits");
                    if gpus.map(|g| g > 0).unwrap_or(false) {
                        println!("  - No GPU partitions with enough GPUs available");
                    }
                } else {
                    println!(
                        "Matching partitions on {} ({}):\n",
                        profile.display_name, profile.name
                    );

                    let best = profile.find_best_partition(*cpus, memory_mb, walltime_secs, *gpus);

                    let rows: Vec<MatchRow> = matching
                        .iter()
                        .map(|p| {
                            let mut notes = Vec::new();
                            if best.map(|b| b.name == p.name).unwrap_or(false) {
                                notes.push("Best match".to_string());
                            }
                            if p.shared {
                                notes.push("Shared".to_string());
                            }
                            if p.requires_explicit_request {
                                notes.push("Requires -p".to_string());
                            }
                            if let Some(min) = p.min_nodes {
                                notes.push(format!("Min {} nodes", min));
                            }

                            MatchRow {
                                name: p.name.clone(),
                                cpus: p.cpus_per_node,
                                memory: format!("{:.0}G", p.memory_gb()),
                                max_time: p.max_walltime_str(),
                                gpus: p
                                    .gpus_per_node
                                    .map(|g| g.to_string())
                                    .unwrap_or_else(|| "-".to_string()),
                                notes: if notes.is_empty() {
                                    "-".to_string()
                                } else {
                                    notes.join(", ")
                                },
                            }
                        })
                        .collect();

                    display_table_with_count(&rows, "matching partitions");

                    if let Some(best) = best {
                        println!();
                        println!("Recommended: {} partition", best.name);
                        if best.requires_explicit_request {
                            println!("  Use: --partition={}", best.name);
                        } else {
                            println!("  (Auto-routed based on requirements)");
                        }
                    }
                }
            }
        }
    }
}
