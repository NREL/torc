# Web Dashboard (torc-dash)

The Torc Dashboard (`torc-dash`) provides a modern web-based interface for monitoring and managing
workflows, offering an intuitive alternative to the command-line interface.

## Overview

`torc-dash` is a Rust-based web application that allows you to:

- **Monitor workflows and jobs** with real-time status updates
- **Create and run workflows** by uploading specification files (YAML, JSON, JSON5, KDL)
- **Visualize workflow DAGs** with interactive dependency graphs
- **Debug failed jobs** with integrated log file viewer
- **Generate resource plots** from time series monitoring data
- **Manage torc-server** start/stop in standalone mode
- **View events** with automatic polling for updates

## Installation

### Building from Source

`torc-dash` is built as part of the Torc workspace:

```bash
# Build torc-dash
cargo build --release -p torc-dash

# Binary location
./target/release/torc-dash
```

### Prerequisites

- A running `torc-server` (or use `--standalone` mode to auto-start one)
- The `torc` CLI binary in your PATH (for workflow execution features)

## Running the Dashboard

### Quick Start (Standalone Mode)

The easiest way to get started is standalone mode, which automatically starts `torc-server`:

```bash
torc-dash --standalone
```

This will:

1. Start `torc-server` on an automatically-detected free port
2. Start the dashboard on http://127.0.0.1:8090
3. Configure the dashboard to connect to the managed server

### Connecting to an Existing Server

If you already have `torc-server` running:

```bash
# Use default API URL (http://localhost:8080/torc-service/v1)
torc-dash

# Specify custom API URL
torc-dash --api-url http://myserver:9000/torc-service/v1

# Or use environment variable
export TORC_API_URL="http://myserver:9000/torc-service/v1"
torc-dash
```

### Command-Line Options

```
Options:
  -p, --port <PORT>           Dashboard port [default: 8090]
      --host <HOST>           Dashboard host [default: 127.0.0.1]
  -a, --api-url <API_URL>     Torc server API URL [default: http://localhost:8080/torc-service/v1]
      --torc-bin <PATH>       Path to torc CLI binary [default: torc]
      --torc-server-bin       Path to torc-server binary [default: torc-server]
      --standalone            Auto-start torc-server alongside dashboard
      --server-port <PORT>    Server port in standalone mode (0 = auto-detect) [default: 0]
      --database <PATH>       Database path for standalone server
      --completion-check-interval-secs <SECS>  Server polling interval [default: 5]
```

## Features

### Workflows Tab

The main workflows view provides:

- **Workflow list** with ID, name, timestamp, user, and description
- **Create Workflow** button to upload new workflow specifications
- **Quick actions** for each workflow:
  - View details and DAG visualization
  - Initialize/reinitialize workflow
  - Run locally or submit to scheduler
  - Delete workflow

#### Creating Workflows

Click "Create Workflow" to open the creation dialog:

1. **Upload a file**: Drag and drop or click to select a workflow specification file
   - Supports YAML, JSON, JSON5, and KDL formats
2. **Or enter a file path**: Specify a path on the server filesystem
3. Click "Create" to register the workflow

### Details Tab

Explore workflow components with interactive tables:

- **Jobs**: View all jobs with status, name, command, and dependencies
- **Files**: Input/output files with paths and timestamps
- **User Data**: Key-value data passed between jobs
- **Results**: Execution results with return codes and resource metrics
- **Compute Nodes**: Available compute resources
- **Resource Requirements**: CPU, memory, GPU specifications
- **Schedulers**: Slurm scheduler configurations

Features:

- **Workflow selector**: Filter by workflow
- **Column sorting**: Click headers to sort
- **Row filtering**: Type in filter boxes (supports `column:value` syntax)
- **Auto-refresh**: Toggle automatic updates

### DAG Visualization

Click "View" on any workflow to see an interactive dependency graph:

- Nodes represent jobs, colored by status
- Edges show dependencies (file-based and explicit)
- Zoom, pan, and click nodes for details
- Legend shows status colors

### Debugging Tab

Investigate failed jobs with the integrated debugger:

1. Select a workflow
2. Configure output directory (where logs are stored)
3. Toggle "Show only failed jobs" to focus on problems
4. Click "Generate Report" to fetch results
5. Click any job row to view its log files:
   - **stdout**: Standard output from the job
   - **stderr**: Error output and stack traces
   - Copy file paths with one click

### Events Tab

Monitor workflow activity:

- Real-time event stream with automatic polling
- Filter by workflow
- View event types, timestamps, and details
- Useful for tracking job state transitions

### Resource Plots Tab

Visualize CPU and memory usage over time:

1. Enter a base directory containing resource database files
2. Click "Scan for Databases" to find `.db` files
3. Select databases to plot
4. Click "Generate Plots" for interactive Plotly charts

Requires workflows run with `granularity: "time_series"` in `resource_monitor` config.

### Configuration Tab

#### Server Management

Start and stop `torc-server` directly from the dashboard:

- **Server Port**: Port to listen on (0 = auto-detect free port)
- **Database Path**: SQLite database file location
- **Completion Check Interval**: How often to check for job completions
- **Log Level**: Server logging verbosity

Click "Start Server" to launch, "Stop Server" to terminate.

#### API Configuration

- **API URL**: Torc server endpoint
- **Test Connection**: Verify connectivity

Settings are saved to browser local storage.

## Common Usage Patterns

### Running a Workflow

1. Navigate to **Workflows** tab
2. Click **Create Workflow**
3. Upload your specification file
4. Click **Create**
5. Click **Initialize** on the new workflow
6. Click **Run Locally** (or **Submit** for Slurm)
7. Monitor progress in the **Details** tab or **Events** tab

### Debugging a Failed Workflow

1. Go to the **Debugging** tab
2. Select the workflow
3. Check "Show only failed jobs"
4. Click **Generate Report**
5. Click on a failed job row
6. Review the **stderr** tab for error messages
7. Check **stdout** for context

### Monitoring Active Jobs

1. Open **Details** tab
2. Select "Jobs" and your workflow
3. Enable **Auto-refresh**
4. Watch job statuses update in real-time

## Security Considerations

1. **Network Access**: By default, binds to 127.0.0.1 (localhost only)
2. **Remote Access**: Use `--host 0.0.0.0` with caution; consider a reverse proxy with HTTPS
3. **Authentication**: Torc server supports htpasswd-based authentication (see
   [Authentication](./authentication.md))

## Troubleshooting

### Cannot Connect to Server

- Verify torc-server is running: `curl http://localhost:8080/torc-service/v1/workflows`
- Check the API URL in Configuration tab
- In standalone mode, check server output for startup errors

### Workflow Creation Fails

- Ensure workflow specification is valid YAML/JSON/KDL
- Check file paths are accessible from the server
- Review browser console for error details

### Resource Plots Not Showing

- Verify workflow used `granularity: "time_series"` mode
- Confirm `.db` files exist in the specified directory
- Check that database files contain data

### Standalone Mode Server Won't Start

- Verify `torc-server` binary is in PATH or specify `--torc-server-bin`
- Check if the port is already in use
- Review console output for error messages

## Architecture

`torc-dash` is a self-contained Rust binary with:

- **Axum web framework** for HTTP server
- **Embedded static assets** (HTML, CSS, JavaScript)
- **API proxy** to forward requests to torc-server
- **CLI integration** for workflow operations

The frontend uses vanilla JavaScript with:

- **Cytoscape.js** for DAG visualization
- **Plotly.js** for resource charts
- **Custom components** for tables and forms

## Next Steps

- [Dashboard Deployment Tutorial](../../specialized/tools/dashboard-deployment.md) - Detailed
  deployment scenarios
- [Authentication](../../specialized/admin/authentication.md) - Secure your deployment
- [Server Deployment](../../specialized/admin/server-deployment.md) - Production server
  configuration
