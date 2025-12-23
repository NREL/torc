# Tutorial: AI-Assisted Workflow Management

This tutorial shows how to use AI assistants like Claude Code and GitHub Copilot to interact with your Torc workflows using natural language.

## Learning Objectives

By the end of this tutorial, you will:

- Use an AI assistant to inspect and debug workflows
- Create and manage workflows through conversation
- Configure AI tools to work with Torc

## Prerequisites

- Torc installed
- Torc server running
- One of the following AI assistants:
  - [Claude Code](https://claude.ai/code) (terminal)
  - [VS Code](https://code.visualstudio.com/) with GitHub Copilot (IDE)

## What Can AI Assistants Do?

With Torc's AI integration, you can manage workflows using natural language:

**Check status:**
> "What's the status of workflow 42?"

**Debug failures:**
> "Why did a job in workflow 5 fail? Show me the logs."

**Create workflows:**
> "Create a workflow with 10 parallel jobs that each run `python process.py --index N`"

**Fix problems:**
> "Restart the failed jobs with doubled memory"

**Investigate resources:**
> "Check if any jobs exceeded their memory limits"

The AI assistant translates your requests into Torc API calls and presents results in a readable format.

## Configuration

Choose the setup that matches your environment:

- **[Claude Code](#claude-code)** - Terminal-based AI assistant
- **[VS Code + Copilot](#vs-code--github-copilot)** - IDE with GitHub Copilot Chat
- **[VS Code + Copilot on HPC](#vs-code-remote-ssh-for-hpc)** - Remote development on HPC clusters

---

## Claude Code

Claude Code connects to Torc through an MCP (Model Context Protocol) server, a lightweight bridge that translates AI requests into Torc API calls.

### Quick Setup

```bash
# Add Torc AI tools to your project
claude mcp add torc \
  --scope project \
  -e TORC_API_URL=http://localhost:8080/torc-service/v1 \
  -e TORC_OUTPUT_DIR=/path/to/your/output \
  -- /path/to/torc-mcp-server
```

Replace `/path/to/torc-mcp-server` with the path to your built binary.

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

### Configuration Scopes

| Scope | File | Use Case |
|-------|------|----------|
| **Project** | `.mcp.json` in project root | Team-shared configuration (commit to git) |
| **Local** | `.mcp.json` with `--scope local` | Personal project settings (gitignored) |
| **User** | `~/.claude.json` | Cross-project personal tools |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TORC_API_URL` | Torc server URL | `http://localhost:8080/torc-service/v1` |
| `TORC_OUTPUT_DIR` | Directory containing job logs | `output` |
| `TORC_USERNAME` | Username for authentication (optional) | — |
| `TORC_PASSWORD` | Password for authentication (optional) | — |

### Verify Configuration

```bash
# List configured MCP servers
claude mcp list

# Get details about the torc server
claude mcp get torc
```

Start a new Claude Code session in your project directory. Claude will automatically have access to the Torc tools.

### Example: Creating a Workflow

```
You: Create a workflow with 3 stages: a preprocess script, 10 work jobs, each taking an index, and a postprocess job.

Claude:
● Created workflow ID 6 (three_stage_pipeline) with:

  | Stage          | Jobs                              | Dependencies                |
  |----------------|-----------------------------------|-----------------------------|
  | 1. Preprocess  | preprocess                        | None                        |
  | 2. Work        | work_00 through work_09 (10 jobs) | Each depends on preprocess  |
  | 3. Postprocess | postprocess                       | Depends on all 10 work jobs |

● Workflow is ready with 12 jobs total. All jobs are currently Uninitialized.

  Would you like me to run or submit it?
```

### Example: Debugging a Failure

```
You: Why did a job in workflow 5 fail?

Claude:
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

## Available AI Tools

The AI assistant has access to these Torc operations:

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

## How It Works

Torc uses the Model Context Protocol (MCP), an open standard for connecting AI assistants to external tools. The `torc-mcp-server` binary:

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

- How to interact with workflows using natural language
- How to configure Claude Code with Torc
- How to configure VS Code + GitHub Copilot with Torc
- How to set up AI tools on HPC clusters via Remote SSH
- Security considerations for production use

## Next Steps

- [Automatic Failure Recovery](./automatic-recovery.md) - Use `torc watch` for automatic failure recovery
- [Automatic Recovery Explained](../explanation/automatic-recovery.md) - Understand the recovery architecture
- [Configuration Files](./configuration.md) - Set up Torc configuration
