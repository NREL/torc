//! HPC system profile commands
//!
//! Commands for listing, detecting, and querying HPC system profiles.

use clap::Subcommand;
use tabled::Tabled;

use super::output::print_json;

use crate::client::commands::slurm::{parse_memory_mb, parse_walltime_secs};
use crate::client::hpc::{HpcDetection, HpcPartition, HpcProfile, HpcProfileRegistry};
use crate::config::{ClientHpcConfig, HpcPartitionConfig, HpcProfileConfig, TorcConfig};

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
    if let Some(env_var) = &config.detect_env_var
        && let Some((var_name, var_value)) = env_var.split_once('=')
    {
        detection.push(HpcDetection::EnvVar {
            name: var_name.to_string(),
            value: var_value.to_string(),
        });
    }

    // Parse hostname pattern
    if let Some(pattern) = &config.detect_hostname {
        detection.push(HpcDetection::HostnamePattern {
            pattern: pattern.clone(),
        });
    }

    // Convert partitions
    let partitions: Vec<HpcPartition> = config.partitions.iter().map(config_to_partition).collect();

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
                print_json(&json_output, "HPC profiles");
            } else {
                println!("Known HPC profiles:\n");
                display_table_with_count(&rows, "profiles");
            }
        }

        HpcCommands::Detect => {
            if let Some(profile) = registry.detect() {
                if format == "json" {
                    print_json(
                        &serde_json::json!({
                            "detected": true,
                            "name": profile.name,
                            "display_name": profile.display_name,
                            "description": profile.description,
                        }),
                        "HPC detection",
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
            } else if format == "json" {
                print_json(
                    &serde_json::json!({
                        "detected": false,
                        "message": "No known HPC system detected",
                    }),
                    "HPC detection",
                );
            } else {
                println!("No known HPC system detected.");
                println!("\nKnown systems:");
                for profile in registry.profiles() {
                    println!("  - {} ({})", profile.display_name, profile.name);
                }
            }
        }

        HpcCommands::Show { name } => {
            if let Some(profile) = registry.get(name) {
                if format == "json" {
                    print_json(&profile, "HPC profile");
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
                print_json(&partitions, "partitions");
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
                print_json(&output, "partition match");
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
