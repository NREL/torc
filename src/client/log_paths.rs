use std::path::PathBuf;

/// Return the name of the job runner log file for the local runner.
pub fn get_job_runner_log_file(
    output_dir: PathBuf,
    hostname: &str,
    workflow_id: i64,
    run_id: i64,
) -> String {
    format!(
        "{}/job_runner_{}_{}_{}.log",
        output_dir.display(),
        hostname,
        workflow_id,
        run_id,
    )
}

/// Return the name of the job runner log file for Slurm schedulers.
pub fn get_slurm_job_runner_log_file(
    output_dir: PathBuf,
    job_id: &str,
    node_id: &str,
    task_pid: usize,
) -> String {
    format!(
        "{}/job_runner_slurm_{}_{}_{}.log",
        output_dir.display(),
        job_id,
        node_id,
        task_pid
    )
}

/// Get the path to a job's stdout log file
pub fn get_job_stdout_path(
    output_dir: &PathBuf,
    workflow_id: i64,
    job_id: i64,
    run_id: i64,
) -> String {
    format!(
        "{}/job_stdio/job_{}_{}_{}.o",
        output_dir.display(),
        workflow_id,
        job_id,
        run_id
    )
}

/// Get the path to a job's stderr log file
pub fn get_job_stderr_path(
    output_dir: &PathBuf,
    workflow_id: i64,
    job_id: i64,
    run_id: i64,
) -> String {
    format!(
        "{}/job_stdio/job_{}_{}_{}.e",
        output_dir.display(),
        workflow_id,
        job_id,
        run_id
    )
}

/// Get the path to Slurm's stdout log file
pub fn get_slurm_stdout_path(output_dir: &PathBuf, slurm_job_id: &str) -> String {
    format!("{}/slurm_output_{}.o", output_dir.display(), slurm_job_id)
}

/// Get the path to Slurm's stderr log file
pub fn get_slurm_stderr_path(output_dir: &PathBuf, slurm_job_id: &str) -> String {
    format!("{}/slurm_output_{}.e", output_dir.display(), slurm_job_id)
}

/// Return the path for the dmesg log file captured by the Slurm job runner.
/// Uses the same identifiers as the job runner log for consistency and easy correlation.
pub fn get_slurm_dmesg_log_file(
    output_dir: PathBuf,
    job_id: &str,
    node_id: &str,
    task_pid: usize,
) -> String {
    format!(
        "{}/dmesg_slurm_{}_{}_{}.log",
        output_dir.display(),
        job_id,
        node_id,
        task_pid
    )
}

/// Return the path for the Slurm environment variables log file.
/// Uses the same identifiers as the job runner log for consistency and easy correlation.
pub fn get_slurm_env_log_file(
    output_dir: PathBuf,
    job_id: &str,
    node_id: &str,
    task_pid: usize,
) -> String {
    format!(
        "{}/slurm_env_{}_{}_{}.log",
        output_dir.display(),
        job_id,
        node_id,
        task_pid
    )
}
