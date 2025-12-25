use anyhow::{Context, Result};
use clap::Parser;
use plotly::common::{AxisSide, Mode};
use plotly::layout::{Axis, Layout};
use plotly::{Plot, Scatter};
use rusqlite::{Connection, Result as SqliteResult};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

/// Tool for generating interactive HTML plots from Torc resource monitoring data
#[derive(Parser, Debug)]
#[command(about = "Generate interactive HTML plots from resource monitoring data", long_about = None)]
pub struct Args {
    /// Path to the resource metrics database file(s)
    #[arg(required = true)]
    pub db_paths: Vec<PathBuf>,

    /// Output directory for generated plots (default: current directory)
    #[arg(short, long, default_value = ".")]
    pub output_dir: PathBuf,

    /// Only plot specific job IDs (comma-separated)
    #[arg(short, long, value_delimiter = ',')]
    pub job_ids: Vec<i64>,

    /// Prefix for output filenames
    #[arg(short = 'p', long, default_value = "resource_plot")]
    pub prefix: String,

    /// Output format: html or json
    #[arg(short = 'f', long, default_value = "html")]
    pub format: String,
}

#[derive(Debug, Clone)]
struct ResourceSample {
    job_id: i64,
    timestamp: i64,
    cpu_percent: f64,
    memory_bytes: i64,
    num_processes: i64,
}

#[derive(Debug)]
struct JobMetrics {
    job_id: i64,
    job_name: Option<String>,
    samples: Vec<ResourceSample>,
    peak_cpu: f64,
    avg_cpu: f64,
    peak_memory_gb: f64,
    avg_memory_gb: f64,
    duration_seconds: f64,
}

pub fn run(args: &Args) -> Result<()> {
    // Create output directory if it doesn't exist
    std::fs::create_dir_all(&args.output_dir).context("Failed to create output directory")?;

    // Load data from all database files
    let mut all_jobs: HashMap<i64, Vec<ResourceSample>> = HashMap::new();
    let mut job_names: HashMap<i64, String> = HashMap::new();

    for db_path in &args.db_paths {
        println!("Loading data from: {}", db_path.display());
        let samples = load_samples(db_path)?;
        let names = load_job_names(db_path)?;
        println!(
            "  Loaded {} samples and {} job names",
            samples.len(),
            names.len()
        );

        for sample in samples {
            all_jobs.entry(sample.job_id).or_default().push(sample);
        }

        // Merge job names
        job_names.extend(names);
    }

    // Filter by job IDs if specified
    let jobs_to_plot: Vec<i64> = if args.job_ids.is_empty() {
        all_jobs.keys().copied().collect()
    } else {
        args.job_ids.clone()
    };

    if jobs_to_plot.is_empty() {
        println!("No jobs found to plot");
        return Ok(());
    }

    // Calculate metrics for each job
    let mut job_metrics: Vec<JobMetrics> = Vec::new();
    for job_id in &jobs_to_plot {
        if let Some(samples) = all_jobs.get(job_id)
            && !samples.is_empty()
        {
            let job_name = job_names.get(job_id).cloned();
            let metrics = calculate_metrics(*job_id, job_name, samples);

            let job_display = if let Some(ref name) = metrics.job_name {
                format!("Job {} ({})", metrics.job_id, name)
            } else {
                format!("Job {}", metrics.job_id)
            };

            println!(
                "{}: {} samples, {:.1}s duration, peak CPU: {:.1}%, peak mem: {:.2} GB",
                job_display,
                samples.len(),
                metrics.duration_seconds,
                metrics.peak_cpu,
                metrics.peak_memory_gb
            );
            job_metrics.push(metrics);
        }
    }

    job_metrics.sort_by_key(|m| m.job_id);

    // Determine file extension based on format
    let extension = match args.format.as_str() {
        "json" => "json",
        _ => "html",
    };

    // Generate plots
    println!("\nGenerating plots...");

    // 1. Individual job plots
    for metrics in &job_metrics {
        let output_path = args.output_dir.join(format!(
            "{}_job_{}.{}",
            args.prefix, metrics.job_id, extension
        ));
        plot_job_timeline(metrics, &output_path, &args.format)?;
        println!("  Created: {}", output_path.display());
    }

    // 2. Overview plots with all jobs
    if job_metrics.len() > 1 {
        let cpu_output_path = args
            .output_dir
            .join(format!("{}_cpu_all_jobs.{}", args.prefix, extension));
        plot_all_jobs_cpu_overview(&job_metrics, &cpu_output_path, &args.format)?;
        println!("  Created: {}", cpu_output_path.display());

        let memory_output_path = args
            .output_dir
            .join(format!("{}_memory_all_jobs.{}", args.prefix, extension));
        plot_all_jobs_memory_overview(&job_metrics, &memory_output_path, &args.format)?;
        println!("  Created: {}", memory_output_path.display());
    }

    // 3. Summary dashboard
    let output_path = args
        .output_dir
        .join(format!("{}_summary.{}", args.prefix, extension));
    plot_summary_dashboard(&job_metrics, &output_path, &args.format)?;
    println!("  Created: {}", output_path.display());

    let total_plots = if job_metrics.len() > 1 {
        job_metrics.len() + 3 // individual jobs + cpu overview + memory overview + summary
    } else {
        job_metrics.len() + 1 // individual job + summary
    };
    println!("\nDone! Generated {} plot(s)", total_plots);

    Ok(())
}

fn load_samples(db_path: &Path) -> Result<Vec<ResourceSample>> {
    let conn = Connection::open(db_path)
        .with_context(|| format!("Failed to open database: {}", db_path.display()))?;

    let mut stmt = conn.prepare(
        "SELECT job_id, timestamp, cpu_percent, memory_bytes, num_processes
         FROM job_resource_samples
         ORDER BY job_id, timestamp",
    )?;

    let samples: SqliteResult<Vec<ResourceSample>> = stmt
        .query_map([], |row| {
            Ok(ResourceSample {
                job_id: row.get(0)?,
                timestamp: row.get(1)?,
                cpu_percent: row.get(2)?,
                memory_bytes: row.get(3)?,
                num_processes: row.get(4)?,
            })
        })?
        .collect();

    Ok(samples?)
}

fn load_job_names(db_path: &Path) -> Result<HashMap<i64, String>> {
    let conn = Connection::open(db_path)
        .with_context(|| format!("Failed to open database: {}", db_path.display()))?;

    // Check if job_metadata table exists
    let table_exists: bool = conn
        .prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='job_metadata'")?
        .exists([])?;

    if !table_exists {
        return Ok(HashMap::new());
    }

    let mut stmt = conn.prepare("SELECT job_id, job_name FROM job_metadata")?;
    let names: SqliteResult<HashMap<i64, String>> = stmt
        .query_map([], |row| Ok((row.get(0)?, row.get(1)?)))?
        .collect();

    Ok(names?)
}

fn calculate_metrics(
    job_id: i64,
    job_name: Option<String>,
    samples: &[ResourceSample],
) -> JobMetrics {
    let peak_cpu = samples.iter().map(|s| s.cpu_percent).fold(0.0, f64::max);
    let avg_cpu = samples.iter().map(|s| s.cpu_percent).sum::<f64>() / samples.len() as f64;

    let peak_memory_bytes = samples.iter().map(|s| s.memory_bytes).max().unwrap_or(0);
    let avg_memory_bytes =
        samples.iter().map(|s| s.memory_bytes).sum::<i64>() / samples.len() as i64;

    let peak_memory_gb = peak_memory_bytes as f64 / (1024.0 * 1024.0 * 1024.0);
    let avg_memory_gb = avg_memory_bytes as f64 / (1024.0 * 1024.0 * 1024.0);

    let start_time = samples.first().unwrap().timestamp;
    let end_time = samples.last().unwrap().timestamp;
    let duration_seconds = (end_time - start_time) as f64;

    JobMetrics {
        job_id,
        job_name,
        samples: samples.to_vec(),
        peak_cpu,
        avg_cpu,
        peak_memory_gb,
        avg_memory_gb,
        duration_seconds,
    }
}

fn write_plot(plot: &Plot, output_path: &Path, format: &str) -> Result<()> {
    match format {
        "json" => {
            let json_str = plot.to_json();
            std::fs::write(output_path, json_str)
                .with_context(|| format!("Failed to write JSON to {}", output_path.display()))?;
        }
        _ => {
            plot.write_html(output_path);
        }
    }
    Ok(())
}

fn plot_job_timeline(metrics: &JobMetrics, output_path: &Path, format: &str) -> Result<()> {
    let mut plot = Plot::new();

    // Convert timestamps to relative seconds
    let start_time = metrics.samples.first().unwrap().timestamp;
    let times: Vec<f64> = metrics
        .samples
        .iter()
        .map(|s| (s.timestamp - start_time) as f64)
        .collect();

    let cpu_values: Vec<f64> = metrics.samples.iter().map(|s| s.cpu_percent).collect();
    let memory_values: Vec<f64> = metrics
        .samples
        .iter()
        .map(|s| s.memory_bytes as f64 / (1024.0 * 1024.0 * 1024.0))
        .collect();
    let process_counts: Vec<i64> = metrics.samples.iter().map(|s| s.num_processes).collect();

    // CPU trace
    let cpu_trace = Scatter::new(times.clone(), cpu_values)
        .name("CPU %")
        .mode(Mode::Lines)
        .y_axis("y1");

    // Memory trace
    let memory_trace = Scatter::new(times.clone(), memory_values)
        .name("Memory (GB)")
        .mode(Mode::Lines)
        .y_axis("y2");

    // Process count trace
    let process_trace = Scatter::new(times, process_counts)
        .name("# Processes")
        .mode(Mode::Lines)
        .y_axis("y3");

    plot.add_trace(cpu_trace);
    plot.add_trace(memory_trace);
    plot.add_trace(process_trace);

    let job_display = if let Some(ref name) = metrics.job_name {
        format!("Job {} ({})", metrics.job_id, name)
    } else {
        format!("Job {}", metrics.job_id)
    };

    let title = format!(
        "{} Resource Usage Timeline<br><sub>Peak: {:.1}% CPU, {:.2} GB Memory | Avg: {:.1}% CPU, {:.2} GB Memory</sub>",
        job_display,
        metrics.peak_cpu,
        metrics.peak_memory_gb,
        metrics.avg_cpu,
        metrics.avg_memory_gb
    );

    let layout = Layout::new()
        .title(&title)
        .x_axis(Axis::new().title("Time (seconds)"))
        .y_axis(Axis::new().title("CPU %"))
        .y_axis2(
            Axis::new()
                .title("Memory (GB)")
                .overlaying("y")
                .side(AxisSide::Right),
        )
        .y_axis3(
            Axis::new()
                .title("Processes")
                .overlaying("y")
                .side(AxisSide::Right)
                .anchor("free")
                .position(0.95),
        );

    plot.set_layout(layout);
    write_plot(&plot, output_path, format)?;

    Ok(())
}

fn plot_all_jobs_cpu_overview(
    metrics: &[JobMetrics],
    output_path: &Path,
    format: &str,
) -> Result<()> {
    let mut plot = Plot::new();

    for job_metrics in metrics {
        let start_time = job_metrics.samples.first().unwrap().timestamp;
        let times: Vec<f64> = job_metrics
            .samples
            .iter()
            .map(|s| (s.timestamp - start_time) as f64)
            .collect();

        let cpu_values: Vec<f64> = job_metrics.samples.iter().map(|s| s.cpu_percent).collect();

        let trace_name = if let Some(ref name) = job_metrics.job_name {
            format!("Job {} ({})", job_metrics.job_id, name)
        } else {
            format!("Job {}", job_metrics.job_id)
        };

        let trace = Scatter::new(times, cpu_values)
            .name(&trace_name)
            .mode(Mode::Lines);

        plot.add_trace(trace);
    }

    let layout = Layout::new()
        .title("CPU Usage - All Jobs")
        .x_axis(Axis::new().title("Time (seconds)"))
        .y_axis(Axis::new().title("CPU %"));

    plot.set_layout(layout);
    write_plot(&plot, output_path, format)?;

    Ok(())
}

fn plot_all_jobs_memory_overview(
    metrics: &[JobMetrics],
    output_path: &Path,
    format: &str,
) -> Result<()> {
    let mut plot = Plot::new();

    for job_metrics in metrics {
        let start_time = job_metrics.samples.first().unwrap().timestamp;
        let times: Vec<f64> = job_metrics
            .samples
            .iter()
            .map(|s| (s.timestamp - start_time) as f64)
            .collect();

        let memory_values: Vec<f64> = job_metrics
            .samples
            .iter()
            .map(|s| s.memory_bytes as f64 / (1024.0 * 1024.0 * 1024.0))
            .collect();

        let trace_name = if let Some(ref name) = job_metrics.job_name {
            format!("Job {} ({})", job_metrics.job_id, name)
        } else {
            format!("Job {}", job_metrics.job_id)
        };

        let trace = Scatter::new(times, memory_values)
            .name(&trace_name)
            .mode(Mode::Lines);

        plot.add_trace(trace);
    }

    let layout = Layout::new()
        .title("Memory Usage - All Jobs")
        .x_axis(Axis::new().title("Time (seconds)"))
        .y_axis(Axis::new().title("Memory (GB)"));

    plot.set_layout(layout);
    write_plot(&plot, output_path, format)?;

    Ok(())
}

fn plot_summary_dashboard(metrics: &[JobMetrics], output_path: &Path, format: &str) -> Result<()> {
    use plotly::Bar;

    let mut plot = Plot::new();

    let job_ids: Vec<String> = metrics.iter().map(|m| m.job_id.to_string()).collect();
    let peak_cpus: Vec<f64> = metrics.iter().map(|m| m.peak_cpu).collect();
    let avg_cpus: Vec<f64> = metrics.iter().map(|m| m.avg_cpu).collect();
    let peak_mems: Vec<f64> = metrics.iter().map(|m| m.peak_memory_gb).collect();
    let avg_mems: Vec<f64> = metrics.iter().map(|m| m.avg_memory_gb).collect();

    // CPU bar chart
    let peak_cpu_trace = Bar::new(job_ids.clone(), peak_cpus)
        .name("Peak CPU %")
        .y_axis("y1");
    let avg_cpu_trace = Bar::new(job_ids.clone(), avg_cpus)
        .name("Avg CPU %")
        .y_axis("y1");

    // Memory bar chart
    let peak_mem_trace = Bar::new(job_ids.clone(), peak_mems)
        .name("Peak Memory (GB)")
        .y_axis("y2");
    let avg_mem_trace = Bar::new(job_ids, avg_mems)
        .name("Avg Memory (GB)")
        .y_axis("y2");

    plot.add_trace(peak_cpu_trace);
    plot.add_trace(avg_cpu_trace);
    plot.add_trace(peak_mem_trace);
    plot.add_trace(avg_mem_trace);

    let layout = Layout::new()
        .title("Resource Usage Summary - All Jobs")
        .x_axis(Axis::new().title("Job ID"))
        .y_axis(Axis::new().title("CPU %"))
        .y_axis2(
            Axis::new()
                .title("Memory (GB)")
                .overlaying("y")
                .side(AxisSide::Right),
        )
        .bar_mode(plotly::layout::BarMode::Group);

    plot.set_layout(layout);
    write_plot(&plot, output_path, format)?;

    Ok(())
}
