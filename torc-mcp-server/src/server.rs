//! MCP server implementation for Torc.

use rmcp::{
    Error as McpError, ServerHandler,
    model::{CallToolResult, Implementation, ProtocolVersion, ServerCapabilities, ServerInfo},
    schemars, tool,
};
use serde::Deserialize;
use std::path::PathBuf;

use torc::client::apis::configuration::Configuration;

use crate::tools;

/// MCP server that exposes Torc workflow operations as tools.
#[derive(Debug, Clone)]
pub struct TorcMcpServer {
    config: Configuration,
    output_dir: PathBuf,
}

impl TorcMcpServer {
    /// Create a new TorcMcpServer with the given API URL and output directory.
    pub fn new(api_url: String, output_dir: PathBuf) -> Self {
        let mut config = Configuration::new();
        config.base_path = api_url;

        Self { config, output_dir }
    }

    /// Create a new TorcMcpServer with authentication.
    pub fn with_auth(
        api_url: String,
        output_dir: PathBuf,
        username: Option<String>,
        password: Option<String>,
    ) -> Self {
        let mut config = Configuration::new();
        config.base_path = api_url;

        if let (Some(user), Some(pass)) = (username, password) {
            config.basic_auth = Some((user, Some(pass)));
        }

        Self { config, output_dir }
    }
}

// Tool parameter types

#[derive(Debug, Deserialize, schemars::JsonSchema)]
pub struct WorkflowIdParam {
    #[schemars(description = "The workflow ID")]
    pub workflow_id: i64,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
pub struct JobIdParam {
    #[schemars(description = "The job ID")]
    pub job_id: i64,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
pub struct GetJobLogsParams {
    #[schemars(description = "The workflow ID")]
    pub workflow_id: i64,
    #[schemars(description = "The job ID")]
    pub job_id: i64,
    #[schemars(description = "The run ID (1 for first run, increments on restart)")]
    pub run_id: i64,
    #[schemars(description = "Log type: 'stdout' or 'stderr'")]
    pub log_type: String,
    #[schemars(
        description = "Number of lines to return from the end (optional, returns all if not specified)"
    )]
    pub tail_lines: Option<usize>,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
pub struct ListJobsByStatusParams {
    #[schemars(description = "The workflow ID")]
    pub workflow_id: i64,
    #[schemars(
        description = "Job status to filter by: 'uninitialized', 'blocked', 'ready', 'pending', 'running', 'completed', 'failed', 'canceled', 'terminated', 'disabled'"
    )]
    pub status: String,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
pub struct UpdateJobResourcesParams {
    #[schemars(description = "The job ID")]
    pub job_id: i64,
    #[schemars(description = "Number of CPUs (optional)")]
    pub num_cpus: Option<i64>,
    #[schemars(description = "Memory requirement, e.g., '4g', '512m' (optional)")]
    pub memory: Option<String>,
    #[schemars(
        description = "Runtime in ISO8601 duration format, e.g., 'PT30M', 'PT2H' (optional)"
    )]
    pub runtime: Option<String>,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
pub struct CreateWorkflowParams {
    #[schemars(
        description = "Workflow specification as JSON string (always use JSON here - it will be auto-converted to the output file_format). For Slurm workflows, must include a 'resource_requirements' section and each job must reference one."
    )]
    pub spec_json: String,
    #[schemars(description = "User that owns the workflow (optional, defaults to current user)")]
    pub user: Option<String>,
    #[schemars(
        description = "Action to perform: 'create_workflow' to create in the database, 'save_spec_file' to save to filesystem only"
    )]
    pub action: String,
    #[schemars(description = "Workflow type: 'local' for local execution, 'slurm' for Slurm HPC")]
    pub workflow_type: String,
    #[schemars(description = "Slurm account (required for slurm workflow_type)")]
    pub account: Option<String>,
    #[schemars(
        description = "HPC profile to use (optional, auto-detected if not specified). Required for slurm if auto-detection fails."
    )]
    pub hpc_profile: Option<String>,
    #[schemars(
        description = "Output file path for save_spec_file action (required for save_spec_file, use .json extension)"
    )]
    pub output_path: Option<String>,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
pub struct CheckResourceUtilizationParams {
    #[schemars(description = "The workflow ID")]
    pub workflow_id: i64,
    #[schemars(
        description = "Include failed jobs in the analysis (recommended for recovery diagnostics)"
    )]
    pub include_failed: Option<bool>,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
pub struct ResetAndRestartWorkflowParams {
    #[schemars(description = "The workflow ID")]
    pub workflow_id: i64,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
pub struct ResubmitWorkflowParams {
    #[schemars(description = "The workflow ID")]
    pub workflow_id: i64,
    #[schemars(
        description = "Slurm account to use (defaults to account from existing schedulers)"
    )]
    pub account: Option<String>,
    #[schemars(description = "HPC profile to use (auto-detected if not specified)")]
    pub profile: Option<String>,
    #[schemars(description = "Preview what would be submitted without actually submitting")]
    pub dry_run: Option<bool>,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
pub struct RestartJobsParams {
    #[schemars(description = "The workflow ID")]
    pub workflow_id: i64,
    #[schemars(description = "Only restart failed jobs (default: true)")]
    pub failed_only: Option<bool>,
    #[schemars(
        description = "Specific job IDs to restart (optional, restarts all failed if not specified)"
    )]
    pub job_ids: Option<Vec<i64>>,
}

// Tool implementations using #[tool(tool_box)]

#[tool(tool_box)]
impl TorcMcpServer {
    /// Get the status of a workflow including job counts by status.
    #[tool(
        description = "Get workflow status summary with job counts by status (completed, failed, running, etc.)"
    )]
    async fn get_workflow_status(
        &self,
        #[tool(aggr)] params: WorkflowIdParam,
    ) -> Result<CallToolResult, McpError> {
        let config = self.config.clone();
        let workflow_id = params.workflow_id;
        tokio::task::spawn_blocking(move || tools::get_workflow_status(&config, workflow_id))
            .await
            .map_err(|e| McpError::internal_error(format!("Task join error: {}", e), None))?
    }

    /// Get detailed information about a specific job.
    #[tool(
        description = "Get detailed job information including command, status, resource requirements, and latest result"
    )]
    async fn get_job_details(
        &self,
        #[tool(aggr)] params: JobIdParam,
    ) -> Result<CallToolResult, McpError> {
        let config = self.config.clone();
        let job_id = params.job_id;
        tokio::task::spawn_blocking(move || tools::get_job_details(&config, job_id))
            .await
            .map_err(|e| McpError::internal_error(format!("Task join error: {}", e), None))?
    }

    /// Read job stdout or stderr logs.
    #[tool(
        description = "Read job execution logs (stdout or stderr). Optionally return only the last N lines."
    )]
    async fn get_job_logs(
        &self,
        #[tool(aggr)] params: GetJobLogsParams,
    ) -> Result<CallToolResult, McpError> {
        let output_dir = self.output_dir.clone();
        let workflow_id = params.workflow_id;
        let job_id = params.job_id;
        let run_id = params.run_id;
        let log_type = params.log_type;
        let tail_lines = params.tail_lines;
        tokio::task::spawn_blocking(move || {
            tools::get_job_logs(
                &output_dir,
                workflow_id,
                job_id,
                run_id,
                &log_type,
                tail_lines,
            )
        })
        .await
        .map_err(|e| McpError::internal_error(format!("Task join error: {}", e), None))?
    }

    /// List all failed jobs in a workflow.
    #[tool(
        description = "List all jobs with 'failed' status in a workflow, including their error information"
    )]
    async fn list_failed_jobs(
        &self,
        #[tool(aggr)] params: WorkflowIdParam,
    ) -> Result<CallToolResult, McpError> {
        let config = self.config.clone();
        let workflow_id = params.workflow_id;
        tokio::task::spawn_blocking(move || tools::list_failed_jobs(&config, workflow_id))
            .await
            .map_err(|e| McpError::internal_error(format!("Task join error: {}", e), None))?
    }

    /// List jobs filtered by status.
    #[tool(
        description = "List jobs in a workflow filtered by status (uninitialized, blocked, ready, pending, running, completed, failed, canceled, terminated, disabled)"
    )]
    async fn list_jobs_by_status(
        &self,
        #[tool(aggr)] params: ListJobsByStatusParams,
    ) -> Result<CallToolResult, McpError> {
        let config = self.config.clone();
        let workflow_id = params.workflow_id;
        let status = params.status;
        tokio::task::spawn_blocking(move || {
            tools::list_jobs_by_status(&config, workflow_id, &status)
        })
        .await
        .map_err(|e| McpError::internal_error(format!("Task join error: {}", e), None))?
    }

    /// Check resource utilization for a workflow.
    #[tool(
        description = "Check resource utilization and identify jobs that exceeded their limits (memory, CPU, runtime). Use --include-failed to analyze failed jobs for recovery diagnostics."
    )]
    async fn check_resource_utilization(
        &self,
        #[tool(aggr)] params: CheckResourceUtilizationParams,
    ) -> Result<CallToolResult, McpError> {
        let workflow_id = params.workflow_id;
        let include_failed = params.include_failed.unwrap_or(true);
        tokio::task::spawn_blocking(move || {
            tools::check_resource_utilization(workflow_id, include_failed)
        })
        .await
        .map_err(|e| McpError::internal_error(format!("Task join error: {}", e), None))?
    }

    /// Reset failed jobs and restart the workflow.
    #[tool(
        description = "Reset all failed jobs in a workflow and restart it. This resets job statuses to uninitialized and re-initializes the workflow. Use after updating resource requirements for failed jobs."
    )]
    async fn reset_and_restart_workflow(
        &self,
        #[tool(aggr)] params: ResetAndRestartWorkflowParams,
    ) -> Result<CallToolResult, McpError> {
        let workflow_id = params.workflow_id;
        tokio::task::spawn_blocking(move || tools::reset_and_restart_workflow(workflow_id))
            .await
            .map_err(|e| McpError::internal_error(format!("Task join error: {}", e), None))?
    }

    /// Update resource requirements for a job.
    #[tool(
        description = "Update a job's resource requirements (CPU, memory, runtime). Use before restarting a job that failed due to resource constraints."
    )]
    async fn update_job_resources(
        &self,
        #[tool(aggr)] params: UpdateJobResourcesParams,
    ) -> Result<CallToolResult, McpError> {
        let config = self.config.clone();
        let job_id = params.job_id;
        let num_cpus = params.num_cpus;
        let memory = params.memory;
        let runtime = params.runtime;
        tokio::task::spawn_blocking(move || {
            tools::update_job_resources(&config, job_id, num_cpus, memory, runtime)
        })
        .await
        .map_err(|e| McpError::internal_error(format!("Task join error: {}", e), None))?
    }

    /// Create a workflow from a specification.
    #[tool(description = r#"Create a workflow from a JSON specification.

ACTIONS:
- action="create_workflow": Create the workflow in the database (ready to run)
- action="save_spec_file": Save the spec to a file (requires output_path and file_format)

WORKFLOW TYPES:
- workflow_type="local": For local execution
- workflow_type="slurm": For Slurm HPC (requires account - ASK USER if not provided)

WORKFLOW SPEC FORMAT:
The spec_json parameter must be a JSON object. Use .json extension for output_path (e.g., workflow.json).
Structure:

{
  "name": "workflow_name",
  "jobs": [
    {
      "name": "job_name",
      "command": "command to run",
      "depends_on": ["other_job_name"],  // optional, list of job names this depends on
      "resource_requirements": "req_name",  // required for slurm, references a name from resource_requirements
      "parameters": {"i": "0:9"}  // optional, for parameterized jobs (see PARAMETERIZATION below)
    }
  ],
  "resource_requirements": [  // required for slurm workflows
    {
      "name": "req_name",
      "num_cpus": 1,
      "memory": "4g",        // e.g., "512m", "4g", "64g"
      "runtime": "PT1H",     // ISO8601: PT30M=30min, PT2H=2hrs, P1D=1day
      "num_gpus": 0,
      "num_nodes": 1
    }
  ]
}

PARAMETERIZATION - Use this to generate multiple jobs from a single template:
When users ask for "N jobs" or "jobs with an index", USE PARAMETERIZATION instead of listing jobs manually.

Job parameters field format:
- Integer range: "0:9" generates 0,1,2,...,9 (10 values, inclusive)
- Integer range with step: "0:100:10" generates 0,10,20,...,100
- List of values: "[1,5,10]" or "['train','test','val']"

Template substitution in name/command:
- {param} - substitutes the parameter value
- {param:03d} - zero-padded integer (e.g., 001, 042)
- {param:.2f} - float with precision

Dependencies on parameterized jobs:
- Use the BASE name (without parameter suffix) in depends_on
- Torc automatically expands to depend on ALL generated jobs

EXAMPLE - Using parameterization (PREFERRED for multiple similar jobs):
User asks: "Create a workflow with preprocess, 10 work jobs (each receiving an index), and postprocess."

{
  "name": "data_pipeline",
  "resource_requirements": [
    {"name": "small", "num_cpus": 1, "memory": "1g", "runtime": "PT1H", "num_gpus": 0, "num_nodes": 1},
    {"name": "worker", "num_cpus": 10, "memory": "50g", "runtime": "PT2H", "num_gpus": 0, "num_nodes": 1}
  ],
  "jobs": [
    {
      "name": "preprocess",
      "command": "python preprocess.py",
      "resource_requirements": "small"
    },
    {
      "name": "work_{i}",
      "command": "python work.py {i}",
      "depends_on": ["preprocess"],
      "resource_requirements": "worker",
      "parameters": {"i": "0:9"}
    },
    {
      "name": "postprocess",
      "command": "python postprocess.py",
      "depends_on": ["work_{i}"],
      "resource_requirements": "small"
    }
  ]
}

This creates: preprocess -> work_0, work_1, ..., work_9 -> postprocess
The postprocess job automatically waits for ALL work_* jobs to complete.

MORE PARAMETERIZATION EXAMPLES:
- 100 jobs: "parameters": {"i": "0:99"}
- Jobs for multiple datasets: "parameters": {"dataset": "['train','test','validation']"}
- Hyperparameter sweep: "parameters": {"lr": "[0.001,0.01,0.1]", "batch": "[32,64,128]"} (creates 9 jobs)

ACTIONS (optional, for workflow lifecycle events):
Actions reference jobs using job_names OR job_name_regexes:
- "job_names": ["preprocess", "postprocess", "work_0", "work_1"] - list of exact job names
- "job_name_regexes": ["^work_\\d+$"] - only use if ONE regex matches ALL parameterized jobs

TIPS:
- ALWAYS use parameterization when user asks for multiple similar jobs with indices
- Jobs with depends_on wait for those jobs to complete first
- Multiple jobs can share the same resource_requirements by name
- Use save_spec_file when user wants to review/edit before creating
- Use create_workflow when user wants to run immediately"#)]
    async fn create_workflow(
        &self,
        #[tool(aggr)] params: CreateWorkflowParams,
    ) -> Result<CallToolResult, McpError> {
        let config = self.config.clone();
        let spec_json = params.spec_json;
        let user = params
            .user
            .unwrap_or_else(|| std::env::var("USER").unwrap_or_else(|_| "unknown".to_string()));
        let action = params.action;
        let workflow_type = params.workflow_type;
        let account = params.account;
        let hpc_profile = params.hpc_profile;
        let output_path = params.output_path;
        tokio::task::spawn_blocking(move || {
            tools::create_workflow(
                &config,
                &spec_json,
                &user,
                &action,
                &workflow_type,
                account.as_deref(),
                hpc_profile.as_deref(),
                output_path.as_deref(),
            )
        })
        .await
        .map_err(|e| McpError::internal_error(format!("Task join error: {}", e), None))?
    }

    /// Resubmit a workflow by regenerating Slurm schedulers and submitting allocations.
    #[tool(
        description = "Regenerate Slurm schedulers for pending jobs and submit allocations. Use after resetting failed jobs to get new Slurm allocations. Analyzes job resource requirements and calculates the minimum allocations needed."
    )]
    async fn resubmit_workflow(
        &self,
        #[tool(aggr)] params: ResubmitWorkflowParams,
    ) -> Result<CallToolResult, McpError> {
        let output_dir = self.output_dir.clone();
        let workflow_id = params.workflow_id;
        let account = params.account;
        let profile = params.profile;
        let dry_run = params.dry_run.unwrap_or(false);
        tokio::task::spawn_blocking(move || {
            tools::resubmit_workflow(&output_dir, workflow_id, account, profile, dry_run)
        })
        .await
        .map_err(|e| McpError::internal_error(format!("Task join error: {}", e), None))?
    }
}

#[tool(tool_box)]
impl ServerHandler for TorcMcpServer {
    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            protocol_version: ProtocolVersion::V_2024_11_05,
            capabilities: ServerCapabilities::builder().enable_tools().build(),
            server_info: Implementation::from_build_env(),
            instructions: Some(
                "Torc MCP Server - Manage computational workflows. \
                 Use get_workflow_status to check workflow progress, \
                 list_failed_jobs to find failures, \
                 get_job_logs to diagnose issues, \
                 check_resource_utilization to identify resource problems, \
                 update_job_resources to fix resource limits, \
                 restart_jobs to reset and restart failed jobs, \
                 and resubmit_workflow to regenerate Slurm schedulers and submit new allocations."
                    .to_string(),
            ),
        }
    }
}
