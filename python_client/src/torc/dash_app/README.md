# Torc Dash Application

A web-based dashboard for managing and monitoring Torc workflows.

## Features

### Configuration Panel
- Configure the Torc API URL
- Set username for workflow operations
- Placeholder for password authentication (planned for future release)

### View Resources Tab
Browse and monitor various Torc resources:
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
- Auto-refresh capability
- Manual refresh button

### Run Workflows Tab
Create and execute workflows:
- **New Workflow**: Upload or specify a workflow specification file
- **Existing Workflow**: Select from existing workflows
- **Execution Modes**:
  - Run locally on your computer
  - Submit to HPC/Slurm scheduler
- **Options**:
  - One-step: Create and run/submit in a single command
  - Two-step: Create workflow first, then run/submit
- Real-time execution output display

## Installation

Install the torc package with the Dash dependencies:

```bash
cd python_client
pip install -e .
```

## Usage

### Starting the Application

Run the dashboard using the command-line interface:

```bash
torc-dash
```

Or with custom host and port:

```bash
torc-dash --host 0.0.0.0 --port 8050 --debug
```

The application will be available at `http://localhost:8050` (or your specified host/port).

### Configuration

1. Click the "Configuration" button to expand the configuration panel
2. Enter your Torc server API URL (e.g., `http://localhost:8080/torc-service/v1`)
3. Enter your username
4. Click "Save Configuration"

The configuration can also be pre-populated using environment variables:
- `TORC_API_URL`: Default API URL
- `USER` or `USERNAME`: Default username

### Viewing Resources

1. Navigate to the "View Resources" tab
2. Select a resource type from the dropdown
3. For resource types that require it, select a workflow from the filter dropdown
4. Enable "Auto-refresh" to automatically update the data every 5 seconds
5. Use the table's built-in filtering and sorting capabilities

### Running Workflows

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

## Architecture

The application consists of four main components:

1. **app.py**: Main Dash application with layout and configuration
2. **layouts.py**: Tab layouts and UI components
3. **callbacks.py**: Callback functions handling user interactions
4. **utils.py**: API wrapper and CLI integration utilities

### API Integration

The application uses the OpenAPI-generated client to communicate with the Torc server:
- Synchronous API calls are run in a thread pool to prevent UI blocking
- Periodic updates for auto-refresh functionality
- Error handling and user feedback

### CLI Integration

Workflow execution uses the Rust `torc` CLI binary:
- `torc run <spec>` - Create and run workflow locally
- `torc submit <spec>` - Create and submit to HPC/Slurm
- `torc workflows create <spec>` - Create workflow from specification

## Requirements

- Python >= 3.11
- Torc server running and accessible
- `torc` CLI binary in PATH (for workflow execution)
- Modern web browser

## Future Enhancements

Planned features for future releases:
- Password authentication support
- Analytics tab with visualizations
- Workflow monitoring with live updates
- Job cancellation support
- Resource usage plots
- Workflow comparison tools
- Export data to CSV/JSON

## Troubleshooting

### Connection Errors
- Ensure the Torc server is running
- Verify the API URL is correct in the configuration
- Check network connectivity

### Execution Errors
- Ensure the `torc` CLI binary is in your PATH
- Check that workflow specification files are valid YAML/JSON
- Verify file paths are correct and accessible

### Auto-refresh Not Working
- Enable the "Auto-refresh" toggle
- Check that you're on the "View Resources" tab
- Verify the API connection is working

## Development

To run in development mode with debug enabled:

```bash
cd python_client/src/torc/dash_app
python run.py --debug
```

This enables hot-reloading and detailed error messages.
