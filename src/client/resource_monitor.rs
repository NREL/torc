use log::{debug, error, info, warn};
use rusqlite::{Connection, Result as SqliteResult};
use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::mpsc::{Receiver, Sender, channel};
use std::sync::{Arc, Mutex};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};
use sysinfo::{
    CpuRefreshKind, Pid, ProcessExt, ProcessRefreshKind, RefreshKind, System, SystemExt,
};

const DB_FILENAME_PREFIX: &str = "resource_metrics";

/// Configuration for resource monitoring
#[derive(Debug, Clone, PartialEq, serde::Deserialize, serde::Serialize)]
#[serde(default)]
pub struct ResourceMonitorConfig {
    pub enabled: bool,
    pub granularity: MonitorGranularity,
    pub sample_interval_seconds: i32,
    pub generate_plots: bool,
}

impl Default for ResourceMonitorConfig {
    fn default() -> Self {
        ResourceMonitorConfig {
            enabled: false,
            granularity: MonitorGranularity::Summary,
            sample_interval_seconds: 5,
            generate_plots: false,
        }
    }
}

#[derive(Debug, Clone, PartialEq, serde::Deserialize, serde::Serialize)]
#[serde(rename_all = "snake_case")]
pub enum MonitorGranularity {
    Summary,
    TimeSeries,
}

/// Metrics collected for a single job
#[derive(Debug, Clone)]
pub struct JobMetrics {
    pub peak_memory_bytes: u64,
    pub avg_memory_bytes: u64,
    pub peak_cpu_percent: f64,
    pub avg_cpu_percent: f64,
    sample_count: usize,
    total_memory_bytes: u64,
    total_cpu_percent: f64,
}

impl JobMetrics {
    fn new() -> Self {
        JobMetrics {
            peak_memory_bytes: 0,
            avg_memory_bytes: 0,
            peak_cpu_percent: 0.0,
            avg_cpu_percent: 0.0,
            sample_count: 0,
            total_memory_bytes: 0,
            total_cpu_percent: 0.0,
        }
    }

    fn add_sample(&mut self, cpu_percent: f64, memory_bytes: u64) {
        self.sample_count += 1;
        self.total_cpu_percent += cpu_percent;
        self.total_memory_bytes += memory_bytes;

        if cpu_percent > self.peak_cpu_percent {
            self.peak_cpu_percent = cpu_percent;
        }
        if memory_bytes > self.peak_memory_bytes {
            self.peak_memory_bytes = memory_bytes;
        }

        self.avg_cpu_percent = self.total_cpu_percent / self.sample_count as f64;
        self.avg_memory_bytes = self.total_memory_bytes / self.sample_count as u64;
    }
}

/// Commands sent to the monitoring thread
enum MonitorCommand {
    StartMonitoring {
        pid: u32,
        job_id: i64,
        job_name: String,
    },
    StopMonitoring {
        pid: u32,
    },
    Shutdown,
}

/// Active job being monitored
struct MonitoredJob {
    job_id: i64,
    #[allow(dead_code)]
    pid: u32,
    metrics: JobMetrics,
}

/// Resource monitor manages a single background thread that monitors all running jobs
pub struct ResourceMonitor {
    tx: Sender<MonitorCommand>,
    metrics: Arc<Mutex<HashMap<u32, JobMetrics>>>,
    handle: Option<JoinHandle<()>>,
}

impl ResourceMonitor {
    /// Create a new resource monitor
    pub fn new(
        config: ResourceMonitorConfig,
        output_dir: PathBuf,
        unique_label: String,
    ) -> Result<Self, Box<dyn std::error::Error>> {
        let (tx, rx) = channel();
        let metrics = Arc::new(Mutex::new(HashMap::new()));
        let metrics_clone = Arc::clone(&metrics);

        let handle = thread::spawn(move || {
            if let Err(e) = run_monitoring_loop(config, output_dir, unique_label, rx, metrics_clone)
            {
                error!("Resource monitoring thread failed: {}", e);
            }
        });

        Ok(ResourceMonitor {
            tx,
            metrics,
            handle: Some(handle),
        })
    }

    /// Start monitoring a process
    pub fn start_monitoring(
        &self,
        pid: u32,
        job_id: i64,
        job_name: String,
    ) -> Result<(), Box<dyn std::error::Error>> {
        self.tx.send(MonitorCommand::StartMonitoring {
            pid,
            job_id,
            job_name,
        })?;
        debug!("Started monitoring job {} with PID {}", job_id, pid);
        Ok(())
    }

    /// Stop monitoring a process and return its metrics
    pub fn stop_monitoring(&self, pid: u32) -> Option<JobMetrics> {
        if let Err(e) = self.tx.send(MonitorCommand::StopMonitoring { pid }) {
            error!("Failed to send stop monitoring command: {}", e);
            return None;
        }

        // Wait briefly for the thread to process the stop command
        thread::sleep(Duration::from_millis(100));

        self.metrics.lock().ok()?.remove(&pid)
    }

    /// Get metrics for a specific PID without stopping monitoring
    pub fn get_metrics(&self, pid: u32) -> Option<JobMetrics> {
        self.metrics.lock().ok()?.get(&pid).cloned()
    }

    /// Shutdown the monitoring thread
    pub fn shutdown(self) {
        if let Err(e) = self.tx.send(MonitorCommand::Shutdown) {
            error!("Failed to send shutdown command: {}", e);
            return;
        }

        if let Some(handle) = self.handle {
            // Wait up to 10 seconds for shutdown
            let start = Instant::now();
            while !handle.is_finished() && start.elapsed() < Duration::from_secs(10) {
                thread::sleep(Duration::from_millis(100));
            }

            if !handle.is_finished() {
                warn!("Resource monitor thread did not shutdown within 10 seconds");
            } else {
                let _ = handle.join();
                info!("Resource monitor thread shutdown successfully");
            }
        }
    }
}

/// Main monitoring loop that runs in a background thread
fn run_monitoring_loop(
    config: ResourceMonitorConfig,
    output_dir: PathBuf,
    unique_label: String,
    rx: Receiver<MonitorCommand>,
    metrics: Arc<Mutex<HashMap<u32, JobMetrics>>>,
) -> Result<(), Box<dyn std::error::Error>> {
    // Use new_with_specifics to only refresh processes, CPU, and memory, avoiding user enumeration
    // which can crash on HPC systems with large LDAP user databases
    let refresh_kind = RefreshKind::new()
        .with_processes(ProcessRefreshKind::everything())
        .with_cpu(CpuRefreshKind::everything())
        .with_memory();
    let mut sys = System::new_with_specifics(refresh_kind);
    let mut monitored_jobs: HashMap<u32, MonitoredJob> = HashMap::new();
    let sample_interval = Duration::from_secs(config.sample_interval_seconds as u64);

    // Initialize database if using TimeSeries
    let mut db_conn = match config.granularity {
        MonitorGranularity::TimeSeries => Some(init_timeseries_db(&output_dir, &unique_label)?),
        MonitorGranularity::Summary => None,
    };

    info!(
        "Resource monitoring started: granularity={:?}, sample_interval={}s",
        config.granularity, config.sample_interval_seconds
    );

    let mut last_sample_time = Instant::now();

    loop {
        // Process all pending commands (non-blocking)
        while let Ok(cmd) = rx.try_recv() {
            match cmd {
                MonitorCommand::StartMonitoring {
                    pid,
                    job_id,
                    job_name,
                } => {
                    // Store job metadata in database
                    if let Some(ref mut conn) = db_conn
                        && let Err(e) = store_job_metadata(conn, job_id, &job_name)
                    {
                        error!("Failed to store job metadata for job {}: {}", job_id, e);
                    }

                    monitored_jobs.insert(
                        pid,
                        MonitoredJob {
                            job_id,
                            pid,
                            metrics: JobMetrics::new(),
                        },
                    );
                    debug!("Now monitoring {} jobs", monitored_jobs.len());
                }
                MonitorCommand::StopMonitoring { pid } => {
                    if let Some(job) = monitored_jobs.remove(&pid) {
                        // Store final metrics in shared map
                        if let Ok(mut metrics_lock) = metrics.lock() {
                            metrics_lock.insert(pid, job.metrics);
                        }
                        debug!(
                            "Stopped monitoring PID {}, {} jobs remaining",
                            pid,
                            monitored_jobs.len()
                        );
                    }
                }
                MonitorCommand::Shutdown => {
                    info!("Resource monitor received shutdown command");
                    return Ok(());
                }
            }
        }

        // Sample all monitored jobs if interval has elapsed
        if last_sample_time.elapsed() >= sample_interval && !monitored_jobs.is_empty() {
            sys.refresh_processes();
            let timestamp = chrono::Utc::now().timestamp();

            for (pid, job) in monitored_jobs.iter_mut() {
                let (cpu_percent, memory_bytes, num_processes) =
                    collect_process_tree_stats(*pid, &sys);

                job.metrics.add_sample(cpu_percent, memory_bytes);

                // Store in database if using TimeSeries
                if let Some(ref mut conn) = db_conn
                    && let Err(e) = store_sample(
                        conn,
                        job.job_id,
                        timestamp,
                        cpu_percent,
                        memory_bytes,
                        num_processes,
                    )
                {
                    error!("Failed to store sample for job {}: {}", job.job_id, e);
                }

                debug!(
                    "Job {} (PID {}): CPU={:.1}%, Mem={:.1}MB, Procs={}",
                    job.job_id,
                    pid,
                    cpu_percent,
                    memory_bytes as f64 / (1024.0 * 1024.0),
                    num_processes
                );
            }

            last_sample_time = Instant::now();
        }

        // Sleep briefly to avoid busy-waiting
        thread::sleep(Duration::from_millis(100));
    }
}

/// Collect CPU and memory stats for a process and all its children
fn collect_process_tree_stats(root_pid: u32, sys: &System) -> (f64, u64, usize) {
    let mut pids_to_check = vec![Pid::from(root_pid as usize)];
    let mut visited = HashSet::new();
    let mut total_cpu = 0.0;
    let mut total_memory = 0;

    while let Some(pid) = pids_to_check.pop() {
        if visited.contains(&pid) {
            continue;
        }
        visited.insert(pid);

        if let Some(process) = sys.process(pid) {
            total_cpu += process.cpu_usage() as f64;
            total_memory += process.memory(); // sysinfo already gives bytes

            // Find all children of this process
            for (child_pid, child_proc) in sys.processes() {
                if child_proc.parent() == Some(pid) && !visited.contains(child_pid) {
                    pids_to_check.push(*child_pid);
                }
            }
        }
    }

    (total_cpu, total_memory, visited.len())
}

/// Initialize the TimeSeries database
fn init_timeseries_db(output_dir: &Path, unique_label: &str) -> SqliteResult<Connection> {
    // Create resource_utilization subdirectory
    let resource_util_dir = output_dir.join("resource_utilization");
    if let Err(e) = std::fs::create_dir_all(&resource_util_dir) {
        error!("Failed to create resource_utilization directory: {}", e);
        return Err(rusqlite::Error::InvalidPath(resource_util_dir.clone()));
    }

    let db_path = resource_util_dir.join(format!("{}_{}.db", DB_FILENAME_PREFIX, unique_label));
    info!(
        "Initializing resource metrics database at: {}",
        db_path.display()
    );

    let conn = Connection::open(&db_path)?;

    conn.execute(
        "CREATE TABLE IF NOT EXISTS job_resource_samples (
            job_id INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            cpu_percent REAL NOT NULL,
            memory_bytes INTEGER NOT NULL,
            num_processes INTEGER NOT NULL,
            PRIMARY KEY (job_id, timestamp)
        )",
        [],
    )?;

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_job_resource_samples_job_id
         ON job_resource_samples(job_id)",
        [],
    )?;

    conn.execute(
        "CREATE TABLE IF NOT EXISTS job_metadata (
            job_id INTEGER PRIMARY KEY,
            job_name TEXT NOT NULL
        )",
        [],
    )?;

    Ok(conn)
}

/// Store job metadata in the TimeSeries database
fn store_job_metadata(conn: &mut Connection, job_id: i64, job_name: &str) -> SqliteResult<()> {
    conn.execute(
        "INSERT OR REPLACE INTO job_metadata (job_id, job_name)
         VALUES (?1, ?2)",
        rusqlite::params![job_id, job_name],
    )?;
    Ok(())
}

/// Store a sample in the TimeSeries database
fn store_sample(
    conn: &mut Connection,
    job_id: i64,
    timestamp: i64,
    cpu_percent: f64,
    memory_bytes: u64,
    num_processes: usize,
) -> SqliteResult<()> {
    conn.execute(
        "INSERT INTO job_resource_samples (job_id, timestamp, cpu_percent, memory_bytes, num_processes)
         VALUES (?1, ?2, ?3, ?4, ?5)",
        rusqlite::params![job_id, timestamp, cpu_percent, memory_bytes as i64, num_processes as i64],
    )?;
    Ok(())
}
