# Tutorial: AI-Assisted Workflow Management

This tutorial shows how to use AI assistants to manage Torc workflows using natural language.

## What You'll Learn

- Set up an AI assistant to work with Torc
- Create and manage workflows through conversation
- Debug failures by asking questions

## Prerequisites

- Torc installed and server running
- [Claude Code](https://claude.ai/code) or VS Code with GitHub Copilot

## What Can AI Assistants Do?

With Torc's AI integration, you can manage workflows using natural language:

| Task             | Example                                            |
| ---------------- | -------------------------------------------------- |
| Check status     | _"What's the status of workflow 42?"_              |
| Debug failures   | _"Why did a job in workflow 5 fail?"_              |
| Create workflows | _"Create a workflow with 10 parallel jobs"_        |
| Fix problems     | _"Restart the failed jobs with doubled memory"_    |
| Investigate      | _"Check if any jobs exceeded their memory limits"_ |

---

## Quick Setup: Claude Code

**Step 1:** Add the Torc MCP server to your project:

```bash
claude mcp add torc \
  --scope project \
  -e TORC_API_URL=http://localhost:8080/torc-service/v1 \
  -e TORC_OUTPUT_DIR=./output \
  -- /path/to/torc-mcp-server
```

**Step 2:** Verify it's configured:

```bash
claude mcp list
```

**Step 3:** Start a new Claude Code session and try:

> "What workflows exist?"

---

## Quick Setup: VS Code + Copilot

**Step 1:** Create `.vscode/mcp.json` in your project:

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

**Step 2:** In Copilot Chat, use Agent Mode and try:

> "What workflows exist?"

---

## Example: Creating a Workflow

```
You: Create a workflow with 3 stages: a preprocess script, 10 work jobs
     that each take an index, and a postprocess job.

Claude:
● Created workflow ID 6 (three_stage_pipeline) with:

  | Stage          | Jobs                              | Dependencies                |
  |----------------|-----------------------------------|-----------------------------|
  | 1. Preprocess  | preprocess                        | None                        |
  | 2. Work        | work_00 through work_09 (10 jobs) | Each depends on preprocess  |
  | 3. Postprocess | postprocess                       | Depends on all 10 work jobs |

● Workflow is ready with 12 jobs total. Would you like me to run or submit it?
```

---

## Example: Debugging a Failure

```
You: Why did a job in workflow 5 fail?

Claude:
● The job failed due to an Out of Memory (OOM) kill:

  Job Details:
  - Name: work_job
  - Command: python work.py
  - Return code: 137 (SIGKILL from OOM killer)

  What happened:
  1. The job was configured with a 200GB memory limit
  2. The script allocated 230GB before being killed
  3. The Linux OOM killer terminated the process

  Recommendation: Increase memory to 256GB and retry.
```

---

## Example: Fixing and Retrying

```
You: Increase the memory to 256GB and restart the failed jobs.

Claude:
● Updated job 5 resource requirements:
  - Memory: 200g → 256g

● Reset job status from "failed" to "ready"

● The job is now queued for execution. Would you like me to submit it to Slurm?
```

---

## What You Learned

- How to configure AI assistants with Torc (one command for Claude Code, one file for VS Code)
- How to create workflows through conversation
- How to debug and fix failures using natural language

## Next Steps

- [AI Assistant Reference](../reference/ai-assistant.md) — Full configuration options, all tools,
  troubleshooting
- [Automatic Failure Recovery](./automatic-recovery.md) — Use `torc watch` for automated recovery
- [Configuration Files](./configuration.md) — Set up Torc configuration
