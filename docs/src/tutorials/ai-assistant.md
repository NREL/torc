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
| Create workflows | _"Create a workflow with 10 parallel jobs"_        |
| Check status     | _"What's the status of workflow 42?"_              |
| Debug failures   | _"Why did a job in workflow 5 fail?"_              |
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
> Create a workflow with 3 stages: a preprocess script, 10 work jobs that each take an index, and a postprocess job. The work jobs each require
 10 CPUs and 20 GB of memory. The other jobs have trivial resource requirements.

⏺ I'll create a workflow spec file with the 3-stage fan-out/fan-in pattern you described.

⏺ Created the workflow spec at ./workflow.json with:

  Structure:
  - Stage 1: preprocess - runs first, outputs preprocess_output.txt
  - Stage 2: work_0 through work_9 - 10 parallel jobs, each reads preprocess output
  - Stage 3: postprocess - waits for all work jobs to complete (fan-in pattern)

  Resource Requirements:
  | Name  | CPUs | Memory | Runtime |
  |-------|------|--------|---------|
  | small | 1    | 1g     | 1 hour  |
  | large | 10   | 20g    | 2 hours |

  Next steps:
  1. Edit the spec to replace placeholder commands with your actual scripts
  2. Run locally: torc run workflow.json
  3. Or submit to Slurm: torc submit workflow.json (requires adding an account)
```

You can create much more complex workflows. Output is not shown, but this prompt will create a
workflow with job dependencies defined implicitly through job-file relationships:

```
Create a workflow with four stages of jobs. There are 3 initial jobs each dependent on an input file. Each of those jobs fans out into 10 work jobs through
  output files. Each of those jobs creates a file. In the third stage there is a script that aggregates each of the 10 jobs into one file. The final
  postprocess job aggregates those three files into one. I will run it with Slurm: account=my_account. The work jobs require 10 cpus and 30 GB of
  memory. The other jobs have trivial resource requirements.
```

---

## Example: Adjusting jobs' resource requirements

Suppose that jobs fail because they use too much CPU or memory.

```
> Check the resource utilization for workflow 20

⏺ torc - check_resource_utilization (MCP)(workflow_id: 20)
  ⎿  {
       "over_utilization_count": 1,
       "run_id": null,
     … +17 lines (ctrl+o to expand)

⏺ Resource Utilization for Workflow 20

  Summary: 3 job results analyzed, 1 resource violation found

  CPU Over-Utilization

  | Job ID | Job Name      | Specified      | Peak Used | Over By |
  |--------|---------------|----------------|-----------|---------|
  | 264    | cpu_heavy_job | 3 cores (300%) | 602.5%    | +100.8% |

  The cpu_heavy_job used approximately 6 CPU cores at peak, but was only allocated 3 cores.

  Would you like me to update the resource requirements for this job? I can increase the CPU allocation to 7 cores to provide headroom for future runs.

> yes

⏺ torc - update_job_resources (MCP)(job_id: 264, num_cpus: 7)
  ⎿  {
       "job_id": 264,
       "resource_requirements_id": 45,
     … +8 lines (ctrl+o to expand)

⏺ Done. Updated cpu_heavy_job (job 264) resources:

  | Setting | Value      |
  |---------|------------|
  | CPUs    | 7 (was 3)  |
  | Memory  | 1g         |
  | Runtime | 15 minutes |

  The job is now configured with enough CPU capacity for future runs.
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
