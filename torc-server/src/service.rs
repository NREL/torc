//! Service management for torc-server
//!
//! This module provides cross-platform service installation and management
//! using systemd (Linux), launchd (macOS), or Windows Service.

use anyhow::{Context, Result};
use service_manager::*;
use std::env;
use std::ffi::OsString;
use std::path::PathBuf;

const SERVICE_NAME: &str = "torc-server";

/// Service management commands
#[derive(Debug, Clone)]
pub enum ServiceCommand {
    Install,
    Uninstall,
    Start,
    Stop,
    Status,
}

/// Configuration for service installation
#[derive(Debug, Clone)]
pub struct ServiceConfig {
    pub log_dir: Option<PathBuf>,
    pub database: Option<String>,
    pub url: String,
    pub port: u16,
    pub threads: u32,
    pub auth_file: Option<String>,
    pub require_auth: bool,
    pub log_level: String,
    pub json_logs: bool,
    pub unblock_interval_seconds: f64,
}

impl ServiceConfig {
    /// Create default configuration for system-level service
    fn default_system() -> Self {
        Self {
            log_dir: Some(PathBuf::from("/var/log/torc")),
            database: Some("/var/lib/torc/torc.db".to_string()),
            url: "0.0.0.0".to_string(),
            port: 8080,
            threads: 4,
            auth_file: None,
            require_auth: false,
            log_level: "info".to_string(),
            json_logs: false,
            unblock_interval_seconds: 60.0,
        }
    }

    /// Create default configuration for user-level service
    fn default_user() -> Self {
        // Get user's home directory
        let home = env::var("HOME").unwrap_or_else(|_| ".".to_string());

        Self {
            log_dir: Some(PathBuf::from(format!("{}/.torc/logs", home))),
            database: Some(format!("{}/.torc/torc.db", home)),
            url: "0.0.0.0".to_string(),
            port: 8080,
            threads: 4,
            auth_file: None,
            require_auth: false,
            log_level: "info".to_string(),
            json_logs: false,
            unblock_interval_seconds: 60.0,
        }
    }

    /// Merge user-provided configuration with defaults
    /// User-provided values (even if None) take precedence, but we fill in sensible defaults
    fn merge_with_defaults(user_config: &ServiceConfig, user_level: bool) -> Self {
        let defaults = if user_level {
            Self::default_user()
        } else {
            Self::default_system()
        };

        Self {
            // Use user config's log_dir if provided, otherwise use default
            log_dir: user_config.log_dir.clone().or(defaults.log_dir),
            database: user_config.database.clone().or(defaults.database),
            url: user_config.url.clone(),
            port: user_config.port,
            threads: user_config.threads,
            auth_file: user_config.auth_file.clone(),
            require_auth: user_config.require_auth,
            log_level: user_config.log_level.clone(),
            json_logs: user_config.json_logs,
            unblock_interval_seconds: user_config.unblock_interval_seconds,
        }
    }
}

impl Default for ServiceConfig {
    fn default() -> Self {
        Self::default_system()
    }
}

/// Get the service manager for the current platform
fn get_service_manager(user_level: bool) -> Result<Box<dyn ServiceManager>> {
    let level = if user_level {
        ServiceLevel::User
    } else {
        ServiceLevel::System
    };

    let mut manager = <dyn ServiceManager>::native()
        .context("Failed to detect native service manager for this platform")?;

    manager
        .set_level(level)
        .context("Failed to set service level")?;

    Ok(manager)
}

/// Build service label
fn service_label() -> ServiceLabel {
    ServiceLabel {
        qualifier: Some("com.github".to_string()),
        organization: Some("torc".to_string()),
        application: SERVICE_NAME.to_string(),
    }
}

/// Install the service with the given configuration
pub fn install_service(config: &ServiceConfig, user_level: bool) -> Result<()> {
    let manager = get_service_manager(user_level)?;

    // Get the path to the current executable
    let exe_path = env::current_exe().context("Failed to get current executable path")?;

    // Build command-line arguments for the service
    let mut args: Vec<OsString> = vec![];

    if let Some(ref log_dir) = config.log_dir {
        args.push("--log-dir".into());
        args.push(log_dir.as_os_str().to_owned());
    }

    if let Some(ref database) = config.database {
        args.push("--database".into());
        args.push(database.into());
    }

    args.push("--url".into());
    args.push(config.url.clone().into());

    args.push("--port".into());
    args.push(config.port.to_string().into());

    args.push("--threads".into());
    args.push(config.threads.to_string().into());

    args.push("--log-level".into());
    args.push(config.log_level.clone().into());

    if config.json_logs {
        args.push("--json-logs".into());
    }

    if let Some(ref auth_file) = config.auth_file {
        args.push("--auth-file".into());
        args.push(auth_file.into());
    }

    if config.require_auth {
        args.push("--require-auth".into());
    }

    args.push("--unblock-interval-seconds".into());
    args.push(config.unblock_interval_seconds.to_string().into());

    // Create service install context
    let install_ctx = ServiceInstallCtx {
        label: service_label(),
        program: exe_path,
        args,
        contents: None, // Optional for systemd unit file overrides
        username: None, // Run as current user by default
        working_directory: None,
        environment: None,
        autostart: true, // Start automatically on boot
    };

    // Install the service
    manager
        .install(install_ctx)
        .context("Failed to install service")?;

    let service_type = if user_level { "user" } else { "system" };
    println!(
        "✓ Service '{}' installed successfully as {} service",
        SERVICE_NAME, service_type
    );
    println!();
    println!("Configuration:");
    if let Some(ref log_dir) = config.log_dir {
        println!("  Log directory: {}", log_dir.display());
    }
    if let Some(ref database) = config.database {
        println!("  Database: {}", database);
    }
    println!("  Listen address: {}:{}", config.url, config.port);
    println!("  Worker threads: {}", config.threads);
    println!("  Log level: {}", config.log_level);
    println!();
    println!("To start the service, run:");
    if user_level {
        println!("  torc-server service start --user");
    } else {
        println!("  sudo torc-server service start");
    }

    Ok(())
}

/// Uninstall the service
pub fn uninstall_service(user_level: bool) -> Result<()> {
    let manager = get_service_manager(user_level)?;

    manager
        .uninstall(ServiceUninstallCtx {
            label: service_label(),
        })
        .context("Failed to uninstall service")?;

    let service_type = if user_level { "user" } else { "system" };
    println!(
        "✓ Service '{}' uninstalled successfully ({} service)",
        SERVICE_NAME, service_type
    );
    Ok(())
}

/// Start the service
pub fn start_service(user_level: bool) -> Result<()> {
    let manager = get_service_manager(user_level)?;
    let label = service_label();

    manager
        .start(ServiceStartCtx { label })
        .context("Failed to start service")?;

    let service_type = if user_level { "user" } else { "system" };
    println!(
        "✓ Service '{}' started successfully ({} service)",
        SERVICE_NAME, service_type
    );
    Ok(())
}

/// Stop the service
pub fn stop_service(user_level: bool) -> Result<()> {
    let manager = get_service_manager(user_level)?;
    let label = service_label();

    manager
        .stop(ServiceStopCtx { label })
        .context("Failed to stop service")?;

    let service_type = if user_level { "user" } else { "system" };
    println!(
        "✓ Service '{}' stopped successfully ({} service)",
        SERVICE_NAME, service_type
    );
    Ok(())
}

/// Check service status
pub fn service_status(user_level: bool) -> Result<()> {
    let service_type = if user_level { "user" } else { "system" };
    println!(
        "Service status check varies by platform ({} service):",
        service_type
    );
    println!();

    #[cfg(target_os = "linux")]
    {
        println!("On Linux (systemd):");
        if user_level {
            println!("  systemctl --user status com.github.torc.torc-server");
            println!();
            println!("Or check service logs:");
            println!("  journalctl --user -u com.github.torc.torc-server -f");
        } else {
            println!("  sudo systemctl status com.github.torc.torc-server");
            println!();
            println!("Or check service logs:");
            println!("  journalctl -u com.github.torc.torc-server -f");
        }
    }

    #[cfg(target_os = "macos")]
    {
        println!("On macOS (launchd):");
        if user_level {
            println!("  launchctl list | grep torc-server");
            println!();
            println!("Or check service logs:");
            println!("  tail -f ~/Library/Logs/torc-server.log");
        } else {
            println!("  sudo launchctl list | grep torc-server");
            println!();
            println!("Or check service logs:");
            println!("  tail -f /var/log/torc/torc-server.log");
        }
    }

    #[cfg(target_os = "windows")]
    {
        println!("On Windows:");
        println!("  sc query torc-server");
        println!();
        println!("Or use Services management console (services.msc)");
    }

    Ok(())
}

/// Execute a service command
pub fn execute_service_command(
    command: ServiceCommand,
    config: Option<&ServiceConfig>,
    user_level: bool,
) -> Result<()> {
    match command {
        ServiceCommand::Install => {
            // Merge user-provided config with appropriate defaults
            let merged_config = if let Some(user_config) = config {
                ServiceConfig::merge_with_defaults(user_config, user_level)
            } else {
                if user_level {
                    ServiceConfig::default_user()
                } else {
                    ServiceConfig::default_system()
                }
            };
            install_service(&merged_config, user_level)
        }
        ServiceCommand::Uninstall => uninstall_service(user_level),
        ServiceCommand::Start => start_service(user_level),
        ServiceCommand::Stop => stop_service(user_level),
        ServiceCommand::Status => service_status(user_level),
    }
}
