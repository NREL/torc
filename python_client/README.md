# Workflow Management System

## Components

### Python CLI (`pytorc`)
Command-line interface for workflow management operations.

### Web Dashboard (`torc-dash`)
A web-based dashboard for managing and monitoring Torc workflows. Provides an intuitive interface for:
- Viewing and filtering workflows, jobs, results, events, files, and other resources
- Running workflows locally or submitting to HPC/Slurm
- Real-time monitoring with auto-refresh
- Interactive tables with sorting and filtering

See [src/torc/dash_app/README.md](src/torc/dash_app/README.md) for detailed documentation.

## Installation

```bash
cd python_client
pip install -e .
```

## Usage

### Web Dashboard

```bash
torc-dash
```

Then open your browser to http://localhost:8050

### CLI

```bash
pytorc --help
```
