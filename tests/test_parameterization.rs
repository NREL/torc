use std::collections::HashMap;
use torc::client::workflow_spec::{FileSpec, JobSpec, WorkflowSpec};

#[test]
fn test_integer_range_expansion() {
    let mut job = JobSpec::new("job_{i}".to_string(), "echo {i}".to_string());

    let mut params = HashMap::new();
    params.insert("i".to_string(), "1:5".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded.len(), 5);
    assert_eq!(expanded[0].name, "job_1");
    assert_eq!(expanded[0].command, "echo 1");
    assert_eq!(expanded[4].name, "job_5");
    assert_eq!(expanded[4].command, "echo 5");
}

#[test]
fn test_integer_range_with_step() {
    let mut job = JobSpec::new("job_{i}".to_string(), "echo {i}".to_string());

    let mut params = HashMap::new();
    params.insert("i".to_string(), "0:10:2".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded.len(), 6);
    assert_eq!(expanded[0].name, "job_0");
    assert_eq!(expanded[1].name, "job_2");
    assert_eq!(expanded[5].name, "job_10");
}

#[test]
fn test_float_range_expansion() {
    let mut job = JobSpec::new("job_{lr}".to_string(), "train.py --lr={lr}".to_string());

    let mut params = HashMap::new();
    params.insert("lr".to_string(), "0.0:1.0:0.5".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded.len(), 3);
    assert_eq!(expanded[0].command, "train.py --lr=0");
    assert_eq!(expanded[1].command, "train.py --lr=0.5");
    assert_eq!(expanded[2].command, "train.py --lr=1");
}

#[test]
fn test_list_expansion() {
    let mut job = JobSpec::new(
        "job_{dataset}".to_string(),
        "process.sh {dataset}".to_string(),
    );

    let mut params = HashMap::new();
    params.insert(
        "dataset".to_string(),
        "['train','test','validation']".to_string(),
    );
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded.len(), 3);
    assert_eq!(expanded[0].name, "job_train");
    assert_eq!(expanded[0].command, "process.sh train");
    assert_eq!(expanded[2].name, "job_validation");
}

#[test]
fn test_multi_dimensional_parameter_sweep() {
    let mut job = JobSpec::new(
        "job_lr{lr}_bs{batch_size}".to_string(),
        "train.py --lr={lr} --batch-size={batch_size}".to_string(),
    );

    let mut params = HashMap::new();
    params.insert("lr".to_string(), "[0.001,0.01,0.1]".to_string());
    params.insert("batch_size".to_string(), "[16,32,64]".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    // Should generate 3 * 3 = 9 combinations
    assert_eq!(expanded.len(), 9);

    // Check a few combinations
    let names: Vec<&str> = expanded.iter().map(|j| j.name.as_str()).collect();
    assert!(names.contains(&"job_lr0.001_bs16"));
    assert!(names.contains(&"job_lr0.1_bs64"));

    let commands: Vec<&str> = expanded.iter().map(|j| j.command.as_str()).collect();
    assert!(commands.contains(&"train.py --lr=0.001 --batch-size=16"));
    assert!(commands.contains(&"train.py --lr=0.1 --batch-size=64"));
}

#[test]
fn test_format_specifier_zero_padding() {
    let mut job = JobSpec::new("job_{i:03d}".to_string(), "echo {i:03d}".to_string());

    let mut params = HashMap::new();
    params.insert("i".to_string(), "1:5".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded[0].name, "job_001");
    assert_eq!(expanded[0].command, "echo 001");
    assert_eq!(expanded[4].name, "job_005");
}

#[test]
fn test_format_specifier_float_precision() {
    let mut job = JobSpec::new(
        "job_{lr:.2f}".to_string(),
        "train.py --lr={lr:.2f}".to_string(),
    );

    let mut params = HashMap::new();
    params.insert("lr".to_string(), "0.0:0.3:0.1".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded[0].name, "job_0.00");
    assert_eq!(expanded[1].name, "job_0.10");
    assert_eq!(expanded[2].name, "job_0.20");
}

#[test]
fn test_file_parameterization() {
    let mut file = FileSpec::new(
        "output_{run_id}".to_string(),
        "/data/output_{run_id}.txt".to_string(),
    );

    let mut params = HashMap::new();
    params.insert("run_id".to_string(), "1:3".to_string());
    file.parameters = Some(params);

    let expanded = file.expand().expect("Failed to expand file");

    assert_eq!(expanded.len(), 3);
    assert_eq!(expanded[0].name, "output_1");
    assert_eq!(expanded[0].path, "/data/output_1.txt");
    assert_eq!(expanded[2].name, "output_3");
    assert_eq!(expanded[2].path, "/data/output_3.txt");
}

#[test]
fn test_job_with_input_output_files() {
    let mut job = JobSpec::new(
        "process_{i}".to_string(),
        "process.sh input_{i}.txt output_{i}.txt".to_string(),
    );
    job.input_file_names = Some(vec!["input_{i}".to_string()]);
    job.output_file_names = Some(vec!["output_{i}".to_string()]);

    let mut params = HashMap::new();
    params.insert("i".to_string(), "1:3".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded.len(), 3);

    assert_eq!(expanded[0].name, "process_1");
    assert_eq!(
        expanded[0].input_file_names,
        Some(vec!["input_1".to_string()])
    );
    assert_eq!(
        expanded[0].output_file_names,
        Some(vec!["output_1".to_string()])
    );

    assert_eq!(expanded[2].name, "process_3");
    assert_eq!(
        expanded[2].input_file_names,
        Some(vec!["input_3".to_string()])
    );
    assert_eq!(
        expanded[2].output_file_names,
        Some(vec!["output_3".to_string()])
    );
}

#[test]
fn test_job_with_blocked_by_names() {
    let mut job = JobSpec::new(
        "dependent_{i}".to_string(),
        "echo dependent {i}".to_string(),
    );
    job.blocked_by_job_names = Some(vec!["upstream_{i}".to_string()]);

    let mut params = HashMap::new();
    params.insert("i".to_string(), "1:3".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded.len(), 3);
    assert_eq!(expanded[0].name, "dependent_1");
    assert_eq!(
        expanded[0].blocked_by_job_names,
        Some(vec!["upstream_1".to_string()])
    );
    assert_eq!(expanded[2].name, "dependent_3");
    assert_eq!(
        expanded[2].blocked_by_job_names,
        Some(vec!["upstream_3".to_string()])
    );
}

#[test]
fn test_no_parameters_returns_original() {
    let job = JobSpec::new("simple_job".to_string(), "echo hello".to_string());

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded.len(), 1);
    assert_eq!(expanded[0].name, "simple_job");
    assert_eq!(expanded[0].command, "echo hello");
}

#[test]
fn test_invalid_range_format() {
    let mut job = JobSpec::new("job_{i}".to_string(), "echo {i}".to_string());

    let mut params = HashMap::new();
    params.insert("i".to_string(), "invalid:range:format:too:many".to_string());
    job.parameters = Some(params);

    let result = job.expand();
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("Invalid range format"));
}

#[test]
fn test_zero_step_error() {
    let mut job = JobSpec::new("job_{i}".to_string(), "echo {i}".to_string());

    let mut params = HashMap::new();
    params.insert("i".to_string(), "1:10:0".to_string());
    job.parameters = Some(params);

    let result = job.expand();
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("Step cannot be zero"));
}

#[test]
fn test_workflow_spec_expand_parameters() {
    let mut spec = WorkflowSpec {
        name: "test_workflow".to_string(),
        description: "Test workflow with parameters".to_string(),
        user: Some("test_user".to_string()),
        compute_node_expiration_buffer_seconds: None,
        compute_node_wait_for_healthy_database_minutes: None,
        compute_node_ignore_workflow_completion: None,
        compute_node_wait_for_new_jobs_seconds: None,
        jobs_sort_method: None,
        jobs: vec![JobSpec {
            name: "job_{i}".to_string(),
            command: "echo {i}".to_string(),
            invocation_script: None,
            cancel_on_blocking_job_failure: Some(false),
            supports_termination: Some(false),
            resource_requirements_name: None,
            scheduler_name: None,
            blocked_by_job_names: None,
            input_file_names: None,
            output_file_names: None,
            input_user_data_names: None,
            output_data_names: None,
            parameters: Some({
                let mut params = HashMap::new();
                params.insert("i".to_string(), "1:3".to_string());
                params
            }),
        }],
        files: Some(vec![{
            let mut file = FileSpec::new("file_{i}".to_string(), "/data/file_{i}.txt".to_string());
            file.parameters = Some({
                let mut params = HashMap::new();
                params.insert("i".to_string(), "1:3".to_string());
                params
            });
            file
        }]),
        user_data: None,
        resource_requirements: None,
        slurm_schedulers: None,
        resource_monitor: None,
        actions: None,
    };

    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // Jobs should be expanded
    assert_eq!(spec.jobs.len(), 3);
    assert_eq!(spec.jobs[0].name, "job_1");
    assert_eq!(spec.jobs[2].name, "job_3");

    // Files should be expanded
    assert_eq!(spec.files.as_ref().unwrap().len(), 3);
    assert_eq!(spec.files.as_ref().unwrap()[0].name, "file_1");
    assert_eq!(spec.files.as_ref().unwrap()[2].name, "file_3");
}

#[test]
fn test_complex_multi_param_with_dependencies() {
    let mut job = JobSpec::new(
        "train_lr{lr}_bs{bs}_epoch{epoch}".to_string(),
        "train.py --lr={lr} --bs={bs} --epochs={epoch}".to_string(),
    );
    job.input_file_names = Some(vec!["data_{bs}".to_string()]);
    job.output_file_names = Some(vec!["model_lr{lr}_bs{bs}_epoch{epoch}.pt".to_string()]);

    let mut params = HashMap::new();
    params.insert("lr".to_string(), "[0.001,0.01]".to_string());
    params.insert("bs".to_string(), "[16,32]".to_string());
    params.insert("epoch".to_string(), "[10,20]".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    // Should generate 2 * 2 * 2 = 8 combinations
    assert_eq!(expanded.len(), 8);

    // Check one specific combination
    let job_001_16_10 = expanded
        .iter()
        .find(|j| j.name == "train_lr0.001_bs16_epoch10")
        .expect("Expected job not found");

    assert_eq!(
        job_001_16_10.command,
        "train.py --lr=0.001 --bs=16 --epochs=10"
    );
    assert_eq!(
        job_001_16_10.input_file_names,
        Some(vec!["data_16".to_string()])
    );
    assert_eq!(
        job_001_16_10.output_file_names,
        Some(vec!["model_lr0.001_bs16_epoch10.pt".to_string()])
    );
}

#[test]
fn test_invocation_script_substitution() {
    let mut job = JobSpec::new("job_{i}".to_string(), "python train.py".to_string());
    job.invocation_script = Some("#!/bin/bash\nexport RUN_ID={i}\n".to_string());

    let mut params = HashMap::new();
    params.insert("i".to_string(), "1:2".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(
        expanded[0].invocation_script,
        Some("#!/bin/bash\nexport RUN_ID=1\n".to_string())
    );
    assert_eq!(
        expanded[1].invocation_script,
        Some("#!/bin/bash\nexport RUN_ID=2\n".to_string())
    );
}

#[test]
fn test_user_data_name_substitution() {
    let mut job = JobSpec::new("job_{stage}".to_string(), "process.sh {stage}".to_string());
    job.input_user_data_names = Some(vec!["config_{stage}".to_string()]);
    job.output_data_names = Some(vec!["results_{stage}".to_string()]);

    let mut params = HashMap::new();
    params.insert("stage".to_string(), "['train','test']".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded.len(), 2);
    assert_eq!(
        expanded[0].input_user_data_names,
        Some(vec!["config_train".to_string()])
    );
    assert_eq!(
        expanded[0].output_data_names,
        Some(vec!["results_train".to_string()])
    );
    assert_eq!(
        expanded[1].input_user_data_names,
        Some(vec!["config_test".to_string()])
    );
    assert_eq!(
        expanded[1].output_data_names,
        Some(vec!["results_test".to_string()])
    );
}
