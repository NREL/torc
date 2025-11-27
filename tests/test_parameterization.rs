use rstest::rstest;
use std::collections::HashMap;
use std::path::PathBuf;
use torc::client::workflow_spec::{FileSpec, JobSpec, WorkflowSpec};

#[rstest]
fn test_kdl_job_parameterization() {
    let kdl_content = r#"
name "test_parameterized"
description "Test parameterized jobs in KDL format"

job "job_{i:03d}" {
    command "echo hello {i}"
    parameters {
        i "1:5"
    }
}
"#;

    let mut spec = WorkflowSpec::from_spec_file_content(kdl_content, "kdl")
        .expect("Failed to parse KDL workflow spec");

    // Before expansion, should have 1 job with parameters
    assert_eq!(spec.jobs.len(), 1);
    assert!(spec.jobs[0].parameters.is_some());

    // Expand parameters
    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // After expansion, should have 5 jobs
    assert_eq!(spec.jobs.len(), 5);
    assert_eq!(spec.jobs[0].name, "job_001");
    assert_eq!(spec.jobs[0].command, "echo hello 1");
    assert_eq!(spec.jobs[4].name, "job_005");
    assert_eq!(spec.jobs[4].command, "echo hello 5");

    // Parameters should be removed from expanded jobs
    for job in &spec.jobs {
        assert!(job.parameters.is_none());
    }
}

#[rstest]
fn test_kdl_file_parameterization() {
    let kdl_content = r#"
name "test_parameterized_files"
description "Test parameterized files in KDL format"

file "output_{run_id}" {
    path "/data/output_{run_id}.txt"
    parameters {
        run_id "1:3"
    }
}

job "process" {
    command "echo test"
}
"#;

    let mut spec = WorkflowSpec::from_spec_file_content(kdl_content, "kdl")
        .expect("Failed to parse KDL workflow spec");

    // Before expansion, should have 1 file with parameters
    assert_eq!(spec.files.as_ref().unwrap().len(), 1);
    assert!(spec.files.as_ref().unwrap()[0].parameters.is_some());

    // Expand parameters
    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // After expansion, should have 3 files
    let files = spec.files.as_ref().unwrap();
    assert_eq!(files.len(), 3);
    assert_eq!(files[0].name, "output_1");
    assert_eq!(files[0].path, "/data/output_1.txt");
    assert_eq!(files[2].name, "output_3");
    assert_eq!(files[2].path, "/data/output_3.txt");

    // Parameters should be removed from expanded files
    for file in files {
        assert!(file.parameters.is_none());
    }
}

#[rstest]
fn test_kdl_multi_dimensional_parameterization() {
    let kdl_content = r#"
name "test_multi_param"
description "Test multi-dimensional parameterization in KDL format"

job "train_lr{lr:.4f}_bs{batch_size}" {
    command "python train.py --lr={lr} --batch-size={batch_size}"
    parameters {
        lr "[0.001,0.01]"
        batch_size "[16,32]"
    }
}
"#;

    let mut spec = WorkflowSpec::from_spec_file_content(kdl_content, "kdl")
        .expect("Failed to parse KDL workflow spec");

    // Expand parameters
    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // Should have 2 * 2 = 4 jobs
    assert_eq!(spec.jobs.len(), 4);

    // Verify all expected combinations exist
    let names: Vec<&str> = spec.jobs.iter().map(|j| j.name.as_str()).collect();
    assert!(names.contains(&"train_lr0.0010_bs16"));
    assert!(names.contains(&"train_lr0.0010_bs32"));
    assert!(names.contains(&"train_lr0.0100_bs16"));
    assert!(names.contains(&"train_lr0.0100_bs32"));
}

#[rstest]
fn test_kdl_example_file_hundred_jobs() {
    // Test parsing the actual KDL example file
    let manifest_dir = env!("CARGO_MANIFEST_DIR");
    let path = PathBuf::from(manifest_dir).join("examples/kdl/hundred_jobs_parameterized.kdl");

    let mut spec = WorkflowSpec::from_spec_file(&path).expect("Failed to parse KDL example file");

    assert_eq!(spec.name, "hundred_jobs_parameterized");
    assert_eq!(spec.jobs.len(), 1);
    assert!(spec.jobs[0].parameters.is_some());

    // Expand parameters
    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // Should have 100 jobs after expansion
    assert_eq!(spec.jobs.len(), 100);
    assert_eq!(spec.jobs[0].name, "job_001");
    assert_eq!(spec.jobs[99].name, "job_100");
}

#[rstest]
fn test_kdl_example_file_hyperparameter_sweep() {
    // Test parsing the actual KDL hyperparameter sweep example
    let manifest_dir = env!("CARGO_MANIFEST_DIR");
    let path = PathBuf::from(manifest_dir).join("examples/kdl/hyperparameter_sweep.kdl");

    let mut spec =
        WorkflowSpec::from_spec_file(&path).expect("Failed to parse KDL hyperparameter sweep file");

    assert_eq!(spec.name, "hyperparameter_sweep");

    // Before expansion: 4 jobs (prepare_train, prepare_val, train template, aggregate template)
    assert_eq!(spec.jobs.len(), 4);

    // Before expansion: 4 files (train_data, val_data, model template, metrics template)
    assert_eq!(spec.files.as_ref().unwrap().len(), 4);

    // Expand parameters
    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // After expansion:
    // - 2 prepare jobs (unchanged)
    // - 18 training jobs (3 lr * 3 batch_size * 2 optimizer)
    // - 18 aggregate jobs (expanded from template)
    // Total: 2 + 18 + 18 = 38 jobs
    assert_eq!(spec.jobs.len(), 38);

    // Files after expansion:
    // - 2 data files (unchanged)
    // - 18 model files (parameterized)
    // - 18 metrics files (parameterized)
    // Total: 2 + 18 + 18 = 38 files
    assert_eq!(spec.files.as_ref().unwrap().len(), 38);
}

#[rstest]
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

#[rstest]
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

#[rstest]
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

#[rstest]
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

#[rstest]
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

#[rstest]
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

#[rstest]
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

#[rstest]
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

#[rstest]
fn test_job_with_input_output_files() {
    let mut job = JobSpec::new(
        "process_{i}".to_string(),
        "process.sh input_{i}.txt output_{i}.txt".to_string(),
    );
    job.input_files = Some(vec!["input_{i}".to_string()]);
    job.output_files = Some(vec!["output_{i}".to_string()]);

    let mut params = HashMap::new();
    params.insert("i".to_string(), "1:3".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded.len(), 3);

    assert_eq!(expanded[0].name, "process_1");
    assert_eq!(expanded[0].input_files, Some(vec!["input_1".to_string()]));
    assert_eq!(expanded[0].output_files, Some(vec!["output_1".to_string()]));

    assert_eq!(expanded[2].name, "process_3");
    assert_eq!(expanded[2].input_files, Some(vec!["input_3".to_string()]));
    assert_eq!(expanded[2].output_files, Some(vec!["output_3".to_string()]));
}

#[rstest]
fn test_job_with_blocked_by_names() {
    let mut job = JobSpec::new(
        "dependent_{i}".to_string(),
        "echo dependent {i}".to_string(),
    );
    job.blocked_by = Some(vec!["upstream_{i}".to_string()]);

    let mut params = HashMap::new();
    params.insert("i".to_string(), "1:3".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded.len(), 3);
    assert_eq!(expanded[0].name, "dependent_1");
    assert_eq!(expanded[0].blocked_by, Some(vec!["upstream_1".to_string()]));
    assert_eq!(expanded[2].name, "dependent_3");
    assert_eq!(expanded[2].blocked_by, Some(vec!["upstream_3".to_string()]));
}

#[rstest]
fn test_no_parameters_returns_original() {
    let job = JobSpec::new("simple_job".to_string(), "echo hello".to_string());

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded.len(), 1);
    assert_eq!(expanded[0].name, "simple_job");
    assert_eq!(expanded[0].command, "echo hello");
}

#[rstest]
fn test_invalid_range_format() {
    let mut job = JobSpec::new("job_{i}".to_string(), "echo {i}".to_string());

    let mut params = HashMap::new();
    params.insert("i".to_string(), "invalid:range:format:too:many".to_string());
    job.parameters = Some(params);

    let result = job.expand();
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("Invalid range format"));
}

#[rstest]
fn test_zero_step_error() {
    let mut job = JobSpec::new("job_{i}".to_string(), "echo {i}".to_string());

    let mut params = HashMap::new();
    params.insert("i".to_string(), "1:10:0".to_string());
    job.parameters = Some(params);

    let result = job.expand();
    assert!(result.is_err());
    assert!(result.unwrap_err().contains("Step cannot be zero"));
}

#[rstest]
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
        parameters: None,
        jobs: vec![JobSpec {
            name: "job_{i}".to_string(),
            command: "echo {i}".to_string(),
            invocation_script: None,
            cancel_on_blocking_job_failure: Some(false),
            supports_termination: Some(false),
            resource_requirements: None,
            scheduler: None,
            blocked_by: None,
            blocked_by_regexes: None,
            input_files: None,
            input_file_regexes: None,
            output_files: None,
            output_file_regexes: None,
            input_user_data: None,
            input_user_data_regexes: None,
            output_user_data: None,
            output_user_data_regexes: None,
            parameters: Some({
                let mut params = HashMap::new();
                params.insert("i".to_string(), "1:3".to_string());
                params
            }),
            use_parameters: None,
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

#[rstest]
fn test_complex_multi_param_with_dependencies() {
    let mut job = JobSpec::new(
        "train_lr{lr}_bs{bs}_epoch{epoch}".to_string(),
        "train.py --lr={lr} --bs={bs} --epochs={epoch}".to_string(),
    );
    job.input_files = Some(vec!["data_{bs}".to_string()]);
    job.output_files = Some(vec!["model_lr{lr}_bs{bs}_epoch{epoch}.pt".to_string()]);

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
    assert_eq!(job_001_16_10.input_files, Some(vec!["data_16".to_string()]));
    assert_eq!(
        job_001_16_10.output_files,
        Some(vec!["model_lr0.001_bs16_epoch10.pt".to_string()])
    );
}

#[rstest]
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

#[rstest]
fn test_user_data_name_substitution() {
    let mut job = JobSpec::new("job_{stage}".to_string(), "process.sh {stage}".to_string());
    job.input_user_data = Some(vec!["config_{stage}".to_string()]);
    job.output_user_data = Some(vec!["results_{stage}".to_string()]);

    let mut params = HashMap::new();
    params.insert("stage".to_string(), "['train','test']".to_string());
    job.parameters = Some(params);

    let expanded = job.expand().expect("Failed to expand job");

    assert_eq!(expanded.len(), 2);
    assert_eq!(
        expanded[0].input_user_data,
        Some(vec!["config_train".to_string()])
    );
    assert_eq!(
        expanded[0].output_user_data,
        Some(vec!["results_train".to_string()])
    );
    assert_eq!(
        expanded[1].input_user_data,
        Some(vec!["config_test".to_string()])
    );
    assert_eq!(
        expanded[1].output_user_data,
        Some(vec!["results_test".to_string()])
    );
}

// ==================== Shared Parameters Tests ====================

#[rstest]
fn test_shared_parameters_yaml() {
    let yaml_content = r#"
name: shared_params_test
description: Test workflow-level shared parameters

parameters:
  i: "1:3"
  prefix: "['a','b']"

jobs:
  - name: job_{i}_{prefix}
    command: echo {i} {prefix}
    use_parameters:
      - i
      - prefix
"#;

    let mut spec = WorkflowSpec::from_spec_file_content(yaml_content, "yaml")
        .expect("Failed to parse YAML workflow spec");

    // Verify workflow-level parameters were parsed
    assert!(spec.parameters.is_some());
    let params = spec.parameters.as_ref().unwrap();
    assert_eq!(params.get("i").unwrap(), "1:3");
    assert_eq!(params.get("prefix").unwrap(), "['a','b']");

    // Verify job has use_parameters
    assert!(spec.jobs[0].use_parameters.is_some());
    assert_eq!(spec.jobs[0].use_parameters.as_ref().unwrap().len(), 2);

    // Expand parameters
    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // Should have 3 * 2 = 6 jobs
    assert_eq!(spec.jobs.len(), 6);

    // Check that all combinations exist
    let names: Vec<&str> = spec.jobs.iter().map(|j| j.name.as_str()).collect();
    assert!(names.contains(&"job_1_a"));
    assert!(names.contains(&"job_1_b"));
    assert!(names.contains(&"job_2_a"));
    assert!(names.contains(&"job_2_b"));
    assert!(names.contains(&"job_3_a"));
    assert!(names.contains(&"job_3_b"));
}

#[rstest]
fn test_shared_parameters_kdl() {
    let kdl_content = r#"
name "shared_params_test"
description "Test workflow-level shared parameters in KDL"

parameters {
    i "1:3"
    prefix "['a','b']"
}

job "job_{i}_{prefix}" {
    command "echo {i} {prefix}"
    use_parameters "i" "prefix"
}
"#;

    let mut spec = WorkflowSpec::from_spec_file_content(kdl_content, "kdl")
        .expect("Failed to parse KDL workflow spec");

    // Verify workflow-level parameters were parsed
    assert!(spec.parameters.is_some());
    let params = spec.parameters.as_ref().unwrap();
    assert_eq!(params.get("i").unwrap(), "1:3");
    assert_eq!(params.get("prefix").unwrap(), "['a','b']");

    // Verify job has use_parameters
    assert!(spec.jobs[0].use_parameters.is_some());

    // Expand parameters
    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // Should have 3 * 2 = 6 jobs
    assert_eq!(spec.jobs.len(), 6);

    // Check that all combinations exist
    let names: Vec<&str> = spec.jobs.iter().map(|j| j.name.as_str()).collect();
    assert!(names.contains(&"job_1_a"));
    assert!(names.contains(&"job_3_b"));
}

#[rstest]
fn test_shared_parameters_json5() {
    let json5_content = r#"
{
    name: "shared_params_test",
    description: "Test workflow-level shared parameters in JSON5",

    parameters: {
        i: "1:3",
        prefix: "['a','b']"
    },

    jobs: [
        {
            name: "job_{i}_{prefix}",
            command: "echo {i} {prefix}",
            use_parameters: ["i", "prefix"]
        }
    ]
}
"#;

    let mut spec = WorkflowSpec::from_spec_file_content(json5_content, "json5")
        .expect("Failed to parse JSON5 workflow spec");

    // Verify workflow-level parameters were parsed
    assert!(spec.parameters.is_some());

    // Expand parameters
    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // Should have 3 * 2 = 6 jobs
    assert_eq!(spec.jobs.len(), 6);
}

#[rstest]
fn test_shared_parameters_selective_inheritance() {
    // Test that use_parameters only inherits specified parameters
    let yaml_content = r#"
name: selective_params_test
description: Test selective parameter inheritance

parameters:
  a: "1:2"
  b: "3:4"
  c: "5:6"

jobs:
  # This job should only use parameters a and b (4 jobs)
  - name: job_{a}_{b}
    command: echo {a} {b}
    use_parameters:
      - a
      - b
"#;

    let mut spec = WorkflowSpec::from_spec_file_content(yaml_content, "yaml")
        .expect("Failed to parse YAML workflow spec");

    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // Should have 2 * 2 = 4 jobs (not using parameter c)
    assert_eq!(spec.jobs.len(), 4);

    // Check that only a and b were used
    let names: Vec<&str> = spec.jobs.iter().map(|j| j.name.as_str()).collect();
    assert!(names.contains(&"job_1_3"));
    assert!(names.contains(&"job_1_4"));
    assert!(names.contains(&"job_2_3"));
    assert!(names.contains(&"job_2_4"));
}

#[rstest]
fn test_shared_parameters_with_files() {
    let yaml_content = r#"
name: file_params_test
description: Test shared parameters with files

parameters:
  i: "1:2"

files:
  - name: file_{i}
    path: /data/file_{i}.txt
    use_parameters:
      - i

jobs:
  - name: job_{i}
    command: process /data/file_{i}.txt
    input_files:
      - file_{i}
    use_parameters:
      - i
"#;

    let mut spec = WorkflowSpec::from_spec_file_content(yaml_content, "yaml")
        .expect("Failed to parse YAML workflow spec");

    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // Should have 2 files
    assert_eq!(spec.files.as_ref().unwrap().len(), 2);
    let file_names: Vec<&str> = spec
        .files
        .as_ref()
        .unwrap()
        .iter()
        .map(|f| f.name.as_str())
        .collect();
    assert!(file_names.contains(&"file_1"));
    assert!(file_names.contains(&"file_2"));

    // Should have 2 jobs
    assert_eq!(spec.jobs.len(), 2);
}

#[rstest]
fn test_local_parameters_override_shared() {
    // Test that local parameters take precedence over shared parameters
    let yaml_content = r#"
name: override_params_test
description: Test local parameters override shared

parameters:
  i: "1:5"

jobs:
  # This job uses local parameters (overrides shared)
  - name: job_{i}
    command: echo {i}
    parameters:
      i: "10:12"
"#;

    let mut spec = WorkflowSpec::from_spec_file_content(yaml_content, "yaml")
        .expect("Failed to parse YAML workflow spec");

    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // Should have 3 jobs (from local 10:12), not 5 (from shared 1:5)
    assert_eq!(spec.jobs.len(), 3);

    // Check that local parameters were used
    let names: Vec<&str> = spec.jobs.iter().map(|j| j.name.as_str()).collect();
    assert!(names.contains(&"job_10"));
    assert!(names.contains(&"job_11"));
    assert!(names.contains(&"job_12"));
}

#[rstest]
fn test_example_file_hyperparameter_sweep_shared_params_yaml() {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("examples/yaml/hyperparameter_sweep_shared_params.yaml");

    let mut spec = WorkflowSpec::from_spec_file(&path)
        .expect("Failed to load hyperparameter_sweep_shared_params.yaml");

    // Verify workflow-level parameters were parsed
    assert!(spec.parameters.is_some());
    let params = spec.parameters.as_ref().unwrap();
    assert_eq!(params.len(), 3);
    assert!(params.contains_key("lr"));
    assert!(params.contains_key("batch_size"));
    assert!(params.contains_key("optimizer"));

    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // Should have same structure as non-shared version (hyperparameter_sweep.yaml):
    // - 2 prepare jobs (no parameters)
    // - 18 training jobs (3 lr * 3 batch_size * 2 optimizer)
    // - 18 aggregate jobs (expanded from template)
    // Total: 2 + 18 + 18 = 38 jobs
    assert_eq!(spec.jobs.len(), 38);

    // Files after expansion:
    // - 2 data files (no parameters)
    // - 18 model files (parameterized)
    // - 18 metrics files (parameterized)
    // Total: 2 + 18 + 18 = 38 files
    assert_eq!(spec.files.as_ref().unwrap().len(), 38);
}

#[rstest]
fn test_example_file_hyperparameter_sweep_shared_params_kdl() {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("examples/kdl/hyperparameter_sweep_shared_params.kdl");

    let mut spec = WorkflowSpec::from_spec_file(&path)
        .expect("Failed to load hyperparameter_sweep_shared_params.kdl");

    // Verify workflow-level parameters were parsed
    assert!(spec.parameters.is_some());

    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // Should have same structure as YAML version: 38 jobs, 38 files
    assert_eq!(spec.jobs.len(), 38);
    assert_eq!(spec.files.as_ref().unwrap().len(), 38);
}

#[rstest]
fn test_example_file_hyperparameter_sweep_shared_params_json5() {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("examples/json/hyperparameter_sweep_shared_params.json5");

    let mut spec = WorkflowSpec::from_spec_file(&path)
        .expect("Failed to load hyperparameter_sweep_shared_params.json5");

    // Verify workflow-level parameters were parsed
    assert!(spec.parameters.is_some());

    spec.expand_parameters()
        .expect("Failed to expand parameters");

    // Should have same structure as YAML/KDL versions: 38 jobs, 38 files
    assert_eq!(spec.jobs.len(), 38);
    assert_eq!(spec.files.as_ref().unwrap().len(), 38);
}
