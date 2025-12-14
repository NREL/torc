# Debugging Workflows

When workflows fail or produce unexpected results, Torc provides comprehensive
debugging tools to help you identify and resolve issues. The primary debugging
tools are:

- **`torc results list`**: Prints a table of return codes for each job execution (non-zero means failure)
- **`torc reports results`**: Generates a detailed JSON report containing job results and all associated log file paths
- **torc-dash Debug tab**: Interactive web interface for visual debugging with log file viewer

## Overview

Torc automatically captures return codes and multiple log files for each job execution:

- **Job stdout/stderr**: Output from your job commands
- **Job runner logs**: Internal logs from the Torc job runner
- **Slurm logs**: Additional logs when using Slurm scheduler (stdout/stderr from Slurm itself)

The `reports results` command consolidates all this information into a single
JSON report, making it easy to locate and examine relevant log files for
debugging.

## Quick Start

View the job return codes in a table:

```bash
torc results list <workflow_id>
```
```
Results for workflow ID 2:
╭────┬────────┬───────┬────────┬─────────────┬───────────┬──────────┬────────────┬──────────────────────────┬────────╮
│ ID │ Job ID │ WF ID │ Run ID │ Return Code │ Exec Time │ Peak Mem │ Peak CPU % │ Completion Time          │ Status │
├────┼────────┼───────┼────────┼─────────────┼───────────┼──────────┼────────────┼──────────────────────────┼────────┤
│ 4  │ 6      │ 2     │ 1      │ 1           │ 1.01      │ 73.8MB   │ 21.9%      │ 2025-11-13T13:35:43.289Z │ Done   │
│ 5  │ 4      │ 2     │ 1      │ 0           │ 1.01      │ 118.1MB  │ 301.3%     │ 2025-11-13T13:35:43.393Z │ Done   │
│ 6  │ 5      │ 2     │ 1      │ 0           │ 1.01      │ 413.6MB  │ 19.9%      │ 2025-11-13T13:35:43.499Z │ Done   │
╰────┴────────┴───────┴────────┴─────────────┴───────────┴──────────┴────────────┴──────────────────────────┴────────╯

Total: 3 results
```

View only failed jobs:

```bash
torc results list <workflow_id> --failed
```

```
Results for workflow ID 2:
╭────┬────────┬───────┬────────┬─────────────┬───────────┬──────────┬────────────┬──────────────────────────┬────────╮
│ ID │ Job ID │ WF ID │ Run ID │ Return Code │ Exec Time │ Peak Mem │ Peak CPU % │ Completion Time          │ Status │
├────┼────────┼───────┼────────┼─────────────┼───────────┼──────────┼────────────┼──────────────────────────┼────────┤
│ 4  │ 6      │ 2     │ 1      │ 1           │ 1.01      │ 73.8MB   │ 21.9%      │ 2025-11-13T13:35:43.289Z │ Done   │
╰────┴────────┴───────┴────────┴─────────────┴───────────┴──────────┴────────────┴──────────────────────────┴────────╯
```

Generate a debugging report for a workflow:

```bash
# Generate report for a specific workflow
torc reports results <workflow_id>

# Specify custom output directory (default: "output")
torc reports results <workflow_id> --output-dir /path/to/output

# Include all workflow runs (default: only latest run)
torc reports results <workflow_id> --all-runs

# Interactive workflow selection (if workflow_id omitted)
torc reports results
```

The command outputs a comprehensive JSON report to stdout. Redirect it to a file for easier analysis:

```bash
torc reports results <workflow_id> > debug_report.json
```

## Report Structure

### Top-Level Fields

The JSON report includes workflow-level information:

```json
{
  "workflow_id": 123,
  "workflow_name": "my_pipeline",
  "workflow_user": "researcher",
  "all_runs": false,
  "total_results": 5,
  "results": [...]
}
```

**Fields**:
- `workflow_id`: Unique identifier for the workflow
- `workflow_name`: Human-readable workflow name
- `workflow_user`: Owner of the workflow
- `all_runs`: Whether report includes all historical runs or just the latest
- `total_results`: Number of job results in the report
- `results`: Array of individual job result records

### Job Result Records

Each entry in the `results` array contains detailed information about a single job execution:

```json
{
  "job_id": 456,
  "job_name": "preprocess_data",
  "status": "Done",
  "run_id": 1,
  "return_code": 0,
  "completion_time": "2024-01-15T14:30:00.000Z",
  "exec_time_minutes": 5.2,
  "compute_node_id": 789,
  "compute_node_type": "local",
  "job_stdout": "output/job_stdio/job_456.o",
  "job_stderr": "output/job_stdio/job_456.e",
  "job_runner_log": "output/job_runner_hostname_123_1.log"
}
```

**Core Fields**:
- `job_id`: Unique identifier for the job
- `job_name`: Human-readable job name from workflow spec
- `status`: Job status (Done, Terminated, Failed, etc.)
- `run_id`: Workflow run number (increments on reinitialization)
- `return_code`: Exit code from job command (0 = success)
- `completion_time`: ISO 8601 timestamp when job completed
- `exec_time_minutes`: Duration of job execution in minutes

**Compute Node Fields**:
- `compute_node_id`: ID of the compute node that executed the job
- `compute_node_type`: Type of compute node ("local" or "slurm")

## Log File Paths

The report includes paths to all log files associated with each job. The specific files depend on the compute node type.

### Local Runner Log Files

For jobs executed by the local job runner (`compute_node_type: "local"`):

```json
{
  "job_stdout": "output/job_stdio/job_456.o",
  "job_stderr": "output/job_stdio/job_456.e",
  "job_runner_log": "output/job_runner_hostname_123_1.log"
}
```

**Log File Descriptions**:

1. **job_stdout** (`output/job_stdio/job_<workflow_id>_<job_id>_<run_id>.o`):
   - Standard output from your job command
   - Contains print statements, normal program output
   - **Use for**: Checking expected output, debugging logic errors

2. **job_stderr** (`output/job_stdio/job_<workflow_id>_<job_id>_<run_id>.e`):
   - Standard error from your job command
   - Contains error messages, warnings, stack traces
   - **Use for**: Investigating crashes, exceptions, error messages

3. **job_runner_log** (`output/job_runner_<hostname>_<workflow_id>_<run_id>.log`):
   - Internal Torc job runner logging
   - Shows job lifecycle events, resource monitoring, process management
   - **Use for**: Understanding Torc's job execution behavior, timing issues

**Log path format conventions**:
- Job stdio logs use job ID in filename
- Runner logs use hostname, workflow ID, and run ID
- All paths are relative to the specified `--output-dir`

### Slurm Runner Log Files

For jobs executed via Slurm scheduler (`compute_node_type: "slurm"`):

```json
{
  "job_stdout": "output/job_stdio/job_456.o",
  "job_stderr": "output/job_stdio/job_456.e",
  "job_runner_log": "output/job_runner_slurm_12345_node01_67890.log",
  "slurm_stdout": "output/slurm_output_12345.o",
  "slurm_stderr": "output/slurm_output_12345.e",
  "slurm_env_log": "output/slurm_env_12345_node01_67890.log",
  "dmesg_log": "output/dmesg_slurm_12345_node01_67890.log"
}
```

In addition to the standard job logs, Slurm jobs include additional log files:

4. **slurm_stdout** (`output/slurm_output_<slurm_job_id>.o`):
   - Standard output from Slurm's perspective
   - Includes Slurm environment setup, job allocation info
   - **Use for**: Debugging Slurm job submission issues

5. **slurm_stderr** (`output/slurm_output_<slurm_job_id>.e`):
   - Standard error from Slurm's perspective
   - Contains Slurm-specific errors (allocation failures, node issues)
   - **Use for**: Investigating Slurm scheduler problems

6. **slurm_env_log** (`output/slurm_env_<slurm_job_id>_<node_id>_<task_pid>.log`):
   - All SLURM environment variables captured at job runner startup
   - Contains job allocation details, resource limits, node assignments
   - **Use for**: Verifying Slurm job configuration, debugging resource allocation issues

7. **dmesg log** (`output/dmesg_slurm_<slurm_job_id>_<node_id>_<task_pid>.log`):
   - Kernel message buffer captured when the Slurm job runner exits
   - Contains system-level events: OOM killer activity, hardware errors, kernel panics
   - **Use for**: Investigating job failures caused by system-level issues (e.g., out-of-memory kills, hardware failures)

**Note**: Slurm job runner logs include the Slurm job ID, node ID, and task PID
in the filename for correlation with Slurm's own logs.

## Using the torc-dash Debugging Tab

The torc-dash web interface provides an interactive Debugging tab for visual debugging of workflow jobs. This is often the quickest way to investigate failed jobs without using command-line tools.

### Accessing the Debugging Tab

1. Start torc-dash (standalone mode recommended for quick setup):
   ```bash
   torc-dash --standalone
   ```

2. Open your browser to `http://localhost:8090`

3. Select a workflow from the dropdown in the sidebar

4. Click the **Debugging** tab in the navigation

### Features

#### Job Results Report

The Debug tab provides a report generator with the following options:

- **Output Directory**: Specify where job logs are stored (default: `output`). This must match the directory used during workflow execution.

- **Include all runs**: Check this to see results from all workflow runs, not just the latest. Useful for comparing job behavior across reinitializations.

- **Show only failed jobs**: Filter to display only jobs with non-zero return codes. This is checked by default to help you focus on problematic jobs.

Click **Generate Report** to fetch job results from the server.

#### Job Results Table

After generating a report, the Debug tab displays an interactive table showing:

- **Job ID**: Unique identifier for the job
- **Job Name**: Human-readable name from the workflow spec
- **Status**: Job completion status (Done, Terminated, etc.)
- **Return Code**: Exit code (0 = success, non-zero = failure)
- **Execution Time**: Duration in minutes
- **Run ID**: Which workflow run the result is from

Click any row to select a job and view its log files.

#### Log File Viewer

When you select a job from the table, the Log File Viewer displays:

- **stdout tab**: Standard output from the job command
  - Shows print statements and normal program output
  - Useful for checking expected behavior and debugging logic

- **stderr tab**: Standard error from the job command
  - Shows error messages, warnings, and stack traces
  - Primary location for investigating crashes and exceptions

Each tab includes:
- **Copy Path** button: Copy the full file path to clipboard
- **File path display**: Shows where the log file is located
- **Scrollable content viewer**: Dark-themed viewer for easy reading

### Quick Debugging Workflow with torc-dash

1. Open torc-dash and select your workflow from the sidebar
2. Go to the **Debugging** tab
3. Ensure "Show only failed jobs" is checked
4. Click **Generate Report**
5. Click on a failed job in the results table
6. Review the **stderr** tab for error messages
7. Check the **stdout** tab for context about what the job was doing

### When to Use torc-dash vs CLI

**Use torc-dash Debugging tab when:**
- You want a visual, interactive debugging experience
- You need to quickly scan multiple failed jobs
- You're investigating jobs and want to easily switch between stdout/stderr
- You prefer not to construct `jq` queries manually

**Use CLI tools (`torc reports results`) when:**
- You need to automate failure detection in CI/CD
- You want to save reports for archival or version control
- You're working on a remote server without browser access
- You need to process results programmatically

## Common Debugging Workflows

### Investigating Failed Jobs

When a job fails, follow these steps:

1. **Generate the debug report**:
   ```bash
   torc reports results <workflow_id> > debug_report.json
   ```

2. **Find the failed job** using `jq` or similar tool:
   ```bash
   # Find jobs with non-zero return codes
   jq '.results[] | select(.return_code != 0)' debug_report.json

   # Find jobs with specific status
   jq '.results[] | select(.status == "Done")' debug_report.json
   ```

3. **Check the job's stderr** for error messages:
   ```bash
   # Extract stderr path for a specific job
   STDERR_PATH=$(jq -r '.results[] | select(.job_name == "my_failing_job") | .job_stderr' debug_report.json)

   # View the error output
   cat "$STDERR_PATH"
   ```

4. **Review job stdout** for context:
   ```bash
   STDOUT_PATH=$(jq -r '.results[] | select(.job_name == "my_failing_job") | .job_stdout' debug_report.json)
   cat "$STDOUT_PATH"
   ```

5. **Check runner logs** for execution issues:
   ```bash
   LOG_PATH=$(jq -r '.results[] | select(.job_name == "my_failing_job") | .job_runner_log' debug_report.json)
   cat "$LOG_PATH"
   ```

### Example: Complete Debugging Session

```bash
# 1. Generate report
torc reports results 123 > report.json

# 2. Check overall success/failure counts
echo "Total jobs: $(jq '.total_results' report.json)"
echo "Failed jobs: $(jq '[.results[] | select(.return_code != 0)] | length' report.json)"

# 3. List all failed jobs with their names
jq -r '.results[] | select(.return_code != 0) | "\(.job_id): \(.job_name) (exit code: \(.return_code))"' report.json

# Output:
# 456: process_batch_2 (exit code: 1)
# 789: validate_results (exit code: 2)

# 4. Examine stderr for first failure
jq -r '.results[] | select(.job_id == 456) | .job_stderr' report.json | xargs cat

# Output might show:
# FileNotFoundError: [Errno 2] No such file or directory: 'input/batch_2.csv'

# 5. Check if job dependencies completed successfully
# (The missing file might be an output from a previous job)
jq -r '.results[] | select(.job_name == "generate_batch_2") | "\(.status) (exit code: \(.return_code))"' report.json
```

### Debugging Across Multiple Runs

When a workflow has been reinitialized multiple times, compare runs to identify regressions:

```bash
# Generate report with all historical runs
torc reports results <workflow_id> --all-runs > full_history.json

# Compare return codes across runs for a specific job
jq -r '.results[] | select(.job_name == "flaky_job") | "Run \(.run_id): exit code \(.return_code)"' full_history.json

# Output:
# Run 1: exit code 0
# Run 2: exit code 1
# Run 3: exit code 0
# Run 4: exit code 1

# Extract stderr paths for failed runs
jq -r '.results[] | select(.job_name == "flaky_job" and .return_code != 0) | "Run \(.run_id): \(.job_stderr)"' full_history.json
```

### Log File Missing Warnings

The `reports results` command automatically checks for log file existence and prints warnings to stderr if files are missing:

```
Warning: job stdout log file does not exist for job 456: output/job_stdio/job_456.o
Warning: job runner log file does not exist for job 456: output/job_runner_host1_123_1.log
```

**Common causes of missing log files**:

1. **Wrong output directory**: Ensure `--output-dir` matches the directory used during workflow execution
2. **Logs not yet written**: Job may still be running or failed to start
3. **Logs cleaned up**: Files may have been manually deleted
4. **Path mismatch**: Output directory moved or renamed after execution

**Solution**: Verify the output directory and ensure it matches what was passed to `torc run` or `torc slurm schedule-nodes`.


## Output Directory Management

The `--output-dir` parameter must match the directory used during workflow execution:

### Local Runner

```bash
# Execute workflow with specific output directory
torc run <workflow_id> /path/to/my_output

# Generate report using the same directory
torc reports results <workflow_id> --output-dir /path/to/my_output
```

### Slurm Scheduler

```bash
# Submit jobs to Slurm with output directory
torc slurm schedule-nodes <workflow_id> --output-dir /path/to/my_output

# Generate report using the same directory
torc reports results <workflow_id> --output-dir /path/to/my_output
```

**Default behavior**: If `--output-dir` is not specified, both the runner and reports command default to `./output`.

## Best Practices

1. **Generate reports after each run**: Create a debug report immediately after workflow execution for easier troubleshooting

2. **Archive reports with logs**: Store the JSON report alongside log files for future reference
   ```bash
   torc reports results "$WF_ID" > "output/report_${WF_ID}_$(date +%Y%m%d_%H%M%S).json"
   ```

3. **Use version control**: Commit debug reports for important workflow runs to track changes over time

4. **Automate failure detection**: Use the report in CI/CD pipelines to automatically detect and report failures

5. **Check warnings**: Pay attention to warnings about missing log files - they often indicate configuration issues

6. **Combine with resource monitoring**: Use `reports results` for log files and `reports check-resource-utilization` for performance issues
   ```bash
   # Check if job failed due to resource constraints
   torc reports check-resource-utilization "$WF_ID"
   torc reports results "$WF_ID" > report.json
   ```

7. **Filter large reports**: For workflows with many jobs, filter the report to focus on relevant jobs
   ```bash
   # Only include failed jobs in filtered report
   jq '{workflow_id, workflow_name, results: [.results[] | select(.return_code != 0)]}' report.json
   ```

## Troubleshooting Common Issues

### "Output directory does not exist" Error

**Cause**: The specified `--output-dir` path doesn't exist.

**Solution**: Verify the directory exists and the path is correct:
```bash
ls -ld output/  # Check if directory exists
torc reports results <workflow_id> --output-dir "$(pwd)/output"
```

### Empty Results Array

**Cause**: No job results exist for the workflow (jobs not yet executed or initialized).

**Solution**: Check workflow status and ensure jobs have been completed:
```bash
torc workflows status <workflow_id>
torc results list <workflow_id>  # Verify results exist
```

### All Log Paths Show Warnings

**Cause**: Output directory mismatch between execution and report generation.

**Solution**: Verify the output directory used during execution:
```bash
# Check where logs actually are
find . -name "job_*.o" -o -name "job_runner_*.log"

# Use correct output directory in report
torc reports results <workflow_id> --output-dir <correct_path>
```

## Slurm-Specific Debugging Tools

When running workflows on Slurm clusters, Torc provides additional debugging tools specifically designed for Slurm environments.

### Parsing Slurm Log Files for Errors

The `torc slurm parse-logs` command scans Slurm stdout/stderr log files for known error patterns and correlates them with affected Torc jobs:

```bash
# Parse logs for a specific workflow
torc slurm parse-logs <workflow_id>

# Specify custom output directory
torc slurm parse-logs <workflow_id> --output-dir /path/to/output

# Output as JSON for programmatic processing
torc slurm parse-logs <workflow_id> --format json
```

The command detects common Slurm failure patterns including:

**Memory Errors:**
- `out of memory`, `oom-kill`, `cannot allocate memory`
- `memory cgroup out of memory`, `Exceeded job memory limit`
- `task/cgroup: .*: Killed`
- `std::bad_alloc` (C++), `MemoryError` (Python)

**Slurm-Specific Errors:**
- `slurmstepd: error:`, `srun: error:`
- `DUE TO TIME LIMIT`, `DUE TO PREEMPTION`
- `NODE_FAIL`, `FAILED`, `CANCELLED`
- `Exceeded.*step.*limit`

**GPU/CUDA Errors:**
- `CUDA out of memory`, `CUDA error`, `GPU memory.*exceeded`

**Signal/Crash Errors:**
- `Segmentation fault`, `SIGSEGV`
- `Bus error`, `SIGBUS`
- `killed by signal`, `core dumped`

**Python Errors:**
- `Traceback (most recent call last)`
- `ModuleNotFoundError`, `ImportError`

**File System Errors:**
- `No space left on device`, `Disk quota exceeded`
- `Read-only file system`, `Permission denied`

**Network Errors:**
- `Connection refused`, `Connection timed out`, `Network is unreachable`

**Example output (table format):**

```
Slurm Log Analysis Results
==========================

Found 2 error(s) in log files:

╭─────────────────────────────┬──────────────┬──────┬─────────────────────────────┬──────────┬──────────────────────────────╮
│ File                        │ Slurm Job ID │ Line │ Pattern                     │ Severity │ Affected Torc Jobs           │
├─────────────────────────────┼──────────────┼──────┼─────────────────────────────┼──────────┼──────────────────────────────┤
│ slurm_output_12345.e        │ 12345        │ 42   │ Out of Memory (OOM) Kill    │ critical │ process_data (ID: 456)       │
│ slurm_output_12346.e        │ 12346        │ 15   │ CUDA out of memory          │ error    │ train_model (ID: 789)        │
╰─────────────────────────────┴──────────────┴──────┴─────────────────────────────┴──────────┴──────────────────────────────╯
```

### Viewing Slurm Accounting Data

The `torc slurm sacct` command displays a summary of Slurm job accounting data for all scheduled compute nodes in a workflow:

```bash
# Display sacct summary table for a workflow
torc slurm sacct <workflow_id>

# Also save full JSON files for detailed analysis
torc slurm sacct <workflow_id> --save-json --output-dir /path/to/output

# Output as JSON for programmatic processing
torc slurm sacct <workflow_id> --format json
```

The command displays a summary table with key metrics:
- **Slurm Job**: The Slurm job ID
- **Job Step**: Name of the job step (e.g., "worker_1", "batch")
- **State**: Job state (COMPLETED, FAILED, TIMEOUT, OUT_OF_MEMORY, etc.)
- **Exit Code**: Exit code of the job step
- **Elapsed**: Wall clock time for the job step
- **Max RSS**: Maximum resident set size (memory usage)
- **CPU Time**: Total CPU time consumed
- **Nodes**: Compute nodes used

**Example output:**

```
Slurm Accounting Summary for Workflow 123

╭────────────┬───────────┬───────────┬───────────┬─────────┬─────────┬──────────┬─────────╮
│ Slurm Job  │ Job Step  │ State     │ Exit Code │ Elapsed │ Max RSS │ CPU Time │ Nodes   │
├────────────┼───────────┼───────────┼───────────┼─────────┼─────────┼──────────┼─────────┤
│ 12345      │ worker_1  │ COMPLETED │ 0         │ 2h 15m  │ 4.5GB   │ 4h 30m   │ node01  │
│ 12345      │ batch     │ COMPLETED │ 0         │ 2h 16m  │ 128.0MB │ 1m 30s   │ node01  │
│ 12346      │ worker_1  │ FAILED    │ 1         │ 45m 30s │ 8.2GB   │ 1h 30m   │ node02  │
╰────────────┴───────────┴───────────┴───────────┴─────────┴─────────┴──────────┴─────────╯

Total: 3 job steps
```

Use `--save-json` to also save full sacct JSON output to files for detailed analysis:
```bash
torc slurm sacct 123 --save-json --output-dir output
# Creates: output/sacct_12345.json, output/sacct_12346.json, etc.
```

### Viewing Slurm Logs in torc-dash

The torc-dash web interface provides two ways to view Slurm logs:

#### Debugging Tab - Slurm Log Analysis

The Debugging tab includes a "Slurm Log Analysis" section:

1. Navigate to the **Debugging** tab
2. Find the **Slurm Log Analysis** section
3. Enter the output directory path (default: `output`)
4. Click **Analyze Slurm Logs**

The results show all detected errors with their Slurm job IDs, line numbers, error patterns, severity levels, and affected Torc jobs.

#### Debugging Tab - Slurm Accounting Data

The Debugging tab also includes a "Slurm Accounting Data" section:

1. Navigate to the **Debugging** tab
2. Find the **Slurm Accounting Data** section
3. Click **Collect sacct Data**

This displays a summary table showing job state, exit codes, elapsed time, memory usage (Max RSS), CPU time, and nodes for all Slurm job steps. The table helps quickly identify failed jobs and resource usage patterns.

#### Scheduled Nodes Tab - View Slurm Logs

You can view individual Slurm job logs directly from the Details view:

1. Select a workflow
2. Go to the **Details** tab
3. Switch to the **Scheduled Nodes** sub-tab
4. Find a Slurm scheduled node in the table
5. Click the **View Logs** button in the Logs column

This opens a modal with tabs for viewing the Slurm job's stdout and stderr files.

### Viewing Slurm Logs in the TUI

The `torc tui` terminal interface also supports Slurm log viewing:

1. Launch the TUI: `torc tui`
2. Select a workflow and press Enter to load details
3. Press Tab to switch to the **Scheduled Nodes** tab
4. Navigate to a Slurm scheduled node using arrow keys
5. Press `l` to view the Slurm job's logs

The log viewer shows:
- **stdout tab**: Slurm job standard output (`slurm_output_<id>.o`)
- **stderr tab**: Slurm job standard error (`slurm_output_<id>.e`)

Use Tab to switch between stdout/stderr, arrow keys to scroll, `/` to search, and `q` to close.

### Debugging Slurm Job Failures

When a Slurm job fails, follow this debugging workflow:

1. **Parse logs for known errors:**
   ```bash
   torc slurm parse-logs <workflow_id>
   ```

2. **If OOM or resource issues are detected, collect sacct data:**
   ```bash
   torc slurm sacct <workflow_id>
   cat output/sacct_<slurm_job_id>.json | jq '.jobs[].steps[].tres.requested'
   ```

3. **View the specific Slurm log files:**
   - Use torc-dash: Details → Scheduled Nodes → View Logs
   - Or use TUI: Scheduled Nodes tab → press `l`
   - Or directly: `cat output/slurm_output_<slurm_job_id>.e`

4. **Check the job's own stderr for application errors:**
   ```bash
   torc reports results <workflow_id> > report.json
   jq -r '.results[] | select(.return_code != 0) | .job_stderr' report.json | xargs cat
   ```

5. **Review dmesg logs for system-level issues:**
   ```bash
   cat output/dmesg_slurm_<slurm_job_id>_*.log
   ```

## Related Commands

- **`torc results list`**: View summary of job results in table format
- **`torc workflows status`**: Check overall workflow status
- **`torc reports check-resource-utilization`**: Analyze resource usage and find over-utilized jobs
- **`torc jobs list`**: View all jobs and their current status
- **`torc slurm parse-logs`**: Parse Slurm logs for known error patterns
- **`torc slurm sacct`**: Collect Slurm accounting data for workflow jobs
- **`torc-dash`**: Launch web interface with interactive Debugging tab
- **`torc tui`**: Launch terminal UI with Slurm log viewing

The `reports results` command and torc-dash Debugging tab complement these by providing complete log file paths and content viewing for in-depth debugging when high-level views aren't sufficient.
