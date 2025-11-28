//! Asynchronous CLI command execution for workflow jobs.
//!
//! This module provides [`AsyncCliCommand`], which wraps a subprocess for executing
//! workflow jobs. It supports:
//!
//! - Non-blocking process execution with status polling
//! - Graceful termination via SIGTERM (Unix) or immediate kill (Windows)
//! - Resource monitoring integration
//! - Exit code capture including signal-based terminations
//!
//! # Termination Signals
//!
//! On Unix systems, the module supports two termination methods:
//!
//! - **`terminate()`** / **`send_sigterm()`**: Sends SIGTERM to the process, allowing it
//!   to perform cleanup before exiting. The process should handle SIGTERM and exit
//!   gracefully within a reasonable time.
//!
//! - **`cancel()`**: Sends SIGKILL to immediately terminate the process. No cleanup
//!   is performed.
//!
//! On non-Unix systems, both methods result in immediate process termination.
//!
//! After calling `terminate()` or `cancel()`, call `wait_for_completion()` to wait
//! for the process to exit and capture its exit code.

use crate::client::resource_monitor::ResourceMonitor;
use crate::models::{JobModel, JobStatus, ResultModel};
use chrono::{DateTime, Utc};
use log::{self, debug, error, info};
use std::fs::File;
use std::io::BufWriter;
use std::path::Path;
use std::process::{Child, Stdio};

#[cfg(unix)]
use std::os::unix::process::ExitStatusExt;

const JOB_STDIO_DIR: &str = "job_stdio";

#[allow(dead_code)]
pub struct AsyncCliCommand {
    pub job: JobModel,
    pub job_id: i64,
    handle: Option<Child>,
    pid: Option<u32>,
    pub is_running: bool,
    start_time: DateTime<Utc>,
    completion_time: Option<DateTime<Utc>>,
    exec_time_s: f64,
    return_code: Option<i64>,
    pub is_complete: bool,
    status: JobStatus,
    stdout_fp: Option<BufWriter<File>>,
    stderr_fp: Option<BufWriter<File>>,
}

impl AsyncCliCommand {
    pub fn new(job: JobModel) -> Self {
        let job_id = job.id.expect("Job must have an ID");
        let status = job.status.expect("Job status must be set");
        AsyncCliCommand {
            job,
            job_id,
            handle: None,
            pid: None,
            is_running: false,
            start_time: Utc::now(),
            completion_time: None,
            exec_time_s: 0.0,
            return_code: None,
            is_complete: false,
            status,
            stdout_fp: None,
            stderr_fp: None,
        }
    }

    pub fn start(
        &mut self,
        output_dir: &Path,
        workflow_id: i64,
        run_id: i64,
        resource_monitor: Option<&ResourceMonitor>,
        api_url: &str,
    ) -> Result<(), Box<dyn std::error::Error>> {
        if self.is_running {
            return Err("Job is already running".into());
        }

        let job_id_str = self.job_id.to_string();
        let workflow_id_str = workflow_id.to_string();

        // Create output file paths
        let stdio_dir = output_dir.join(JOB_STDIO_DIR);
        std::fs::create_dir_all(&stdio_dir)?;

        let stdout_path =
            stdio_dir.join(format!("job_{}_{}_{}.o", workflow_id, self.job_id, run_id));
        let stderr_path =
            stdio_dir.join(format!("job_{}_{}_{}.e", workflow_id, self.job_id, run_id));

        let stdout_file = File::create(&stdout_path)?;
        let stderr_file = File::create(&stderr_path)?;
        self.stdout_fp = Some(BufWriter::new(stdout_file));
        self.stderr_fp = Some(BufWriter::new(stderr_file));

        let mut cmd = if cfg!(target_os = "windows") {
            let mut c = std::process::Command::new("cmd");
            c.arg("/C");
            c
        } else {
            let mut c = std::process::Command::new("bash");
            c.arg("-c");
            c
        };

        let command_str = if let Some(ref invocation_script) = self.job.invocation_script {
            format!("{} {}", invocation_script, self.job.command)
        } else {
            self.job.command.clone()
        };
        let child = cmd
            .arg(&command_str)
            .env("TORC_WORKFLOW_ID", workflow_id_str)
            .env("TORC_JOB_ID", job_id_str)
            .env("TORC_API_URL", api_url)
            .stdout(Stdio::from(File::create(&stdout_path)?))
            .stderr(Stdio::from(File::create(&stderr_path)?))
            .spawn()?;

        let pid = child.id();
        self.pid = Some(pid);
        self.handle = Some(child);
        self.is_running = true;
        self.start_time = Utc::now();
        self.status = JobStatus::Running;
        debug!("Started job {} with PID {}", self.get_job_id(), pid);

        // Start resource monitoring if enabled
        if let Some(monitor) = resource_monitor {
            monitor.start_monitoring(pid, self.job_id, self.job.name.clone())?;
        }

        // TODO: CPU Affinity
        Ok(())
    }

    pub fn check_status(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        if !self.is_running || self.handle.is_none() {
            return Ok(());
        }

        if let Some(ref mut child) = self.handle {
            match child.try_wait()? {
                None => {
                    // Process is still running
                }
                Some(exit_status) => {
                    let return_code = exit_status.code().unwrap_or(-1);
                    let status = if return_code == 0 {
                        JobStatus::Completed
                    } else {
                        JobStatus::Failed
                    };
                    return match self.handle_completion(return_code as i64, status) {
                        Ok(_) => Ok(()),
                        Err(e) => Err(e),
                    };
                }
            }
        }

        Ok(())
    }

    /// Get the result of the completed job as a ResultModel.
    pub fn get_result(
        &self,
        run_id: i64,
        compute_node_id: i64,
        resource_monitor: Option<&ResourceMonitor>,
    ) -> ResultModel {
        assert!(self.is_complete, "Job is not yet complete");
        let timestamp = self
            .completion_time
            .expect("A completed job must have a completion_time");
        let timestamp_str = timestamp.format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string();

        // Get resource metrics if monitoring is enabled
        // NOTE: stop_monitoring() transfers metrics from the monitoring thread's local HashMap
        // to the shared HashMap and returns them. Using get_metrics() won't work because
        // metrics are only transferred when StopMonitoring command is processed.
        let (peak_mem, avg_mem, peak_cpu, avg_cpu) = if let Some(monitor) = resource_monitor {
            if let Some(pid) = self.pid {
                if let Some(metrics) = monitor.stop_monitoring(pid) {
                    (
                        Some(metrics.peak_memory_bytes as i64),
                        Some(metrics.avg_memory_bytes as i64),
                        Some(metrics.peak_cpu_percent),
                        Some(metrics.avg_cpu_percent),
                    )
                } else {
                    (None, None, None, None)
                }
            } else {
                (None, None, None, None)
            }
        } else {
            (None, None, None, None)
        };

        let mut result = ResultModel::new(
            self.job_id,
            self.job.workflow_id,
            run_id,
            compute_node_id,
            self.return_code
                .expect("A completed job must have a return code"),
            self.exec_time_s / 60.0,
            timestamp_str,
            self.status.clone(),
        );

        // Set resource metrics
        result.peak_memory_bytes = peak_mem;
        result.avg_memory_bytes = avg_mem;
        result.peak_cpu_percent = peak_cpu;
        result.avg_cpu_percent = avg_cpu;

        result
    }

    /// Immediately kills the job process using SIGKILL.
    ///
    /// This method sends SIGKILL to the process, which cannot be caught or ignored.
    /// The process will be terminated immediately without any cleanup. Use this for
    /// jobs that don't support graceful termination.
    ///
    /// **Note**: This method does not wait for the process to exit. Call
    /// [`wait_for_completion()`] afterwards to wait for the process and capture its exit code.
    ///
    /// # Example
    ///
    /// ```ignore
    /// async_cmd.cancel()?;
    /// let exit_code = async_cmd.wait_for_completion()?;
    /// ```
    pub fn cancel(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(ref mut child) = self.handle {
            child.kill()?;
        }
        Ok(())
    }

    /// Sends SIGTERM to the process for graceful termination (Unix only).
    ///
    /// SIGTERM is a signal that requests the process to terminate gracefully. Well-behaved
    /// processes should catch this signal and perform cleanup (save state, flush buffers,
    /// release resources) before exiting.
    ///
    /// **Note**: This method does not wait for the process to exit. Call
    /// [`wait_for_completion()`] afterwards to wait for the process and capture its exit code.
    ///
    /// # Platform Behavior
    ///
    /// - **Unix**: Sends SIGTERM via `libc::kill()`
    /// - **Windows/Other**: Falls back to `kill()` (SIGKILL equivalent)
    ///
    /// # Example
    ///
    /// ```ignore
    /// async_cmd.send_sigterm()?;
    /// let exit_code = async_cmd.wait_for_completion()?;
    /// // exit_code will be negative (-15) if killed by SIGTERM on Unix
    /// ```
    #[cfg(unix)]
    pub fn send_sigterm(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(ref child) = self.handle {
            let pid = child.id();
            debug!("Sending SIGTERM to job {} (PID {})", self.job_id, pid);
            let result = unsafe { libc::kill(pid as libc::pid_t, libc::SIGTERM) };
            if result != 0 {
                let err = std::io::Error::last_os_error();
                return Err(format!(
                    "Failed to send SIGTERM to job {} (PID {}): {}",
                    self.job_id, pid, err
                )
                .into());
            }
        }
        Ok(())
    }

    /// Sends a termination signal to the process (non-Unix fallback).
    ///
    /// On non-Unix systems (Windows, etc.), SIGTERM is not available, so this method
    /// falls back to immediately killing the process. Jobs running on these platforms
    /// will not have an opportunity for graceful cleanup.
    ///
    /// **Note**: This method does not wait for the process to exit. Call
    /// [`wait_for_completion()`] afterwards to wait for the process and capture its exit code.
    #[cfg(not(unix))]
    pub fn send_sigterm(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(ref mut child) = self.handle {
            debug!(
                "Sending kill signal to job {} (SIGTERM not available on this platform)",
                self.job_id
            );
            child.kill()?;
        }
        Ok(())
    }

    /// Requests graceful termination of the job by sending SIGTERM.
    ///
    /// This is an alias for [`send_sigterm()`]. Use this method when you want to give
    /// the job process an opportunity to clean up before exiting.
    ///
    /// **Note**: This method does not wait for the process to exit. Call
    /// [`wait_for_completion()`] afterwards to wait for the process and capture its exit code.
    ///
    /// # Graceful Shutdown Flow
    ///
    /// 1. Call `terminate()` to send SIGTERM
    /// 2. The process catches SIGTERM and performs cleanup
    /// 3. Call `wait_for_completion()` to wait for exit and get the exit code
    ///
    /// # Example
    ///
    /// ```ignore
    /// // Graceful termination
    /// async_cmd.terminate()?;
    /// let exit_code = async_cmd.wait_for_completion()?;
    /// assert!(async_cmd.is_complete);
    /// ```
    pub fn terminate(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        self.send_sigterm()
    }

    /// Force the job to completion with a return code and status. Does not send anything
    /// to the process.
    // pub fn force_complete(mut self, return_code: i64, status: JobStatus) -> Result<(), Box<dyn std::error::Error>>  {
    //     match self.handle_completion(return_code, status) {
    //         Ok(_) => Ok(()),
    //         Err(e) => Err(e),
    //     }
    // }

    /// Perform cleanup operations after the command has completed.
    fn handle_completion(
        &mut self,
        return_code: i64,
        status: JobStatus,
    ) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(ref mut child) = self.handle {
            child.kill()?;
            child.wait()?;
        }
        self.is_running = false;
        self.is_complete = true;
        self.completion_time = Some(Utc::now());
        self.exec_time_s =
            (self.completion_time.unwrap() - self.start_time).num_milliseconds() as f64 / 1000.0;
        self.status = status;
        self.return_code = Some(return_code);
        self.stdout_fp = None;
        self.stderr_fp = None;
        self.handle = None;
        info!(
            "Job ID {} completed return_code={} status={} exec_time_s={}",
            self.get_job_id(),
            return_code,
            status,
            self.exec_time_s
        );
        Ok(())
    }

    /// Return the job ID.
    #[allow(dead_code)]
    pub fn get_job_id(&self) -> i64 {
        self.job.id.expect("Job ID must be set")
    }

    // Get the process ID of the running job. Can only be called if the job is running.
    // pub fn get_pid(&self) -> Result<u32, Box<dyn std::error::Error>> {
    //     if !self.is_running {
    //         return Err("Job is not running".into());
    //     }

    //     if let Some(ref child) = self.handle {
    //         Ok(child.id())
    //     } else {
    //         Err("No process handle available".into())
    //     }
    // }

    // pub fn get_exec_time_minutes(&self) -> f64 {
    //     self.exec_time_s / 60.0
    // }

    /// Waits for the process to exit and returns its exit code.
    ///
    /// This method blocks until the process exits. It should be called after
    /// [`terminate()`] or [`cancel()`] to wait for the process to finish and
    /// capture its exit code.
    ///
    /// After this method returns, the job is marked as complete with status
    /// `JobStatus::Terminated`.
    ///
    /// # Returns
    ///
    /// - **Positive value**: Normal exit code from the process
    /// - **Negative value** (Unix): Signal number that killed the process (e.g., -15 for SIGTERM, -9 for SIGKILL)
    /// - **-1**: Unknown exit status
    ///
    /// # Example
    ///
    /// ```ignore
    /// async_cmd.terminate()?;  // Send SIGTERM
    /// let exit_code = async_cmd.wait_for_completion()?;
    ///
    /// if exit_code == 0 {
    ///     println!("Job exited normally");
    /// } else if exit_code < 0 {
    ///     println!("Job killed by signal {}", -exit_code);
    /// } else {
    ///     println!("Job exited with error code {}", exit_code);
    /// }
    /// ```
    pub fn wait_for_completion(&mut self) -> Result<i32, Box<dyn std::error::Error>> {
        let exit_code = if let Some(ref mut child) = self.handle {
            // If we have issues with the process hanging, we could try_wait
            // with a timeout.
            let exit_status = child.wait()?;

            #[cfg(unix)]
            {
                // On Unix, check if the process was terminated by a signal
                if let Some(code) = exit_status.code() {
                    code
                } else if let Some(signal) = exit_status.signal() {
                    // Process was killed by a signal - return negative signal number
                    // This is a common Unix convention
                    debug!("Job {} was terminated by signal {}", self.job_id, signal);
                    -(signal as i32)
                } else {
                    -1
                }
            }
            #[cfg(not(unix))]
            {
                exit_status.code().unwrap_or(-1)
            }
        } else {
            -1
        };

        // Mark as terminated with the actual exit code
        self.handle_completion(exit_code as i64, JobStatus::Terminated)?;
        Ok(exit_code)
    }
}

impl Drop for AsyncCliCommand {
    fn drop(&mut self) {
        if self.is_running {
            error!(
                "Job is being dropped while running. Terminating job {}",
                self.get_job_id()
            );
            let _ = self.terminate();
        }
    }
}
