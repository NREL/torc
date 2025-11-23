mod common;

use common::{ServerProcess, start_server};
use rstest::rstest;
use serde_json;
use std::fs;
use tempfile::NamedTempFile;
use torc::client::default_api;
use torc::client::workflow_spec::{
    FileSpec, JobSpec, ResourceRequirementsSpec, SlurmSchedulerSpec, UserDataSpec, WorkflowSpec,
};

#[test]
fn test_job_specification_new() {
    let job = JobSpec::new("test_job".to_string(), "echo hello".to_string());

    assert_eq!(job.name, "test_job");
    assert_eq!(job.command, "echo hello");
    assert_eq!(job.invocation_script, None);
    assert_eq!(job.cancel_on_blocking_job_failure, Some(false));
    assert_eq!(job.supports_termination, Some(false));
    assert_eq!(job.resource_requirements, None);
    assert_eq!(job.blocked_by, None);
    assert_eq!(job.input_files, None);
    assert_eq!(job.output_files, None);
    assert_eq!(job.input_user_data, None);
    assert_eq!(job.output_user_data, None);
    assert_eq!(job.scheduler, None);
}

#[test]
fn test_job_specification_all_fields() {
    let mut job = JobSpec::new("complex_job".to_string(), "python script.py".to_string());

    job.invocation_script = Some("#!/bin/bash\nset -e\n".to_string());
    job.cancel_on_blocking_job_failure = Some(true);
    job.supports_termination = Some(true);
    job.resource_requirements = Some("large_job".to_string());
    job.blocked_by = Some(vec!["job1".to_string(), "job2".to_string()]);
    job.input_files = Some(vec!["input.csv".to_string()]);
    job.output_files = Some(vec!["output.json".to_string()]);
    job.input_user_data = Some(vec!["config".to_string()]);
    job.output_user_data = Some(vec!["results".to_string()]);
    job.scheduler = Some("gpu_scheduler".to_string());

    assert_eq!(job.name, "complex_job");
    assert_eq!(job.command, "python script.py");
    assert_eq!(
        job.invocation_script,
        Some("#!/bin/bash\nset -e\n".to_string())
    );
    assert_eq!(job.cancel_on_blocking_job_failure, Some(true));
    assert_eq!(job.supports_termination, Some(true));
    assert_eq!(job.resource_requirements, Some("large_job".to_string()));
    assert_eq!(
        job.blocked_by,
        Some(vec!["job1".to_string(), "job2".to_string()])
    );
    assert_eq!(job.input_files, Some(vec!["input.csv".to_string()]));
    assert_eq!(job.output_files, Some(vec!["output.json".to_string()]));
    assert_eq!(job.input_user_data, Some(vec!["config".to_string()]));
    assert_eq!(job.output_user_data, Some(vec!["results".to_string()]));
    assert_eq!(job.scheduler, Some("gpu_scheduler".to_string()));
}

#[test]
fn test_workflow_specification_new() {
    let jobs = vec![
        JobSpec::new("job1".to_string(), "echo hello".to_string()),
        JobSpec::new("job2".to_string(), "echo world".to_string()),
    ];

    let workflow = WorkflowSpec::new(
        "test_workflow".to_string(),
        "test_user".to_string(),
        "Test workflow description".to_string(),
        jobs.clone(),
    );

    assert_eq!(workflow.name, "test_workflow");
    assert_eq!(workflow.user, Some("test_user".to_string()));
    assert_eq!(workflow.description, "Test workflow description");
    assert_eq!(workflow.jobs.len(), 2);
    assert_eq!(workflow.jobs[0].name, "job1");
    assert_eq!(workflow.jobs[1].name, "job2");
    assert_eq!(workflow.files, None);
    assert_eq!(workflow.user_data, None);
    assert_eq!(workflow.resource_requirements, None);
    assert_eq!(workflow.slurm_schedulers, None);
}

#[test]
fn test_workflow_specification_minimal_serialization() {
    let jobs = vec![JobSpec::new("simple_job".to_string(), "ls".to_string())];
    let workflow = WorkflowSpec::new(
        "minimal_workflow".to_string(),
        "user".to_string(),
        "Minimal test".to_string(),
        jobs,
    );

    let json = serde_json::to_string_pretty(&workflow).expect("Failed to serialize");
    let deserialized: WorkflowSpec = serde_json::from_str(&json).expect("Failed to deserialize");

    assert_eq!(workflow, deserialized);
}

#[test]
fn test_workflow_specification_complete_serialization() {
    // Create files
    let files = vec![
        FileSpec::new("input.txt".to_string(), "/data/input.txt".to_string()),
        FileSpec::new("output.txt".to_string(), "/data/output.txt".to_string()),
    ];

    // Create user data
    let user_data = vec![
        UserDataSpec {
            is_ephemeral: Some(true),
            name: Some("config".to_string()),
            data: Some(serde_json::json!({"key": "value"})),
        },
        UserDataSpec {
            is_ephemeral: Some(false),
            name: Some("results".to_string()),
            data: Some(serde_json::json!({"count": 42})),
        },
    ];

    // Create resource requirements
    let resource_requirements = vec![
        ResourceRequirementsSpec {
            name: "small_job".to_string(),
            num_cpus: 1,
            num_gpus: 0,
            num_nodes: 1,
            memory: "2g".to_string(),
            runtime: "PT30M".to_string(),
        },
        ResourceRequirementsSpec {
            name: "large_job".to_string(),
            num_cpus: 8,
            num_gpus: 2,
            num_nodes: 2,
            memory: "64g".to_string(),
            runtime: "PT4H".to_string(),
        },
    ];

    // Create slurm schedulers
    let slurm_schedulers = vec![
        SlurmSchedulerSpec {
            name: Some("default".to_string()),
            account: "project1".to_string(),
            gres: None,
            mem: Some("8G".to_string()),
            nodes: 1,
            ntasks_per_node: Some(1),
            partition: Some("general".to_string()),
            qos: Some("normal".to_string()),
            tmp: Some("10G".to_string()),
            walltime: "01:00:00".to_string(),
            extra: None,
        },
        SlurmSchedulerSpec {
            name: Some("gpu".to_string()),
            account: "gpu_project".to_string(),
            gres: Some("gpu:2".to_string()),
            mem: Some("32G".to_string()),
            nodes: 1,
            ntasks_per_node: Some(2),
            partition: Some("gpu".to_string()),
            qos: Some("high".to_string()),
            tmp: Some("50G".to_string()),
            walltime: "04:00:00".to_string(),
            extra: Some("--constraint=v100".to_string()),
        },
    ];

    // Create complex jobs
    let mut job1 = JobSpec::new("preprocess".to_string(), "python preprocess.py".to_string());
    job1.invocation_script = Some("#!/bin/bash\nexport PYTHONPATH=/opt/tools\n".to_string());
    job1.supports_termination = Some(true);
    job1.resource_requirements = Some("small_job".to_string());
    job1.input_files = Some(vec!["input.txt".to_string()]);
    job1.output_files = Some(vec!["output.txt".to_string()]);
    job1.input_user_data = Some(vec!["config".to_string()]);
    job1.output_user_data = Some(vec!["results".to_string()]);
    job1.scheduler = Some("default".to_string());

    let mut job2 = JobSpec::new("analyze".to_string(), "python analyze.py".to_string());
    job2.cancel_on_blocking_job_failure = Some(true);
    job2.supports_termination = Some(true);
    job2.resource_requirements = Some("large_job".to_string());
    job2.blocked_by = Some(vec!["preprocess".to_string()]);
    job2.input_files = Some(vec!["output.txt".to_string()]);
    job2.input_user_data = Some(vec!["results".to_string()]);
    job2.scheduler = Some("gpu".to_string());

    let jobs = vec![job1, job2];

    let mut workflow = WorkflowSpec::new(
        "complex_workflow".to_string(),
        "data_scientist".to_string(),
        "Complex data processing workflow".to_string(),
        jobs,
    );

    workflow.files = Some(files);
    workflow.user_data = Some(user_data);
    workflow.resource_requirements = Some(resource_requirements);
    workflow.slurm_schedulers = Some(slurm_schedulers);

    let json = serde_json::to_string_pretty(&workflow).expect("Failed to serialize");
    let deserialized: WorkflowSpec = serde_json::from_str(&json).expect("Failed to deserialize");

    assert_eq!(workflow, deserialized);
    assert_eq!(deserialized.files.as_ref().unwrap().len(), 2);
    assert_eq!(deserialized.user_data.as_ref().unwrap().len(), 2);
    assert_eq!(
        deserialized.resource_requirements.as_ref().unwrap().len(),
        2
    );
    assert_eq!(deserialized.slurm_schedulers.as_ref().unwrap().len(), 2);
    assert_eq!(deserialized.jobs.len(), 2);
}

#[test]
fn test_from_json_file() {
    let workflow_data = serde_json::json!({
        "name": "file_test_workflow",
        "user": "file_user",
        "description": "Test reading from file",
        "jobs": [
            {
                "name": "test_job",
                "command": "echo hello",
                "invocation_script": null,
                "cancel_on_blocking_job_failure": false,
                "supports_termination": false,
                "resource_requirements": null,
                "blocked_by": null,
                "input_files": null,
                "output_files": null,
                "input_user_data": null,
                "output_user_data": null,
                "scheduler": null
            }
        ],
        "files": null,
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let workflow =
        WorkflowSpec::from_spec_file(&temp_file.path()).expect("Failed to read from JSON file");

    assert_eq!(workflow.name, "file_test_workflow");
    assert_eq!(workflow.user, Some("file_user".to_string()));
    assert_eq!(workflow.description, "Test reading from file");
    assert_eq!(workflow.jobs.len(), 1);
    assert_eq!(workflow.jobs[0].name, "test_job");
}

#[test]
fn test_from_json_file_invalid_json() {
    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(&temp_file.path(), "{ invalid json }").expect("Failed to write temp file");

    let result = WorkflowSpec::from_spec_file(&temp_file.path());
    assert!(result.is_err());
}

#[test]
fn test_from_json_file_missing_required_fields() {
    let workflow_data = serde_json::json!({
        "name": "incomplete_workflow",
        "user": "test_user"
        // Missing description and jobs
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let result = WorkflowSpec::from_spec_file(&temp_file.path());
    assert!(result.is_err());
}

#[test]
fn test_empty_jobs_list() {
    let workflow_data = serde_json::json!({
        "name": "empty_workflow",
        "user": "test_user",
        "description": "Workflow with no jobs",
        "jobs": [],
        "files": null,
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let workflow =
        WorkflowSpec::from_spec_file(&temp_file.path()).expect("Failed to read from JSON file");

    assert_eq!(workflow.jobs.len(), 0);
}

#[test]
fn test_job_with_all_optional_fields_none() {
    let job_data = serde_json::json!({
        "name": "minimal_job",
        "command": "echo test",
        "invocation_script": null,
        "cancel_on_blocking_job_failure": false,
        "supports_termination": false,
        "resource_requirements": null,
        "blocked_by": null,
        "input_files": null,
        "output_files": null,
        "input_user_data": null,
        "output_user_data": null,
        "scheduler": null
    });

    let job: JobSpec = serde_json::from_value(job_data).expect("Failed to deserialize job");

    assert_eq!(job.name, "minimal_job");
    assert_eq!(job.command, "echo test");
    assert_eq!(job.invocation_script, None);
    assert_eq!(job.cancel_on_blocking_job_failure, Some(false));
    assert_eq!(job.supports_termination, Some(false));
    assert_eq!(job.resource_requirements, None);
    assert_eq!(job.blocked_by, None);
    assert_eq!(job.input_files, None);
    assert_eq!(job.output_files, None);
    assert_eq!(job.input_user_data, None);
    assert_eq!(job.output_user_data, None);
    assert_eq!(job.scheduler, None);
}

#[test]
fn test_job_with_empty_arrays() {
    let job_data = serde_json::json!({
        "name": "empty_arrays_job",
        "command": "echo test",
        "invocation_script": null,
        "cancel_on_blocking_job_failure": false,
        "supports_termination": false,
        "resource_requirements": null,
        "blocked_by": [],
        "input_files": [],
        "output_files": [],
        "input_user_data": [],
        "output_user_data": [],
        "scheduler": null
    });

    let job: JobSpec = serde_json::from_value(job_data).expect("Failed to deserialize job");

    assert_eq!(job.blocked_by, Some(vec![]));
    assert_eq!(job.input_files, Some(vec![]));
    assert_eq!(job.output_files, Some(vec![]));
    assert_eq!(job.input_user_data, Some(vec![]));
    assert_eq!(job.output_user_data, Some(vec![]));
}

#[test]
fn test_workflow_with_complex_dependencies() {
    let jobs = vec![
        {
            let mut job = JobSpec::new("job_a".to_string(), "echo a".to_string());
            job.output_files = Some(vec!["file_a".to_string()]);
            job.output_user_data = Some(vec!["data_a".to_string()]);
            job
        },
        {
            let mut job = JobSpec::new("job_b".to_string(), "echo b".to_string());
            job.output_files = Some(vec!["file_b".to_string()]);
            job.output_user_data = Some(vec!["data_b".to_string()]);
            job
        },
        {
            let mut job = JobSpec::new("job_c".to_string(), "echo c".to_string());
            job.blocked_by = Some(vec!["job_a".to_string(), "job_b".to_string()]);
            job.input_files = Some(vec!["file_a".to_string(), "file_b".to_string()]);
            job.input_user_data = Some(vec!["data_a".to_string(), "data_b".to_string()]);
            job.output_files = Some(vec!["file_c".to_string()]);
            job
        },
    ];

    let workflow = WorkflowSpec::new(
        "dependency_test".to_string(),
        "test_user".to_string(),
        "Test complex dependencies".to_string(),
        jobs,
    );

    // Serialize and deserialize to ensure structure is preserved
    let json = serde_json::to_string_pretty(&workflow).expect("Failed to serialize");
    let deserialized: WorkflowSpec = serde_json::from_str(&json).expect("Failed to deserialize");

    assert_eq!(deserialized.jobs.len(), 3);

    // Check job_c dependencies
    let job_c = &deserialized.jobs[2];
    assert_eq!(job_c.name, "job_c");
    assert_eq!(
        job_c.blocked_by,
        Some(vec!["job_a".to_string(), "job_b".to_string()])
    );
    assert_eq!(
        job_c.input_files,
        Some(vec!["file_a".to_string(), "file_b".to_string()])
    );
    assert_eq!(
        job_c.input_user_data,
        Some(vec!["data_a".to_string(), "data_b".to_string()])
    );
}

#[rstest]
fn test_create_workflow_from_json_file_minimal(start_server: &ServerProcess) {
    let workflow_data = serde_json::json!({
        "name": "integration_test_workflow",
        "user": "integration_user",
        "description": "Integration test workflow",
        "jobs": [
            {
                "name": "simple_job",
                "command": "echo 'Hello World'",
                "invocation_script": null,
                "cancel_on_blocking_job_failure": false,
                "supports_termination": false,
                "resource_requirements": null,
                "blocked_by": null,
                "input_files": null,
                "output_files": null,
                "input_user_data": null,
                "output_user_data": null,
                "scheduler": null
            }
        ],
        "files": null,
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let workflow_id = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        workflow_data["user"].as_str().unwrap(),
        false,
    )
    .expect("Failed to create workflow from spec file");

    assert!(workflow_id > 0);

    // Verify workflow was created by fetching it
    let created_workflow = default_api::get_workflow(&start_server.config, workflow_id)
        .expect("Failed to get created workflow");

    assert_eq!(created_workflow.name, "integration_test_workflow");
    assert_eq!(created_workflow.user, "integration_user");
    assert_eq!(
        created_workflow.description,
        Some("Integration test workflow".to_string())
    );
}

#[rstest]
fn test_create_workflow_from_json_file_with_files(start_server: &ServerProcess) {
    let workflow_data = serde_json::json!({
        "name": "workflow_with_files",
        "user": "file_user",
        "description": "Workflow with file dependencies",
        "jobs": [
            {
                "name": "file_job",
                "command": "cat input.txt > output.txt",
                "invocation_script": null,
                "cancel_on_blocking_job_failure": false,
                "supports_termination": false,
                "resource_requirements": null,
                "blocked_by": null,
                "input_files": ["input_file"],
                "output_files": ["output_file"],
                "input_user_data": null,
                "output_user_data": null,
                "scheduler": null
            }
        ],
        "files": [
            {
                "name": "input_file",
                "path": "/data/input.txt"
            },
            {
                "name": "output_file",
                "path": "/data/output.txt"
            }
        ],
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let workflow_id = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        workflow_data["user"].as_str().unwrap(),
        false,
    )
    .expect("Failed to create workflow from spec file");

    assert!(workflow_id > 0);
}

#[rstest]
fn test_create_workflow_from_json_file_with_dependencies(start_server: &ServerProcess) {
    let workflow_data = serde_json::json!({
        "name": "workflow_with_deps",
        "user": "deps_user",
        "description": "Workflow with job dependencies",
        "jobs": [
            {
                "name": "first_job",
                "command": "echo 'First job'",
                "invocation_script": null,
                "cancel_on_blocking_job_failure": false,
                "supports_termination": false,
                "resource_requirements": null,
                "blocked_by": null,
                "input_files": null,
                "output_files": null,
                "input_user_data": null,
                "output_user_data": null,
                "scheduler": null
            },
            {
                "name": "second_job",
                "command": "echo 'Second job'",
                "invocation_script": null,
                "cancel_on_blocking_job_failure": true,
                "supports_termination": false,
                "resource_requirements": null,
                "blocked_by": ["first_job"],
                "input_files": null,
                "output_files": null,
                "input_user_data": null,
                "output_user_data": null,
                "scheduler": null
            }
        ],
        "files": null,
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let workflow_id = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        workflow_data["user"].as_str().unwrap(),
        false,
    )
    .expect("Failed to create workflow from spec file");

    assert!(workflow_id > 0);
}

#[rstest]
fn test_create_workflow_from_json_file_duplicate_file_names(start_server: &ServerProcess) {
    let workflow_data = serde_json::json!({
        "name": "duplicate_files_workflow",
        "user": "error_user",
        "description": "Workflow with duplicate file names",
        "jobs": [
            {
                "name": "test_job",
                "command": "echo test",
                "invocation_script": null,
                "cancel_on_blocking_job_failure": false,
                "supports_termination": false,
                "resource_requirements": null,
                "blocked_by": null,
                "input_files": null,
                "output_files": null,
                "input_user_data": null,
                "output_user_data": null,
                "scheduler": null
            }
        ],
        "files": [
            {
                "name": "duplicate_name",
                "path": "/data/file1.txt"
            },
            {
                "name": "duplicate_name",
                "path": "/data/file2.txt"
            }
        ],
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let result = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        workflow_data["user"].as_str().unwrap(),
        false,
    );

    assert!(result.is_err());
    assert!(
        result
            .unwrap_err()
            .to_string()
            .contains("Duplicate file name")
    );
}

#[rstest]
fn test_create_workflow_from_json_file_missing_file_reference(start_server: &ServerProcess) {
    let workflow_data = serde_json::json!({
        "name": "missing_file_workflow",
        "user": "error_user",
        "description": "Workflow with missing file reference",
        "jobs": [
            {
                "name": "test_job",
                "command": "echo test",
                "invocation_script": null,
                "cancel_on_blocking_job_failure": false,
                "supports_termination": false,
                "resource_requirements": null,
                "blocked_by": null,
                "input_files": ["nonexistent_file"],
                "output_files": null,
                "input_user_data": null,
                "output_user_data": null,
                "scheduler": null
            }
        ],
        "files": null,
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let result = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        workflow_data["user"].as_str().unwrap(),
        false,
    );

    assert!(result.is_err());
    assert!(
        result
            .unwrap_err()
            .to_string()
            .contains("not found for job")
    );
}

#[rstest]
fn test_create_workflow_from_json_file_missing_job_dependency(start_server: &ServerProcess) {
    let workflow_data = serde_json::json!({
        "name": "missing_dep_workflow",
        "user": "error_user",
        "description": "Workflow with missing job dependency",
        "jobs": [
            {
                "name": "dependent_job",
                "command": "echo test",
                "invocation_script": null,
                "cancel_on_blocking_job_failure": false,
                "supports_termination": false,
                "resource_requirements": null,
                "blocked_by": ["nonexistent_job"],
                "input_files": null,
                "output_files": null,
                "input_user_data": null,
                "output_user_data": null,
                "scheduler": null
            }
        ],
        "files": null,
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let result = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        workflow_data["user"].as_str().unwrap(),
        false,
    );

    assert!(result.is_err());
    assert!(
        result
            .unwrap_err()
            .to_string()
            .contains("not found for job")
    );
}

#[rstest]
fn test_create_workflow_from_json5_file(start_server: &ServerProcess) {
    let workflow_data = r#"{
        // JSON5 format with comments
        "name": "json5_test_workflow",
        "user": "json5_user",
        "description": "Test workflow using JSON5 format",
        "jobs": [
            {
                "name": "json5_job",
                "command": "echo 'JSON5 Hello World'",
                "invocation_script": null,
                "cancel_on_blocking_job_failure": false,
                "supports_termination": false,
                "resource_requirements": null,
                "blocked_by": null,
                "input_files": null,
                "output_files": null,
                "input_user_data": null,
                "output_user_data": null,
                "scheduler": null
            }
        ],
        "files": null,
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    }"#;

    let temp_file = NamedTempFile::with_suffix(".json5").expect("Failed to create temp file");
    fs::write(&temp_file.path(), workflow_data).expect("Failed to write temp file");

    let workflow_id = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        "json5_user",
        false,
    )
    .expect("Failed to create workflow from JSON5 file");

    assert!(workflow_id > 0);
}

#[rstest]
fn test_create_workflow_from_yaml_file(start_server: &ServerProcess) {
    let workflow_data = r#"
# YAML format with comments
name: yaml_test_workflow
user: yaml_user
description: Test workflow using YAML format
jobs:
  - name: yaml_job
    command: echo 'YAML Hello World'
    invocation_script: null
    cancel_on_blocking_job_failure: false
    supports_termination: false
    resource_requirements: null
    blocked_by: null
    input_files: null
    output_files: null
    input_user_data: null
    output_user_data: null
    scheduler: null
files: null
user_data: null
resource_requirements: null
slurm_schedulers: null
"#;

    let temp_file = NamedTempFile::with_suffix(".yaml").expect("Failed to create temp file");
    fs::write(&temp_file.path(), workflow_data).expect("Failed to write temp file");

    let workflow_id = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        "yaml_user",
        false,
    )
    .expect("Failed to create workflow from YAML file");

    assert!(workflow_id > 0);
}

#[rstest]
fn test_create_workflow_from_yaml_file_with_user(start_server: &ServerProcess) {
    let workflow_data = r#"
# YAML format with comments
name: yaml_test_workflow
user: yaml_user
description: Test workflow using YAML format
jobs:
  - name: yaml_job
    command: echo 'YAML Hello World'
    invocation_script: null
    cancel_on_blocking_job_failure: false
    supports_termination: false
    resource_requirements: null
    blocked_by: null
    input_files: null
    output_files: null
    input_user_data: null
    output_user_data: null
    scheduler: null
files: null
user_data: null
resource_requirements: null
slurm_schedulers: null
"#;

    let temp_file = NamedTempFile::with_suffix(".yaml").expect("Failed to create temp file");
    fs::write(&temp_file.path(), workflow_data).expect("Failed to write temp file");

    let workflow_id = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        "yaml_user",
        false,
    )
    .expect("Failed to create workflow from YAML file");

    assert!(workflow_id > 0);
}

#[rstest]
fn test_create_workflow_from_spec_auto_detect_json(start_server: &ServerProcess) {
    let workflow_data = serde_json::json!({
        "name": "auto_detect_json_workflow",
        "user": "auto_user",
        "description": "Test auto-detection of JSON format",
        "jobs": [
            {
                "name": "auto_job",
                "command": "echo 'Auto-detected JSON'",
                "invocation_script": null,
                "cancel_on_blocking_job_failure": false,
                "supports_termination": false,
                "resource_requirements": null,
                "blocked_by": null,
                "input_files": null,
                "output_files": null,
                "input_user_data": null,
                "output_user_data": null,
                "scheduler": null
            }
        ],
        "files": null,
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    // Create file without extension to test auto-detection
    let temp_file = NamedTempFile::with_suffix(".spec").expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let workflow_id = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        "auto_user",
        false,
    )
    .expect("Failed to create workflow from spec file with auto-detection");

    assert!(workflow_id > 0);
}

#[rstest]
fn test_from_spec_file_json5_format() {
    let json5_content = r#"{
        // JSON5 test with comments
        "name": "test_workflow",
        "user": "test_user", 
        "description": "JSON5 test",
        "jobs": [],
        "files": null,
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    }"#;

    let temp_file = NamedTempFile::with_suffix(".json5").expect("Failed to create temp file");
    fs::write(&temp_file.path(), json5_content).expect("Failed to write temp file");

    let spec =
        WorkflowSpec::from_spec_file(&temp_file.path()).expect("Failed to parse JSON5 spec file");

    assert_eq!(spec.name, "test_workflow");
    assert_eq!(spec.user, Some("test_user".to_string()));
    assert_eq!(spec.description, "JSON5 test");
}

#[rstest]
fn test_from_spec_file_yaml_format() {
    let yaml_content = r#"
# YAML test with comments
name: test_workflow
user: test_user
description: YAML test
jobs: []
files: null
user_data: null
resource_requirements: null
slurm_schedulers: null
"#;

    let temp_file = NamedTempFile::with_suffix(".yaml").expect("Failed to create temp file");
    fs::write(&temp_file.path(), yaml_content).expect("Failed to write temp file");

    let spec =
        WorkflowSpec::from_spec_file(&temp_file.path()).expect("Failed to parse YAML spec file");

    assert_eq!(spec.name, "test_workflow");
    assert_eq!(spec.user, Some("test_user".to_string()));
    assert_eq!(spec.description, "YAML test");
}

#[test]
fn test_workflow_specification_with_all_resource_types() {
    // Create a workflow that uses all possible resource types
    let files = vec![FileSpec::new(
        "script.py".to_string(),
        "/scripts/script.py".to_string(),
    )];

    let user_data = vec![UserDataSpec {
        is_ephemeral: Some(false),
        name: Some("config_data".to_string()),
        data: Some(serde_json::json!({"param": "value"})),
    }];

    let resource_requirements = vec![ResourceRequirementsSpec {
        name: "test_resources".to_string(),
        num_cpus: 4,
        num_gpus: 1,
        num_nodes: 1,
        memory: "8g".to_string(),
        runtime: "PT1H".to_string(),
    }];

    let slurm_schedulers = vec![SlurmSchedulerSpec {
        name: Some("test_scheduler".to_string()),
        account: "test_account".to_string(),
        gres: Some("gpu:1".to_string()),
        mem: Some("16G".to_string()),
        nodes: 1,
        ntasks_per_node: Some(1),
        partition: Some("test".to_string()),
        qos: Some("normal".to_string()),
        tmp: Some("20G".to_string()),
        walltime: "02:00:00".to_string(),
        extra: Some("--test-flag".to_string()),
    }];

    let mut job = JobSpec::new(
        "comprehensive_job".to_string(),
        "python script.py".to_string(),
    );
    job.invocation_script = Some("#!/bin/bash\nset -euo pipefail\n".to_string());
    job.cancel_on_blocking_job_failure = Some(true);
    job.supports_termination = Some(true);
    job.resource_requirements = Some("test_resources".to_string());
    job.input_files = Some(vec!["script.py".to_string()]);
    job.input_user_data = Some(vec!["config_data".to_string()]);
    job.scheduler = Some("test_scheduler".to_string());

    let mut workflow = WorkflowSpec::new(
        "comprehensive_workflow".to_string(),
        "comprehensive_user".to_string(),
        "Uses all resource types".to_string(),
        vec![job],
    );

    workflow.files = Some(files);
    workflow.user_data = Some(user_data);
    workflow.resource_requirements = Some(resource_requirements);
    workflow.slurm_schedulers = Some(slurm_schedulers);

    // Test serialization roundtrip
    let json = serde_json::to_string_pretty(&workflow).expect("Failed to serialize");
    let deserialized: WorkflowSpec = serde_json::from_str(&json).expect("Failed to deserialize");

    assert_eq!(workflow, deserialized);

    // Verify all resource types are present
    assert!(deserialized.files.is_some());
    assert!(deserialized.user_data.is_some());
    assert!(deserialized.resource_requirements.is_some());
    assert!(deserialized.slurm_schedulers.is_some());

    // Verify job references all resource types
    let job = &deserialized.jobs[0];
    assert!(job.invocation_script.is_some());
    assert_eq!(job.cancel_on_blocking_job_failure, Some(true));
    assert_eq!(job.supports_termination, Some(true));
    assert!(job.resource_requirements.is_some());
    assert!(job.input_files.is_some());
    assert!(job.input_user_data.is_some());
    assert!(job.scheduler.is_some());
}

#[test]
fn test_job_specification_boolean_permutations() {
    // Test all combinations of boolean fields
    let bool_combinations = vec![(false, false), (false, true), (true, false), (true, true)];

    for (cancel_on_failure, supports_termination) in bool_combinations {
        let mut job = JobSpec::new("bool_test".to_string(), "echo test".to_string());
        job.cancel_on_blocking_job_failure = Some(cancel_on_failure);
        job.supports_termination = Some(supports_termination);

        let json = serde_json::to_string(&job).expect("Failed to serialize job");
        let deserialized: JobSpec = serde_json::from_str(&json).expect("Failed to deserialize job");

        assert_eq!(
            deserialized.cancel_on_blocking_job_failure,
            Some(cancel_on_failure)
        );
        assert_eq!(
            deserialized.supports_termination,
            Some(supports_termination)
        );
    }
}

#[test]
fn test_workflow_with_large_number_of_jobs() {
    // Test workflow with many jobs to ensure batching works
    let mut jobs = Vec::new();
    for i in 0..2500 {
        // More than 2 batches of 1000
        jobs.push(JobSpec::new(
            format!("job_{}", i),
            format!("echo 'Job {}'", i),
        ));
    }

    let workflow = WorkflowSpec::new(
        "large_workflow".to_string(),
        "batch_user".to_string(),
        "Workflow with many jobs".to_string(),
        jobs,
    );

    assert_eq!(workflow.jobs.len(), 2500);

    // Test serialization
    let json = serde_json::to_string(&workflow).expect("Failed to serialize large workflow");
    let deserialized: WorkflowSpec =
        serde_json::from_str(&json).expect("Failed to deserialize large workflow");

    assert_eq!(deserialized.jobs.len(), 2500);
    assert_eq!(deserialized.jobs[0].name, "job_0");
    assert_eq!(deserialized.jobs[2499].name, "job_2499");
}

#[test]
fn test_workflow_specification_default_values() {
    // Test that Default trait works correctly
    let default_workflow = WorkflowSpec::default();

    assert_eq!(default_workflow.name, "");
    assert_eq!(default_workflow.user, None);
    assert_eq!(default_workflow.description, "");
    assert_eq!(default_workflow.jobs.len(), 0);
    assert_eq!(default_workflow.files, None);
    assert_eq!(default_workflow.user_data, None);
    assert_eq!(default_workflow.resource_requirements, None);
    assert_eq!(default_workflow.slurm_schedulers, None);
}

#[test]
fn test_job_specification_default_values() {
    // Test that Default trait works correctly for JobSpec
    let default_job = JobSpec::new("test_job".to_string(), "echo hello".to_string());

    assert_eq!(default_job.name, "test_job");
    assert_eq!(default_job.command, "echo hello");
    assert_eq!(default_job.invocation_script, None);
    assert_eq!(default_job.cancel_on_blocking_job_failure, Some(false));
    assert_eq!(default_job.supports_termination, Some(false));
    assert_eq!(default_job.resource_requirements, None);
    assert_eq!(default_job.blocked_by, None);
    assert_eq!(default_job.input_files, None);
    assert_eq!(default_job.output_files, None);
    assert_eq!(default_job.input_user_data, None);
    assert_eq!(default_job.output_user_data, None);
    assert_eq!(default_job.scheduler, None);
}

#[test]
fn test_specification_structs_serialization() {
    // Test that the new specification structs serialize/deserialize correctly
    let file_spec = FileSpec::new(
        "test_file.txt".to_string(),
        "/path/to/test_file.txt".to_string(),
    );

    let user_data_spec = UserDataSpec {
        is_ephemeral: Some(true),
        name: Some("test_data".to_string()),
        data: Some(serde_json::json!({"key": "value"})),
    };

    let resource_spec = ResourceRequirementsSpec {
        name: "test_resource".to_string(),
        num_cpus: 4,
        num_gpus: 1,
        num_nodes: 2,
        memory: "8g".to_string(),
        runtime: "PT2H".to_string(),
    };

    let scheduler_spec = SlurmSchedulerSpec {
        name: Some("test_scheduler".to_string()),
        account: "test_account".to_string(),
        gres: Some("gpu:1".to_string()),
        mem: Some("16G".to_string()),
        nodes: 2,
        ntasks_per_node: Some(4),
        partition: Some("gpu".to_string()),
        qos: Some("high".to_string()),
        tmp: Some("50G".to_string()),
        walltime: "04:00:00".to_string(),
        extra: Some("--test-flag".to_string()),
    };

    // Test serialization roundtrip
    let file_json = serde_json::to_string(&file_spec).expect("Failed to serialize FileSpec");
    let file_deserialized: FileSpec =
        serde_json::from_str(&file_json).expect("Failed to deserialize FileSpec");
    assert_eq!(file_spec, file_deserialized);

    let user_data_json =
        serde_json::to_string(&user_data_spec).expect("Failed to serialize UserDataSpec");
    let user_data_deserialized: UserDataSpec =
        serde_json::from_str(&user_data_json).expect("Failed to deserialize UserDataSpec");
    assert_eq!(user_data_spec, user_data_deserialized);

    let resource_json = serde_json::to_string(&resource_spec)
        .expect("Failed to serialize ResourceRequirementsSpec");
    let resource_deserialized: ResourceRequirementsSpec = serde_json::from_str(&resource_json)
        .expect("Failed to deserialize ResourceRequirementsSpec");
    assert_eq!(resource_spec, resource_deserialized);

    let scheduler_json =
        serde_json::to_string(&scheduler_spec).expect("Failed to serialize SlurmSchedulerSpec");
    let scheduler_deserialized: SlurmSchedulerSpec =
        serde_json::from_str(&scheduler_json).expect("Failed to deserialize SlurmSchedulerSpec");
    assert_eq!(scheduler_spec, scheduler_deserialized);
}

#[test]
fn test_workflow_specification_with_new_structs() {
    // Test that a complete workflow specification works with the new specification structs
    let files = vec![
        FileSpec::new("input.dat".to_string(), "/data/input.dat".to_string()),
        FileSpec::new("output.dat".to_string(), "/data/output.dat".to_string()),
    ];

    let user_data = vec![UserDataSpec {
        is_ephemeral: Some(false),
        name: Some("config".to_string()),
        data: Some(serde_json::json!({"batch_size": 100})),
    }];

    let resource_requirements = vec![ResourceRequirementsSpec {
        name: "medium_job".to_string(),
        num_cpus: 4,
        num_gpus: 0,
        num_nodes: 1,
        memory: "16g".to_string(),
        runtime: "PT1H30M".to_string(),
    }];

    let slurm_schedulers = vec![SlurmSchedulerSpec {
        name: Some("cpu_scheduler".to_string()),
        account: "research".to_string(),
        gres: None,
        mem: Some("32G".to_string()),
        nodes: 1,
        ntasks_per_node: Some(4),
        partition: Some("cpu".to_string()),
        qos: Some("normal".to_string()),
        tmp: Some("10G".to_string()),
        walltime: "02:00:00".to_string(),
        extra: None,
    }];

    let mut job = JobSpec::new("process_data".to_string(), "python process.py".to_string());
    job.input_files = Some(vec!["input.dat".to_string()]);
    job.output_files = Some(vec!["output.dat".to_string()]);
    job.input_user_data = Some(vec!["config".to_string()]);
    job.resource_requirements = Some("medium_job".to_string());
    job.scheduler = Some("cpu_scheduler".to_string());

    let mut workflow = WorkflowSpec::new(
        "data_processing".to_string(),
        "scientist".to_string(),
        "Process scientific data".to_string(),
        vec![job],
    );

    workflow.files = Some(files);
    workflow.user_data = Some(user_data);
    workflow.resource_requirements = Some(resource_requirements);
    workflow.slurm_schedulers = Some(slurm_schedulers);

    // Test serialization roundtrip
    let json = serde_json::to_string_pretty(&workflow).expect("Failed to serialize workflow");
    let deserialized: WorkflowSpec =
        serde_json::from_str(&json).expect("Failed to deserialize workflow");

    assert_eq!(workflow, deserialized);
    assert_eq!(deserialized.files.as_ref().unwrap().len(), 2);
    assert_eq!(deserialized.user_data.as_ref().unwrap().len(), 1);
    assert_eq!(
        deserialized.resource_requirements.as_ref().unwrap().len(),
        1
    );
    assert_eq!(deserialized.slurm_schedulers.as_ref().unwrap().len(), 1);

    // Verify that the JSON doesn't contain workflow_id or id fields
    assert!(!json.contains("workflow_id"));
    assert!(!json.contains("\"id\""));
    assert!(!json.contains("st_mtime"));
}

#[test]
fn test_json_field_name_compatibility() {
    // Test that JSON field names match exactly what's expected
    let job = JobSpec {
        name: "test".to_string(),
        command: "echo".to_string(),
        invocation_script: Some("script".to_string()),
        cancel_on_blocking_job_failure: Some(true),
        supports_termination: Some(false),
        resource_requirements: Some("req".to_string()),
        blocked_by: Some(vec!["dep".to_string()]),
        blocked_by_regexes: None,
        input_files: Some(vec!["in.txt".to_string()]),
        input_file_regexes: None,
        output_files: Some(vec!["out.txt".to_string()]),
        output_file_regexes: None,
        input_user_data: Some(vec!["in_data".to_string()]),
        input_user_data_regexes: None,
        output_user_data: Some(vec!["out_data".to_string()]),
        output_user_data_regexes: None,
        scheduler: Some("sched".to_string()),
        parameters: None,
    };

    let json = serde_json::to_value(&job).expect("Failed to serialize to JSON value");

    // Check that all expected fields are present with correct names
    assert!(json.get("name").is_some());
    assert!(json.get("command").is_some());
    assert!(json.get("invocation_script").is_some());
    assert!(json.get("cancel_on_blocking_job_failure").is_some());
    assert!(json.get("supports_termination").is_some());
    assert!(json.get("resource_requirements").is_some());
    assert!(json.get("blocked_by").is_some());
    assert!(json.get("input_files").is_some());
    assert!(json.get("output_files").is_some());
    assert!(json.get("input_user_data").is_some());
    assert!(json.get("output_user_data").is_some());
    assert!(json.get("scheduler").is_some());
}

#[rstest]
fn test_create_workflow_rollback_on_error(start_server: &ServerProcess) {
    // Test that workflow is properly cleaned up when creation fails
    let workflow_data = serde_json::json!({
        "name": "rollback_test_workflow",
        "user": "rollback_user",
        "description": "Should be rolled back",
        "jobs": [
            {
                "name": "failing_job",
                "command": "echo test",
                "invocation_script": null,
                "cancel_on_blocking_job_failure": false,
                "supports_termination": false,
                "resource_requirements": "nonexistent_resource", // This should cause failure
                "blocked_by": null,
                "input_files": null,
                "output_files": null,
                "input_user_data": null,
                "output_user_data": null,
                "scheduler": null
            }
        ],
        "files": null,
        "user_data": null,
        "resource_requirements": null, // Missing the required resource
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let result = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        "rollback_user",
        false,
    );

    // Should fail due to missing resource requirements
    assert!(result.is_err());
    assert!(
        result
            .unwrap_err()
            .to_string()
            .contains("not found for job")
    );

    // Verify no workflow with this name exists (confirming rollback)
    let workflows = default_api::list_workflows(
        &start_server.config,
        None,
        None,
        None,
        Some(100),
        Some("rollback_test_workflow"),
        Some("rollback_user"),
        None,
        None,
    )
    .expect("Failed to list workflows");

    assert_eq!(workflows.items.unwrap_or_default().len(), 0);
}

#[rstest]
fn test_create_workflow_with_regex_job_dependencies(start_server: &ServerProcess) {
    use tempfile::TempDir;

    // Create temp directory for files
    let temp_dir = TempDir::new().expect("Failed to create temp dir");
    let input_path = temp_dir.path().join("input.txt");
    fs::write(&input_path, "test input").expect("Failed to write input file");

    let workflow_data = serde_json::json!({
        "name": "regex_job_deps_workflow",
        "user": "regex_user",
        "description": "Test workflow with regex job dependencies",
        "jobs": [
            {
                "name": "preprocess",
                "command": "echo 'preprocess'",
            },
            {
                "name": "work_1",
                "command": "echo 'work 1'",
                "blocked_by": ["preprocess"],
            },
            {
                "name": "work_2",
                "command": "echo 'work 2'",
                "blocked_by": ["preprocess"],
            },
            {
                "name": "work_3",
                "command": "echo 'work 3'",
                "blocked_by": ["preprocess"],
            },
            {
                "name": "postprocess",
                "command": "echo 'postprocess'",
                "blocked_by_regexes": ["work_.*"],
            }
        ],
        "files": null,
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let workflow_id = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        "regex_user",
        false,
    )
    .expect("Failed to create workflow with regex job dependencies");

    assert!(workflow_id > 0);

    // Verify that postprocess job has dependencies on all work_* jobs
    let jobs = default_api::list_jobs(
        &start_server.config,
        workflow_id,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        Some(true), // include_relationships - needed for tests that check dependencies/files
    )
    .expect("Failed to list jobs");

    let job_items = jobs.items.unwrap();
    let postprocess_job = job_items
        .iter()
        .find(|j| j.name == "postprocess")
        .expect("Postprocess job not found");

    let deps = postprocess_job
        .blocked_by_job_ids
        .as_ref()
        .expect("No dependencies found");
    assert_eq!(
        deps.len(),
        3,
        "Expected 3 dependencies (work_1, work_2, work_3)"
    );
}

#[rstest]
fn test_create_workflow_with_regex_file_dependencies(start_server: &ServerProcess) {
    use tempfile::TempDir;

    // Create temp directory and files
    let temp_dir = TempDir::new().expect("Failed to create temp dir");
    let file1 = temp_dir.path().join("data_1.txt");
    let file2 = temp_dir.path().join("data_2.txt");
    let file3 = temp_dir.path().join("data_3.txt");
    fs::write(&file1, "data 1").expect("Failed to write file1");
    fs::write(&file2, "data 2").expect("Failed to write file2");
    fs::write(&file3, "data 3").expect("Failed to write file3");

    let workflow_data = serde_json::json!({
        "name": "regex_file_deps_workflow",
        "user": "regex_user",
        "description": "Test workflow with regex file dependencies",
        "jobs": [
            {
                "name": "aggregate",
                "command": "echo 'aggregate all data files'",
                "input_file_regexes": [r"data_\d+"],
            }
        ],
        "files": [
            {
                "name": "data_1",
                "path": file1.to_str().unwrap(),
            },
            {
                "name": "data_2",
                "path": file2.to_str().unwrap(),
            },
            {
                "name": "data_3",
                "path": file3.to_str().unwrap(),
            }
        ],
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let workflow_id = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        "regex_user",
        false,
    )
    .expect("Failed to create workflow with regex file dependencies");

    assert!(workflow_id > 0);

    // Verify that aggregate job has all 3 data files as inputs
    let jobs = default_api::list_jobs(
        &start_server.config,
        workflow_id,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        Some(true), // include_relationships - needed for tests that check dependencies/files
    )
    .expect("Failed to list jobs");

    let job_items = jobs.items.unwrap();
    let aggregate_job = job_items
        .iter()
        .find(|j| j.name == "aggregate")
        .expect("Aggregate job not found");

    let input_files = aggregate_job
        .input_file_ids
        .as_ref()
        .expect("No input files found");
    assert_eq!(
        input_files.len(),
        3,
        "Expected 3 input files (data_1.txt, data_2.txt, data_3.txt)"
    );
}

#[rstest]
fn test_create_workflow_with_regex_user_data_dependencies(start_server: &ServerProcess) {
    let workflow_data = serde_json::json!({
        "name": "regex_user_data_deps_workflow",
        "user": "regex_user",
        "description": "Test workflow with regex user data dependencies",
        "jobs": [
            {
                "name": "process_all_configs",
                "command": "echo 'process all config data'",
                "input_user_data_regexes": ["config_.*"],
            }
        ],
        "files": null,
        "user_data": [
            {
                "name": "config_dev",
                "data": {"env": "development"},
            },
            {
                "name": "config_test",
                "data": {"env": "test"},
            },
            {
                "name": "config_prod",
                "data": {"env": "production"},
            },
            {
                "name": "other_data",
                "data": {"type": "other"},
            }
        ],
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let workflow_id = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        "regex_user",
        false,
    )
    .expect("Failed to create workflow with regex user data dependencies");

    assert!(workflow_id > 0);

    // Verify that process_all_configs job has only the config_* user data (not other_data)
    let jobs = default_api::list_jobs(
        &start_server.config,
        workflow_id,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        Some(true), // include_relationships - needed for tests that check dependencies/files
    )
    .expect("Failed to list jobs");

    let job_items = jobs.items.unwrap();
    let process_job = job_items
        .iter()
        .find(|j| j.name == "process_all_configs")
        .expect("Process job not found");

    let input_user_data = process_job
        .input_user_data_ids
        .as_ref()
        .expect("No input user data found");
    assert_eq!(
        input_user_data.len(),
        3,
        "Expected 3 user data items (config_dev, config_test, config_prod, but not other_data)"
    );
}

#[rstest]
fn test_create_workflow_with_mixed_exact_and_regex_dependencies(start_server: &ServerProcess) {
    let workflow_data = serde_json::json!({
        "name": "mixed_deps_workflow",
        "user": "regex_user",
        "description": "Test workflow with both exact and regex dependencies",
        "jobs": [
            {
                "name": "init",
                "command": "echo 'init'",
            },
            {
                "name": "process_1",
                "command": "echo 'process 1'",
                "blocked_by": ["init"],
            },
            {
                "name": "process_2",
                "command": "echo 'process 2'",
                "blocked_by": ["init"],
            },
            {
                "name": "special",
                "command": "echo 'special'",
                "blocked_by": ["init"],
            },
            {
                "name": "finalize",
                "command": "echo 'finalize'",
                "blocked_by": ["special"],
                "blocked_by_regexes": ["process_.*"],
            }
        ],
        "files": null,
        "user_data": null,
        "resource_requirements": null,
        "slurm_schedulers": null
    });

    let temp_file = NamedTempFile::new().expect("Failed to create temp file");
    fs::write(
        &temp_file.path(),
        serde_json::to_string_pretty(&workflow_data).unwrap(),
    )
    .expect("Failed to write temp file");

    let workflow_id = WorkflowSpec::create_workflow_from_spec(
        &start_server.config,
        &temp_file.path(),
        "regex_user",
        false,
    )
    .expect("Failed to create workflow with mixed dependencies");

    assert!(workflow_id > 0);

    // Verify that finalize job has dependencies on special + process_1 + process_2
    let jobs = default_api::list_jobs(
        &start_server.config,
        workflow_id,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        Some(true), // include_relationships - needed for tests that check dependencies/files
    )
    .expect("Failed to list jobs");

    let job_items = jobs.items.unwrap();
    let finalize_job = job_items
        .iter()
        .find(|j| j.name == "finalize")
        .expect("Finalize job not found");

    let deps = finalize_job
        .blocked_by_job_ids
        .as_ref()
        .expect("No dependencies found");
    assert_eq!(
        deps.len(),
        3,
        "Expected 3 dependencies (special, process_1, process_2)"
    );
}

#[rstest]
fn test_create_workflows_from_all_example_files(start_server: &ServerProcess) {
    use std::path::PathBuf;

    // Define the subdirectories to check
    let examples_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("examples");
    let subdirs = vec!["yaml", "json", "kdl"];

    let mut all_spec_files = Vec::new();

    // Iterate over each subdirectory and collect workflow spec files
    for subdir in &subdirs {
        let subdir_path = examples_dir.join(subdir);

        // Skip if subdirectory doesn't exist
        if !subdir_path.exists() {
            eprintln!(
                "Warning: Subdirectory {:?} does not exist, skipping",
                subdir
            );
            continue;
        }

        let spec_files: Vec<PathBuf> = fs::read_dir(&subdir_path)
            .unwrap_or_else(|e| panic!("Failed to read {} directory: {}", subdir, e))
            .filter_map(|entry| {
                let entry = entry.ok()?;
                let path = entry.path();
                if path.is_file() {
                    let extension = path.extension()?.to_str()?;
                    if matches!(extension, "json" | "json5" | "yaml" | "kdl" | "yml") {
                        return Some(path);
                    }
                }
                None
            })
            .collect();

        eprintln!(
            "Found {} workflow spec files in examples/{}/",
            spec_files.len(),
            subdir
        );

        all_spec_files.extend(spec_files);
    }

    eprintln!(
        "\nTotal: {} workflow spec files across all subdirectories\n",
        all_spec_files.len()
    );
    assert!(
        !all_spec_files.is_empty(),
        "No workflow spec files found in examples subdirectories"
    );

    // Test each spec file
    for spec_file in all_spec_files {
        eprintln!(
            "Testing workflow spec: {:?}",
            spec_file.strip_prefix(&examples_dir).unwrap_or(&spec_file)
        );

        // Read the spec to get the user field
        let spec = WorkflowSpec::from_spec_file(&spec_file)
            .unwrap_or_else(|e| panic!("Failed to read spec from {:?}: {}", spec_file, e));

        let user = spec.user.unwrap_or_else(|| "test_user".to_string());

        // Create the workflow
        let workflow_id =
            WorkflowSpec::create_workflow_from_spec(&start_server.config, &spec_file, &user, false)
                .unwrap_or_else(|e| {
                    panic!("Failed to create workflow from {:?}: {}", spec_file, e)
                });

        assert!(workflow_id > 0, "Invalid workflow ID for {:?}", spec_file);

        // Verify the workflow was created by fetching it
        let created_workflow = default_api::get_workflow(&start_server.config, workflow_id)
            .unwrap_or_else(|e| {
                panic!("Failed to get created workflow from {:?}: {}", spec_file, e)
            });

        assert_eq!(
            created_workflow.id,
            Some(workflow_id),
            "Workflow ID mismatch for {:?}",
            spec_file
        );
        assert_eq!(
            created_workflow.user, user,
            "Workflow user mismatch for {:?}",
            spec_file
        );

        eprintln!(
            "  ✓ Successfully created and verified workflow '{}' (ID: {})",
            created_workflow.name, workflow_id
        );

        default_api::delete_workflow(&start_server.config, workflow_id, None)
            .expect("Warning: Failed to delete workflow");
    }
}
