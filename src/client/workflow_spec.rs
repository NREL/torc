use crate::client::apis::{configuration::Configuration, default_api};
use crate::client::parameter_expansion::{
    ParameterValue, cartesian_product, parse_parameter_value, substitute_parameters,
};
use crate::models;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::Path;

#[cfg(feature = "client")]
use kdl::{KdlDocument, KdlNode};

/// File specification for JSON serialization (without workflow_id, id, and st_mtime)
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct FileSpec {
    /// Name of the file
    pub name: String,
    /// Path to the file
    pub path: String,
    /// Optional parameters for generating multiple files
    /// Supports range notation (e.g., "1:100" or "1:100:5") and lists (e.g., "[1,5,10]")
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parameters: Option<HashMap<String, String>>,
}

impl FileSpec {
    /// Create a new FileSpec with only required fields
    #[allow(dead_code)]
    pub fn new(name: String, path: String) -> FileSpec {
        FileSpec {
            name,
            path,
            parameters: None,
        }
    }

    /// Expand this FileSpec into multiple FileSpecs based on its parameters
    /// Returns a single-element vec if no parameters are present
    pub fn expand(&self) -> Result<Vec<FileSpec>, String> {
        // If no parameters, return a clone
        let Some(ref params) = self.parameters else {
            return Ok(vec![self.clone()]);
        };

        // Parse all parameter values
        let mut parsed_params: HashMap<String, Vec<ParameterValue>> = HashMap::new();
        for (name, value) in params {
            let values = parse_parameter_value(value)?;
            parsed_params.insert(name.clone(), values);
        }

        // Generate Cartesian product of all parameters
        let combinations = cartesian_product(&parsed_params);

        // Create a FileSpec for each combination
        let mut expanded = Vec::new();
        for combo in combinations {
            let mut new_spec = self.clone();
            new_spec.parameters = None; // Remove parameters from expanded specs

            // Substitute parameters in name and path
            new_spec.name = substitute_parameters(&self.name, &combo);
            new_spec.path = substitute_parameters(&self.path, &combo);

            expanded.push(new_spec);
        }

        Ok(expanded)
    }
}

/// User data specification for JSON serialization (without workflow_id and id)
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct UserDataSpec {
    /// Whether the user data is ephemeral
    pub is_ephemeral: Option<bool>,
    /// Name of the user data
    pub name: Option<String>,
    /// The data content as JSON value
    pub data: Option<serde_json::Value>,
}

/// Workflow action specification for defining conditional actions
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct WorkflowActionSpec {
    /// Trigger type: on_workflow_start, on_workflow_complete, on_jobs_ready, on_jobs_complete
    pub trigger_type: String,
    /// Action type: run_commands, schedule_nodes
    pub action_type: String,
    /// For on_jobs_ready/on_jobs_complete: exact job names to match
    #[serde(skip_serializing_if = "Option::is_none")]
    pub job_names: Option<Vec<String>>,
    /// For on_jobs_ready/on_jobs_complete: regex patterns to match job names
    #[serde(skip_serializing_if = "Option::is_none")]
    pub job_name_regexes: Option<Vec<String>>,
    /// For run_commands action: array of commands to execute
    #[serde(skip_serializing_if = "Option::is_none")]
    pub commands: Option<Vec<String>>,
    /// For schedule_nodes action: scheduler name (will be translated to scheduler_id)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scheduler_name: Option<String>,
    /// For schedule_nodes action: scheduler type (e.g., "slurm", "local")
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scheduler_type: Option<String>,
    /// For schedule_nodes action: number of node allocations to request
    #[serde(skip_serializing_if = "Option::is_none")]
    pub num_allocations: Option<i64>,
    /// For schedule_nodes action: whether to start one worker per node
    #[serde(skip_serializing_if = "Option::is_none")]
    pub start_one_worker_per_node: Option<bool>,
    /// For schedule_nodes action: maximum parallel jobs
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_parallel_jobs: Option<i32>,
    /// Whether the action persists and can be claimed by multiple workers (default: false)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub persistent: Option<bool>,
}

/// Resource requirements specification for JSON serialization (without workflow_id and id)
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ResourceRequirementsSpec {
    /// Name of the resource requirements configuration
    pub name: String,
    /// Number of CPUs required
    pub num_cpus: i64,
    /// Number of GPUs required
    pub num_gpus: i64,
    /// Number of nodes required
    pub num_nodes: i64,
    /// Memory requirement
    pub memory: String,
    /// Runtime limit
    pub runtime: String,
}

/// Slurm scheduler specification for JSON serialization (without workflow_id and id)
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct SlurmSchedulerSpec {
    /// Name of the scheduler
    pub name: Option<String>,
    /// Slurm account
    pub account: String,
    /// Generic resources (GRES)
    pub gres: Option<String>,
    /// Memory specification
    pub mem: Option<String>,
    /// Number of nodes
    pub nodes: i64,
    /// Number of tasks per node
    pub ntasks_per_node: Option<i64>,
    /// Partition name
    pub partition: Option<String>,
    /// Quality of service
    pub qos: Option<String>,
    /// Temporary storage
    pub tmp: Option<String>,
    /// Wall time limit
    pub walltime: String,
    /// Extra parameters
    pub extra: Option<String>,
}

/// Specification for a job within a workflow
#[derive(Clone, Default, Debug, PartialEq, Serialize, Deserialize)]
pub struct JobSpec {
    /// Name of the job
    pub name: String,
    /// Command to execute for this job
    pub command: String,
    /// Optional script for job invocation
    pub invocation_script: Option<String>,
    /// Whether to cancel this job if a blocking job fails
    pub cancel_on_blocking_job_failure: Option<bool>,
    /// Whether this job supports termination
    pub supports_termination: Option<bool>,
    /// Name of the resource requirements configuration
    pub resource_requirements_name: Option<String>,
    /// Names of jobs that must complete before this job can run (exact matches)
    pub blocked_by_job_names: Option<Vec<String>>,
    /// Regex patterns for jobs that must complete before this job can run
    #[serde(skip_serializing_if = "Option::is_none")]
    pub blocked_by_job_name_regexes: Option<Vec<String>>,
    /// Names of input files required by this job (exact matches)
    pub input_file_names: Option<Vec<String>>,
    /// Regex patterns for input files required by this job
    #[serde(skip_serializing_if = "Option::is_none")]
    pub input_file_name_regexes: Option<Vec<String>>,
    /// Names of output files produced by this job (exact matches)
    pub output_file_names: Option<Vec<String>>,
    /// Regex patterns for output files produced by this job
    #[serde(skip_serializing_if = "Option::is_none")]
    pub output_file_name_regexes: Option<Vec<String>>,
    /// Names of input user data required by this job (exact matches)
    pub input_user_data_names: Option<Vec<String>>,
    /// Regex patterns for input user data required by this job
    #[serde(skip_serializing_if = "Option::is_none")]
    pub input_user_data_name_regexes: Option<Vec<String>>,
    /// Names of output data produced by this job (exact matches)
    pub output_data_names: Option<Vec<String>>,
    /// Regex patterns for output data produced by this job
    #[serde(skip_serializing_if = "Option::is_none")]
    pub output_user_data_name_regexes: Option<Vec<String>>,
    /// Name of the scheduler to use for this job
    pub scheduler_name: Option<String>,
    /// Optional parameters for generating multiple jobs
    /// Supports range notation (e.g., "1:100" or "1:100:5") and lists (e.g., "[1,5,10]")
    /// Multiple parameters create a Cartesian product of jobs
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parameters: Option<HashMap<String, String>>,
}

impl JobSpec {
    /// Create a new JobSpec with only required fields
    #[allow(dead_code)]
    pub fn new(name: String, command: String) -> JobSpec {
        JobSpec {
            name,
            command,
            invocation_script: None,
            cancel_on_blocking_job_failure: Some(false),
            supports_termination: Some(false),
            resource_requirements_name: None,
            blocked_by_job_names: None,
            blocked_by_job_name_regexes: None,
            input_file_names: None,
            input_file_name_regexes: None,
            output_file_names: None,
            output_file_name_regexes: None,
            input_user_data_names: None,
            input_user_data_name_regexes: None,
            output_data_names: None,
            output_user_data_name_regexes: None,
            scheduler_name: None,
            parameters: None,
        }
    }

    /// Expand this JobSpec into multiple JobSpecs based on its parameters
    /// Returns a single-element vec if no parameters are present
    pub fn expand(&self) -> Result<Vec<JobSpec>, String> {
        // If no parameters, return a clone
        let Some(ref params) = self.parameters else {
            return Ok(vec![self.clone()]);
        };

        // Parse all parameter values
        let mut parsed_params: HashMap<String, Vec<ParameterValue>> = HashMap::new();
        for (name, value) in params {
            let values = parse_parameter_value(value)?;
            parsed_params.insert(name.clone(), values);
        }

        // Generate Cartesian product of all parameters
        let combinations = cartesian_product(&parsed_params);

        // Create a JobSpec for each combination
        let mut expanded = Vec::new();
        for combo in combinations {
            let mut new_spec = self.clone();
            new_spec.parameters = None; // Remove parameters from expanded specs

            // Substitute parameters in all string fields
            new_spec.name = substitute_parameters(&self.name, &combo);
            new_spec.command = substitute_parameters(&self.command, &combo);

            if let Some(ref script) = self.invocation_script {
                new_spec.invocation_script = Some(substitute_parameters(script, &combo));
            }

            if let Some(ref rr_name) = self.resource_requirements_name {
                new_spec.resource_requirements_name = Some(substitute_parameters(rr_name, &combo));
            }

            if let Some(ref sched_name) = self.scheduler_name {
                new_spec.scheduler_name = Some(substitute_parameters(sched_name, &combo));
            }

            // Substitute parameters in name vectors
            if let Some(ref names) = self.blocked_by_job_names {
                new_spec.blocked_by_job_names = Some(
                    names
                        .iter()
                        .map(|n| substitute_parameters(n, &combo))
                        .collect(),
                );
            }

            if let Some(ref names) = self.input_file_names {
                new_spec.input_file_names = Some(
                    names
                        .iter()
                        .map(|n| substitute_parameters(n, &combo))
                        .collect(),
                );
            }

            if let Some(ref names) = self.output_file_names {
                new_spec.output_file_names = Some(
                    names
                        .iter()
                        .map(|n| substitute_parameters(n, &combo))
                        .collect(),
                );
            }

            if let Some(ref names) = self.input_user_data_names {
                new_spec.input_user_data_names = Some(
                    names
                        .iter()
                        .map(|n| substitute_parameters(n, &combo))
                        .collect(),
                );
            }

            if let Some(ref names) = self.output_data_names {
                new_spec.output_data_names = Some(
                    names
                        .iter()
                        .map(|n| substitute_parameters(n, &combo))
                        .collect(),
                );
            }

            // Substitute parameters in regex pattern vectors
            if let Some(ref regexes) = self.blocked_by_job_name_regexes {
                new_spec.blocked_by_job_name_regexes = Some(
                    regexes
                        .iter()
                        .map(|r| substitute_parameters(r, &combo))
                        .collect(),
                );
            }

            if let Some(ref regexes) = self.input_file_name_regexes {
                new_spec.input_file_name_regexes = Some(
                    regexes
                        .iter()
                        .map(|r| substitute_parameters(r, &combo))
                        .collect(),
                );
            }

            if let Some(ref regexes) = self.output_file_name_regexes {
                new_spec.output_file_name_regexes = Some(
                    regexes
                        .iter()
                        .map(|r| substitute_parameters(r, &combo))
                        .collect(),
                );
            }

            if let Some(ref regexes) = self.input_user_data_name_regexes {
                new_spec.input_user_data_name_regexes = Some(
                    regexes
                        .iter()
                        .map(|r| substitute_parameters(r, &combo))
                        .collect(),
                );
            }

            if let Some(ref regexes) = self.output_user_data_name_regexes {
                new_spec.output_user_data_name_regexes = Some(
                    regexes
                        .iter()
                        .map(|r| substitute_parameters(r, &combo))
                        .collect(),
                );
            }

            expanded.push(new_spec);
        }

        Ok(expanded)
    }
}

/// Specification for a complete workflow
#[derive(Clone, Default, Debug, PartialEq, Serialize, Deserialize)]
pub struct WorkflowSpec {
    /// Name of the workflow
    pub name: String,
    /// User who owns this workflow (optional - will default to current user)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub user: Option<String>,
    /// Description of the workflow
    pub description: String,
    /// Inform all compute nodes to shut down this number of seconds before the expiration time
    #[serde(skip_serializing_if = "Option::is_none")]
    pub compute_node_expiration_buffer_seconds: Option<i64>,
    /// Inform all compute nodes to wait for new jobs for this time period before exiting
    #[serde(skip_serializing_if = "Option::is_none")]
    pub compute_node_wait_for_new_jobs_seconds: Option<i64>,
    /// Inform all compute nodes to ignore workflow completions and hold onto allocations indefinitely
    #[serde(skip_serializing_if = "Option::is_none")]
    pub compute_node_ignore_workflow_completion: Option<bool>,
    /// Inform all compute nodes to wait this number of minutes if the database becomes unresponsive
    #[serde(skip_serializing_if = "Option::is_none")]
    pub compute_node_wait_for_healthy_database_minutes: Option<i64>,
    /// Method for sorting jobs when claiming them from the server
    #[serde(skip_serializing_if = "Option::is_none")]
    pub jobs_sort_method: Option<models::ClaimJobsSortMethod>,
    /// Jobs that make up this workflow
    pub jobs: Vec<JobSpec>,
    /// Files associated with this workflow
    pub files: Option<Vec<FileSpec>>,
    /// User data associated with this workflow
    pub user_data: Option<Vec<UserDataSpec>>,
    /// Resource requirements available for this workflow
    pub resource_requirements: Option<Vec<ResourceRequirementsSpec>>,
    /// Slurm schedulers available for this workflow
    pub slurm_schedulers: Option<Vec<SlurmSchedulerSpec>>,
    /// Resource monitoring configuration
    pub resource_monitor: Option<crate::client::resource_monitor::ResourceMonitorConfig>,
    /// Actions to execute based on workflow/job state transitions
    #[serde(skip_serializing_if = "Option::is_none")]
    pub actions: Option<Vec<WorkflowActionSpec>>,
}

impl WorkflowSpec {
    /// Create a new WorkflowSpec with required fields
    #[allow(dead_code)]
    pub fn new(
        name: String,
        user: String,
        description: String,
        jobs: Vec<JobSpec>,
    ) -> WorkflowSpec {
        WorkflowSpec {
            name,
            user: Some(user),
            description,
            compute_node_expiration_buffer_seconds: None,
            compute_node_wait_for_new_jobs_seconds: None,
            compute_node_ignore_workflow_completion: None,
            compute_node_wait_for_healthy_database_minutes: None,
            jobs_sort_method: None,
            jobs,
            files: None,
            user_data: None,
            resource_requirements: None,
            slurm_schedulers: None,
            resource_monitor: None,
            actions: None,
        }
    }

    /// Expand all parameterized jobs and files in this workflow spec
    /// This modifies the spec in-place, replacing parameterized specs with their expanded versions
    pub fn expand_parameters(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        // Expand all jobs
        let mut expanded_jobs = Vec::new();
        for job in &self.jobs {
            let expanded = job
                .expand()
                .map_err(|e| format!("Failed to expand job '{}': {}", job.name, e))?;
            expanded_jobs.extend(expanded);
        }
        self.jobs = expanded_jobs;

        // Expand all files
        if let Some(ref files) = self.files {
            let mut expanded_files = Vec::new();
            for file in files {
                let expanded = file
                    .expand()
                    .map_err(|e| format!("Failed to expand file '{}': {}", file.name, e))?;
                expanded_files.extend(expanded);
            }
            self.files = Some(expanded_files);
        }

        Ok(())
    }

    /// Validate workflow actions
    pub fn validate_actions(&self) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(ref actions) = self.actions {
            for action in actions {
                // Validate schedule_nodes actions
                if action.action_type == "schedule_nodes" {
                    // Ensure scheduler_type is provided
                    let scheduler_type = action
                        .scheduler_type
                        .as_ref()
                        .ok_or("schedule_nodes action requires scheduler_type")?;

                    // Ensure scheduler_name is provided
                    let scheduler_name = action
                        .scheduler_name
                        .as_ref()
                        .ok_or("schedule_nodes action requires scheduler_name")?;

                    // If scheduler_type is slurm, verify that a slurm_scheduler with that name exists
                    if scheduler_type == "slurm" {
                        let slurm_schedulers = self
                            .slurm_schedulers
                            .as_ref()
                            .ok_or("schedule_nodes action with scheduler_type=slurm requires slurm_schedulers to be defined")?;

                        let scheduler_exists = slurm_schedulers
                            .iter()
                            .any(|s| s.name.as_ref() == Some(scheduler_name));

                        if !scheduler_exists {
                            return Err(format!(
                                "schedule_nodes action references slurm_scheduler '{}' which does not exist",
                                scheduler_name
                            )
                            .into());
                        }
                    }
                }
            }
        }
        Ok(())
    }

    /// Check if the workflow spec has an on_workflow_start action with schedule_nodes
    /// Returns true if such an action exists, false otherwise
    pub fn has_schedule_nodes_action(&self) -> bool {
        if let Some(ref actions) = self.actions {
            actions.iter().any(|action| {
                action.trigger_type == "on_workflow_start" && action.action_type == "schedule_nodes"
            })
        } else {
            false
        }
    }

    /// Create a WorkflowModel on the server from a JSON file
    /// Create a workflow from a specification file (JSON, JSON5, or YAML) with all associated data
    ///
    /// This function will create the workflow and all associated models (files, user data, etc.)
    /// If any errors occur, the workflow will be deleted (which cascades to all other objects)
    pub fn create_workflow_from_spec<P: AsRef<Path>>(
        config: &Configuration,
        path: P,
        user: &str,
        enable_resource_monitoring: bool,
    ) -> Result<i64, Box<dyn std::error::Error>> {
        // Step 1: Deserialize the WorkflowSpecification from spec file
        let mut spec = Self::from_spec_file(path)?;
        spec.user = Some(user.to_string());

        // Apply default resource monitoring if enabled and not already configured
        if enable_resource_monitoring && spec.resource_monitor.is_none() {
            spec.resource_monitor = Some(crate::client::resource_monitor::ResourceMonitorConfig {
                enabled: true,
                granularity: crate::client::resource_monitor::MonitorGranularity::Summary,
                sample_interval_seconds: 5,
                generate_plots: false,
            });
        }

        // Step 1.25: Expand parameterized jobs and files
        spec.expand_parameters()?;

        // Step 1.4: Validate workflow actions
        spec.validate_actions()?;

        // Step 1.5: Perform variable substitution in commands
        spec.substitute_variables()?;

        // Step 2: Create WorkflowModel
        let workflow_id = Self::create_workflow(config, &spec)?;

        // If any step fails, delete the workflow (which cascades to all other objects)
        let rollback = |workflow_id: i64| {
            let _ = default_api::delete_workflow(config, workflow_id, None);
        };

        // Step 3: Create supporting models and build name-to-id mappings
        let file_name_to_id = match Self::create_files(config, workflow_id, &spec) {
            Ok(mapping) => mapping,
            Err(e) => {
                rollback(workflow_id);
                return Err(e);
            }
        };

        let user_data_name_to_id = match Self::create_user_data(config, workflow_id, &spec) {
            Ok(mapping) => mapping,
            Err(e) => {
                rollback(workflow_id);
                return Err(e);
            }
        };

        let resource_req_name_to_id =
            match Self::create_resource_requirements(config, workflow_id, &spec) {
                Ok(mapping) => mapping,
                Err(e) => {
                    rollback(workflow_id);
                    return Err(e);
                }
            };

        let slurm_scheduler_name_to_id =
            match Self::create_slurm_schedulers(config, workflow_id, &spec) {
                Ok(mapping) => mapping,
                Err(e) => {
                    rollback(workflow_id);
                    return Err(e);
                }
            };

        // Step 4: Create JobModels (with dependencies set during creation)
        let (job_name_to_id, _created_jobs) = match Self::create_jobs(
            config,
            workflow_id,
            &spec,
            &file_name_to_id,
            &user_data_name_to_id,
            &resource_req_name_to_id,
            &slurm_scheduler_name_to_id,
        ) {
            Ok((mapping, jobs)) => (mapping, jobs),
            Err(e) => {
                rollback(workflow_id);
                return Err(e);
            }
        };

        // Step 5: Create workflow actions
        match Self::create_actions(
            config,
            workflow_id,
            &spec,
            &slurm_scheduler_name_to_id,
            &job_name_to_id,
        ) {
            Ok(_) => {}
            Err(e) => {
                rollback(workflow_id);
                return Err(e);
            }
        }

        Ok(workflow_id)
    }

    /// Create the workflow on the server
    fn create_workflow(
        config: &Configuration,
        spec: &WorkflowSpec,
    ) -> Result<i64, Box<dyn std::error::Error>> {
        let user = spec.user.clone().unwrap_or_else(|| "unknown".to_string());
        let mut workflow_model = models::WorkflowModel::new(spec.name.clone(), user);
        workflow_model.description = Some(spec.description.clone());

        // Set compute node configuration fields if present
        if let Some(value) = spec.compute_node_expiration_buffer_seconds {
            workflow_model.compute_node_expiration_buffer_seconds = Some(value);
        }
        if let Some(value) = spec.compute_node_wait_for_new_jobs_seconds {
            workflow_model.compute_node_wait_for_new_jobs_seconds = Some(value);
        }
        if let Some(value) = spec.compute_node_ignore_workflow_completion {
            workflow_model.compute_node_ignore_workflow_completion = Some(value);
        }
        if let Some(value) = spec.compute_node_wait_for_healthy_database_minutes {
            workflow_model.compute_node_wait_for_healthy_database_minutes = Some(value);
        }
        if let Some(ref value) = spec.jobs_sort_method {
            workflow_model.jobs_sort_method = Some(value.clone());
        }

        // Serialize resource_monitor config if present
        if let Some(ref resource_monitor) = spec.resource_monitor {
            let config_json = serde_json::to_string(resource_monitor)
                .map_err(|e| format!("Failed to serialize resource monitor config: {}", e))?;
            workflow_model.resource_monitor_config = Some(config_json);
        }

        let created_workflow = default_api::create_workflow(config, workflow_model)
            .map_err(|e| format!("Failed to create workflow: {:?}", e))?;

        created_workflow
            .id
            .ok_or("Created workflow missing ID".into())
    }

    /// Create FileModels and build name-to-id mapping
    fn create_files(
        config: &Configuration,
        workflow_id: i64,
        spec: &WorkflowSpec,
    ) -> Result<HashMap<String, i64>, Box<dyn std::error::Error>> {
        let mut file_name_to_id = HashMap::new();

        if let Some(files) = &spec.files {
            for file_spec in files {
                // Check for duplicate names
                if file_name_to_id.contains_key(&file_spec.name) {
                    return Err(format!("Duplicate file name: {}", file_spec.name).into());
                }

                let file_model = models::FileModel {
                    id: None, // Server will assign ID
                    workflow_id,
                    name: file_spec.name.clone(),
                    path: file_spec.path.clone(),
                    st_mtime: None, // Not included in specification
                };

                let created_file = default_api::create_file(config, file_model)
                    .map_err(|e| format!("Failed to create file {}: {:?}", file_spec.name, e))?;

                let file_id = created_file.id.ok_or("Created file missing ID")?;
                file_name_to_id.insert(file_spec.name.clone(), file_id);
            }
        }

        Ok(file_name_to_id)
    }

    /// Create UserDataModels and build name-to-id mapping
    fn create_user_data(
        config: &Configuration,
        workflow_id: i64,
        spec: &WorkflowSpec,
    ) -> Result<HashMap<String, i64>, Box<dyn std::error::Error>> {
        let mut user_data_name_to_id = HashMap::new();

        if let Some(user_data_list) = &spec.user_data {
            for user_data_spec in user_data_list {
                if let Some(name) = &user_data_spec.name {
                    // Check for duplicate names
                    if user_data_name_to_id.contains_key(name) {
                        return Err(format!("Duplicate user data name: {}", name).into());
                    }

                    let user_data_model = models::UserDataModel {
                        id: None, // Server will assign ID
                        workflow_id,
                        is_ephemeral: user_data_spec.is_ephemeral,
                        name: name.clone(),
                        data: user_data_spec.data.clone(),
                    };

                    let created_user_data =
                        default_api::create_user_data(config, user_data_model, None, None)
                            .map_err(|e| format!("Failed to create user data {}: {:?}", name, e))?;

                    let user_data_id =
                        created_user_data.id.ok_or("Created user data missing ID")?;
                    user_data_name_to_id.insert(name.clone(), user_data_id);
                }
            }
        }

        Ok(user_data_name_to_id)
    }

    /// Create ResourceRequirementsModels and build name-to-id mapping
    fn create_resource_requirements(
        config: &Configuration,
        workflow_id: i64,
        spec: &WorkflowSpec,
    ) -> Result<HashMap<String, i64>, Box<dyn std::error::Error>> {
        let mut resource_req_name_to_id = HashMap::new();

        if let Some(resource_requirements) = &spec.resource_requirements {
            for resource_req_spec in resource_requirements {
                // Check for duplicate names
                if resource_req_name_to_id.contains_key(&resource_req_spec.name) {
                    return Err(format!(
                        "Duplicate resource requirements name: {}",
                        resource_req_spec.name
                    )
                    .into());
                }

                let resource_req_model = models::ResourceRequirementsModel {
                    id: None, // Server will assign ID
                    workflow_id,
                    name: resource_req_spec.name.clone(),
                    num_cpus: resource_req_spec.num_cpus,
                    num_gpus: resource_req_spec.num_gpus,
                    num_nodes: resource_req_spec.num_nodes,
                    memory: resource_req_spec.memory.clone(),
                    runtime: resource_req_spec.runtime.clone(),
                };

                let created_resource_req =
                    default_api::create_resource_requirements(config, resource_req_model).map_err(
                        |e| {
                            format!(
                                "Failed to create resource requirements {}: {:?}",
                                resource_req_spec.name, e
                            )
                        },
                    )?;

                let resource_req_id = created_resource_req
                    .id
                    .ok_or("Created resource requirements missing ID")?;
                resource_req_name_to_id.insert(resource_req_spec.name.clone(), resource_req_id);
            }
        }

        Ok(resource_req_name_to_id)
    }

    /// Create SlurmSchedulerModels and build name-to-id mapping
    fn create_slurm_schedulers(
        config: &Configuration,
        workflow_id: i64,
        spec: &WorkflowSpec,
    ) -> Result<HashMap<String, i64>, Box<dyn std::error::Error>> {
        let mut slurm_scheduler_name_to_id = HashMap::new();

        if let Some(slurm_schedulers) = &spec.slurm_schedulers {
            for scheduler_spec in slurm_schedulers {
                if let Some(name) = &scheduler_spec.name {
                    // Check for duplicate names
                    if slurm_scheduler_name_to_id.contains_key(name) {
                        return Err(format!("Duplicate slurm scheduler name: {}", name).into());
                    }

                    let scheduler_model = models::SlurmSchedulerModel {
                        id: None, // Server will assign ID
                        workflow_id,
                        name: scheduler_spec.name.clone(),
                        account: scheduler_spec.account.clone(),
                        gres: scheduler_spec.gres.clone(),
                        mem: scheduler_spec.mem.clone(),
                        nodes: scheduler_spec.nodes,
                        ntasks_per_node: scheduler_spec.ntasks_per_node,
                        partition: scheduler_spec.partition.clone(),
                        qos: scheduler_spec.qos.clone(),
                        tmp: scheduler_spec.tmp.clone(),
                        walltime: scheduler_spec.walltime.clone(),
                        extra: scheduler_spec.extra.clone(),
                    };

                    let created_scheduler =
                        default_api::create_slurm_scheduler(config, scheduler_model).map_err(
                            |e| format!("Failed to create slurm scheduler {}: {:?}", name, e),
                        )?;

                    let scheduler_id = created_scheduler
                        .id
                        .ok_or("Created slurm scheduler missing ID")?;
                    slurm_scheduler_name_to_id.insert(name.clone(), scheduler_id);
                }
            }
        }

        Ok(slurm_scheduler_name_to_id)
    }

    /// Create workflow actions
    fn create_actions(
        config: &Configuration,
        workflow_id: i64,
        spec: &WorkflowSpec,
        slurm_scheduler_name_to_id: &HashMap<String, i64>,
        job_name_to_id: &HashMap<String, i64>,
    ) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(actions) = &spec.actions {
            for action_spec in actions {
                // Resolve job_names and job_name_regexes to job_ids
                let job_ids =
                    if action_spec.job_names.is_some() || action_spec.job_name_regexes.is_some() {
                        let mut matched_job_ids = Vec::new();

                        // Match exact job names
                        if let Some(ref patterns) = action_spec.job_names {
                            for pattern in patterns {
                                if let Some(job_id) = job_name_to_id.get(pattern) {
                                    matched_job_ids.push(*job_id);
                                } else {
                                    return Err(format!(
                                        "Action references job '{}' which does not exist",
                                        pattern
                                    )
                                    .into());
                                }
                            }
                        }

                        // Match job names using regexes
                        if let Some(ref regexes) = action_spec.job_name_regexes {
                            use regex::Regex;
                            for regex_str in regexes {
                                let re = Regex::new(regex_str)
                                    .map_err(|e| format!("Invalid regex '{}': {}", regex_str, e))?;

                                for (job_name, job_id) in job_name_to_id {
                                    if re.is_match(job_name) && !matched_job_ids.contains(job_id) {
                                        matched_job_ids.push(*job_id);
                                    }
                                }
                            }
                        }

                        if matched_job_ids.is_empty() {
                            return Err("Action did not match any jobs".into());
                        }

                        Some(matched_job_ids)
                    } else {
                        None
                    };

                // Build action_config JSON based on action_type
                let action_config = match action_spec.action_type.as_str() {
                    "run_commands" => {
                        let commands = action_spec
                            .commands
                            .as_ref()
                            .ok_or("run_commands action requires 'commands' field")?;
                        serde_json::json!({
                            "commands": commands
                        })
                    }
                    "schedule_nodes" => {
                        let scheduler_type = action_spec
                            .scheduler_type
                            .as_ref()
                            .ok_or("schedule_nodes action requires 'scheduler_type' field")?;
                        let scheduler_name = action_spec
                            .scheduler_name
                            .as_ref()
                            .ok_or("schedule_nodes action requires 'scheduler_name' field")?;

                        // Translate scheduler_name to scheduler_id
                        let scheduler_id = if scheduler_type == "slurm" {
                            slurm_scheduler_name_to_id
                                .get(scheduler_name)
                                .ok_or(format!("Slurm scheduler '{}' not found", scheduler_name))?
                        } else {
                            // For other scheduler types, we might need a different lookup
                            // For now, just use 0 as placeholder
                            &0
                        };

                        let mut config = serde_json::json!({
                            "scheduler_type": scheduler_type,
                            "scheduler_id": scheduler_id,
                            "num_allocations": action_spec.num_allocations.unwrap_or(1),
                            "start_one_worker_per_node": action_spec.start_one_worker_per_node.unwrap_or(true),
                        });
                        // Only include max_parallel_jobs if explicitly specified
                        if let Some(max_parallel_jobs) = action_spec.max_parallel_jobs {
                            config["max_parallel_jobs"] = serde_json::json!(max_parallel_jobs);
                        }
                        config
                    }
                    _ => {
                        return Err(
                            format!("Unknown action_type: {}", action_spec.action_type).into()
                        );
                    }
                };

                // Create the action via API
                let action_body = serde_json::json!({
                    "workflow_id": workflow_id,
                    "trigger_type": action_spec.trigger_type,
                    "action_type": action_spec.action_type,
                    "action_config": action_config,
                    "job_ids": job_ids,
                    "persistent": action_spec.persistent.unwrap_or(false),
                });

                default_api::create_workflow_action(config, workflow_id, action_body)
                    .map_err(|e| format!("Failed to create workflow action: {:?}", e))?;
            }
        }

        Ok(())
    }

    /// Helper function to resolve names and regex patterns to IDs
    /// Returns a vector of IDs matching either the exact names or the regex patterns
    fn resolve_names_and_regexes(
        exact_names: &Option<Vec<String>>,
        regex_patterns: &Option<Vec<String>>,
        name_to_id: &HashMap<String, i64>,
        resource_type: &str, // e.g., "Input file", "Job dependency"
        job_name: &str,      // The job that needs this resource
    ) -> Result<Vec<i64>, Box<dyn std::error::Error>> {
        let mut ids = Vec::new();

        // Add IDs for exact name matches
        if let Some(names) = exact_names {
            for name in names {
                match name_to_id.get(name) {
                    Some(&id) => ids.push(id),
                    None => {
                        return Err(format!(
                            "{} '{}' not found for job '{}'",
                            resource_type, name, job_name
                        )
                        .into());
                    }
                }
            }
        }

        // Add IDs for regex pattern matches
        if let Some(patterns) = regex_patterns {
            for pattern_str in patterns {
                let re = Regex::new(pattern_str).map_err(|e| {
                    format!(
                        "Invalid regex '{}' for {} in job '{}': {}",
                        pattern_str,
                        resource_type.to_lowercase(),
                        job_name,
                        e
                    )
                })?;

                let mut found_match = false;
                for (name, &id) in name_to_id {
                    if re.is_match(name) && !ids.contains(&id) {
                        ids.push(id);
                        found_match = true;
                    }
                }

                // Error if regex didn't match anything
                if !found_match {
                    return Err(format!(
                        "{} regex '{}' did not match any names for job '{}'",
                        resource_type, pattern_str, job_name
                    )
                    .into());
                }
            }
        }

        Ok(ids)
    }

    /// Topologically sort jobs into levels based on dependencies
    /// Returns a vector of levels, where each level contains jobs that can be created together
    fn topological_sort_jobs<'a>(
        jobs: &'a [JobSpec],
        dependencies: &HashMap<String, Vec<String>>,
    ) -> Result<Vec<Vec<&'a JobSpec>>, Box<dyn std::error::Error>> {
        use std::collections::HashSet;

        let mut levels = Vec::new();
        let mut remaining: HashSet<String> = jobs.iter().map(|j| j.name.clone()).collect();
        let mut processed = HashSet::new();

        while !remaining.is_empty() {
            let mut current_level = Vec::new();

            // Find all jobs whose dependencies are satisfied
            for job in jobs {
                if remaining.contains(&job.name) {
                    let deps = dependencies.get(&job.name).unwrap();
                    if deps.iter().all(|d| processed.contains(d)) {
                        current_level.push(job);
                    }
                }
            }

            if current_level.is_empty() {
                return Err("Circular dependency detected in job graph".into());
            }

            // Mark these jobs as processed
            for job in &current_level {
                remaining.remove(&job.name);
                processed.insert(job.name.clone());
            }

            levels.push(current_level);
        }

        Ok(levels)
    }

    /// Create JobModels with proper ID mapping using bulk API in batches of 1000
    /// Jobs are created in dependency order with blocked_by_job_ids set during initial creation
    fn create_jobs(
        config: &Configuration,
        workflow_id: i64,
        spec: &WorkflowSpec,
        file_name_to_id: &HashMap<String, i64>,
        user_data_name_to_id: &HashMap<String, i64>,
        resource_req_name_to_id: &HashMap<String, i64>,
        slurm_scheduler_name_to_id: &HashMap<String, i64>,
    ) -> Result<(HashMap<String, i64>, HashMap<String, models::JobModel>), Box<dyn std::error::Error>>
    {
        let mut job_name_to_id = HashMap::new();
        let mut created_jobs = HashMap::new();

        // Step 1: Build a set of all job names for validation
        let all_job_names: std::collections::HashSet<String> =
            spec.jobs.iter().map(|j| j.name.clone()).collect();

        // Step 2: Build dependency graph (job_name -> Vec<dependency_job_names>)
        let mut dependencies: HashMap<String, Vec<String>> = HashMap::new();

        for job_spec in &spec.jobs {
            let mut deps = Vec::new();

            // Add explicit dependencies
            if let Some(ref names) = job_spec.blocked_by_job_names {
                for dep_name in names {
                    // Validate that the dependency exists
                    if !all_job_names.contains(dep_name) {
                        return Err(format!(
                            "Blocking job '{}' not found for job '{}'",
                            dep_name, job_spec.name
                        )
                        .into());
                    }
                    deps.push(dep_name.clone());
                }
            }

            // Resolve regex dependencies
            if let Some(ref regexes) = job_spec.blocked_by_job_name_regexes {
                for regex_str in regexes {
                    let re = Regex::new(regex_str).map_err(|e| {
                        format!(
                            "Invalid regex '{}' in job '{}': {}",
                            regex_str, job_spec.name, e
                        )
                    })?;
                    let mut found_match = false;
                    for other_job in &spec.jobs {
                        if re.is_match(&other_job.name) && !deps.contains(&other_job.name) {
                            deps.push(other_job.name.clone());
                            found_match = true;
                        }
                    }
                    // Error if regex didn't match anything
                    if !found_match {
                        return Err(format!(
                            "Blocking job regex '{}' did not match any jobs for job '{}'",
                            regex_str, job_spec.name
                        )
                        .into());
                    }
                }
            }

            dependencies.insert(job_spec.name.clone(), deps);
        }

        // Step 3: Topologically sort jobs into levels
        let levels = Self::topological_sort_jobs(&spec.jobs, &dependencies)?;

        // Step 4: Create jobs level by level
        const BATCH_SIZE: usize = 1000;

        for level in levels {
            // Create job models for this level with blocked_by_job_ids resolved
            let mut job_models = Vec::new();
            let mut job_spec_mapping = Vec::new();

            for job_spec in level {
                let mut job_model = models::JobModel::new(
                    workflow_id,
                    job_spec.name.clone(),
                    job_spec.command.clone(),
                );

                // Set optional fields
                job_model.invocation_script = job_spec.invocation_script.clone();
                job_model.cancel_on_blocking_job_failure = job_spec.cancel_on_blocking_job_failure;
                job_model.supports_termination = job_spec.supports_termination;

                // Map file names and regexes to IDs
                let input_file_ids = Self::resolve_names_and_regexes(
                    &job_spec.input_file_names,
                    &job_spec.input_file_name_regexes,
                    file_name_to_id,
                    "Input file",
                    &job_spec.name,
                )?;
                if !input_file_ids.is_empty() {
                    job_model.input_file_ids = Some(input_file_ids);
                }

                let output_file_ids = Self::resolve_names_and_regexes(
                    &job_spec.output_file_names,
                    &job_spec.output_file_name_regexes,
                    file_name_to_id,
                    "Output file",
                    &job_spec.name,
                )?;
                if !output_file_ids.is_empty() {
                    job_model.output_file_ids = Some(output_file_ids);
                }

                // Map user data names and regexes to IDs
                let input_user_data_ids = Self::resolve_names_and_regexes(
                    &job_spec.input_user_data_names,
                    &job_spec.input_user_data_name_regexes,
                    user_data_name_to_id,
                    "Input user data",
                    &job_spec.name,
                )?;
                if !input_user_data_ids.is_empty() {
                    job_model.input_user_data_ids = Some(input_user_data_ids);
                }

                let output_user_data_ids = Self::resolve_names_and_regexes(
                    &job_spec.output_data_names,
                    &job_spec.output_user_data_name_regexes,
                    user_data_name_to_id,
                    "Output user data",
                    &job_spec.name,
                )?;
                if !output_user_data_ids.is_empty() {
                    job_model.output_user_data_ids = Some(output_user_data_ids);
                }

                // Map resource requirements name to ID
                if let Some(resource_req_name) = &job_spec.resource_requirements_name {
                    match resource_req_name_to_id.get(resource_req_name) {
                        Some(&resource_req_id) => {
                            job_model.resource_requirements_id = Some(resource_req_id)
                        }
                        None => {
                            return Err(format!(
                                "Resource requirements '{}' not found for job '{}'",
                                resource_req_name, job_spec.name
                            )
                            .into());
                        }
                    }
                }

                // Map scheduler name to ID
                if let Some(scheduler_name) = &job_spec.scheduler_name {
                    match slurm_scheduler_name_to_id.get(scheduler_name) {
                        Some(&scheduler_id) => job_model.scheduler_id = Some(scheduler_id),
                        None => {
                            return Err(format!(
                                "Scheduler '{}' not found for job '{}'",
                                scheduler_name, job_spec.name
                            )
                            .into());
                        }
                    }
                }

                // NEW: Resolve blocked_by_job_ids using accumulated job_name_to_id
                let dep_names = dependencies.get(&job_spec.name).unwrap();
                if !dep_names.is_empty() {
                    let mut blocked_ids = Vec::new();
                    for dep_name in dep_names {
                        let dep_id = job_name_to_id.get(dep_name).ok_or_else(|| {
                            format!(
                                "Dependency '{}' not found for job '{}' (not yet created)",
                                dep_name, job_spec.name
                            )
                        })?;
                        blocked_ids.push(*dep_id);
                    }
                    job_model.blocked_by_job_ids = Some(blocked_ids);
                }

                job_models.push(job_model);
                job_spec_mapping.push(job_spec);
            }

            // Create this level's jobs in batches of 1000
            for (batch_index, batch) in job_models.chunks(BATCH_SIZE).enumerate() {
                let jobs_model = models::JobsModel::new(batch.to_vec());

                let response = default_api::create_jobs(config, jobs_model).map_err(|e| {
                    format!(
                        "Failed to create batch {} of jobs: {:?}",
                        batch_index + 1,
                        e
                    )
                })?;

                let created_batch = response.jobs.ok_or("Create jobs response missing items")?;

                if created_batch.len() != batch.len() {
                    return Err(format!(
                        "Batch {} returned {} jobs but expected {}",
                        batch_index + 1,
                        created_batch.len(),
                        batch.len()
                    )
                    .into());
                }

                // Update mappings
                let batch_start = batch_index * BATCH_SIZE;
                for (i, created_job) in created_batch.iter().enumerate() {
                    let job_spec = job_spec_mapping[batch_start + i];
                    let job_id = created_job.id.ok_or("Created job missing ID")?;
                    job_name_to_id.insert(job_spec.name.clone(), job_id);
                    created_jobs.insert(job_spec.name.clone(), created_job.clone());
                }
            }
        }

        Ok((job_name_to_id, created_jobs))
    }

    /// Parse a WorkflowSpec from a KDL string
    #[cfg(feature = "client")]
    fn from_kdl_str(content: &str) -> Result<WorkflowSpec, Box<dyn std::error::Error>> {
        let doc: KdlDocument = content
            .parse()
            .map_err(|e| format!("Failed to parse KDL document: {}", e))?;

        let mut spec = WorkflowSpec::default();
        let mut jobs = Vec::new();
        let mut files = Vec::new();
        let mut user_data = Vec::new();
        let mut resource_requirements = Vec::new();
        let mut slurm_schedulers = Vec::new();
        let mut actions = Vec::new();

        for node in doc.nodes() {
            match node.name().value() {
                "name" => {
                    spec.name = node
                        .entries()
                        .first()
                        .and_then(|e| e.value().as_string())
                        .ok_or("name must have a string value")?
                        .to_string();
                }
                "user" => {
                    spec.user = Some(
                        node.entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .ok_or("user must have a string value")?
                            .to_string(),
                    );
                }
                "description" => {
                    spec.description = node
                        .entries()
                        .first()
                        .and_then(|e| e.value().as_string())
                        .ok_or("description must have a string value")?
                        .to_string();
                }
                "compute_node_expiration_buffer_seconds" => {
                    spec.compute_node_expiration_buffer_seconds = node
                        .entries()
                        .first()
                        .and_then(|e| e.value().as_integer())
                        .and_then(|i| i.try_into().ok());
                }
                "compute_node_wait_for_new_jobs_seconds" => {
                    spec.compute_node_wait_for_new_jobs_seconds = node
                        .entries()
                        .first()
                        .and_then(|e| e.value().as_integer())
                        .and_then(|i| i.try_into().ok());
                }
                "compute_node_ignore_workflow_completion" => {
                    spec.compute_node_ignore_workflow_completion =
                        node.entries().first().and_then(|e| e.value().as_bool());
                }
                "compute_node_wait_for_healthy_database_minutes" => {
                    spec.compute_node_wait_for_healthy_database_minutes = node
                        .entries()
                        .first()
                        .and_then(|e| e.value().as_integer())
                        .and_then(|i| i.try_into().ok());
                }
                "jobs_sort_method" => {
                    if let Some(value_str) =
                        node.entries().first().and_then(|e| e.value().as_string())
                    {
                        spec.jobs_sort_method = match value_str {
                            "gpus_runtime_memory" => {
                                Some(models::ClaimJobsSortMethod::GpusRuntimeMemory)
                            }
                            "gpus_memory_runtime" => {
                                Some(models::ClaimJobsSortMethod::GpusMemoryRuntime)
                            }
                            "none" => Some(models::ClaimJobsSortMethod::None),
                            _ => {
                                return Err(
                                    format!("Invalid jobs_sort_method: {}", value_str).into()
                                );
                            }
                        };
                    }
                }
                "job" => {
                    let job_spec = Self::parse_kdl_job(node)?;
                    jobs.push(job_spec);
                }
                "file" => {
                    let file_spec = Self::parse_kdl_file(node)?;
                    files.push(file_spec);
                }
                "user_data" => {
                    let user_data_spec = Self::parse_kdl_user_data(node)?;
                    user_data.push(user_data_spec);
                }
                "resource_requirements" => {
                    let resource_req_spec = Self::parse_kdl_resource_requirements(node)?;
                    resource_requirements.push(resource_req_spec);
                }
                "slurm_scheduler" => {
                    let scheduler_spec = Self::parse_kdl_slurm_scheduler(node)?;
                    slurm_schedulers.push(scheduler_spec);
                }
                "action" => {
                    let action_spec = Self::parse_kdl_action(node)?;
                    actions.push(action_spec);
                }
                "resource_monitor" => {
                    let monitor_config = Self::parse_kdl_resource_monitor(node)?;
                    spec.resource_monitor = Some(monitor_config);
                }
                _ => {
                    // Ignore unknown nodes
                }
            }
        }

        spec.jobs = jobs;
        spec.files = Some(files).filter(|v| !v.is_empty());
        spec.user_data = Some(user_data).filter(|v| !v.is_empty());
        spec.resource_requirements = Some(resource_requirements).filter(|v| !v.is_empty());
        spec.slurm_schedulers = Some(slurm_schedulers).filter(|v| !v.is_empty());
        spec.actions = Some(actions).filter(|v| !v.is_empty());

        Ok(spec)
    }

    #[cfg(feature = "client")]
    fn parse_kdl_job(node: &KdlNode) -> Result<JobSpec, Box<dyn std::error::Error>> {
        let name = node
            .entries()
            .first()
            .and_then(|e| e.value().as_string())
            .ok_or("job must have a name")?
            .to_string();

        let mut job_spec = JobSpec {
            name,
            ..Default::default()
        };

        if let Some(children) = node.children() {
            for child in children.nodes() {
                match child.name().value() {
                    "command" => {
                        job_spec.command = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .ok_or("command must have a string value")?
                            .to_string();
                    }
                    "invocation_script" => {
                        job_spec.invocation_script = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .map(|s| s.to_string());
                    }
                    "cancel_on_blocking_job_failure" => {
                        job_spec.cancel_on_blocking_job_failure =
                            child.entries().first().and_then(|e| e.value().as_bool());
                    }
                    "supports_termination" => {
                        job_spec.supports_termination =
                            child.entries().first().and_then(|e| e.value().as_bool());
                    }
                    "resource_requirements_name" => {
                        job_spec.resource_requirements_name = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .map(|s| s.to_string());
                    }
                    "blocked_by_job" => {
                        if job_spec.blocked_by_job_names.is_none() {
                            job_spec.blocked_by_job_names = Some(Vec::new());
                        }
                        if let Some(job_name) =
                            child.entries().first().and_then(|e| e.value().as_string())
                        {
                            job_spec
                                .blocked_by_job_names
                                .as_mut()
                                .unwrap()
                                .push(job_name.to_string());
                        }
                    }
                    "input_file" => {
                        if job_spec.input_file_names.is_none() {
                            job_spec.input_file_names = Some(Vec::new());
                        }
                        if let Some(file_name) =
                            child.entries().first().and_then(|e| e.value().as_string())
                        {
                            job_spec
                                .input_file_names
                                .as_mut()
                                .unwrap()
                                .push(file_name.to_string());
                        }
                    }
                    "output_file" => {
                        if job_spec.output_file_names.is_none() {
                            job_spec.output_file_names = Some(Vec::new());
                        }
                        if let Some(file_name) =
                            child.entries().first().and_then(|e| e.value().as_string())
                        {
                            job_spec
                                .output_file_names
                                .as_mut()
                                .unwrap()
                                .push(file_name.to_string());
                        }
                    }
                    "input_user_data" => {
                        if job_spec.input_user_data_names.is_none() {
                            job_spec.input_user_data_names = Some(Vec::new());
                        }
                        if let Some(data_name) =
                            child.entries().first().and_then(|e| e.value().as_string())
                        {
                            job_spec
                                .input_user_data_names
                                .as_mut()
                                .unwrap()
                                .push(data_name.to_string());
                        }
                    }
                    "output_data" => {
                        if job_spec.output_data_names.is_none() {
                            job_spec.output_data_names = Some(Vec::new());
                        }
                        if let Some(data_name) =
                            child.entries().first().and_then(|e| e.value().as_string())
                        {
                            job_spec
                                .output_data_names
                                .as_mut()
                                .unwrap()
                                .push(data_name.to_string());
                        }
                    }
                    "scheduler_name" => {
                        job_spec.scheduler_name = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .map(|s| s.to_string());
                    }
                    _ => {}
                }
            }
        }

        Ok(job_spec)
    }

    #[cfg(feature = "client")]
    fn parse_kdl_file(node: &KdlNode) -> Result<FileSpec, Box<dyn std::error::Error>> {
        let name = node
            .entries()
            .first()
            .and_then(|e| e.value().as_string())
            .ok_or("file must have a name")?
            .to_string();

        let path = node
            .get("path")
            .and_then(|e| e.as_string())
            .ok_or("file must have a path property")?
            .to_string();

        Ok(FileSpec {
            name,
            path,
            parameters: None,
        })
    }

    #[cfg(feature = "client")]
    fn parse_kdl_user_data(node: &KdlNode) -> Result<UserDataSpec, Box<dyn std::error::Error>> {
        let name = node
            .entries()
            .first()
            .and_then(|e| e.value().as_string())
            .map(|s| s.to_string());

        let mut is_ephemeral = None;
        let mut data_str: Option<&str> = None;

        if let Some(children) = node.children() {
            for child in children.nodes() {
                match child.name().value() {
                    "is_ephemeral" => {
                        is_ephemeral = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_bool());
                    }
                    "data" => {
                        data_str = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string());
                    }
                    _ => {}
                }
            }
        }

        let data_str = data_str.ok_or("user_data must have a data property")?;
        let data: serde_json::Value = serde_json::from_str(data_str)?;

        Ok(UserDataSpec {
            is_ephemeral,
            name,
            data: Some(data),
        })
    }

    #[cfg(feature = "client")]
    fn parse_kdl_resource_requirements(
        node: &KdlNode,
    ) -> Result<ResourceRequirementsSpec, Box<dyn std::error::Error>> {
        let name = node
            .entries()
            .first()
            .and_then(|e| e.value().as_string())
            .ok_or("resource_requirements must have a name")?
            .to_string();

        let mut spec = ResourceRequirementsSpec {
            name,
            num_cpus: 0,
            num_gpus: 0,
            num_nodes: 0,
            memory: String::new(),
            runtime: String::new(),
        };

        if let Some(children) = node.children() {
            for child in children.nodes() {
                match child.name().value() {
                    "num_cpus" => {
                        spec.num_cpus = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_integer())
                            .and_then(|i| i.try_into().ok())
                            .ok_or("num_cpus must have a valid integer value")?;
                    }
                    "num_gpus" => {
                        spec.num_gpus = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_integer())
                            .and_then(|i| i.try_into().ok())
                            .ok_or("num_gpus must have a valid integer value")?;
                    }
                    "num_nodes" => {
                        spec.num_nodes = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_integer())
                            .and_then(|i| i.try_into().ok())
                            .ok_or("num_nodes must have a valid integer value")?;
                    }
                    "memory" => {
                        spec.memory = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .ok_or("memory must have a string value")?
                            .to_string();
                    }
                    "runtime" => {
                        spec.runtime = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .ok_or("runtime must have a string value")?
                            .to_string();
                    }
                    _ => {}
                }
            }
        }

        Ok(spec)
    }

    #[cfg(feature = "client")]
    fn parse_kdl_slurm_scheduler(
        node: &KdlNode,
    ) -> Result<SlurmSchedulerSpec, Box<dyn std::error::Error>> {
        let name = node
            .entries()
            .first()
            .and_then(|e| e.value().as_string())
            .map(|s| s.to_string());

        let mut spec = SlurmSchedulerSpec {
            name,
            account: String::new(),
            gres: None,
            mem: None,
            nodes: 0,
            ntasks_per_node: None,
            partition: None,
            qos: None,
            tmp: None,
            walltime: String::new(),
            extra: None,
        };

        if let Some(children) = node.children() {
            for child in children.nodes() {
                match child.name().value() {
                    "account" => {
                        spec.account = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .ok_or("account must have a string value")?
                            .to_string();
                    }
                    "gres" => {
                        spec.gres = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .map(|s| s.to_string());
                    }
                    "mem" => {
                        spec.mem = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .map(|s| s.to_string());
                    }
                    "nodes" => {
                        spec.nodes = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_integer())
                            .and_then(|i| i.try_into().ok())
                            .ok_or("nodes must have a valid integer value")?;
                    }
                    "ntasks_per_node" => {
                        spec.ntasks_per_node = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_integer())
                            .and_then(|i| i.try_into().ok());
                    }
                    "partition" => {
                        spec.partition = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .map(|s| s.to_string());
                    }
                    "qos" => {
                        spec.qos = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .map(|s| s.to_string());
                    }
                    "tmp" => {
                        spec.tmp = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .map(|s| s.to_string());
                    }
                    "walltime" => {
                        spec.walltime = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .ok_or("walltime must have a string value")?
                            .to_string();
                    }
                    "extra" => {
                        spec.extra = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .map(|s| s.to_string());
                    }
                    _ => {}
                }
            }
        }

        // Validate required fields
        if spec.walltime.is_empty() {
            return Err("walltime is required for Slurm scheduler".into());
        }

        Ok(spec)
    }

    #[cfg(feature = "client")]
    fn parse_kdl_resource_monitor(
        node: &KdlNode,
    ) -> Result<crate::client::resource_monitor::ResourceMonitorConfig, Box<dyn std::error::Error>>
    {
        let mut config = crate::client::resource_monitor::ResourceMonitorConfig::default();

        if let Some(children) = node.children() {
            for child in children.nodes() {
                match child.name().value() {
                    "enabled" => {
                        config.enabled = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_bool())
                            .ok_or("enabled must have a boolean value")?;
                    }
                    "granularity" => {
                        if let Some(value_str) =
                            child.entries().first().and_then(|e| e.value().as_string())
                        {
                            config.granularity = match value_str {
                                "summary" => {
                                    crate::client::resource_monitor::MonitorGranularity::Summary
                                }
                                "time_series" => {
                                    crate::client::resource_monitor::MonitorGranularity::TimeSeries
                                }
                                _ => {
                                    return Err(format!("Invalid granularity: {}", value_str).into());
                                }
                            };
                        }
                    }
                    "sample_interval_seconds" => {
                        config.sample_interval_seconds = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_integer())
                            .and_then(|i| i.try_into().ok())
                            .ok_or("sample_interval_seconds must have a valid integer value")?;
                    }
                    "generate_plots" => {
                        config.generate_plots = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_bool())
                            .ok_or("generate_plots must have a boolean value")?;
                    }
                    _ => {}
                }
            }
        }

        Ok(config)
    }

    #[cfg(feature = "client")]
    fn parse_kdl_action(
        node: &KdlNode,
    ) -> Result<WorkflowActionSpec, Box<dyn std::error::Error>> {
        let mut spec = WorkflowActionSpec {
            trigger_type: String::new(),
            action_type: String::new(),
            job_names: None,
            job_name_regexes: None,
            commands: None,
            scheduler_name: None,
            scheduler_type: None,
            num_allocations: None,
            start_one_worker_per_node: None,
            max_parallel_jobs: None,
            persistent: None,
        };

        if let Some(children) = node.children() {
            for child in children.nodes() {
                match child.name().value() {
                    "trigger_type" => {
                        spec.trigger_type = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .ok_or("trigger_type must have a string value")?
                            .to_string();
                    }
                    "action_type" => {
                        spec.action_type = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .ok_or("action_type must have a string value")?
                            .to_string();
                    }
                    "job_name" => {
                        if spec.job_names.is_none() {
                            spec.job_names = Some(Vec::new());
                        }
                        if let Some(job_name) =
                            child.entries().first().and_then(|e| e.value().as_string())
                        {
                            spec.job_names.as_mut().unwrap().push(job_name.to_string());
                        }
                    }
                    "job_name_regex" => {
                        if spec.job_name_regexes.is_none() {
                            spec.job_name_regexes = Some(Vec::new());
                        }
                        if let Some(regex) =
                            child.entries().first().and_then(|e| e.value().as_string())
                        {
                            spec.job_name_regexes
                                .as_mut()
                                .unwrap()
                                .push(regex.to_string());
                        }
                    }
                    "command" => {
                        if spec.commands.is_none() {
                            spec.commands = Some(Vec::new());
                        }
                        if let Some(command) =
                            child.entries().first().and_then(|e| e.value().as_string())
                        {
                            spec.commands.as_mut().unwrap().push(command.to_string());
                        }
                    }
                    "scheduler_name" => {
                        spec.scheduler_name = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .map(|s| s.to_string());
                    }
                    "scheduler_type" => {
                        spec.scheduler_type = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_string())
                            .map(|s| s.to_string());
                    }
                    "num_allocations" => {
                        spec.num_allocations = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_integer())
                            .and_then(|i| i.try_into().ok());
                    }
                    "start_one_worker_per_node" => {
                        spec.start_one_worker_per_node =
                            child.entries().first().and_then(|e| e.value().as_bool());
                    }
                    "max_parallel_jobs" => {
                        spec.max_parallel_jobs = child
                            .entries()
                            .first()
                            .and_then(|e| e.value().as_integer())
                            .and_then(|i| i.try_into().ok());
                    }
                    "persistent" => {
                        spec.persistent = child.entries().first().and_then(|e| e.value().as_bool());
                    }
                    _ => {}
                }
            }
        }

        // Validate required fields
        if spec.trigger_type.is_empty() {
            return Err("trigger_type is required for action".into());
        }
        if spec.action_type.is_empty() {
            return Err("action_type is required for action".into());
        }

        Ok(spec)
    }

    /// Deserialize a WorkflowSpec from a specification file (JSON, JSON5, or YAML)
    pub fn from_spec_file<P: AsRef<Path>>(
        path: P,
    ) -> Result<WorkflowSpec, Box<dyn std::error::Error>> {
        let path_ref = path.as_ref();
        let file_content = fs::read_to_string(path_ref)?;

        // Determine file type based on extension
        let extension = path_ref
            .extension()
            .and_then(|ext| ext.to_str())
            .unwrap_or("");

        let workflow_spec: WorkflowSpec = match extension.to_lowercase().as_str() {
            "json" => serde_json::from_str(&file_content)?,
            "json5" => json5::from_str(&file_content)?,
            "yaml" | "yml" => serde_yaml::from_str(&file_content)?,
            #[cfg(feature = "client")]
            "kdl" => Self::from_kdl_str(&file_content)?,
            _ => {
                // Try to parse as JSON first, then JSON5, then YAML, then KDL
                if let Ok(spec) = serde_json::from_str::<WorkflowSpec>(&file_content) {
                    spec
                } else if let Ok(spec) = json5::from_str::<WorkflowSpec>(&file_content) {
                    spec
                } else if let Ok(spec) = serde_yaml::from_str::<WorkflowSpec>(&file_content) {
                    spec
                } else {
                    #[cfg(feature = "client")]
                    {
                        Self::from_kdl_str(&file_content)?
                    }
                    #[cfg(not(feature = "client"))]
                    {
                        return Err("Unable to parse workflow spec file".into());
                    }
                }
            }
        };

        Ok(workflow_spec)
    }

    /// Perform variable substitution on job commands and invocation scripts
    /// Supported variables:
    /// - ${files.input.NAME} - input file (automatically adds to input_file_names)
    /// - ${files.output.NAME} - output file (automatically adds to output_file_names)
    /// - ${user_data.input.NAME} - input user data (automatically adds to input_user_data_names)
    /// - ${user_data.output.NAME} - output user data (automatically adds to output_data_names)
    fn substitute_variables(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        // Build file name to path mapping
        let mut file_name_to_path = HashMap::new();
        if let Some(files) = &self.files {
            for file_spec in files {
                file_name_to_path.insert(file_spec.name.clone(), file_spec.path.clone());
            }
        }

        // Build user data name to data mapping
        let mut user_data_name_to_data = HashMap::new();
        if let Some(user_data_list) = &self.user_data {
            for user_data_spec in user_data_list {
                if let Some(name) = &user_data_spec.name {
                    if let Some(data) = &user_data_spec.data {
                        user_data_name_to_data.insert(name.clone(), data.clone());
                    }
                }
            }
        }

        // Substitute variables in each job and extract dependencies
        for job in &mut self.jobs {
            let (new_command, input_files, output_files, input_user_data, output_user_data) =
                Self::substitute_and_extract(
                    &job.command,
                    &file_name_to_path,
                    &user_data_name_to_data,
                )?;
            job.command = new_command;

            // Set input/output file names from extracted dependencies
            if !input_files.is_empty() {
                job.input_file_names = Some(input_files);
            }
            if !output_files.is_empty() {
                job.output_file_names = Some(output_files);
            }
            if !input_user_data.is_empty() {
                job.input_user_data_names = Some(input_user_data);
            }
            if !output_user_data.is_empty() {
                job.output_data_names = Some(output_user_data);
            }

            // Process invocation script if present
            if let Some(script) = &job.invocation_script {
                let (
                    new_script,
                    script_input_files,
                    script_output_files,
                    script_input_user_data,
                    script_output_user_data,
                ) = Self::substitute_and_extract(
                    script,
                    &file_name_to_path,
                    &user_data_name_to_data,
                )?;
                job.invocation_script = Some(new_script);

                // Merge dependencies from invocation script
                if !script_input_files.is_empty() {
                    let mut combined = job.input_file_names.clone().unwrap_or_default();
                    combined.extend(script_input_files);
                    combined.sort();
                    combined.dedup();
                    job.input_file_names = Some(combined);
                }
                if !script_output_files.is_empty() {
                    let mut combined = job.output_file_names.clone().unwrap_or_default();
                    combined.extend(script_output_files);
                    combined.sort();
                    combined.dedup();
                    job.output_file_names = Some(combined);
                }
                if !script_input_user_data.is_empty() {
                    let mut combined = job.input_user_data_names.clone().unwrap_or_default();
                    combined.extend(script_input_user_data);
                    combined.sort();
                    combined.dedup();
                    job.input_user_data_names = Some(combined);
                }
                if !script_output_user_data.is_empty() {
                    let mut combined = job.output_data_names.clone().unwrap_or_default();
                    combined.extend(script_output_user_data);
                    combined.sort();
                    combined.dedup();
                    job.output_data_names = Some(combined);
                }
            }
        }

        Ok(())
    }

    /// Substitute variables and extract input/output dependencies
    /// Returns: (substituted_string, input_files, output_files, input_user_data, output_user_data)
    fn substitute_and_extract(
        input: &str,
        file_name_to_path: &HashMap<String, String>,
        user_data_name_to_data: &HashMap<String, serde_json::Value>,
    ) -> Result<
        (String, Vec<String>, Vec<String>, Vec<String>, Vec<String>),
        Box<dyn std::error::Error>,
    > {
        let mut result = input.to_string();
        let mut input_files = Vec::new();
        let mut output_files = Vec::new();
        let mut input_user_data = Vec::new();
        let mut output_user_data = Vec::new();

        // Extract and replace ${files.input.NAME}
        for (name, path) in file_name_to_path {
            let input_pattern = format!("${{files.input.{}}}", name);
            if result.contains(&input_pattern) {
                result = result.replace(&input_pattern, path);
                input_files.push(name.clone());
            }
        }

        // Extract and replace ${files.output.NAME}
        for (name, path) in file_name_to_path {
            let output_pattern = format!("${{files.output.{}}}", name);
            if result.contains(&output_pattern) {
                result = result.replace(&output_pattern, path);
                output_files.push(name.clone());
            }
        }

        // Extract and replace ${user_data.input.NAME}
        for (name, data) in user_data_name_to_data {
            let input_pattern = format!("${{user_data.input.{}}}", name);
            if result.contains(&input_pattern) {
                let data_str = serde_json::to_string(data)?;
                result = result.replace(&input_pattern, &data_str);
                input_user_data.push(name.clone());
            }
        }

        // Extract and replace ${user_data.output.NAME}
        for (name, data) in user_data_name_to_data {
            let output_pattern = format!("${{user_data.output.{}}}", name);
            if result.contains(&output_pattern) {
                let data_str = serde_json::to_string(data)?;
                result = result.replace(&output_pattern, &data_str);
                output_user_data.push(name.clone());
            }
        }

        Ok((
            result,
            input_files,
            output_files,
            input_user_data,
            output_user_data,
        ))
    }
}
