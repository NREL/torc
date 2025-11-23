# Resource Monitoring

Torc provides built-in resource monitoring to track CPU and memory usage of your
workflow jobs. This feature helps you understand resource consumption patterns,
optimize job resource requirements, and debug performance issues.

## Overview

Resource monitoring automatically tracks:
- **CPU usage**: Percentage of CPU utilization across all processes
- **Memory usage**: Total memory consumption in bytes/GB
- **Process count**: Number of processes spawned by each job

The monitoring system uses a single background thread that tracks all running
jobs, collecting samples at regular intervals. It automatically monitors process
trees, so child processes spawned by your jobs are included in the metrics.

## Default Behavior

**Resource monitoring is enabled by default** for all workflows created from
specification files. When you create a workflow without explicitly configuring
resource monitoring, Torc automatically enables it with these settings:

- **Granularity**: `summary` (stores peak and average metrics)
- **Sample interval**: 5 seconds
- **Plots**: Disabled

## Granularity Modes

Torc offers two granularity levels for resource monitoring:

### Summary Mode (Default)

Records only summary statistics for each job:
- Peak CPU percentage
- Average CPU percentage
- Peak memory usage
- Average memory usage

**When to use**: For most workflows where you want lightweight monitoring with
minimal storage overhead.

**Storage**: Minimal - only 4 metrics per job stored in the main database.

### Time Series Mode

Records detailed resource samples at regular intervals throughout job execution, storing:
- CPU percentage at each sample point
- Memory usage at each sample point
- Process count at each sample point
- Timestamp for each sample
- Job metadata (job ID, job name)

**When to use**: When you need to analyze resource usage patterns over time,
identify bottlenecks, or generate detailed visualizations.

**Storage**: Creates a separate SQLite database in
`<output_dir>/resource_utilization/resource_metrics_<hostname>_<workflow_id>_<run_id>.db`

## Configuration

### Enabling in Workflow Specifications

Add a `resource_monitor` section to your workflow spec file:

```yaml
name: "My Workflow"
user: "username"

resource_monitor:
  enabled: true
  granularity: "time_series"  # or "summary"
  sample_interval_seconds: 2
  generate_plots: false

jobs:
  - name: "my_job"
    command: "python train.py"
    # ... job configuration
```

**Configuration options**:

- `enabled` (boolean): Enable/disable monitoring
- `granularity` (string): `"summary"` or `"time_series"`
- `sample_interval_seconds` (integer): How often to sample resources (in seconds)
- `generate_plots` (boolean): Reserved for future use

### Disabling Default Monitoring

If you want to create a workflow without resource monitoring, use the `--no-resource-monitoring` flag:

```bash
torc workflows create-from-spec my_workflow.yaml --no-resource-monitoring
```

## Viewing Resource Metrics

### Summary Mode Results

For workflows using summary mode, resource metrics are stored in the results table. View them with:

```bash
torc results list <workflow_id>
```

The output includes columns for:
- `Peak CPU %`
- `Avg CPU %`
- `Peak Mem (GB)`
- `Avg Mem (GB)`

### Time Series Data

For workflows using time series mode, metrics are stored in a SQLite database. You can:

1. **Query directly**:
   ```bash
   sqlite3 -table output/resource_utilization/resource_metrics_1_1.db
   ```

   Example query:
   ```sql
   SELECT job_id, timestamp, cpu_percent, memory_bytes, num_processes
   FROM job_resource_samples
   WHERE job_id = 1
   ORDER BY timestamp;
   ```

2. **View job metadata**:
   ```sql
   SELECT * FROM job_metadata;
   ```

## Analyzing Resource Utilization

Torc provides the `reports check-resource-utilization` command to automatically
identify jobs that exceeded their specified resource requirements. This helps
you:

- **Detect over-allocation**: Find jobs that need more resources than specified (risk of failures)
- **Detect under-utilization**: Find jobs that could use smaller resource requirements (cost optimization)
- **Validate specifications**: Verify that your resource requirements match actual usage

### Basic Usage

```bash
# Check resource utilization for a workflow (latest run)
torc reports check-resource-utilization <workflow_id>

# Check a specific run
torc reports check-resource-utilization <workflow_id> --run-id <run_id>

# Show all jobs (including those within limits)
torc reports check-resource-utilization <workflow_id> --all

# Output as JSON for programmatic analysis
torc --format json reports check-resource-utilization <workflow_id>
```

### What Gets Checked

The command compares actual peak usage against specified requirements for:

1. **Memory**: Peak memory usage vs. specified memory
2. **CPU**: Peak CPU utilization vs. allocated CPU cores
3. **Runtime**: Actual execution time vs. specified runtime limit

### Example Output

**Default (violations only)**:

```
⚠ Found 3 resource over-utilization violations:

Job ID | Job Name         | Resource | Specified | Peak Used | Over-Utilization
-------|------------------|----------|-----------|-----------|------------------
15     | train_model      | Memory   | 8.00 GB   | 10.50 GB  | +31.3%
15     | train_model      | Runtime  | 2h 0m 0s  | 2h 45m 0s | +37.5%
16     | large_preprocess | CPU      | 800% (8 cores) | 950.5%    | +18.8%

Note: Use --all to see all jobs, including those that stayed within limits
```

**With --all flag**:

```
Job ID | Job Name    | Resource | Specified | Peak Used | Over-Utilization
-------|-------------|----------|-----------|-----------|------------------
15     | train_model | Memory   | 8.00 GB   | 10.50 GB  | +31.3%
15     | train_model | Runtime  | 2h 0m 0s  | 2h 45m 0s | +37.5%
15     | train_model | CPU      | 800% (8 cores) | 720.3%    | -9.9%
16     | preprocess  | Memory   | 4.00 GB   | 2.10 GB   | -47.5%
16     | preprocess  | CPU      | 400% (4 cores) | 380.2%    | -5.0%
16     | preprocess  | Runtime  | 10m 0s    | 7m 30s    | -25.0%
```

### Interpreting Results

**Over-utilization (positive percentages)**:

These are **critical issues** that need attention:

- **Memory over-utilization**: Job used more memory than specified
  - **Risk**: Out-of-memory errors, job failures, system instability
  - **Action**: Increase memory in resource requirements
  - **Example**: If a job specified 8 GB but used 10.5 GB (+31%), increase to at least 12 GB

- **Runtime over-utilization**: Job ran longer than time limit
  - **Risk**: Job may be killed by scheduler on next run
  - **Action**: Increase runtime limit
  - **Example**: If a job specified 2h but took 2h 45m (+37%), increase to at least 3h

- **CPU over-utilization**: Job used more CPU than allocated cores
  - **Risk**: CPU throttling, poor performance, unfair resource sharing
  - **Action**: Increase CPU allocation
  - **Example**: If a job allocated 8 cores (800%) but used 950% (+19%), increase to 10-12 cores

**Under-utilization (negative percentages)**:

These represent **optimization opportunities**:

- **Memory under-utilization**: Job used significantly less memory than allocated
  - **Benefit**: Reduce memory requests to allow more jobs to run concurrently
  - **Action**: Consider reducing memory if consistently under-utilized
  - **Example**: If a job allocated 4 GB but only used 2.1 GB (-47%), consider reducing to 2.5-3 GB

- **CPU under-utilization**: Job didn't use all allocated cores
  - **Possible causes**: I/O-bound workload, serial code, inefficient parallelization
  - **Action**: Reduce CPU allocation or optimize code for better parallelism

- **Runtime under-utilization**: Job finished much faster than time limit
  - **Benefit**: More accurate scheduling, faster queue times
  - **Action**: Reduce runtime limit to be more accurate
  - **Note**: Some buffer is normal (10-20% under-utilization is fine)

### When to Use This Command

**Use `check-resource-utilization` when**:

1. **After initial workflow runs**: Validate that resource specifications are appropriate
2. **Troubleshooting failures**: Identify if jobs are running out of resources
3. **Optimizing costs**: Find opportunities to reduce resource requests
4. **Regular audits**: Periodically check that specs still match actual usage as code evolves
5. **Before production**: Ensure resource requirements are correct before scaling up

**Use raw `results list` when**:

1. **Checking individual jobs**: You want to see specific job metrics
2. **Comparing runs**: Looking at how results change across different workflow runs
3. **Debugging**: Investigating return codes, completion times, or specific failures

### Integration with Resource Requirements

After identifying over-utilized jobs, update your workflow specification:

```yaml
# Before (from initial guess)
jobs:
  - name: train_model
    command: python train.py
    resource_requirements: initial_guess

resource_requirements:
  - name: initial_guess
    num_cpus: 8
    memory: 8g        # ← Too low, job used 10.5 GB
    runtime: PT2H     # ← Too low, job took 2h 45m
```

```yaml
# After (adjusted based on check-resource-utilization report)
jobs:
  - name: train_model
    command: python train.py
    resource_requirements: optimized

resource_requirements:
  - name: optimized
    num_cpus: 8
    memory: 12g       # ← Increased to 12 GB (10.5 GB + 15% buffer)
    runtime: PT3H     # ← Increased to 3 hours (2h 45m + buffer)
```

### Best Practices

1. **Allow some buffer**: Don't set requirements exactly at peak usage
   - Memory: Add 10-20% buffer above peak
   - Runtime: Add 15-30% buffer above average completion time
   - CPU: Round up to next core count

2. **Check multiple runs**: Resource usage can vary between runs
   - Run workflow 2-3 times before finalizing requirements
   - Use `--run-id` to check specific runs
   - Look for patterns across runs

3. **Focus on violations first**: Use default mode (violations only) to find critical issues
   - Fix over-utilization issues immediately (risk of failures)
   - Address under-utilization during optimization phases

4. **Use --all for optimization**: When optimizing costs, use `--all` to see full picture
   - Identify jobs with consistent under-utilization
   - Don't over-optimize (some headroom is good)

5. **Combine with plots**: For jobs with violations, generate time series plots to understand behavior
   ```bash
   # First, identify violations
   torc reports check-resource-utilization <workflow_id>

   # Then, plot detailed metrics for problematic jobs
   torc-plot-resources output/resource_utilization/resource_metrics_*.db \
     --job-ids 15,16
   ```

### JSON Output Format

For automation and CI/CD integration, use JSON output:

```bash
torc --format json reports check-resource-utilization <workflow_id>
```

Example JSON output:

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

This format is useful for:
- Automated testing (fail build if violations found)
- Dashboard integration
- Historical tracking
- Reporting systems

## Generating Plots

Torc includes a standalone tool for generating interactive HTML visualizations from time series data:

```bash
torc-plot-resources <database_path> -o <output_dir>
```

### What Gets Generated

The tool creates several types of interactive Plotly visualizations:

1. **Individual job plots** (`resource_plot_job_<id>.html`):
   - CPU percentage over time
   - Memory usage (GB) over time
   - Process count over time
   - All on a single timeline with multiple Y-axes

2. **CPU overview** (`resource_plot_cpu_all_jobs.html`):
   - CPU usage comparison across all jobs
   - Useful for identifying CPU-intensive jobs

3. **Memory overview** (`resource_plot_memory_all_jobs.html`):
   - Memory usage comparison across all jobs
   - Helps identify memory-intensive jobs

4. **Summary dashboard** (`resource_plot_summary.html`):
   - Bar charts comparing peak vs. average metrics
   - Quick overview of all jobs

### Example Usage

```bash
# Generate plots from a resource monitoring database
torc-plot-resources output/resource_utilization/resource_metrics_1_1.db \
  -o output/plots

# Generate plots for specific jobs only
torc-plot-resources output/resource_utilization/resource_metrics_1_1.db \
  -o output/plots \
  --job-ids 1,3,5

# Use custom filename prefix
torc-plot-resources output/resource_utilization/resource_metrics_1_1.db \
  -o output/plots \
  --prefix my_experiment
```

The generated HTML files are self-contained and can be opened in any web browser. They include:
- Interactive hover tooltips showing exact values
- Zoom and pan capabilities
- Legend toggling to show/hide specific traces
- Export options (PNG, SVG, etc.)

## Process Tree Monitoring

One of the key features of Torc's resource monitoring is **automatic process tree tracking**. When a job spawns child processes (e.g., using multiprocessing in Python), the monitoring system automatically discovers and tracks all descendants.

**Example**: If your job spawns 4 worker processes, the monitoring will track:
- Parent process resources
- All 4 child process resources
- Combined totals in the metrics

This ensures accurate resource accounting for parallel and distributed workloads.

## Use Cases

### Optimizing Resource Requirements

Use monitoring data to right-size your job resource requests:

1. Run workflow with monitoring enabled
2. Use `torc reports check-resource-utilization <workflow_id>` to identify violations
3. Review peak and average metrics for specific jobs
4. Adjust `resource_requirements` in job specs:
   ```yaml
   resource_requirements:
     cpus: 4              # Based on peak CPU usage
     memory: "16g"        # Based on peak memory + buffer
     runtime: "PT30M"     # Based on observed duration
   ```

The `check-resource-utilization` command makes this process much faster by automatically highlighting jobs that need adjustment.

### Debugging Performance Issues

Time series data helps identify:
- **Memory leaks**: Steadily increasing memory usage over time
- **CPU bottlenecks**: Unexpectedly low CPU usage might indicate I/O waits
- **Startup overhead**: Time spent before actual computation begins
- **Process spawning patterns**: When and how many child processes are created

### Comparing Implementations

Run multiple implementations with monitoring to compare:
- Different algorithms (serial vs. parallel)
- Different parameter settings
- Different tools or libraries

The plot comparisons make differences immediately visible.

## Best Practices

1. **Start with defaults**: The automatic summary mode is sufficient for most workflows

2. **Use time series for optimization**: Switch to time series mode when you need to:
   - Debug performance problems
   - Optimize resource requirements
   - Understand job behavior over time

3. **Choose appropriate sample intervals**:
   - **Short jobs (<1 hour)**: Use 1-2 second intervals
   - **Medium jobs (<4 hours>)**: Use 5 second intervals (default)
   - **Long jobs (>4 hours)**: Use 10-30 second intervals

4. **Keep job names descriptive**: Job names appear in plots and make them much easier to interpret

5. **Clean up old databases**: Time series databases can accumulate. Consider archiving or removing old monitoring data periodically

6. **Use plots for communication**: The interactive HTML plots are great for sharing results with collaborators or including in reports

## Performance Impact

Resource monitoring is designed to have minimal performance impact:

- **Single thread**: All monitoring uses one background thread regardless of job count
- **Efficient sampling**: Uses native OS APIs (sysinfo crate) for fast metrics collection
- **Async design**: Monitoring doesn't block job execution
- **Minimal overhead**: Typically <1% CPU overhead even with 1-second sampling

The monitoring thread samples resources at configured intervals and immediately returns to waiting, ensuring it doesn't compete with your compute jobs.

## Troubleshooting

### No metrics recorded

**Possible causes**:
- Monitoring disabled with `--no-resource-monitoring`
- Job completed too quickly (before first sample)
- Process ID not available (job failed to start)

**Solution**: Check workflow config and ensure jobs run long enough for at least one sample.

### Database not created (time series mode)

**Possible causes**:
- Output directory not writable
- Monitoring disabled

**Solution**: Verify output directory permissions and monitoring configuration.

### Missing child processes in metrics

**Cause**: Extremely short-lived processes might be missed between samples.

**Solution**: Decrease `sample_interval_seconds` to catch short-lived processes.

## Example Workflow

Here's a complete example demonstrating resource monitoring:

```yaml
name: "ML Training Pipeline"
description: "Train models with resource monitoring"
user: "researcher"

resource_monitor:
  enabled: true
  granularity: "time_series"
  sample_interval_seconds: 2
  generate_plots: false

jobs:
  - name: "preprocess_data"
    command: "python preprocess.py --input data.csv --output processed.pkl"
    resource_requirements:
      cpus: 4
      memory: "8g"
      runtime: "PT10M"

  - name: "train_model"
    command: "python train.py --data processed.pkl --model model.pkl"
    blocked_by:
      - "preprocess_data"
    resource_requirements:
      cpus: 8
      memory: "32g"
      runtime: "PT2H"

  - name: "evaluate_model"
    command: "python evaluate.py --model model.pkl --output metrics.json"
    blocked_by:
      - "train_model"
    resource_requirements:
      cpus: 2
      memory: "4g"
      runtime: "PT5M"
```

After running this workflow:

```bash
# Create and run the workflow
torc workflows create-from-spec ml_pipeline.yaml
torc run-jobs <workflow_id>

# Check for resource over-utilization
torc reports check-resource-utilization <workflow_id>

# View detailed summary metrics
torc results list <workflow_id>

# Generate interactive plots for problematic jobs
torc-plot-resources output/resource_utilization/resource_metrics_*.db \
  -o plots/ml_pipeline
```

This workflow gives you:
- ✓ Automatic identification of resource requirement violations
- ✓ Summary metrics for all jobs
- ✓ Interactive time-series visualizations
- ✓ Complete visibility into resource usage across your entire pipeline!
