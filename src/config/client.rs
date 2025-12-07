//! Client configuration for the torc CLI

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Configuration for the torc CLI client
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct ClientConfig {
    /// URL of the torc-server API
    pub api_url: String,

    /// Output format (table or json)
    pub format: String,

    /// Username for basic authentication
    pub username: Option<String>,

    /// Log level (error, warn, info, debug, trace)
    pub log_level: String,

    /// Run command configuration
    pub run: ClientRunConfig,
}

impl Default for ClientConfig {
    fn default() -> Self {
        Self {
            api_url: "http://localhost:8080/torc-service/v1".to_string(),
            format: "table".to_string(),
            username: None,
            log_level: "info".to_string(),
            run: ClientRunConfig::default(),
        }
    }
}

/// Configuration for the `torc run` command
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct ClientRunConfig {
    /// Job completion poll interval in seconds
    pub poll_interval: f64,

    /// Maximum number of parallel jobs to run concurrently
    pub max_parallel_jobs: Option<i64>,

    /// Output directory for jobs
    pub output_dir: PathBuf,

    /// Database poll interval in seconds
    pub database_poll_interval: i64,

    /// Number of CPUs available
    pub num_cpus: Option<i64>,

    /// Memory in GB
    pub memory_gb: Option<f64>,

    /// Number of GPUs available
    pub num_gpus: Option<i64>,
}

impl Default for ClientRunConfig {
    fn default() -> Self {
        Self {
            poll_interval: 5.0,
            max_parallel_jobs: None,
            output_dir: PathBuf::from("output"),
            database_poll_interval: 30,
            num_cpus: None,
            memory_gb: None,
            num_gpus: None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_client_config_defaults() {
        let config = ClientConfig::default();
        assert_eq!(
            config.api_url,
            "http://localhost:8080/torc-service/v1".to_string()
        );
        assert_eq!(config.format, "table");
        assert!(config.username.is_none());
        assert_eq!(config.log_level, "info");
    }

    #[test]
    fn test_run_config_defaults() {
        let config = ClientRunConfig::default();
        assert_eq!(config.poll_interval, 5.0);
        assert!(config.max_parallel_jobs.is_none());
        assert_eq!(config.output_dir, PathBuf::from("output"));
    }
}
