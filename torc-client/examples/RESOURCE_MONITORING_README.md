# Resource Monitoring Demo

This example demonstrates the resource monitoring feature in Torc, which tracks CPU and memory usage for all jobs in a workflow.

## Overview

The `resource_monitoring_demo.yaml` workflow creates 3 independent Python jobs that run for approximately 60 seconds each:

1. **cpu_heavy_job** - Computes prime numbers (CPU-intensive, minimal memory)
2. **memory_heavy_job** - Allocates and manipulates large data structures (memory-intensive)
3. **mixed_workload_job** - Alternates between CPU computation and memory allocation

All jobs use only Python standard library functions, so no additional dependencies are required.

## Resource Monitoring Configuration

The workflow enables resource monitoring with these settings:

```yaml
resource_monitor:
  enabled: true
  granularity: "time_series"        # Collect full time-series data
  sample_interval_seconds: 2         # Sample every 2 seconds
  generate_plots: false              # Plot generation not yet implemented
```

### Granularity Options

- **summary**: Collects only peak and average statistics (stored in result records)
- **time_series**: Collects full time-series data (stored in SQLite database) plus summary stats

## Running the Example

### 1. Start the Torc Server

```bash
# In the torc-server directory
cargo run --bin torc-server
```

### 2. Create the Workflow

```bash
# From the torc repo root
torc-client workflows create-from-spec torc-client/examples/resource_monitoring_demo.yaml
```

This will output a workflow ID (e.g., `1`).

### 3. Start the Workflow

```bash
# Replace <workflow_id> with the ID from step 2
torc-client workflows start <workflow_id>
```

### 4. Run the Job Runner

```bash
# Replace <workflow_id> with your workflow ID
torc-job-runner <workflow_id>
```

The job runner will:
- Execute all 3 jobs concurrently
- Monitor CPU and memory usage every 2 seconds
- Store metrics in a SQLite database in the output directory

## Viewing Results

### View Job Results with Resource Metrics

```bash
# List all results for the workflow
torc-client results list <workflow_id>
```

The output will include resource metrics for each job:
- `peak_memory_bytes`: Maximum memory usage (in bytes)
- `avg_memory_bytes`: Average memory usage (in bytes)
- `peak_cpu_percent`: Maximum CPU usage (can exceed 100% for multi-core)
- `avg_cpu_percent`: Average CPU usage

### View Time-Series Data

When using `granularity: "time_series"`, detailed monitoring data is stored in:
```
output/resource_utilization/resource_metrics_<hostname>_<workflow_id>_<run_id>.db
```

You can query this database to see the time-series data:

```bash
sqlite3 -table output/resource_utilization/resource_metrics_*.db "SELECT * FROM job_resource_samples LIMIT 10"
```

The table schema:
```sql
CREATE TABLE job_resource_samples (
    job_id INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,      -- Unix timestamp
    cpu_percent REAL NOT NULL,       -- CPU usage percentage
    memory_bytes INTEGER NOT NULL,   -- Memory usage in bytes
    num_processes INTEGER NOT NULL,  -- Number of processes (includes children)
    PRIMARY KEY (job_id, timestamp)
);
```

## Expected Resource Usage

Based on the job implementations:

- **cpu_heavy_job**: High CPU (50-100%), low memory (~50-100 MB)
- **memory_heavy_job**: Moderate CPU (10-30%), high memory (~80-150 MB)
- **mixed_workload_job**: Variable CPU (20-60%), moderate memory (~80-100 MB)

Actual values will depend on your system's performance.

## Notes

- All jobs use Python 3's standard library only
- Jobs are designed to run for approximately 60 seconds
- The monitoring thread samples every 2 seconds, so you should see ~30 samples per job
- Child processes spawned by jobs are automatically tracked and included in the metrics
- The job runner creates a separate log file: `output/job_runner_<hostname>_<workflow_id>_<run_id>.log`

## Troubleshooting

**Jobs fail with "python3 not found"**:
- Make sure Python 3 is installed and in your PATH
- Or modify the workflow to use `python` instead of `python3`

**No resource metrics in results**:
- Verify that `resource_monitor.enabled` is `true` in the workflow spec
- Check the job runner logs for any monitoring errors
- Ensure the workflow was created with the resource_monitor config (recreate if needed)

**Time-series database not created**:
- Check that `granularity` is set to `"time_series"` (not `"summary"`)
- Verify the output directory exists and is writable
- Look for the database file: `output/resource_utilization/resource_metrics_*.db`
