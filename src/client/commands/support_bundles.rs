//! Support bundle collection and parsing commands
//!
//! Collects all torc-related log files for a workflow into a compressed tarball
//! for debugging and support purposes.

use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::commands::{get_env_user_name, print_error, select_workflow_interactively};
use flate2::Compression;
use flate2::read::GzDecoder;
use flate2::write::GzEncoder;
use regex::Regex;
use std::collections::HashMap;
use std::fs::File;
use std::io::Read;
use std::path::{Path, PathBuf};
use tar::{Archive, Builder};

/// Support bundle subcommands
#[derive(clap::Subcommand)]
pub enum SupportBundleCommands {
    /// Collect all log files for a workflow into a support bundle tarball
    Collect {
        /// Workflow ID to collect logs for
        #[arg()]
        workflow_id: Option<i64>,
        /// Output directory where logs are stored (the same directory passed to `torc run`)
        #[arg(short, long, default_value = "output")]
        output_dir: PathBuf,
        /// Directory to write the support bundle to
        #[arg(long, default_value = ".")]
        bundle_dir: PathBuf,
    },
    /// Parse a support bundle and extract error information
    Parse {
        /// Path to the support bundle tarball
        #[arg()]
        bundle_path: PathBuf,
    },
}

/// Handle support bundle commands
pub fn handle_support_bundle_commands(config: &Configuration, command: &SupportBundleCommands) {
    match command {
        SupportBundleCommands::Collect {
            workflow_id,
            output_dir,
            bundle_dir,
        } => {
            collect_bundle(config, *workflow_id, output_dir, bundle_dir);
        }
        SupportBundleCommands::Parse { bundle_path } => {
            parse_bundle(bundle_path);
        }
    }
}

/// Collect all log files for a workflow into a support bundle
fn collect_bundle(
    config: &Configuration,
    workflow_id: Option<i64>,
    output_dir: &Path,
    bundle_dir: &Path,
) {
    // Get or select workflow ID
    let user = get_env_user_name();
    let wf_id = match workflow_id {
        Some(id) => id,
        None => match select_workflow_interactively(config, &user) {
            Ok(id) => id,
            Err(e) => {
                eprintln!("Error selecting workflow: {}", e);
                std::process::exit(1);
            }
        },
    };

    // Create the bundle filename
    let bundle_filename = format!("wf{}.tar.gz", wf_id);
    let bundle_path = bundle_dir.join(&bundle_filename);

    // Get workflow info for metadata
    let workflow = match default_api::get_workflow(config, wf_id) {
        Ok(w) => w,
        Err(e) => {
            print_error("getting workflow", &e);
            std::process::exit(1);
        }
    };

    println!(
        "Collecting support bundle for workflow {} ({})",
        wf_id, workflow.name
    );
    println!("Output directory: {}", output_dir.display());
    println!("Bundle path: {}", bundle_path.display());

    // Create the tarball
    let tar_file = match File::create(&bundle_path) {
        Ok(f) => f,
        Err(e) => {
            eprintln!("Error creating bundle file: {}", e);
            std::process::exit(1);
        }
    };
    let encoder = GzEncoder::new(tar_file, Compression::default());
    let mut tar_builder = Builder::new(encoder);

    // Collect files matching workflow patterns
    let wf_pattern = format!("wf{}", wf_id);
    let mut files_collected = 0;
    let mut total_size: u64 = 0;

    // Scan output directory for matching files
    if output_dir.exists() {
        files_collected +=
            collect_matching_files(&mut tar_builder, output_dir, &wf_pattern, &mut total_size);

        // Also check job_stdio subdirectory
        let job_stdio_dir = output_dir.join("job_stdio");
        if job_stdio_dir.exists() {
            files_collected += collect_matching_files(
                &mut tar_builder,
                &job_stdio_dir,
                &wf_pattern,
                &mut total_size,
            );
        }
    } else {
        eprintln!(
            "Warning: Output directory does not exist: {}",
            output_dir.display()
        );
    }

    // Write workflow metadata as a JSON file in the bundle
    let metadata = serde_json::json!({
        "workflow_id": wf_id,
        "workflow_name": workflow.name,
        "workflow_description": workflow.description,
        "workflow_user": workflow.user,
        "collected_at": chrono::Utc::now().to_rfc3339(),
        "files_collected": files_collected,
        "total_size_bytes": total_size,
    });
    let metadata_json = serde_json::to_string_pretty(&metadata).unwrap();

    // Add metadata to the tarball
    let mut header = tar::Header::new_gnu();
    header.set_size(metadata_json.len() as u64);
    header.set_mode(0o644);
    header.set_cksum();
    tar_builder
        .append_data(
            &mut header,
            "bundle_metadata.json",
            metadata_json.as_bytes(),
        )
        .unwrap();

    // Finalize the tarball
    match tar_builder.into_inner() {
        Ok(encoder) => {
            if let Err(e) = encoder.finish() {
                eprintln!("Error finishing compression: {}", e);
                std::process::exit(1);
            }
        }
        Err(e) => {
            eprintln!("Error finalizing tarball: {}", e);
            std::process::exit(1);
        }
    }

    println!();
    println!("Support bundle created successfully:");
    println!("  File: {}", bundle_path.display());
    println!("  Files collected: {}", files_collected);
    println!("  Total size: {} bytes", total_size);
    println!();
    println!("To analyze the bundle, run:");
    println!("  torc support-bundles parse {}", bundle_path.display());
}

/// Collect files matching the workflow pattern from a directory
fn collect_matching_files<W: std::io::Write>(
    tar_builder: &mut Builder<W>,
    dir: &Path,
    wf_pattern: &str,
    total_size: &mut u64,
) -> usize {
    let mut count = 0;

    let entries = match std::fs::read_dir(dir) {
        Ok(e) => e,
        Err(e) => {
            eprintln!("Warning: Cannot read directory {}: {}", dir.display(), e);
            return 0;
        }
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_file() {
            let filename = path.file_name().unwrap_or_default().to_string_lossy();
            if filename.contains(wf_pattern) {
                match File::open(&path) {
                    Ok(mut file) => {
                        let metadata = file.metadata().unwrap();
                        *total_size += metadata.len();

                        // Use relative path in the archive
                        let archive_name = if let Some(parent) = path.parent() {
                            if let Some(parent_name) = parent.file_name() {
                                format!("{}/{}", parent_name.to_string_lossy(), filename)
                            } else {
                                filename.to_string()
                            }
                        } else {
                            filename.to_string()
                        };

                        if tar_builder.append_file(&archive_name, &mut file).is_ok() {
                            println!("  Added: {}", archive_name);
                            count += 1;
                        }
                    }
                    Err(e) => {
                        eprintln!("Warning: Cannot read file {}: {}", path.display(), e);
                    }
                }
            }
        }
    }

    count
}

/// Error patterns to search for in log files
struct ErrorPattern {
    name: &'static str,
    pattern: Regex,
    severity: ErrorSeverity,
}

#[derive(Debug, Clone, Copy, PartialEq)]
#[allow(dead_code)]
enum ErrorSeverity {
    Error,
    Warning,
    Info,
}

impl std::fmt::Display for ErrorSeverity {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ErrorSeverity::Error => write!(f, "ERROR"),
            ErrorSeverity::Warning => write!(f, "WARN"),
            ErrorSeverity::Info => write!(f, "INFO"),
        }
    }
}

/// Detected error in a log file
#[derive(Debug)]
struct DetectedError {
    file: String,
    line_number: usize,
    pattern_name: String,
    severity: ErrorSeverity,
    line_content: String,
}

/// Parse a support bundle and extract error information
fn parse_bundle(bundle_path: &Path) {
    if !bundle_path.exists() {
        eprintln!("Error: Bundle file not found: {}", bundle_path.display());
        std::process::exit(1);
    }

    println!("Parsing support bundle: {}", bundle_path.display());
    println!();

    // Open and decompress the tarball
    let file = match File::open(bundle_path) {
        Ok(f) => f,
        Err(e) => {
            eprintln!("Error opening bundle: {}", e);
            std::process::exit(1);
        }
    };
    let decoder = GzDecoder::new(file);
    let mut archive = Archive::new(decoder);

    // Define error patterns to search for
    let patterns = vec![
        ErrorPattern {
            name: "OOM Killed",
            pattern: Regex::new(r"(?i)(out of memory|oom|killed|cannot allocate memory)").unwrap(),
            severity: ErrorSeverity::Error,
        },
        ErrorPattern {
            name: "Timeout",
            pattern: Regex::new(r"(?i)(timeout|time limit|timed out|walltime)").unwrap(),
            severity: ErrorSeverity::Error,
        },
        ErrorPattern {
            name: "Segmentation Fault",
            pattern: Regex::new(r"(?i)(segmentation fault|segfault|sigsegv)").unwrap(),
            severity: ErrorSeverity::Error,
        },
        ErrorPattern {
            name: "Permission Denied",
            pattern: Regex::new(r"(?i)(permission denied|access denied|EACCES)").unwrap(),
            severity: ErrorSeverity::Error,
        },
        ErrorPattern {
            name: "File Not Found",
            pattern: Regex::new(r"(?i)(no such file|file not found|ENOENT)").unwrap(),
            severity: ErrorSeverity::Error,
        },
        ErrorPattern {
            name: "Disk Full",
            pattern: Regex::new(r"(?i)(no space left|disk full|quota exceeded|ENOSPC)").unwrap(),
            severity: ErrorSeverity::Error,
        },
        ErrorPattern {
            name: "Connection Error",
            pattern: Regex::new(
                r"(?i)(connection refused|connection reset|network unreachable|ECONNREFUSED)",
            )
            .unwrap(),
            severity: ErrorSeverity::Error,
        },
        ErrorPattern {
            name: "Rust Panic",
            pattern: Regex::new(r"thread .* panicked at").unwrap(),
            severity: ErrorSeverity::Error,
        },
        ErrorPattern {
            name: "Python Exception",
            pattern: Regex::new(r"(Traceback \(most recent call last\)|raise \w+Error)").unwrap(),
            severity: ErrorSeverity::Error,
        },
        ErrorPattern {
            name: "Generic Error",
            pattern: Regex::new(r"(?i)\b(error|failed|failure|exception)\b").unwrap(),
            severity: ErrorSeverity::Warning,
        },
        ErrorPattern {
            name: "Slurm Error",
            pattern: Regex::new(r"(?i)(slurmstepd|slurm_|CANCELLED|TIMEOUT|OUT_OF_MEMORY)")
                .unwrap(),
            severity: ErrorSeverity::Error,
        },
    ];

    let mut errors: Vec<DetectedError> = Vec::new();
    let mut files_parsed = 0;
    let mut metadata: Option<serde_json::Value> = None;

    // Process each file in the archive
    let entries = match archive.entries() {
        Ok(e) => e,
        Err(e) => {
            eprintln!("Error reading archive entries: {}", e);
            std::process::exit(1);
        }
    };

    for entry_result in entries {
        let mut entry = match entry_result {
            Ok(e) => e,
            Err(e) => {
                eprintln!("Warning: Error reading entry: {}", e);
                continue;
            }
        };

        let path = match entry.path() {
            Ok(p) => p.to_path_buf(),
            Err(_) => continue,
        };
        let filename = path.to_string_lossy().to_string();

        // Check if this is the metadata file
        if filename == "bundle_metadata.json" {
            let mut content = String::new();
            if entry.read_to_string(&mut content).is_ok() {
                metadata = serde_json::from_str(&content).ok();
            }
            continue;
        }

        // Parse log files
        if filename.ends_with(".log") || filename.ends_with(".o") || filename.ends_with(".e") {
            files_parsed += 1;

            // Read entry content into memory
            let mut content = String::new();
            if entry.read_to_string(&mut content).is_err() {
                continue;
            }

            for (line_number, line) in content.lines().enumerate() {
                for pattern in &patterns {
                    if pattern.pattern.is_match(line) {
                        errors.push(DetectedError {
                            file: filename.clone(),
                            line_number: line_number + 1,
                            pattern_name: pattern.name.to_string(),
                            severity: pattern.severity,
                            line_content: truncate_line(line, 120),
                        });
                        break; // Only report first matching pattern per line
                    }
                }
            }
        }
    }

    // Print metadata if available
    if let Some(meta) = &metadata {
        println!("Bundle Information:");
        println!(
            "  Workflow ID: {}",
            meta.get("workflow_id").unwrap_or(&serde_json::Value::Null)
        );
        println!(
            "  Workflow Name: {}",
            meta.get("workflow_name")
                .unwrap_or(&serde_json::Value::Null)
        );
        println!(
            "  Workflow Status: {}",
            meta.get("workflow_status")
                .unwrap_or(&serde_json::Value::Null)
        );
        println!(
            "  Collected At: {}",
            meta.get("collected_at").unwrap_or(&serde_json::Value::Null)
        );
        println!();
    }

    println!("Files parsed: {}", files_parsed);
    println!();

    if errors.is_empty() {
        println!("No errors detected in log files.");
        return;
    }

    // Group errors by file
    let mut errors_by_file: HashMap<String, Vec<&DetectedError>> = HashMap::new();
    for error in &errors {
        errors_by_file
            .entry(error.file.clone())
            .or_default()
            .push(error);
    }

    // Count errors by severity
    let error_count = errors
        .iter()
        .filter(|e| e.severity == ErrorSeverity::Error)
        .count();
    let warning_count = errors
        .iter()
        .filter(|e| e.severity == ErrorSeverity::Warning)
        .count();

    println!("Detected Issues:");
    println!("  Errors: {}", error_count);
    println!("  Warnings: {}", warning_count);
    println!();

    // Print errors grouped by file
    for (file, file_errors) in &errors_by_file {
        println!("{}:", file);
        for error in file_errors {
            if error.severity == ErrorSeverity::Error {
                println!(
                    "  [{}] Line {}: {} - {}",
                    error.severity, error.line_number, error.pattern_name, error.line_content
                );
            }
        }
        println!();
    }

    // Summary of error types
    println!("Error Type Summary:");
    let mut pattern_counts: HashMap<String, usize> = HashMap::new();
    for error in &errors {
        if error.severity == ErrorSeverity::Error {
            *pattern_counts
                .entry(error.pattern_name.clone())
                .or_default() += 1;
        }
    }
    for (pattern, count) in pattern_counts.iter() {
        println!("  {}: {} occurrence(s)", pattern, count);
    }
}

/// Truncate a line to a maximum length
fn truncate_line(s: &str, max_len: usize) -> String {
    if s.len() <= max_len {
        s.to_string()
    } else {
        format!("{}...", &s[..max_len.saturating_sub(3)])
    }
}
