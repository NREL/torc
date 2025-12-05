# Resource Monitoring Reference

Technical reference for Torc's resource monitoring system.

## Configuration Options

The `resource_monitor` section in workflow specifications accepts the following fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable or disable monitoring |
| `granularity` | string | `"summary"` | `"summary"` or `"time_series"` |
| `sample_interval_seconds` | integer | `5` | Seconds between resource samples |
| `generate_plots` | boolean | `false` | Reserved for future use |

### Granularity Modes

**Summary mode** (`"summary"`):
- Stores only peak and average values per job
- Metrics stored in the main database results table
- Minimal storage overhead

**Time series mode** (`"time_series"`):
- Stores samples at regular intervals
- Creates separate SQLite database per workflow run
- Database location: `<output_dir>/resource_utilization/resource_metrics_<hostname>_<workflow_id>_<run_id>.db`

### Sample Interval Guidelines

| Job Duration | Recommended Interval |
|--------------|---------------------|
| < 1 hour | 1-2 seconds |
| 1-4 hours | 5 seconds (default) |
| > 4 hours | 10-30 seconds |

## Time Series Database Schema

### `job_resource_samples` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `job_id` | INTEGER | Torc job ID |
| `timestamp` | REAL | Unix timestamp |
| `cpu_percent` | REAL | CPU utilization percentage |
| `memory_bytes` | INTEGER | Memory usage in bytes |
| `num_processes` | INTEGER | Process count including children |

### `job_metadata` Table

| Column | Type | Description |
|--------|------|-------------|
| `job_id` | INTEGER | Primary key, Torc job ID |
| `job_name` | TEXT | Human-readable job name |

## Summary Metrics in Results

When using summary mode, the following fields are added to job results:

| Field | Type | Description |
|-------|------|-------------|
| `peak_cpu_percent` | float | Maximum CPU percentage observed |
| `avg_cpu_percent` | float | Average CPU percentage |
| `peak_memory_gb` | float | Maximum memory in GB |
| `avg_memory_gb` | float | Average memory in GB |

## check-resource-utilization JSON Output

When using `--format json`:

```json
{
  "workflow_id": 123,
  "run_id": null,
  "total_results": 10,
  "over_utilization_count": 3,
  "violations": [
    {
      "job_id": 15,
      "job_name": "train_model",
      "resource_type": "Memory",
      "specified": "8.00 GB",
      "peak_used": "10.50 GB",
      "over_utilization": "+31.3%"
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `workflow_id` | Workflow being analyzed |
| `run_id` | Specific run ID if provided, otherwise `null` for latest |
| `total_results` | Total number of completed jobs analyzed |
| `over_utilization_count` | Number of violations found |
| `violations` | Array of violation details |

### Violation Object

| Field | Description |
|-------|-------------|
| `job_id` | Job ID with violation |
| `job_name` | Human-readable job name |
| `resource_type` | `"Memory"`, `"CPU"`, or `"Runtime"` |
| `specified` | Resource requirement from workflow spec |
| `peak_used` | Actual peak usage observed |
| `over_utilization` | Percentage over/under specification |

## plot-resources Output Files

| File | Description |
|------|-------------|
| `resource_plot_job_<id>.html` | Per-job timeline with CPU, memory, process count |
| `resource_plot_cpu_all_jobs.html` | CPU comparison across all jobs |
| `resource_plot_memory_all_jobs.html` | Memory comparison across all jobs |
| `resource_plot_summary.html` | Bar chart dashboard of peak vs average |

All plots are self-contained HTML files using Plotly.js with:
- Interactive hover tooltips
- Zoom and pan controls
- Legend toggling
- Export options (PNG, SVG)

## Monitored Metrics

| Metric | Unit | Description |
|--------|------|-------------|
| CPU percentage | % | Total CPU utilization across all cores |
| Memory usage | bytes | Resident memory consumption |
| Process count | count | Number of processes in job's process tree |

### Process Tree Tracking

The monitoring system automatically tracks child processes spawned by jobs. When a job creates worker processes (e.g., Python multiprocessing), all descendants are included in the aggregated metrics.

## Performance Characteristics

- Single background monitoring thread regardless of job count
- Typical overhead: <1% CPU even with 1-second sampling
- Uses native OS APIs via the `sysinfo` crate
- Non-blocking async design
