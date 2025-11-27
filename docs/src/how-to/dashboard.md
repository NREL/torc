# Web Dashboard (torc-dash)

The Torc Dashboard provides a web-based interface for monitoring and managing workflows, offering an alternative to the command-line interface.

## Overview

`torc-dash` is a Dash-based web application that allows you to:

- **Monitor workflows and jobs** with real-time updates
- **Browse resources** (workflows, jobs, files, events, compute nodes, etc.)
- **Execute workflows** locally or submit to HPC/Slurm schedulers
- **Filter and sort** data with interactive tables
- **Configure** API connection and credentials

## Installation

### Prerequisites

- Python 3.11 or later
- A running Torc server
- The `torc` CLI binary in your PATH (for workflow execution features)

### Setup

1. **Create a Python virtual environment** (recommended):

   ```bash
   cd python_client
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install the torc package**:

   ```bash
   pip install -e .
   ```

   This installs the `torc_client` Python package with all dependencies including Dash and the `torc-dash` command-line entry point.

3. **Verify installation**:

   ```bash
   torc-dash --help
   ```

## Running the Dashboard

### Quick Start

Start the dashboard with default settings (http://127.0.0.1:8050):

```bash
torc-dash
```

### Custom Configuration

Run with custom host and port:

```bash
torc-dash --host 0.0.0.0 --port 8080
```

Run in debug mode (auto-reload on code changes):

```bash
torc-dash --debug
```

### Environment Variables

Pre-configure the dashboard using environment variables:

```bash
export TORC_API_URL="http://localhost:8080/torc-service/v1"
torc-dash
```

## First-Time Setup

1. **Start the application**:
   ```bash
   torc-dash
   ```

2. **Open your browser** and navigate to http://localhost:8050

3. **Configure the API connection**:
   - Click the "Configuration" button at the top
   - Enter your Torc server API URL (e.g., `http://localhost:8080/torc-service/v1`)
   - Enter your username
   - Click "Save Configuration"

4. **Test the connection**:
   - Navigate to the "View Resources" tab
   - Select "Workflows" from the dropdown
   - Click "Refresh"
   - You should see a list of workflows (if any exist)

## Features

### Configuration Panel

- Set the Torc API URL
- Configure username for workflow operations

### View Resources Tab

Browse and monitor Torc resources with interactive tables:

- **Workflows**: View all workflows with filtering and sorting
- **Jobs**: View jobs for a specific workflow
- **Results**: View execution results
- **Events**: View workflow events
- **Files**: View input/output files
- **User Data**: View user-defined data
- **Compute Nodes**: View available compute resources
- **Resource Requirements**: View resource specifications

Features:
- Interactive tables with filtering and sorting
- Workflow-based filtering for resource types
- Auto-refresh every 5 seconds (optional)
- Manual refresh button

### Run Workflows Tab

Create and execute workflows through the web interface:

#### Method 1: Upload a Workflow Specification

1. Navigate to the "Run Workflows" tab
2. Select "New Workflow" tab
3. Drag and drop a workflow spec file (YAML/JSON) or click to browse
4. Select execution mode (Run locally or Submit to HPC/Slurm)
5. Click "Execute Workflow"

#### Method 2: Specify a File Path

1. Navigate to the "Run Workflows" tab
2. Select "New Workflow" tab
3. Enter the path to your workflow specification file
4. Select execution mode
5. Click "Execute Workflow"

#### Method 3: Use an Existing Workflow

1. Navigate to the "Run Workflows" tab
2. Select "Existing Workflow" tab
3. Choose a workflow from the dropdown
4. Select execution mode
5. Click "Execute Workflow"

**Execution Modes:**
- **Run locally**: Executes `torc run <spec>` to create and run the workflow on your local machine
- **Submit to HPC/Slurm**: Executes `torc submit <spec>` to create and submit the workflow to a scheduler

Real-time execution output is displayed in the "Execution Output" section.

## Common Usage Patterns

### Monitoring Active Workflows

1. Go to "View Resources" tab
2. Select "Workflows" from the resource type dropdown
3. Enable "Auto-refresh" for live updates
4. Use the table's filter boxes to search for specific workflows

### Viewing Job Status

1. Go to "View Resources" tab
2. Select "Jobs" from the resource type dropdown
3. Select a workflow from the filter dropdown
4. Monitor job status changes with auto-refresh enabled

### Running a Quick Test

1. Go to "Run Workflows" tab
2. Under "New Workflow" tab, upload a simple workflow specification
3. Select "Run Locally" execution mode
4. Click "Execute Workflow"
5. Monitor the output in the "Execution Output" section

## Troubleshooting

### Connection Errors

**Problem**: Cannot connect to Torc server

**Solutions**:
- Verify the Torc server is running: `curl http://localhost:8080/torc-service/v1/workflows`
- Check the API URL in the configuration panel
- Ensure there are no firewall issues
- Verify network connectivity

### Execution Errors

**Problem**: Workflow execution fails

**Solutions**:
- Ensure the `torc` CLI binary is in your PATH: `which torc`
- Verify workflow specification files are valid YAML/JSON
- Check that file paths are correct and accessible
- Review the execution output for specific error messages

### Port Already in Use

**Problem**: Port 8050 is already in use

**Solution**:
```bash
torc-dash --port 8051
```

### Auto-refresh Not Working

**Solutions**:
- Ensure the "Auto-refresh" toggle is enabled
- Verify you're on the "View Resources" tab
- Check that the API connection is working
- Manually refresh to test connectivity

## Production Deployment

### Using Gunicorn

For production deployment, use a production WSGI server:

```bash
pip install gunicorn
gunicorn torc.dash_app.app:server -b 0.0.0.0:8050 -w 4
```

With additional configuration:

```bash
gunicorn torc.dash_app.app:server \
    --bind 0.0.0.0:8050 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY python_client /app/python_client

RUN cd python_client && pip install .

EXPOSE 8050

CMD ["torc-dash", "--host", "0.0.0.0", "--port", "8050"]
```

Build and run:

```bash
docker build -t torc-dash .
docker run -p 8050:8050 \
    -e TORC_API_URL=http://your-server:8080/torc-service/v1 \
    torc-dash
```

## Security Considerations

1. **Network Access**: By default, the app binds to 127.0.0.1 (localhost only)
2. **Production Use**: Use `--host 0.0.0.0` with caution in production environments
3. **Authentication**: Password authentication is planned but not yet implemented
4. **HTTPS**: For production, run behind a reverse proxy with HTTPS (nginx, Apache, etc.)

## Development

To run in development mode with auto-reload:

```bash
cd python_client/src/torc/dash_app
python run.py --debug --host 127.0.0.1 --port 8050
```

This enables:
- Hot-reloading on code changes
- Detailed error messages
- Debug toolbar in the browser

## Architecture

The dashboard consists of four main components:

1. **app.py**: Main Dash application with layout and configuration
2. **layouts.py**: Tab layouts and UI components
3. **callbacks.py**: Callback functions handling user interactions
4. **utils.py**: API wrapper and CLI integration utilities

### API Integration

The application uses the OpenAPI-generated client to communicate with the Torc server:
- Synchronous API calls run in a thread pool to prevent UI blocking
- Periodic updates for auto-refresh functionality
- Error handling and user feedback

### CLI Integration

Workflow execution uses the Rust `torc` CLI binary:
- `torc run <spec>` - Create and run workflow locally
- `torc submit <spec>` - Create and submit to HPC/Slurm
- `torc workflows create <spec>` - Create workflow from specification

## Future Enhancements

Planned features for future releases:
- Password authentication support
- Analytics tab with visualizations
- Workflow monitoring with live updates
- Job cancellation support
- Resource usage plots
- Workflow comparison tools
- Export data to CSV/JSON
