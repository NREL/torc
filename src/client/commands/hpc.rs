//! HPC system profile commands
//!
//! Commands for listing, detecting, and querying HPC system profiles.

use clap::Subcommand;
use std::collections::HashMap;
use std::process::Command;
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

    /// Generate an HPC profile from Slurm cluster info
    ///
    /// This command queries the current Slurm cluster using sinfo and scontrol
    /// to automatically generate an HPC profile configuration.
    Generate {
        /// Profile name (defaults to SLURM_CLUSTER_NAME or hostname)
        #[arg(long)]
        name: Option<String>,

        /// Display name for the profile
        #[arg(long)]
        display_name: Option<String>,

        /// Output file (defaults to stdout)
        #[arg(short, long)]
        output: Option<std::path::PathBuf>,

        /// Skip standby partitions (names ending in -stdby)
        #[arg(long)]
        skip_stdby: bool,
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

        HpcCommands::Generate {
            name,
            display_name,
            output,
            skip_stdby,
        } => match generate_profile_from_slurm(name.clone(), display_name.clone(), *skip_stdby) {
            Ok(toml_output) => {
                if let Some(path) = output {
                    if let Err(e) = std::fs::write(path, &toml_output) {
                        eprintln!("Failed to write output file: {}", e);
                        std::process::exit(1);
                    }
                    eprintln!("Profile written to: {}", path.display());
                } else {
                    println!("{}", toml_output);
                }
            }
            Err(e) => {
                eprintln!("Failed to generate profile: {}", e);
                std::process::exit(1);
            }
        },
    }
}

/// Information about a partition gathered from sinfo
#[derive(Debug)]
pub struct SinfoPartition {
    pub name: String,
    pub cpus: u32,
    pub memory_mb: u64,
    pub timelimit_secs: u64,
    pub gres: Option<String>,
}

/// Additional partition info from scontrol
#[derive(Debug, Default)]
struct ScontrolPartitionInfo {
    min_nodes: Option<u32>,
    max_nodes: Option<u32>,
    oversubscribe: Option<String>,
    default_qos: Option<String>,
}

/// Generate an HPC profile from the current Slurm cluster
fn generate_profile_from_slurm(
    name: Option<String>,
    display_name: Option<String>,
    skip_stdby: bool,
) -> Result<String, String> {
    // Get cluster name
    let cluster_name = name.unwrap_or_else(|| {
        std::env::var("SLURM_CLUSTER_NAME")
            .or_else(|_| {
                // Try to get from scontrol
                Command::new("scontrol")
                    .args(["show", "config"])
                    .output()
                    .ok()
                    .and_then(|out| {
                        String::from_utf8(out.stdout).ok().and_then(|s| {
                            s.lines()
                                .find(|l| l.starts_with("ClusterName"))
                                .and_then(|l| l.split('=').nth(1))
                                .map(|s| s.trim().to_string())
                        })
                    })
                    .ok_or(())
            })
            .unwrap_or_else(|_| {
                // Fall back to hostname
                hostname::get()
                    .map(|h| h.to_string_lossy().to_string())
                    .unwrap_or_else(|_| "unknown".to_string())
            })
    });

    let display = display_name.unwrap_or_else(|| {
        // Capitalize first letter
        let mut chars = cluster_name.chars();
        match chars.next() {
            None => cluster_name.clone(),
            Some(c) => c.to_uppercase().chain(chars).collect(),
        }
    });

    // Get partition info from sinfo
    let sinfo_partitions = parse_sinfo_output()?;

    if sinfo_partitions.is_empty() {
        return Err("No partitions found. Is Slurm available on this system?".to_string());
    }

    // Group partitions by name (Slurm reports each node type separately)
    let mut partition_map: HashMap<String, Vec<&SinfoPartition>> = HashMap::new();
    for sp in &sinfo_partitions {
        partition_map.entry(sp.name.clone()).or_default().push(sp);
    }

    // Deduplicate and merge partition info
    let mut partitions = Vec::new();
    let mut seen_names: Vec<String> = partition_map.keys().cloned().collect();
    seen_names.sort(); // Consistent ordering

    for name in seen_names {
        // Skip standby partitions if requested
        if skip_stdby && name.ends_with("-stdby") {
            continue;
        }
        let group = partition_map.get(&name).unwrap();

        // Get scontrol info (same for all nodes in partition)
        let scontrol_info = parse_scontrol_partition(&name).unwrap_or_default();

        // Merge partition info from all node types:
        // - CPUs: use minimum (guaranteed on all nodes)
        // - Memory: use minimum (guaranteed on all nodes)
        // - Walltime: should be same, use max to be safe
        // - GPUs: if any node has GPUs, capture that info
        let mut min_cpus = u32::MAX;
        let mut min_memory = u64::MAX;
        let mut max_walltime = 0u64;
        let mut gpus_per_node: Option<u32> = None;
        let mut gpu_type: Option<String> = None;

        for sp in group {
            min_cpus = min_cpus.min(sp.cpus);
            min_memory = min_memory.min(sp.memory_mb);
            max_walltime = max_walltime.max(sp.timelimit_secs);

            // Capture GPU info if present
            let (gp, gt) = parse_gres(&sp.gres);
            if gp.is_some() {
                gpus_per_node = gp;
                gpu_type = gt;
            }
        }

        // Fallback: infer GPU info from partition name if GRES wasn't reported
        if gpus_per_node.is_none()
            && let Some((inferred_count, inferred_type)) = infer_gpu_from_name(&name)
        {
            gpus_per_node = Some(inferred_count);
            gpu_type = Some(inferred_type);
        }

        // Determine if shared based on OverSubscribe setting or partition name
        let shared = scontrol_info.oversubscribe.as_ref().is_some_and(|o| {
            o.to_lowercase().contains("yes") || o.to_lowercase().contains("force")
        }) || name.to_lowercase().contains("shared")
            || gpus_per_node.is_some(); // GPU partitions are typically shared

        let partition = HpcPartitionConfig {
            name,
            description: String::new(),
            cpus_per_node: min_cpus,
            memory_mb: min_memory,
            max_walltime_secs: max_walltime,
            gpus_per_node,
            gpu_type,
            gpu_memory_gb: None,
            shared,
            requires_explicit_request: false,
        };

        partitions.push(partition);
    }

    // Generate TOML output
    generate_toml_profile(&cluster_name, &display, &partitions)
}

/// Parse output from sinfo command
fn parse_sinfo_output() -> Result<Vec<SinfoPartition>, String> {
    // Run sinfo with specific format
    // %P = partition, %c = cpus, %m = memory, %l = timelimit, %G = gres, %D = nodes
    let output = Command::new("sinfo")
        .args(["-e", "-o", "%P|%c|%m|%l|%G|%D", "--noheader"])
        .output()
        .map_err(|e| format!("Failed to run sinfo: {}", e))?;

    if !output.status.success() {
        return Err(format!(
            "sinfo failed: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    parse_sinfo_string(&stdout)
}

/// Parse sinfo output string into partition info
/// Format: "%P|%c|%m|%l|%G|%D" (partition|cpus|memory|timelimit|gres|nodes)
pub fn parse_sinfo_string(input: &str) -> Result<Vec<SinfoPartition>, String> {
    let mut partitions = Vec::new();

    for line in input.lines() {
        let parts: Vec<&str> = line.split('|').collect();
        if parts.len() < 6 {
            continue;
        }

        // Remove trailing * from default partition name
        let name = parts[0].trim_end_matches('*').to_string();

        let cpus: u32 = parts[1].parse().unwrap_or(1);

        // Memory is in MB
        let memory_mb: u64 = parts[2].parse().unwrap_or(1024);

        // Parse timelimit (formats: "infinite", "1-00:00:00", "4:00:00", "30:00")
        let timelimit_secs = parse_slurm_timelimit(parts[3]);

        let gres = if parts[4] == "(null)" || parts[4].is_empty() {
            None
        } else {
            Some(parts[4].to_string())
        };

        partitions.push(SinfoPartition {
            name,
            cpus,
            memory_mb,
            timelimit_secs,
            gres,
        });
    }

    Ok(partitions)
}

/// Parse timelimit string from Slurm format to seconds
fn parse_slurm_timelimit(s: &str) -> u64 {
    let s = s.trim();

    if s == "infinite" || s == "UNLIMITED" {
        return 365 * 24 * 3600; // 1 year as "infinite"
    }

    // Try formats: "D-HH:MM:SS", "HH:MM:SS", "MM:SS", "MM"
    if let Some((days, rest)) = s.split_once('-') {
        let days: u64 = days.parse().unwrap_or(0);
        let time_secs = parse_time_component(rest);
        return days * 24 * 3600 + time_secs;
    }

    parse_time_component(s)
}

/// Parse time component (HH:MM:SS, MM:SS, or MM)
fn parse_time_component(s: &str) -> u64 {
    let parts: Vec<&str> = s.split(':').collect();
    match parts.len() {
        3 => {
            let hours: u64 = parts[0].parse().unwrap_or(0);
            let mins: u64 = parts[1].parse().unwrap_or(0);
            let secs: u64 = parts[2].parse().unwrap_or(0);
            hours * 3600 + mins * 60 + secs
        }
        2 => {
            let mins: u64 = parts[0].parse().unwrap_or(0);
            let secs: u64 = parts[1].parse().unwrap_or(0);
            mins * 60 + secs
        }
        1 => {
            let mins: u64 = parts[0].parse().unwrap_or(0);
            mins * 60
        }
        _ => 0,
    }
}

/// Parse scontrol show partition output for additional info
fn parse_scontrol_partition(partition_name: &str) -> Result<ScontrolPartitionInfo, String> {
    let output = Command::new("scontrol")
        .args(["show", "partition", partition_name])
        .output()
        .map_err(|e| format!("Failed to run scontrol: {}", e))?;

    if !output.status.success() {
        return Err(format!(
            "scontrol failed: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let mut info = ScontrolPartitionInfo::default();

    // Parse key=value pairs
    let mut kv_map: HashMap<&str, &str> = HashMap::new();
    for line in stdout.lines() {
        for part in line.split_whitespace() {
            if let Some((key, value)) = part.split_once('=') {
                kv_map.insert(key, value);
            }
        }
    }

    if let Some(v) = kv_map.get("MinNodes") {
        info.min_nodes = v.parse().ok();
    }
    if let Some(v) = kv_map.get("MaxNodes")
        && *v != "UNLIMITED"
    {
        info.max_nodes = v.parse().ok();
    }
    if let Some(v) = kv_map.get("OverSubscribe") {
        info.oversubscribe = Some(v.to_string());
    }
    if let Some(v) = kv_map.get("QoS")
        && *v != "N/A"
    {
        info.default_qos = Some(v.to_string());
    }

    Ok(info)
}

/// Infer GPU info from partition name when GRES isn't reported by Slurm.
///
/// This is a heuristic fallback used when `sinfo` doesn't report GRES information.
/// Common partition naming patterns: "gpu-h100", "gpu-a100", "gpu-v100", "debug-gpu"
///
/// **Important**: The default of 4 GPUs per node is a reasonable estimate for many
/// HPC clusters, but actual counts vary (1, 2, 4, or 8 GPUs per node are common).
/// Administrators should review and adjust the generated profile as needed.
fn infer_gpu_from_name(name: &str) -> Option<(u32, String)> {
    let name_lower = name.to_lowercase();

    // Must contain "gpu" to be considered a GPU partition
    if !name_lower.contains("gpu") {
        return None;
    }

    // Try to extract GPU type from name
    // Common patterns: gpu-h100, gpu-a100, gpu-v100, gpu-h100s, gpu-h100l
    // Default count of 4 is a heuristic - actual GPU counts vary by cluster
    let gpu_types = [
        ("h100", "h100", 4),
        ("a100", "a100", 4),
        ("v100", "v100", 4),
        ("a40", "a40", 4),
        ("a30", "a30", 4),
        ("l40", "l40", 4),
    ];

    for (pattern, gpu_type, default_count) in gpu_types {
        if name_lower.contains(pattern) {
            return Some((default_count, gpu_type.to_string()));
        }
    }

    // Generic GPU partition without specific type
    // Default to 4 GPUs - this is a heuristic; verify against actual cluster config
    Some((4, "gpu".to_string()))
}

/// Parse GRES string to extract GPU count and type
/// Examples: "gpu:4", "gpu:a100:4", "gpu:h100:2,nvme:1"
fn parse_gres(gres: &Option<String>) -> (Option<u32>, Option<String>) {
    let gres = match gres {
        Some(g) => g,
        None => return (None, None),
    };

    // Find gpu entry (might be multiple GRES separated by comma)
    for entry in gres.split(',') {
        // Strip socket info like "(S:0-3)" before parsing
        // This info can contain colons which would confuse the split
        let entry = entry.split('(').next().unwrap_or(entry);

        let parts: Vec<&str> = entry.split(':').collect();
        if parts.first() != Some(&"gpu") {
            continue;
        }

        match parts.len() {
            2 => {
                // gpu:COUNT
                let count: u32 = parts[1].parse().unwrap_or(0);
                if count > 0 {
                    return (Some(count), None);
                }
            }
            3 => {
                // gpu:TYPE:COUNT
                let gpu_type = parts[1].to_string();
                let count: u32 = parts[2].parse().unwrap_or(0);
                if count > 0 {
                    return (Some(count), Some(gpu_type));
                }
            }
            _ => {}
        }
    }

    (None, None)
}

/// Generate TOML configuration for the profile
fn generate_toml_profile(
    name: &str,
    display_name: &str,
    partitions: &[HpcPartitionConfig],
) -> Result<String, String> {
    let mut output = String::new();

    // Header comment
    output.push_str(&format!(
        "# HPC profile for {} generated from Slurm\n",
        display_name
    ));
    output.push_str(&format!(
        "# Generated: {}\n",
        chrono::Utc::now().format("%Y-%m-%d %H:%M:%S UTC")
    ));
    output.push_str("#\n");
    output.push_str("# To use this profile, add it to your torc config file:\n");
    output.push_str("#   ~/.config/torc/config.toml (Linux/macOS)\n");
    output.push_str("#   %APPDATA%\\torc\\config.toml (Windows)\n");
    output.push_str("#\n");
    output.push_str("# You may want to review and adjust:\n");
    output.push_str(
        "#   - requires_explicit_request: set to true for partitions that shouldn't auto-route\n",
    );
    output.push_str("#   - gpu_memory_gb: add GPU memory if known\n");
    output.push_str("#   - description: add human-readable descriptions\n");
    output.push('\n');

    // Profile header
    output.push_str(&format!("[client.hpc.custom_profiles.{}]\n", name));
    output.push_str(&format!("display_name = \"{}\"\n", display_name));

    // Try to generate hostname detection pattern
    if let Ok(hostname) = hostname::get() {
        let hostname = hostname.to_string_lossy();
        // Extract domain pattern (e.g., "node01.cluster.edu" -> ".*\\.cluster\\.edu")
        if let Some(dot_pos) = hostname.find('.') {
            let domain = &hostname[dot_pos + 1..];
            let pattern = format!(".*\\\\.{}", domain.replace('.', "\\\\."));
            output.push_str(&format!("detect_hostname = \"{}\"\n", pattern));
        }
    }

    output.push('\n');

    // Partitions
    for partition in partitions {
        output.push_str(&format!(
            "[[client.hpc.custom_profiles.{}.partitions]]\n",
            name
        ));
        output.push_str(&format!("name = \"{}\"\n", partition.name));
        output.push_str(&format!("cpus_per_node = {}\n", partition.cpus_per_node));
        output.push_str(&format!("memory_mb = {}\n", partition.memory_mb));
        output.push_str(&format!(
            "max_walltime_secs = {}\n",
            partition.max_walltime_secs
        ));

        if let Some(gpus) = partition.gpus_per_node {
            output.push_str(&format!("gpus_per_node = {}\n", gpus));
        }
        if let Some(ref gpu_type) = partition.gpu_type {
            output.push_str(&format!("gpu_type = \"{}\"\n", gpu_type));
        }
        if partition.shared {
            output.push_str("shared = true\n");
        }

        output.push('\n');
    }

    Ok(output)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_gres_simple_count() {
        // gpu:4
        let (count, gpu_type) = parse_gres(&Some("gpu:4".to_string()));
        assert_eq!(count, Some(4));
        assert_eq!(gpu_type, None);
    }

    #[test]
    fn test_parse_gres_with_type() {
        // gpu:a100:4
        let (count, gpu_type) = parse_gres(&Some("gpu:a100:4".to_string()));
        assert_eq!(count, Some(4));
        assert_eq!(gpu_type, Some("a100".to_string()));
    }

    #[test]
    fn test_parse_gres_with_socket_info() {
        // gpu:h100:4(S:0-3)
        let (count, gpu_type) = parse_gres(&Some("gpu:h100:4(S:0-3)".to_string()));
        assert_eq!(count, Some(4));
        assert_eq!(gpu_type, Some("h100".to_string()));
    }

    #[test]
    fn test_parse_gres_simple_with_socket_info() {
        // gpu:4(S:0-3)
        let (count, gpu_type) = parse_gres(&Some("gpu:4(S:0-3)".to_string()));
        assert_eq!(count, Some(4));
        assert_eq!(gpu_type, None);
    }

    #[test]
    fn test_parse_gres_multiple_resources() {
        // gpu:a100:2,nvme:1
        let (count, gpu_type) = parse_gres(&Some("gpu:a100:2,nvme:1".to_string()));
        assert_eq!(count, Some(2));
        assert_eq!(gpu_type, Some("a100".to_string()));
    }

    #[test]
    fn test_parse_gres_none() {
        let (count, gpu_type) = parse_gres(&None);
        assert_eq!(count, None);
        assert_eq!(gpu_type, None);
    }

    #[test]
    fn test_parse_gres_no_gpu() {
        // nvme:1
        let (count, gpu_type) = parse_gres(&Some("nvme:1".to_string()));
        assert_eq!(count, None);
        assert_eq!(gpu_type, None);
    }
}
