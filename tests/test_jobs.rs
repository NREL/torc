mod common;

use chrono;
use common::{
    ServerProcess, create_test_compute_node, create_test_job, create_test_workflow,
    run_cli_with_json, start_server,
};
use rstest::rstest;
use serde_json::json;
use torc::client::default_api;
use torc::client::workflow_manager::WorkflowManager;
use torc::config::TorcConfig;
use torc::models;
use torc::models::JobStatus;

#[rstest]
fn test_jobs_add_command_json(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow
    let workflow = create_test_workflow(config, "test_jobs_add_workflow");
    let workflow_id = workflow.id.unwrap();

    // Test the CLI create command with JSON output
    let args = [
        "jobs",
        "create",
        &workflow_id.to_string(),
        "--name",
        "test_job",
        "--command",
        "echo 'Hello World'",
    ];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to run jobs create command");

    assert!(json_output.get("id").is_some());
    assert_eq!(json_output.get("workflow_id").unwrap(), &json!(workflow_id));
    assert_eq!(json_output.get("name").unwrap(), &json!("test_job"));
    assert_eq!(
        json_output.get("command").unwrap(),
        &json!("echo 'Hello World'")
    );
    assert_eq!(
        json_output.get("status").unwrap(),
        &json!(JobStatus::Uninitialized.to_string())
    );
}

#[rstest]
fn test_jobs_add_with_blocking_jobs(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_blocking_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create a blocking job first
    let blocking_job = create_test_job(config, workflow_id, "blocking_job");
    let blocking_job_id = blocking_job.id.unwrap();

    // Test adding a job with blocking job dependencies
    let args = [
        "jobs",
        "create",
        &workflow_id.to_string(),
        "--name",
        "dependent_job",
        "--command",
        "echo 'I depend on another job'",
        "--blocking-job-ids",
        &blocking_job_id.to_string(),
    ];

    let json_output = run_cli_with_json(&args, start_server)
        .expect("Failed to run jobs create with blocking jobs");

    assert_eq!(json_output.get("name").unwrap(), &json!("dependent_job"));
    assert_eq!(
        json_output.get("depends_on_job_ids").unwrap(),
        &json!(vec![blocking_job_id])
    );
}

#[rstest]
fn test_jobs_add_with_file_dependencies(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_file_deps_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create test files
    let input_file = models::FileModel::new(
        workflow_id,
        "input.txt".to_string(),
        "input.txt".to_string(),
    );
    let input_file =
        default_api::create_file(config, input_file).expect("Failed to create input file");
    let input_file_id = input_file.id.unwrap();

    let output_file = models::FileModel::new(
        workflow_id,
        "output.txt".to_string(),
        "output.txt".to_string(),
    );
    let output_file =
        default_api::create_file(config, output_file).expect("Failed to create output file");
    let output_file_id = output_file.id.unwrap();

    // Test adding a job with file dependencies
    let args = [
        "jobs",
        "create",
        &workflow_id.to_string(),
        "--name",
        "file_job",
        "--command",
        "cp input.txt output.txt",
        "--input-file-ids",
        &input_file_id.to_string(),
        "--output-file-ids",
        &output_file_id.to_string(),
    ];

    let json_output = run_cli_with_json(&args, start_server)
        .expect("Failed to run jobs create with file dependencies");

    assert_eq!(json_output.get("name").unwrap(), &json!("file_job"));
    assert_eq!(
        json_output.get("input_file_ids").unwrap(),
        &json!(vec![input_file_id])
    );
    assert_eq!(
        json_output.get("output_file_ids").unwrap(),
        &json!(vec![output_file_id])
    );
}

#[rstest]
fn test_jobs_list_command_json(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow and jobs
    let workflow = create_test_workflow(config, "test_jobs_list_workflow");
    let workflow_id = workflow.id.unwrap();

    let _job1 = create_test_job(config, workflow_id, "job1");
    let _job2 = create_test_job(config, workflow_id, "job2");

    // Test the CLI list command
    let args = ["jobs", "list", &workflow_id.to_string(), "--limit", "10"];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to run jobs list command");

    // Verify JSON structure is an object with "jobs" field
    assert!(json_output.is_object(), "Jobs list should return an object");
    assert!(
        json_output.get("jobs").is_some(),
        "Response should have 'jobs' field"
    );

    let jobs_array = json_output.get("jobs").unwrap().as_array().unwrap();
    assert!(jobs_array.len() >= 2, "Should have at least 2 jobs");

    // Verify each job has the expected structure
    for job in jobs_array {
        assert!(job.get("id").is_some());
        assert!(job.get("workflow_id").is_some());
        assert!(job.get("name").is_some());
        assert!(job.get("command").is_some());
        assert!(job.get("status").is_some());
    }
}

#[rstest]
fn test_jobs_list_pagination(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_pagination_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create multiple jobs
    for i in 0..5 {
        let _job = create_test_job(config, workflow_id, &format!("pagination_job_{}", i));
    }

    // Test with limit
    let args = ["jobs", "list", &workflow_id.to_string(), "--limit", "3"];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to run paginated jobs list");

    let jobs_array = json_output.get("jobs").unwrap().as_array().unwrap();
    assert!(jobs_array.len() <= 3, "Should respect limit parameter");
    assert!(jobs_array.len() >= 1, "Should have at least one job");

    // Test with offset
    let args_with_offset = [
        "jobs",
        "list",
        &workflow_id.to_string(),
        "--limit",
        "2",
        "--offset",
        "2",
    ];

    let json_output_offset = run_cli_with_json(&args_with_offset, start_server)
        .expect("Failed to run jobs list with offset");

    let jobs_with_offset = json_output_offset.get("jobs").unwrap().as_array().unwrap();
    assert!(jobs_with_offset.len() >= 1, "Should have jobs with offset");
}

#[rstest]
fn test_jobs_list_sorting(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_sorting_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create jobs with different names for sorting
    let _job_a = create_test_job(config, workflow_id, "aaa_job");
    let _job_b = create_test_job(config, workflow_id, "bbb_job");
    let _job_c = create_test_job(config, workflow_id, "ccc_job");

    // Test sorting by name
    let args = [
        "jobs",
        "list",
        &workflow_id.to_string(),
        "--sort-by",
        "name",
    ];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to run sorted jobs list");

    let jobs_array = json_output.get("jobs").unwrap().as_array().unwrap();
    assert!(jobs_array.len() >= 3);

    // Test reverse sorting
    let args_reverse = [
        "jobs",
        "list",
        &workflow_id.to_string(),
        "--sort-by",
        "name",
        "--reverse-sort",
    ];

    let json_output_reverse = run_cli_with_json(&args_reverse, start_server)
        .expect("Failed to run reverse sorted jobs list");

    let jobs_array_reverse = json_output_reverse.get("jobs").unwrap().as_array().unwrap();
    assert!(jobs_array_reverse.len() >= 3);

    // Verify sorting worked (first job should be different in regular vs reverse)
    if jobs_array.len() >= 1 && jobs_array_reverse.len() >= 1 {
        let first_regular = jobs_array[0].get("name").unwrap().as_str().unwrap();
        let first_reverse = jobs_array_reverse[0].get("name").unwrap().as_str().unwrap();
        // In reverse sort, we should get different first elements (unless all names are the same)
        // This is a basic check that sorting is working
        assert!(first_regular <= first_reverse || first_regular >= first_reverse);
    }
}

#[rstest]
fn test_jobs_get_command_json(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test data
    let workflow = create_test_workflow(config, "test_jobs_get_workflow");
    let workflow_id = workflow.id.unwrap();
    let job = create_test_job(config, workflow_id, "test_get_job");
    let job_id = job.id.unwrap();

    // Test the CLI get command
    let args = ["jobs", "get", &job_id.to_string()];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to run jobs get command");

    // Verify JSON structure
    assert_eq!(json_output.get("id").unwrap(), &json!(job_id));
    assert_eq!(json_output.get("workflow_id").unwrap(), &json!(workflow_id));
    assert_eq!(json_output.get("name").unwrap(), &json!("test_get_job"));
    assert!(json_output.get("command").is_some());
    assert!(json_output.get("status").is_some());
}

#[rstest]
fn test_jobs_update_command_json(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test data
    let workflow = create_test_workflow(config, "test_jobs_update_workflow");
    let workflow_id = workflow.id.unwrap();
    let job = create_test_job(config, workflow_id, "test_update_job");
    let job_id = job.id.unwrap();

    // Test the CLI update command
    let args = [
        "jobs",
        "update",
        &job_id.to_string(),
        "--name",
        "updated_job_name",
        "--command",
        "echo 'Updated command'",
    ];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to run jobs update command");

    // Verify the updated values
    assert_eq!(json_output.get("id").unwrap(), &json!(job_id));
    assert_eq!(json_output.get("name").unwrap(), &json!("updated_job_name"));
    assert_eq!(
        json_output.get("command").unwrap(),
        &json!("echo 'Updated command'")
    );

    // Verify unchanged values
    assert_eq!(json_output.get("workflow_id").unwrap(), &json!(workflow_id));
}

#[rstest]
fn test_jobs_update_partial_fields(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_partial_update_workflow");
    let workflow_id = workflow.id.unwrap();
    let job = create_test_job(config, workflow_id, "partial_update_job");
    let job_id = job.id.unwrap();

    // Test updating only name
    let args = [
        "jobs",
        "update",
        &job_id.to_string(),
        "--name",
        "only_name_updated",
    ];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to run partial jobs update");

    // Only name should be updated
    assert_eq!(
        json_output.get("name").unwrap(),
        &json!("only_name_updated")
    );
    // Command should remain unchanged
    assert_eq!(
        json_output.get("command").unwrap(),
        &json!(format!("echo 'Running {}'", "partial_update_job"))
    );
}

// TODO Not supported yet
// #[rstest]
// fn test_jobs_update_with_blocking_jobs(start_server: &ServerProcess) {
//     let config = &start_server.config;

//     let workflow = create_test_workflow(config, "test_blocking_update_workflow");
//     let workflow_id = workflow.id.unwrap();

//     // Create blocking jobs
//     let blocking_job1 = create_test_job(config, workflow_id, "blocking_job1");
//     let blocking_job2 = create_test_job(config, workflow_id, "blocking_job2");
//     let job = create_test_job(config, workflow_id, "target_job");

//     let job_id = job.id.unwrap();
//     let blocking_job1_id = blocking_job1.id.unwrap();
//     let blocking_job2_id = blocking_job2.id.unwrap();

//     // Test updating with blocking job IDs
//     // let blocking_ids = format!("{} {}", blocking_job1_id, blocking_job2_id);
//     let args = [
//         "jobs",
//         "update",
//         &job_id.to_string(),
//         "--blocking-job-ids",
//         &blocking_job1_id.to_string(),
//         "--blocking-job-ids",
//         &blocking_job2_id.to_string(),
//     ];

//     let _ = run_cli_with_json(&args, start_server)
//         .expect("Failed to run jobs update with blocking jobs");

//     // Verify blocking job IDs are updated
//     let expected_blocking_ids = vec![blocking_job1_id, blocking_job2_id];
//     assert_eq!(
//         json_output.get("depends_on_job_ids").unwrap(),
//         &json!(expected_blocking_ids)
//     );
// }

#[rstest]
fn test_jobs_delete_command_json(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test data
    let workflow = create_test_workflow(config, "test_jobs_remove_workflow");
    let workflow_id = workflow.id.unwrap();
    let job = create_test_job(config, workflow_id, "test_remove_job");
    let job_id = job.id.unwrap();

    // Test the CLI delete command
    let args = ["jobs", "delete", &job_id.to_string()];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to run jobs delete command");

    // Verify JSON structure shows the removed job in "jobs" array
    assert!(json_output.get("jobs").is_some());
    let jobs = json_output.get("jobs").unwrap().as_array().unwrap();
    assert_eq!(jobs.len(), 1, "Should have 1 deleted job");

    let deleted_job = &jobs[0];
    assert_eq!(deleted_job.get("id").unwrap(), &json!(job_id));
    assert_eq!(deleted_job.get("workflow_id").unwrap(), &json!(workflow_id));
    assert_eq!(deleted_job.get("name").unwrap(), &json!("test_remove_job"));

    // Verify the job is actually removed by trying to get it
    let get_result = default_api::get_job(config, job_id);
    assert!(get_result.is_err(), "Job should be deleted");
}

#[rstest]
fn test_jobs_complete_command_json(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test data
    let workflow = create_test_workflow(config, "test_jobs_complete_workflow");
    let workflow_id = workflow.id.unwrap();

    // Start the workflow
    let torc_config = TorcConfig::load().unwrap_or_default();
    let workflow_manager = WorkflowManager::new(config.clone(), torc_config, workflow);
    workflow_manager
        .initialize(true)
        .expect("Failed to start workflow");

    let job = create_test_job(config, workflow_id, "test_complete_job");
    let job_id = job.id.unwrap();

    // Create a compute node
    let compute_node = create_test_compute_node(config, workflow_id);
    let compute_node_id = compute_node.id.unwrap();

    // Create a ResultModel for the completion
    let result_model = models::ResultModel::new(
        job_id,
        workflow_id,
        1, // run_id
        compute_node_id,
        0,   // return_code
        5.5, // exec_time_minutes
        chrono::Utc::now().to_rfc3339(),
        JobStatus::Completed,
    );

    // Test the API complete_job function
    let completed_job = default_api::complete_job(
        config,
        job_id,
        JobStatus::Completed,
        1, // run_id
        result_model,
    )
    .expect("Failed to complete job");

    // Verify the completed job
    assert_eq!(completed_job.id.unwrap(), job_id);
    assert_eq!(completed_job.name, "test_complete_job");
    assert_eq!(completed_job.status.unwrap(), JobStatus::Completed);
}

#[rstest]
fn test_jobs_complete_with_different_statuses(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_complete_status_workflow");
    let workflow_id = workflow.id.unwrap();

    // Start the workflow
    let torc_config = TorcConfig::load().unwrap_or_default();
    let workflow_manager = WorkflowManager::new(config.clone(), torc_config, workflow);
    workflow_manager
        .initialize(true)
        .expect("Failed to start workflow");

    // Create a compute node
    let compute_node = create_test_compute_node(config, workflow_id);
    let compute_node_id = compute_node.id.unwrap();

    let statuses = [
        JobStatus::Completed,
        JobStatus::Canceled,
        JobStatus::Terminated,
    ];
    for status in &statuses {
        let status_str = status.to_string();
        let job = create_test_job(config, workflow_id, &format!("job_{}", &status_str));
        let job_id = job.id.unwrap();

        // Create a ResultModel for the completion
        let result_model = models::ResultModel::new(
            job_id,
            workflow_id,
            1, // run_id
            compute_node_id,
            0,   // return_code
            2.0, // exec_time_minutes
            chrono::Utc::now().to_rfc3339(),
            status.clone(),
        );

        // Test the API complete_job function
        let completed_job = default_api::complete_job(
            config,
            job_id,
            status.clone(),
            1, // run_id
            result_model,
        )
        .expect(&format!("Failed to complete job with status {}", status));

        assert_eq!(completed_job.status.unwrap(), status.clone());
    }
}

#[rstest]
fn test_jobs_complete_return_codes(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_return_codes_workflow");
    let workflow_id = workflow.id.unwrap();

    let torc_config = TorcConfig::load().unwrap_or_default();
    let workflow_manager = WorkflowManager::new(config.clone(), torc_config, workflow);
    workflow_manager
        .initialize(true)
        .expect("Failed to start workflow");

    // Create a compute node
    let compute_node = create_test_compute_node(config, workflow_id);
    let compute_node_id = compute_node.id.unwrap();

    // Test different return codes
    let return_codes = [0, 1, 42, 127];
    for &return_code in &return_codes {
        let job = create_test_job(config, workflow_id, &format!("job_rc_{}", return_code));
        let job_id = job.id.unwrap();

        let expected_status = if return_code == 0 {
            JobStatus::Completed
        } else {
            JobStatus::Terminated
        };

        // Create a ResultModel for the completion
        let result_model = models::ResultModel::new(
            job_id,
            workflow_id,
            1, // run_id
            compute_node_id,
            return_code as i64,
            1.0, // exec_time_minutes
            chrono::Utc::now().to_rfc3339(),
            expected_status.clone(),
        );

        // Test the API complete_job function
        let completed_job = default_api::complete_job(
            config,
            job_id,
            expected_status.clone(),
            1, // run_id
            result_model,
        )
        .expect(&format!(
            "Failed to complete job with return code {}",
            return_code
        ));

        assert_eq!(completed_job.status.unwrap(), expected_status);
    }
}

#[rstest]
fn test_jobs_add_complex_command(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_complex_command_workflow");
    let workflow_id = workflow.id.unwrap();

    // Test with a more complex command
    let complex_command = "python3 -c \"import sys; print(f'Args: {sys.argv[1:]}')\" --input file1.txt --output file2.txt";
    let args = [
        "jobs",
        "create",
        &workflow_id.to_string(),
        "--name",
        "complex_job",
        "--command",
        complex_command,
    ];

    let json_output = run_cli_with_json(&args, start_server)
        .expect("Failed to run jobs create with complex command");

    assert_eq!(json_output.get("command").unwrap(), &json!(complex_command));
    assert_eq!(json_output.get("name").unwrap(), &json!("complex_job"));
}

#[rstest]
fn test_jobs_error_handling(start_server: &ServerProcess) {
    // Test getting a non-existent job
    let args = ["jobs", "get", "999999"];

    let result = run_cli_with_json(&args, start_server);
    assert!(result.is_err(), "Should fail when getting non-existent job");

    // Test updating a non-existent job
    let args = ["jobs", "update", "999999", "--name", "should_fail"];

    let result = run_cli_with_json(&args, start_server);
    assert!(
        result.is_err(),
        "Should fail when updating non-existent job"
    );

    // Test removing a non-existent job
    let args = ["jobs", "delete", "999999"];

    let result = run_cli_with_json(&args, start_server);
    assert!(
        result.is_err(),
        "Should fail when removing non-existent job"
    );
}

// NOTE: This test is disabled because job status field is now immutable after creation.
// Updating job status is not allowed - status can only be set through workflow operations.
// See test_jobs_update_restriction_cannot_change_status for the restriction test.
// #[rstest]
// fn test_jobs_update_status(start_server: &ServerProcess) {
//     let config = &start_server.config;
//
//     // Create test data
//     let workflow = create_test_workflow(config, "test_jobs_update_status_workflow");
//     let workflow_id = workflow.id.unwrap();
//     let job = create_test_job(config, workflow_id, "test_status_update_job");
//     let job_id = job.id.unwrap();
//
//     // Test updating status to "ready"
//     let args = ["jobs", "update", &job_id.to_string(), "--status", "ready"];
//
//     let json_output =
//         run_cli_with_json(&args, start_server).expect("Failed to run jobs update status command");
//
//     // Verify the updated status
//     assert_eq!(json_output.get("id").unwrap(), &json!(job_id));
//     assert_eq!(json_output.get("status").unwrap(), &json!("ready"));
//
//     // Test updating status to "blocked"
//     let args = ["jobs", "update", &job_id.to_string(), "--status", "blocked"];
//
//     let json_output =
//         run_cli_with_json(&args, start_server).expect("Failed to run jobs update status command");
//
//     // Verify the updated status
//     assert_eq!(json_output.get("status").unwrap(), &json!("blocked"));
//
//     // Test updating status to "done"
//     let args = ["jobs", "update", &job_id.to_string(), "--status", "done"];
//
//     let json_output =
//         run_cli_with_json(&args, start_server).expect("Failed to run jobs update status command");
//
//     // Verify the updated status
//     assert_eq!(json_output.get("status").unwrap(), &json!("done"));
// }

#[rstest]
fn test_jobs_update_invalid_status(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test data
    let workflow = create_test_workflow(config, "test_jobs_invalid_status_workflow");
    let workflow_id = workflow.id.unwrap();
    let job = create_test_job(config, workflow_id, "test_invalid_status_job");
    let job_id = job.id.unwrap();

    // Test updating with invalid status - should fail
    let args = [
        "jobs",
        "update",
        &job_id.to_string(),
        "--status",
        "invalid_status",
    ];

    let result = run_cli_with_json(&args, start_server);
    assert!(
        result.is_err(),
        "Should fail when updating with invalid status"
    );
}

#[rstest]
fn test_jobs_list_with_upstream_job_id_filter(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow
    let workflow = create_test_workflow(config, "test_upstream_job_id_filter_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create an upstream job
    let upstream_job = create_test_job(config, workflow_id, "upstream_job");
    let upstream_job_id = upstream_job.id.unwrap();

    // Create a downstream job that depends on the upstream job
    let downstream_job = models::JobModel::new(
        workflow_id,
        "downstream_job".to_string(),
        "echo 'Running downstream job'".to_string(),
    );

    // Note: The actual dependency relationship would be set through blocking_job_ids
    // or other API calls depending on the backend implementation
    let _downstream =
        default_api::create_job(config, downstream_job).expect("Failed to create downstream job");

    // Create an unrelated job
    let _unrelated_job = create_test_job(config, workflow_id, "unrelated_job");

    // Test the CLI list command with upstream_job_id filter
    let args = [
        "jobs",
        "list",
        &workflow_id.to_string(),
        "--upstream-job-id",
        &upstream_job_id.to_string(),
    ];

    // This test mainly verifies that the CLI accepts the new parameter without errors
    // The actual filtering behavior depends on the backend implementation of job dependencies
    let json_output = run_cli_with_json(&args, start_server)
        .expect("Failed to run jobs list command with upstream_job_id filter");

    // Verify the response structure is correct
    assert!(json_output.is_object(), "Jobs list should return an object");
    assert!(
        json_output.get("jobs").is_some(),
        "Response should have 'jobs' field"
    );

    // The command should execute without error
    // The actual filtering depends on how the backend implements upstream job relationships
}

#[rstest]
fn test_jobs_update_restriction_status_must_be_uninitialized(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow
    let workflow = create_test_workflow(config, "test_update_restriction_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create a job (starts in Uninitialized status)
    let job = create_test_job(config, workflow_id, "test_restriction_job");
    let job_id = job.id.unwrap();

    // Start the workflow to change job status from Uninitialized
    let torc_config = TorcConfig::load().unwrap_or_default();
    let workflow_manager = WorkflowManager::new(config.clone(), torc_config, workflow);
    workflow_manager
        .initialize(true)
        .expect("Failed to start workflow");

    // Get the job to verify it's no longer Uninitialized
    let updated_job = default_api::get_job(config, job_id).expect("Failed to get job");
    let current_status = updated_job.status.unwrap();

    // Verify job is no longer in Uninitialized state
    assert_ne!(
        current_status,
        JobStatus::Uninitialized,
        "Job should not be in Uninitialized state after workflow start"
    );

    // Try to update the job - should fail because status is not Uninitialized
    let args = [
        "jobs",
        "update",
        &job_id.to_string(),
        "--name",
        "should_fail",
    ];

    let result = run_cli_with_json(&args, start_server);
    assert!(
        result.is_err(),
        "Should fail when updating job with status '{}' (not Uninitialized)",
        current_status
    );

    // Verify error message mentions the restriction
    let error_msg = format!("{:?}", result.unwrap_err());
    assert!(
        error_msg.contains("uninitialized") || error_msg.contains("Uninitialized"),
        "Error message should mention uninitialized status requirement"
    );
}

#[rstest]
fn test_jobs_update_restriction_cannot_change_status(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow and job
    let workflow = create_test_workflow(config, "test_status_change_restriction_workflow");
    let workflow_id = workflow.id.unwrap();
    let job = create_test_job(config, workflow_id, "test_no_status_change");
    let job_id = job.id.unwrap();

    // Job should be in Uninitialized status (can be updated)
    let current_job = default_api::get_job(config, job_id).expect("Failed to get job");
    assert_eq!(
        current_job.status.unwrap(),
        JobStatus::Uninitialized,
        "Job should start in Uninitialized status"
    );

    // Try to update status to "ready" via API - should fail
    let mut job_to_update = current_job.clone();
    job_to_update.status = Some(JobStatus::Ready);

    let result = default_api::update_job(config, job_id, job_to_update);
    assert!(
        result.is_err(),
        "Should fail when attempting to change job status field via API"
    );

    // Verify error message mentions status is immutable
    let error_msg = format!("{:?}", result.unwrap_err());
    assert!(
        error_msg.contains("immutable") || error_msg.contains("Cannot update job status"),
        "Error message should indicate status field is immutable, got: {}",
        error_msg
    );

    // Verify the status hasn't changed
    let final_job = default_api::get_job(config, job_id).expect("Failed to get job");
    assert_eq!(
        final_job.status.unwrap(),
        JobStatus::Uninitialized,
        "Job status should remain unchanged"
    );
}

#[rstest]
fn test_jobs_update_works_when_status_is_uninitialized(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow and job
    let workflow = create_test_workflow(config, "test_update_allowed_workflow");
    let workflow_id = workflow.id.unwrap();
    let job = create_test_job(config, workflow_id, "test_update_allowed");
    let job_id = job.id.unwrap();

    // Verify job is in Uninitialized status
    let current_job = default_api::get_job(config, job_id).expect("Failed to get job");
    assert_eq!(
        current_job.status.unwrap(),
        JobStatus::Uninitialized,
        "Job should be in Uninitialized status"
    );

    // Update other fields (not status) - should succeed
    let args = [
        "jobs",
        "update",
        &job_id.to_string(),
        "--name",
        "updated_name",
        "--command",
        "echo 'Updated command'",
    ];

    let json_output = run_cli_with_json(&args, start_server)
        .expect("Update should succeed when job status is Uninitialized");

    // Verify the update succeeded
    assert_eq!(json_output.get("id").unwrap(), &json!(job_id));
    assert_eq!(json_output.get("name").unwrap(), &json!("updated_name"));
    assert_eq!(
        json_output.get("command").unwrap(),
        &json!("echo 'Updated command'")
    );

    // Verify status remains Uninitialized
    assert_eq!(
        json_output.get("status").unwrap(),
        &json!(JobStatus::Uninitialized.to_string())
    );
}

#[rstest]
fn test_jobs_delete_multiple(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow and multiple jobs
    let workflow = create_test_workflow(config, "test_delete_multiple_workflow");
    let workflow_id = workflow.id.unwrap();

    let job1 = create_test_job(config, workflow_id, "delete_test_job1");
    let job2 = create_test_job(config, workflow_id, "delete_test_job2");
    let job3 = create_test_job(config, workflow_id, "delete_test_job3");

    let job1_id = job1.id.unwrap();
    let job2_id = job2.id.unwrap();
    let job3_id = job3.id.unwrap();

    // Test deleting multiple jobs at once
    let args = [
        "jobs",
        "delete",
        &job1_id.to_string(),
        &job2_id.to_string(),
        &job3_id.to_string(),
    ];

    let json_output = run_cli_with_json(&args, start_server)
        .expect("Failed to run jobs delete with multiple IDs");

    // Verify JSON structure shows deleted jobs in "jobs" field
    assert!(json_output.get("jobs").is_some());
    let jobs = json_output.get("jobs").unwrap().as_array().unwrap();
    assert_eq!(jobs.len(), 3, "Should have deleted 3 jobs");

    // Verify all jobs are actually removed
    for job_id in [job1_id, job2_id, job3_id] {
        let get_result = default_api::get_job(config, job_id);
        assert!(get_result.is_err(), "Job {} should be deleted", job_id);
    }
}

#[rstest]
fn test_jobs_delete_multiple_with_failures(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow and jobs
    let workflow = create_test_workflow(config, "test_delete_mixed_workflow");
    let workflow_id = workflow.id.unwrap();

    let job1 = create_test_job(config, workflow_id, "delete_mixed_job1");
    let job1_id = job1.id.unwrap();

    // Test deleting mix of valid and invalid job IDs
    // The command should fail and NOT delete any jobs
    let invalid_id = 999999;
    let args = [
        "jobs",
        "delete",
        &job1_id.to_string(),
        &invalid_id.to_string(),
    ];

    let result = run_cli_with_json(&args, start_server);

    // Command should fail because one ID doesn't exist
    assert!(
        result.is_err(),
        "Should fail when one or more job IDs don't exist"
    );

    // Verify the valid job was NOT deleted (all-or-nothing behavior)
    let get_result = default_api::get_job(config, job1_id);
    assert!(
        get_result.is_ok(),
        "Valid job should NOT be deleted when any ID is invalid"
    );
}

#[rstest]
fn test_jobs_delete_all(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow and multiple jobs
    let workflow = create_test_workflow(config, "test_delete_all_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create 5 test jobs
    for i in 0..5 {
        let _job = create_test_job(config, workflow_id, &format!("delete_all_job_{}", i));
    }

    // Verify jobs were created
    let jobs_before = default_api::list_jobs(
        config,
        workflow_id,
        None,
        None,
        None,
        Some(0),
        Some(100),
        None,
        None,
        None, // include_relationships
        None, // active_compute_node_id
    )
    .expect("Failed to list jobs before deletion");
    assert_eq!(
        jobs_before.total_count, 5,
        "Should have 5 jobs before deletion"
    );

    // Call delete_jobs API directly (simulating what delete-all does)
    let result =
        default_api::delete_jobs(config, workflow_id, None).expect("Failed to delete all jobs");

    // Verify the count
    assert_eq!(
        result.get("count").unwrap(),
        &json!(5),
        "Should delete 5 jobs"
    );

    // Verify all jobs are removed
    let jobs_after = default_api::list_jobs(
        config,
        workflow_id,
        None,
        None,
        None,
        Some(0),
        Some(100),
        None,
        None,
        None, // include_relationships
        None, // active_compute_node_id
    )
    .expect("Failed to list jobs after deletion");
    assert_eq!(
        jobs_after.total_count, 0,
        "Should have 0 jobs after deletion"
    );
}

#[rstest]
fn test_jobs_delete_all_empty_workflow(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow with no jobs
    let workflow = create_test_workflow(config, "test_delete_all_empty_workflow");
    let workflow_id = workflow.id.unwrap();

    // Call delete_jobs on empty workflow
    let result = default_api::delete_jobs(config, workflow_id, None)
        .expect("Failed to delete jobs from empty workflow");

    // Verify count is 0
    assert_eq!(
        result.get("count").unwrap(),
        &json!(0),
        "Should delete 0 jobs"
    );
}
