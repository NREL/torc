# Tutorial: Using the MCP Server

This tutorial shows how to use the Torc MCP (Model Context Protocol) server to enable AI assistants to interact with your Torc workflows directly.

## Learning Objectives

By the end of this tutorial, you will:

- Understand what the MCP server provides
- Know how to configure your AI assistant to use the Torc MCP server
- Be able to inspect and manage your workflows using natural language

## Prerequisites

- Torc installed
- Torc server running
- One of the following AI assistants:
  - [Claude Code](https://claude.ai/code) (terminal)
  - [VS Code](https://code.visualstudio.com/) with GitHub Copilot (IDE)

## What is the MCP Server?

The Model Context Protocol (MCP) is an open standard for connecting AI assistants to external tools and data sources. The `torc-mcp-server` binary exposes Torc's workflow management capabilities as MCP tools.

**Available Tools:**

| Tool | Description |
|------|-------------|
| `get_workflow_status` | Get workflow info with job counts by status |
| `get_job_details` | Get detailed job info including resource requirements |
| `get_job_logs` | Read stdout/stderr from job log files |
| `list_failed_jobs` | List all failed jobs in a workflow |
| `list_jobs_by_status` | Filter jobs by status |
| `check_resource_utilization` | Analyze resource usage and detect OOM/timeout issues |
| `update_job_resources` | Modify job resource requirements |
| `restart_jobs` | Reset and restart failed jobs |
| `resubmit_workflow` | Regenerate Slurm schedulers and submit new allocations |
| `cancel_jobs` | Cancel specific jobs |
| `create_workflow_from_spec` | Create a workflow from JSON specification |

## Configuration

Choose the setup that matches your environment:

- **[Claude Code](#claude-code)** - Terminal-based AI assistant
- **[VS Code + Copilot](#vs-code--github-copilot)** - IDE with GitHub Copilot Chat
- **[VS Code + Copilot on HPC](#vs-code-remote-ssh-for-hpc)** - Remote development on HPC clusters

---

## Claude Code

Claude Code supports MCP configuration at three scopes:

| Scope | File | Use Case |
|-------|------|----------|
| **Project** | `.mcp.json` in project root | Team-shared configuration (commit to git) |
| **Local** | `.mcp.json` with `--scope local` | Personal project settings (gitignored) |
| **User** | `~/.claude.json` | Cross-project personal tools |

### Using the CLI (Recommended)

```bash
# Add the Torc MCP server to your project
claude mcp add torc \
  --scope project \
  -e TORC_API_URL=http://localhost:8080/torc-service/v1 \
  -e TORC_OUTPUT_DIR=/path/to/your/output \
  -- /path/to/torc-mcp-server
```

### Manual Configuration

Create or edit `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "torc": {
      "command": "/path/to/torc-mcp-server",
      "env": {
        "TORC_API_URL": "http://localhost:8080/torc-service/v1",
        "TORC_OUTPUT_DIR": "/path/to/your/output"
      }
    }
  }
}
```

Replace `/path/to/torc-mcp-server` with the actual path to your built binary.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TORC_API_URL` | Torc server URL | `http://localhost:8080/torc-service/v1` |
| `TORC_OUTPUT_DIR` | Directory containing job logs | `output` |
| `TORC_USERNAME` | Username for authentication (optional) | — |
| `TORC_PASSWORD` | Password for authentication (optional) | — |

You can also use environment variable expansion in `.mcp.json`:

```json
{
  "mcpServers": {
    "torc": {
      "command": "/path/to/torc-mcp-server",
      "env": {
        "TORC_API_URL": "${TORC_API_URL:-http://localhost:8080/torc-service/v1}",
        "TORC_OUTPUT_DIR": "${TORC_OUTPUT_DIR:-./output}"
      }
    }
  }
}
```

### Verify Configuration

Check that the MCP server is configured correctly:

```bash
# List configured MCP servers
claude mcp list

# Get details about the torc server
claude mcp get torc
```

Start a new Claude Code session in your project directory. Claude will automatically have access to the Torc tools.

### Example Conversations

#### Create a workflow

```
You: Using the mcp server, create a workflow with 3 stages: a preprocess script, 10 work jobs, each taking an index, and a postprocess job.

Claude:
● Created workflow ID 6 (three_stage_pipeline) with:

  | Stage          | Jobs                              | Dependencies                |
  |----------------|-----------------------------------|-----------------------------|
  | 1. Preprocess  | preprocess                        | None                        |
  | 2. Work        | work_00 through work_09 (10 jobs) | Each depends on preprocess  |
  | 3. Postprocess | postprocess                       | Depends on all 10 work jobs |

● torc - get_workflow_status (MCP)(workflow_id: 6)
  ⎿  {
       "description": "Pipeline with preprocess, 10 parallel work jobs, and postprocess",
       "job_counts_by_status": {
     … +7 lines (ctrl+o to expand)

● Workflow is ready with 12 jobs total (1 preprocess + 10 work + 1 postprocess). All jobs are currently Uninitialized.

  Would you like me to run or submit it?
```

#### Debug a workflow
```
You: Why did a job in workflow 5 fail?

Claude:
● torc - get_workflow_status (MCP)(workflow_id: 5)
  ⎿  {
       "description": null,
       "job_counts_by_status": {
     … +7 lines (ctrl+o to expand)

● torc - list_failed_jobs (MCP)(workflow_id: 5)
  ⎿  {
       "failed_job_count": 1,
       "failed_jobs": [
     … +8 lines (ctrl+o to expand)

● Let me get more details about this job and check its logs:

● torc - get_job_details (MCP)(job_id: 5)
  ⎿  {
       "cancel_on_blocking_job_failure": true,
       "command": "bash tests/scripts/oom_test.sh 20 10",
     … +23 lines (ctrl+o to expand)

● torc - get_job_logs (MCP)(workflow_id: 5, job_id: 5, run_id: 1, log_type: "stderr")
  ⎿  tests/scripts/oom_test.sh: line 74: 649452 Killed                  python3  <<EOF
     import sys
     import time
     … +32 lines (ctrl+o to expand)

● torc - get_job_logs (MCP)(workflow_id: 5, job_id: 5, run_id: 1, log_type: "stdout")
  ⎿  OOM Test Script Starting
     ========================
     Hostname: x1003c1s1b1n0                                                                                                                               … +39 lines (ctrl+o to expand)

● The job failed due to an Out of Memory (OOM) kill. Here's what happened:

  Job Details:
  - Name: work_job
  - Command: python work.py
  - Return code: 137 (128 + SIGKILL from OOM killer)

  What occurred:
  1. The job ran the user's work script.
  2. The node had ~250GB total memory available
  3. The script successfully allocated 230GB before being killed
  4. The job was configured with a 200GB memory limit but exceeded it
  5. The Linux OOM killer terminated the process with SIGKILL (exit code 137)

  From stderr:
  tests/scripts/oom_test.sh: line 74: 649452 Killed  python3 ...
```

### Troubleshooting Claude Code

**Claude doesn't see the tools:**
- Verify the MCP server is configured: `claude mcp list`
- Check the config file is valid JSON: `cat .mcp.json | jq .`
- Check that the path to `torc-mcp-server` is correct and the binary exists
- Start a new Claude Code session (MCP servers are loaded at startup)

**Remove the MCP server:**
```bash
claude mcp remove torc
```

---

## VS Code + GitHub Copilot

VS Code with GitHub Copilot Chat supports MCP servers for enhanced AI-assisted workflow management.

### Prerequisites

- VS Code 1.99 or later
- GitHub Copilot extension installed
- GitHub Copilot subscription (Business, Enterprise, Pro, or Pro+)

### Configuration

Create `.vscode/mcp.json` in your project root:

```json
{
  "servers": {
    "torc": {
      "command": "/path/to/torc-mcp-server",
      "env": {
        "TORC_API_URL": "http://localhost:8080/torc-service/v1",
        "TORC_OUTPUT_DIR": "./output"
      }
    }
  }
}
```

### Verify Setup

1. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Run "MCP: List Servers"
3. Verify "torc" appears in the list

### Usage

In Copilot Chat, use **Agent Mode** (`@workspace` or the agent icon) to access MCP tools:

> "What's the status of workflow 42?"

> "Show me the failed jobs and their error logs"

---

## VS Code Remote SSH for HPC

For users running Torc on HPC clusters, VS Code's Remote SSH extension allows you to use Copilot Chat with the MCP server running directly on the cluster.

### Architecture

```
┌─────────────────────┐         ┌─────────────────────────────────────┐
│  Local Machine      │   SSH   │  HPC Cluster                        │
│                     │◄───────►│                                     │
│  VS Code            │         │  torc-mcp-server ◄──► torc-server   │
│  (Copilot Chat)     │         │        ▲                            │
│                     │         │        │                            │
└─────────────────────┘         │  .vscode/mcp.json                   │
                                └─────────────────────────────────────┘
```

The MCP server runs on the HPC, communicates with the Torc server on the HPC, and VS Code proxies requests through SSH. No ports need to be exposed to your local machine.

### Step 1: Build `torc-mcp-server` on the HPC

```bash
# On the HPC (via SSH or login node)
cd /path/to/torc
cargo build --release -p torc-mcp-server
```

### Step 2: Configure MCP in your project

Create `.vscode/mcp.json` in your project directory **on the HPC**:

```json
{
  "servers": {
    "torc": {
      "command": "/path/on/hpc/torc/target/release/torc-mcp-server",
      "env": {
        "TORC_API_URL": "http://localhost:8080/torc-service/v1",
        "TORC_OUTPUT_DIR": "./output"
      }
    }
  }
}
```

> **Important:** MCP servers configured in workspace settings (`.vscode/mcp.json`) run on the remote host, not your local machine.

### Step 3: Connect and use

1. Install the [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) extension
2. Connect to the HPC: `Remote-SSH: Connect to Host...`
3. Open your project folder on the HPC
4. Open Copilot Chat and use Agent Mode

### HPC-Specific Tips

- **Module systems:** If your HPC uses modules, you may need to set `PATH` in the env to include required dependencies
- **Shared filesystems:** Place `.vscode/mcp.json` in a project directory on a shared filesystem accessible from compute nodes
- **Firewalls:** The MCP server only needs to reach the Torc server on the HPC's internal network

---

## Interact with Workflows

Once configured, you can ask your AI assistant to help manage workflows using natural language:

**Check workflow status:**
> "What's the status of workflow 42?"

**Investigate failures:**
> "List all failed jobs in workflow 42 and show me the error logs"

**Take action:**
> "Restart the failed jobs in workflow 42 with doubled memory"

**Create workflows:**
> "Create a workflow with 10 parallel jobs that each run `python process.py index`"

---

## How It Works

The MCP server:

1. **Receives tool calls** from the AI assistant via stdio
2. **Translates them** to Torc REST API calls
3. **Returns results** in a format the assistant can understand

The server is stateless—it simply proxies requests to your running Torc server. All workflow state remains in Torc's database.

## Security Considerations

- The MCP server has full access to your Torc server
- Consider using authentication (`TORC_USERNAME`/`TORC_PASSWORD`) if your Torc server is exposed
- The server can modify workflows (restart, cancel, update resources)
- Review proposed actions before they execute

## Troubleshooting

### "Failed to connect to server"
- Ensure your Torc server is running
- Check that `TORC_API_URL` is correct
- Verify network connectivity

### "Permission denied" or "Authentication failed"
- Set `TORC_USERNAME` and `TORC_PASSWORD` if your server requires auth
- Check that the credentials are correct

### Logs not found
- Ensure `TORC_OUTPUT_DIR` points to your job output directory
- Check that jobs have actually run (logs are created at runtime)

## What You Learned

In this tutorial, you learned:

- ✅ What the Torc MCP server provides
- ✅ How to configure Claude Code to use it
- ✅ How to configure VS Code + GitHub Copilot to use it
- ✅ How to set up MCP on HPC clusters via Remote SSH
- ✅ How to interact with workflows using natural language
- ✅ Security considerations for production use

## Next Steps

- [Automatic Failure Recovery](./automatic-recovery.md) - Use `torc watch` for automatic failure recovery
- [Automatic Recovery Explained](../explanation/automatic-recovery.md) - Understand the recovery architecture
- [Configuration Files](./configuration.md) - Set up Torc configuration
