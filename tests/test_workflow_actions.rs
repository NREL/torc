mod common;

use common::{ServerProcess, create_test_workflow, start_server};
use rstest::rstest;
use serde_json::json;
use torc::client::default_api;
use torc::models::JobModel;

/// Helper function to create a test job
fn create_test_job(
    config: &torc::client::Configuration,
    workflow_id: i64,
    name: &str,
) -> Result<JobModel, Box<dyn std::error::Error>> {
    let job = JobModel::new(
        workflow_id,
        name.to_string(),
        format!("echo 'Running {}'", name),
    );

    let created_job = default_api::create_job(config, job)?;
    Ok(created_job)
}

/// Helper function to create a compute node
fn create_test_compute_node(
    config: &torc::client::Configuration,
    workflow_id: i64,
) -> Result<i64, Box<dyn std::error::Error>> {
    let compute_node = torc::models::ComputeNodeModel::new(
        workflow_id,
        "test-host".to_string(),
        12345,
        chrono::Utc::now().to_rfc3339(),
        4,
        8.0,
        0,
        1,
        "local".to_string(),
        None,
    );

    let created = default_api::create_compute_node(config, compute_node)?;
    Ok(created.id.expect("Compute node should have ID"))
}

#[rstest]
fn test_create_workflow_action_run_commands(start_server: &ServerProcess) {
    let config = &start_server.config;
    let workflow = create_test_workflow(config, "action_test_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create a run_commands action
    let action_config = json!({
        "commands": ["echo 'Starting workflow'", "mkdir -p output"]
    });

    let action_body = json!({
        "workflow_id": workflow_id,
        "trigger_type": "on_workflow_start",
        "action_type": "run_commands",
        "action_config": action_config,
    });

    let result = default_api::create_workflow_action(config, workflow_id, action_body)
        .expect("Failed to create workflow action");

    assert!(result.id.is_some());
    assert_eq!(result.workflow_id, workflow_id);
    assert_eq!(result.trigger_type.as_str(), "on_workflow_start");
    assert_eq!(result.action_type.as_str(), "run_commands");
}

#[rstest]
fn test_create_workflow_action_schedule_nodes(start_server: &ServerProcess) {
    let config = &start_server.config;
    let workflow = create_test_workflow(config, "action_schedule_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create a schedule_nodes action
    let action_config = json!({
        "scheduler_type": "slurm",
        "scheduler_id": 1,
        "num_allocations": 2,
        "start_one_worker_per_node": true,
        "max_parallel_jobs": 4
    });

    let action_body = json!({
        "workflow_id": workflow_id,
        "trigger_type": "on_jobs_ready",
        "action_type": "schedule_nodes",
        "action_config": action_config,
    });

    let result = default_api::create_workflow_action(config, workflow_id, action_body)
        .expect("Failed to create schedule_nodes action");

    assert!(result.id.is_some());
    assert_eq!(result.action_type.as_str(), "schedule_nodes");
}

#[rstest]
fn test_get_workflow_actions(start_server: &ServerProcess) {
    let config = &start_server.config;
    let workflow = create_test_workflow(config, "action_get_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create multiple actions
    for i in 0..3 {
        let action_config = json!({
            "commands": [format!("echo 'Command {}'", i)]
        });

        let action_body = json!({
            "workflow_id": workflow_id,
            "trigger_type": "on_workflow_start",
            "action_type": "run_commands",
            "action_config": action_config,
            "jobs": null,
            "job_name_regexes": null,
            "job_ids": null,
        });

        default_api::create_workflow_action(config, workflow_id, action_body)
            .expect("Failed to create action");
    }

    // Get all actions
    let actions = default_api::get_workflow_actions(config, workflow_id)
        .expect("Failed to get workflow actions");

    assert_eq!(actions.len(), 3);
    for action in &actions {
        assert_eq!(action.workflow_id, workflow_id);
        assert_eq!(action.trigger_type.as_str(), "on_workflow_start");
    }
}

#[rstest]
fn test_get_pending_actions(start_server: &ServerProcess) {
    let config = &start_server.config;
    let workflow = create_test_workflow(config, "action_pending_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create an action
    let action_config = json!({
        "commands": ["echo 'Pending action'"]
    });

    let action_body = json!({
        "workflow_id": workflow_id,
        "trigger_type": "on_workflow_start",
        "action_type": "run_commands",
        "action_config": action_config,
    });

    default_api::create_workflow_action(config, workflow_id, action_body)
        .expect("Failed to create action");

    // Initialize the workflow to trigger on_workflow_start actions
    default_api::initialize_jobs(config, workflow_id, None, None, None)
        .expect("Failed to initialize workflow");

    // Get pending actions (should include the newly created action)
    let pending_actions = default_api::get_pending_actions(config, workflow_id, None)
        .expect("Failed to get pending actions");

    assert_eq!(pending_actions.len(), 1);
    assert_eq!(pending_actions[0].executed, false);
}

#[rstest]
fn test_claim_action_success(start_server: &ServerProcess) {
    let config = &start_server.config;
    let workflow = create_test_workflow(config, "action_claim_workflow");
    let workflow_id = workflow.id.unwrap();
    let compute_node_id =
        create_test_compute_node(config, workflow_id).expect("Failed to create compute node");

    // Create an action
    let action_config = json!({
        "commands": ["echo 'Claimable action'"]
    });

    let action_body = json!({
        "workflow_id": workflow_id,
        "trigger_type": "on_workflow_start",
        "action_type": "run_commands",
        "action_config": action_config,
    });

    let created_action = default_api::create_workflow_action(config, workflow_id, action_body)
        .expect("Failed to create action");
    let action_id = created_action.id.unwrap();

    // Initialize the workflow to trigger on_workflow_start actions
    default_api::initialize_jobs(config, workflow_id, None, None, None)
        .expect("Failed to initialize workflow");

    // Claim the action
    let claim_body = json!({
        "compute_node_id": compute_node_id
    });

    let claim_result = default_api::claim_action(config, workflow_id, action_id, claim_body)
        .expect("Failed to claim action");

    assert_eq!(
        claim_result.get("claimed").unwrap().as_bool().unwrap(),
        true
    );
    assert_eq!(
        claim_result.get("action_id").unwrap().as_i64().unwrap(),
        action_id
    );

    // Verify the action is no longer pending
    let pending_actions = default_api::get_pending_actions(config, workflow_id, None)
        .expect("Failed to get pending actions");
    assert_eq!(pending_actions.len(), 0);
}

#[rstest]
fn test_claim_action_already_claimed(start_server: &ServerProcess) {
    let config = &start_server.config;
    let workflow = create_test_workflow(config, "action_double_claim_workflow");
    let workflow_id = workflow.id.unwrap();
    let compute_node_id1 =
        create_test_compute_node(config, workflow_id).expect("Failed to create compute node 1");
    let compute_node_id2 =
        create_test_compute_node(config, workflow_id).expect("Failed to create compute node 2");

    // Create an action
    let action_config = json!({
        "commands": ["echo 'Double claim test'"]
    });

    let action_body = json!({
        "workflow_id": workflow_id,
        "trigger_type": "on_workflow_start",
        "action_type": "run_commands",
        "action_config": action_config,
    });

    let created_action = default_api::create_workflow_action(config, workflow_id, action_body)
        .expect("Failed to create action");
    let action_id = created_action.id.unwrap();

    // Initialize the workflow to trigger on_workflow_start actions
    default_api::initialize_jobs(config, workflow_id, None, None, None)
        .expect("Failed to initialize workflow");

    // First claim should succeed
    let claim_body1 = json!({
        "compute_node_id": compute_node_id1
    });

    let claim_result1 = default_api::claim_action(config, workflow_id, action_id, claim_body1)
        .expect("Failed to claim action first time");
    assert_eq!(
        claim_result1.get("claimed").unwrap().as_bool().unwrap(),
        true
    );

    // Second claim should return CONFLICT
    let claim_body2 = json!({
        "compute_node_id": compute_node_id2
    });

    let claim_result2 = default_api::claim_action(config, workflow_id, action_id, claim_body2);

    match claim_result2 {
        Err(torc::client::apis::Error::ResponseError(ref response_content)) => {
            assert_eq!(response_content.status, reqwest::StatusCode::CONFLICT);
        }
        _ => panic!("Expected CONFLICT error for already claimed action"),
    }
}

#[rstest]
fn test_action_with_job_names(start_server: &ServerProcess) {
    let config = &start_server.config;
    let workflow = create_test_workflow(config, "action_patterns_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create test jobs
    let job1 =
        create_test_job(config, workflow_id, "train_model_1").expect("Failed to create job 1");
    let job2 =
        create_test_job(config, workflow_id, "train_model_2").expect("Failed to create job 2");
    let _job3 =
        create_test_job(config, workflow_id, "evaluate_model").expect("Failed to create job 3");

    // Create action with job_ids
    let action_config = json!({
        "scheduler_type": "slurm",
        "scheduler_id": 1,
        "num_allocations": 1
    });

    let job_ids_array = vec![job1.id.unwrap(), job2.id.unwrap()];
    let action_body = json!({
        "workflow_id": workflow_id,
        "trigger_type": "on_jobs_ready",
        "action_type": "schedule_nodes",
        "action_config": action_config,
        "job_ids": job_ids_array,
    });

    let created_action = default_api::create_workflow_action(config, workflow_id, action_body)
        .expect("Failed to create action");

    // Verify job_ids were set correctly
    assert!(created_action.job_ids.is_some());
    let stored_ids = created_action.job_ids.unwrap();
    assert!(stored_ids.contains(&job1.id.unwrap()));
    assert!(stored_ids.contains(&job2.id.unwrap()));
}

#[rstest]
fn test_action_with_job_name_regexes(start_server: &ServerProcess) {
    let config = &start_server.config;
    let workflow = create_test_workflow(config, "action_regex_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create test jobs
    let job1 =
        create_test_job(config, workflow_id, "train_model_001").expect("Failed to create job 1");
    let job2 =
        create_test_job(config, workflow_id, "train_model_002").expect("Failed to create job 2");
    let _job3 =
        create_test_job(config, workflow_id, "evaluate_model").expect("Failed to create job 3");

    // Create action with job_ids
    let action_config = json!({
        "scheduler_type": "slurm",
        "scheduler_id": 1,
        "num_allocations": 1
    });

    let job_ids_array = vec![job1.id.unwrap(), job2.id.unwrap()];
    let action_body = json!({
        "workflow_id": workflow_id,
        "trigger_type": "on_jobs_ready",
        "action_type": "schedule_nodes",
        "action_config": action_config,
        "job_ids": job_ids_array,
    });

    let created_action = default_api::create_workflow_action(config, workflow_id, action_body)
        .expect("Failed to create action");

    // Verify job_ids were set correctly
    assert!(created_action.job_ids.is_some());
    let stored_ids = created_action.job_ids.unwrap();
    assert!(stored_ids.contains(&job1.id.unwrap()));
    assert!(stored_ids.contains(&job2.id.unwrap()));
}

#[rstest]
fn test_action_with_combined_patterns_and_regexes(start_server: &ServerProcess) {
    let config = &start_server.config;
    let workflow = create_test_workflow(config, "action_combined_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create test jobs
    let job1 = create_test_job(config, workflow_id, "preprocess").expect("Failed to create job 1");
    let job2 =
        create_test_job(config, workflow_id, "train_model_001").expect("Failed to create job 2");
    let job3 =
        create_test_job(config, workflow_id, "train_model_002").expect("Failed to create job 3");
    let _job4 = create_test_job(config, workflow_id, "evaluate").expect("Failed to create job 4");

    // Create action with job_ids
    let action_config = json!({
        "commands": ["echo 'All training ready'"]
    });

    let action_body = json!({
        "workflow_id": workflow_id,
        "trigger_type": "on_jobs_ready",
        "action_type": "run_commands",
        "action_config": action_config,
        "job_ids": [job1.id.unwrap(), job2.id.unwrap(), job3.id.unwrap()],
    });

    let created_action = default_api::create_workflow_action(config, workflow_id, action_body)
        .expect("Failed to create action");

    // Verify job_ids were set correctly
    assert!(created_action.job_ids.is_some());
    let stored_ids = created_action.job_ids.unwrap();
    assert!(stored_ids.contains(&job1.id.unwrap()));
    assert!(stored_ids.contains(&job2.id.unwrap()));
    assert!(stored_ids.contains(&job3.id.unwrap()));
}

#[rstest]
fn test_multiple_actions_different_triggers(start_server: &ServerProcess) {
    let config = &start_server.config;
    let workflow = create_test_workflow(config, "action_multi_trigger_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create actions with different trigger types
    let triggers = vec![
        "on_workflow_start",
        "on_workflow_complete",
        "on_jobs_ready",
        "on_jobs_complete",
    ];

    for trigger in &triggers {
        let action_config = json!({
            "commands": [format!("echo 'Trigger: {}'", trigger)]
        });

        let action_body = json!({
            "workflow_id": workflow_id,
            "trigger_type": trigger,
            "action_type": "run_commands",
            "action_config": action_config,
            "jobs": null,
            "job_name_regexes": null,
            "job_ids": null,
        });

        default_api::create_workflow_action(config, workflow_id, action_body)
            .expect(&format!("Failed to create action for trigger: {}", trigger));
    }

    // Verify all actions were created
    let actions = default_api::get_workflow_actions(config, workflow_id)
        .expect("Failed to get workflow actions");

    assert_eq!(actions.len(), 4);

    // Verify each trigger type is present
    let trigger_types: Vec<String> = actions.iter().map(|a| a.trigger_type.clone()).collect();

    for trigger in &triggers {
        assert!(trigger_types.contains(&trigger.to_string()));
    }
}

#[rstest]
fn test_action_status_lifecycle(start_server: &ServerProcess) {
    let config = &start_server.config;
    let workflow = create_test_workflow(config, "action_lifecycle_workflow");
    let workflow_id = workflow.id.unwrap();
    let compute_node_id =
        create_test_compute_node(config, workflow_id).expect("Failed to create compute node");

    // Create an action
    let action_config = json!({
        "commands": ["echo 'Status lifecycle test'"]
    });

    let action_body = json!({
        "workflow_id": workflow_id,
        "trigger_type": "on_workflow_start",
        "action_type": "run_commands",
        "action_config": action_config,
    });

    let created_action = default_api::create_workflow_action(config, workflow_id, action_body)
        .expect("Failed to create action");
    let action_id = created_action.id.unwrap();

    // Initial status should be "not executed"
    assert_eq!(created_action.executed, false);
    assert!(created_action.executed_by.is_none());

    // Initialize the workflow to trigger on_workflow_start actions
    default_api::initialize_jobs(config, workflow_id, None, None, None)
        .expect("Failed to initialize workflow");

    // Claim the action
    let claim_body = json!({
        "compute_node_id": compute_node_id
    });

    default_api::claim_action(config, workflow_id, action_id, claim_body)
        .expect("Failed to claim action");

    // Get all actions and verify status changed
    let actions = default_api::get_workflow_actions(config, workflow_id)
        .expect("Failed to get workflow actions");

    let claimed_action = actions
        .iter()
        .find(|a| a.id.unwrap() == action_id)
        .expect("Action not found");

    assert_eq!(claimed_action.executed, true);
    assert_eq!(claimed_action.executed_by.unwrap(), compute_node_id);

    // Verify it's no longer in pending actions
    let pending_actions = default_api::get_pending_actions(config, workflow_id, None)
        .expect("Failed to get pending actions");
    assert_eq!(pending_actions.len(), 0);
}
