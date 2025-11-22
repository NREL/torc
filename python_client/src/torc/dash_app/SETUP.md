# Torc Dash Application - Setup Guide

This guide will help you set up and run the Torc Dash web application.

## Prerequisites

1. **Python 3.11+**: Ensure you have Python 3.11 or later installed
2. **Torc Server**: A running Torc server instance
3. **Torc CLI**: The `torc` command-line binary (for workflow execution features)

## Installation

### Step 1: Install the Package

From the `python_client` directory:

```bash
cd python_client
pip install -e .
```

This will install:
- The `torc` Python package
- All required dependencies including Dash and Dash Bootstrap Components
- The `torc-dash` command-line entry point

### Step 2: Verify Installation

Check that the installation was successful:

```bash
torc-dash --help
```

You should see help text with command-line options.

## Running the Application

### Quick Start

The simplest way to run the application:

```bash
torc-dash
```

This will start the server on http://127.0.0.1:8050

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

Set default configuration using environment variables:

```bash
export TORC_API_URL="http://localhost:8080/torc-service/v1"
export USER="your_username"
torc-dash
```

## First-Time Setup

1. **Start the Application**
   ```bash
   torc-dash
   ```

2. **Open Your Browser**
   Navigate to http://localhost:8050

3. **Configure the API Connection**
   - Click the "Configuration" button at the top
   - Enter your Torc server API URL (e.g., `http://localhost:8080/torc-service/v1`)
   - Enter your username
   - Click "Save Configuration"

4. **Test the Connection**
   - Navigate to the "View Resources" tab
   - Select "Workflows" from the dropdown
   - Click "Refresh"
   - You should see a list of workflows (if any exist)

## Usage Examples

### Viewing Workflows

1. Go to "View Resources" tab
2. Select "Workflows" from the resource type dropdown
3. Enable "Auto-refresh" for live updates
4. Use table filters and sorting to find specific workflows

### Viewing Jobs for a Workflow

1. Go to "View Resources" tab
2. Select "Jobs" from the resource type dropdown
3. Select a workflow from the filter dropdown
4. The jobs table will display

### Running a Workflow Locally

1. Go to "Run Workflows" tab
2. Under "New Workflow" tab:
   - Upload a workflow spec file or enter its path
3. Select "Run Locally" execution mode
4. Click "Execute Workflow"
5. Monitor the output in the "Execution Output" section

### Submitting to HPC/Slurm

1. Go to "Run Workflows" tab
2. Select or upload your workflow
3. Select "Submit to HPC/Slurm" execution mode
4. Click "Execute Workflow"
5. View submission results in the output

## Troubleshooting

### Port Already in Use

If port 8050 is already in use:

```bash
torc-dash --port 8051
```

### Cannot Connect to Torc Server

1. Verify the server is running:
   ```bash
   curl http://localhost:8080/torc-service/v1/workflows
   ```

2. Check the API URL in the configuration panel

3. Ensure there are no firewall issues

### Torc CLI Not Found

If you get errors about the `torc` command not being found:

1. Ensure the Rust `torc` binary is in your PATH:
   ```bash
   which torc
   ```

2. If not, add it to your PATH or build it:
   ```bash
   cd /path/to/torc
   cargo build --release --bin torc
   export PATH="/path/to/torc/target/release:$PATH"
   ```

### Module Import Errors

If you see import errors:

```bash
pip install --upgrade dash dash-bootstrap-components
```

## Development Mode

For development with auto-reload:

```bash
cd python_client/src/torc/dash_app
python run.py --debug --host 127.0.0.1 --port 8050
```

This enables:
- Hot-reloading on code changes
- Detailed error messages
- Debug toolbar in the browser

## Production Deployment

For production deployment, consider using a production WSGI server:

```bash
pip install gunicorn
gunicorn torc.dash_app.app:server -b 0.0.0.0:8050 -w 4
```

Or with additional configuration:

```bash
gunicorn torc.dash_app.app:server \
    --bind 0.0.0.0:8050 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

## Docker Deployment (Optional)

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
2. **Production Use**: Use `--host 0.0.0.0` with caution in production
3. **Authentication**: Password authentication is planned but not yet implemented
4. **HTTPS**: For production, run behind a reverse proxy with HTTPS (nginx, Apache, etc.)

## Getting Help

- Check the main README: [python_client/src/torc/dash_app/README.md](README.md)
- Review example workflows: [examples/](../../../../examples/)
- Report issues: https://github.com/NREL/torc/issues

## Next Steps

After setup:
1. Explore the View Resources tab with different resource types
2. Try running a simple workflow locally
3. Experiment with the auto-refresh feature
4. Check out the example workflow specifications in the `examples/` directory
