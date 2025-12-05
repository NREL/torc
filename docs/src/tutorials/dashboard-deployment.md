# Dashboard Deployment Tutorial

This tutorial covers three common deployment scenarios for the Torc web dashboard (`torc-dash`). Each scenario addresses different environments and use cases.

## Overview of Deployment Scenarios

| Scenario | Environment | Use Case |
|----------|-------------|----------|
| 1. Standalone | Local computer | Development, testing, single-user workflows |
| 2. Shared Server | HPC login node | Multi-user access to central server |
| 3. All-in-One Login Node | HPC login node | Complete Torc stack on login node |

## Prerequisites

Before starting, ensure you have:

1. **Built Torc binaries** (see [Installation](../installation.md)):
   ```bash
   cargo build --release --workspace
   ```

2. **Added binaries to PATH**:
   ```bash
   export PATH="$PATH:/path/to/torc/target/release"
   ```

3. **Initialized the database** (if not using standalone mode):
   ```bash
   sqlx database setup
   ```

---

## Scenario 1: Local Development (Standalone Mode)

**Best for**: Development, testing, learning Torc, single-user workflows on your laptop or workstation.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Your Computer                       │
│                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────┐  │
│  │  torc-dash  │───▶│ torc-server │◀───│  torc   │  │
│  │  (web UI)   │    │  (managed)  │    │  (CLI)  │  │
│  └─────────────┘    └─────────────┘    └─────────┘  │
│        │                   │                         │
│        ▼                   ▼                         │
│    Browser             SQLite DB                     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Setup

**Step 1: Start the dashboard in standalone mode**

```bash
torc-dash --standalone
```

This single command:
- Automatically starts `torc-server` on a free port
- Starts the dashboard on http://127.0.0.1:8090
- Configures the dashboard to connect to the managed server

**Step 2: Open your browser**

Navigate to http://localhost:8090

**Step 3: Create and run a workflow**

1. Click **Create Workflow**
2. Upload a workflow specification file (YAML, JSON, or KDL)
3. Click **Create**
4. Click **Initialize** on the new workflow
5. Click **Run Locally** to execute

### Configuration Options

```bash
# Custom dashboard port
torc-dash --standalone --port 8080

# Specify database location
torc-dash --standalone --database /path/to/my.db

# Faster job completion detection
torc-dash --standalone --completion-check-interval-secs 2

# Specify binary paths (if not in PATH)
torc-dash --standalone \
  --torc-bin /path/to/torc \
  --torc-server-bin /path/to/torc-server
```

### Stopping

Press `Ctrl+C` in the terminal. This stops both the dashboard and the managed server.

---

## Scenario 2: Shared Server on HPC

**Best for**: Multi-user environments where a central `torc-server` runs persistently on a shared machine, and users access it via `torc-dash` from login nodes.

### Architecture

```
┌──────────────────────────┐     ┌──────────────────────────┐
│     Shared Server        │     │      Login Node          │
│                          │     │                          │
│  ┌─────────────┐         │     │  ┌─────────────┐         │
│  │ torc-server │◀────────│─────│──│  torc-dash  │         │
│  │  (port 8080)│         │     │  │  (port 8090)│         │
│  └─────────────┘         │     │  └─────────────┘         │
│        │                 │     │        │                 │
│        ▼                 │     │        ▼                 │
│    SQLite DB             │     │    Browser (SSH tunnel)  │
│                          │     │                          │
│                          │     │  ┌─────────────┐         │
│                          │◀────│──│    torc     │         │
│                          │     │  │    (CLI)    │         │
│                          │     │  └─────────────┘         │
└──────────────────────────┘     └──────────────────────────┘
```

### Setup

**Step 1: Start torc-server on the shared server**

On the shared server (e.g., a dedicated service node):

```bash
# Start server with production settings
torc-server run \
  --port 8080 \
  --database /shared/storage/torc.db \
  --completion-check-interval-secs 30
```

For production, consider running as a systemd service:

```bash
torc-server service install --user \
  --port 8080 \
  --database /shared/storage/torc.db
```

**Step 2: Start torc-dash on a login node**

SSH to the login node and start the dashboard:

```bash
# Connect to the shared server
export TORC_API_URL="http://shared-server:8080/torc-service/v1"

# Start dashboard (accessible only from login node by default)
torc-dash --port 8090
```

**Step 3: Access the dashboard via SSH tunnel**

From your local machine, create an SSH tunnel:

```bash
ssh -L 8090:localhost:8090 user@login-node
```

> **Important**: Use `localhost` in the tunnel command, not the login node's hostname.
> The tunnel forwards your local port to `localhost:8090` *as seen from the login node*,
> which matches where torc-dash binds (127.0.0.1:8090).

Then open http://localhost:8090 in your local browser.

### Using the CLI

Users can also interact with the shared server via CLI:

```bash
# Set the API URL
export TORC_API_URL="http://shared-server:8080/torc-service/v1"

# Create and run workflows
torc workflows create my_workflow.yaml
torc workflows run <workflow_id>
```

### Authentication

For multi-user environments, enable authentication:

```bash
# Create htpasswd file with users
torc-htpasswd create /path/to/htpasswd
torc-htpasswd add /path/to/htpasswd alice
torc-htpasswd add /path/to/htpasswd bob

# Start server with authentication
torc-server run \
  --port 8080 \
  --auth-file /path/to/htpasswd \
  --require-auth
```

See [Authentication](../how-to/authentication.md) for details.

---

## Scenario 3: All-in-One Login Node

**Best for**: HPC environments where you want the complete Torc stack running on the login node, with jobs submitted to Slurm.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            Login Node                                    │
│                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────┐                      │
│  │  torc-dash  │───▶│ torc-server │◀───│  torc   │                      │
│  │  (port 8090)│    │  (port 8080)│    │  (CLI)  │                      │
│  └─────────────┘    └─────────────┘    └─────────┘                      │
│        │                   │                │                            │
│        ▼                   ▼                ▼                            │
│    Browser            SQLite DB        sbatch/squeue                     │
│  (SSH tunnel)                               │                            │
│                                             │                            │
└─────────────────────────────────────────────│────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Compute Nodes (Slurm)                            │
│                                                                          │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐ │
│  │ torc-slurm-job-    │  │ torc-slurm-job-    │  │ torc-slurm-job-    │ │
│  │ runner (job 1)     │  │ runner (job 2)     │  │ runner (job N)     │ │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Setup

**Step 1: Start torc-server on the login node**

```bash
# Start server
torc-server run \
  --port 8080 \
  --database $SCRATCH/torc.db \
  --completion-check-interval-secs 10
```

Or as a background process:

```bash
nohup torc-server run \
  --port 8080 \
  --database $SCRATCH/torc.db \
  > $SCRATCH/torc-server.log 2>&1 &
```

**Step 2: Start torc-dash on the same login node**

```bash
# Set API URL to local server
export TORC_API_URL="http://localhost:8080/torc-service/v1"

# Start dashboard
torc-dash --port 8090
```

Or in the background:

```bash
nohup torc-dash --port 8090 > $SCRATCH/torc-dash.log 2>&1 &
```

**Step 3: Access via SSH tunnel**

From your local machine:

```bash
ssh -L 8090:localhost:8090 user@login-node
```

> **Important**: Use `localhost` in the tunnel command, not the login node's hostname.
> This works because torc-dash binds to 127.0.0.1 by default.

Open http://localhost:8090 in your browser.

### Submitting to Slurm

**Via Dashboard:**

1. Create a workflow with Slurm scheduler configuration
2. Click **Initialize**
3. Click **Submit to Scheduler** (not "Run Locally")

**Via CLI:**

```bash
export TORC_API_URL="http://localhost:8080/torc-service/v1"

# Create workflow with Slurm actions
torc workflows create my_slurm_workflow.yaml

# Submit to Slurm
torc submit <workflow_id>
```

### Example Slurm Workflow

```yaml
name: slurm_example
description: Example workflow for Slurm submission

slurm_schedulers:
  - name: default_scheduler
    account: myproject
    partition: compute
    qos: normal
    output_dir: output

resource_requirements:
  - name: standard
    num_cpus: 4
    memory: 8g
    runtime: PT1H

jobs:
  - name: process_data
    command: python process.py
    scheduler: default_scheduler
    resource_requirements: standard

on_workflow_start:
  - schedule_nodes:
      scheduler: default_scheduler
      num_nodes: 2
```

### Monitoring Slurm Jobs

The dashboard shows job status updates as Slurm jobs progress:

1. Go to **Details** tab
2. Select **Jobs**
3. Enable **Auto-refresh**
4. Watch status change from `pending` → `running` → `completed`

You can also monitor via:
- **Events** tab for state transitions
- **Debugging** tab for job logs after completion

---

## Comparison Summary

| Feature | Standalone | Shared Server | Login Node |
|---------|------------|---------------|------------|
| Setup complexity | Low | Medium | Medium |
| Multi-user support | No | Yes | Yes (single node) |
| Slurm integration | No | Optional | Yes |
| Database location | Local | Shared storage | Login node |
| Persistence | Session only | Persistent | Depends on setup |
| Best for | Development | Production | HPC workflows |

## Troubleshooting

### Cannot connect to server

```bash
# Check if server is running
curl http://localhost:8080/torc-service/v1/workflows

# Check server logs
tail -f torc-server.log
```

### SSH tunnel not working

```bash
# Verify tunnel is established
lsof -i :8090

# Check for port conflicts
netstat -tuln | grep 8090
```

### Slurm jobs not starting

```bash
# Check Slurm queue
squeue -u $USER

# Check Slurm job logs
cat output/slurm_output_*.e
```

### Dashboard shows "Disconnected"

- Verify API URL in Configuration tab
- Check network connectivity to server
- Ensure server is running and accessible

## Next Steps

- [Web Dashboard Guide](../how-to/dashboard.md) - Complete feature reference
- [Working with Slurm](../how-to/slurm.md) - Detailed Slurm configuration
- [Server Deployment](../how-to/server-deployment.md) - Production server setup
- [Authentication](../how-to/authentication.md) - Securing your deployment
