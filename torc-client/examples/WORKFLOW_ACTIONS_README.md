# Workflow Actions Guide

## Overview

Workflow Actions allow you to automatically execute commands or allocate resources when specific conditions are met during workflow execution. This enables powerful automation patterns like:

- Running setup/cleanup scripts
- Dynamically allocating compute resources based on workload
- Archiving results when job groups complete
- Sending notifications at workflow milestones

## Action Types

### 1. `run_commands`

Execute shell commands when the trigger condition is met.

**Configuration:**
```yaml
- trigger_type: "on_workflow_start"
  action_type: "run_commands"
  commands:
    - "mkdir -p output logs"
    - "echo 'Workflow started' > logs/status.txt"
```

**Use Cases:**
- Creating directory structures
- Running initialization scripts
- Archiving/compressing results
- Sending notifications
- Cleanup operations

**Important Notes:**
- Commands run in the workflow's output directory
- Commands are executed sequentially
- If any command fails, the action fails (but workflow continues)
- Commands run on a compute node, not the submission node

### 2. `schedule_nodes`

Dynamically allocate compute nodes when jobs are ready.

**Configuration:**
```yaml
- trigger_type: "on_jobs_ready"
  action_type: "schedule_nodes"
  job_name_regexes: ["train_model_.*"]
  scheduler_name: "gpu_cluster"
  scheduler_type: "slurm"
  num_allocations: 2
  start_one_worker_per_node: true
  max_parallel_jobs: 8
```

**Use Cases:**
- Auto-scaling for large job arrays
- Just-in-time resource allocation
- Cost optimization (allocate only when needed)
- Separating phases with different resource requirements

**Important Notes:**
- Requires a scheduler configuration (e.g., `slurm_schedulers`)
- Creates scheduled compute node records
- Actual node allocation handled by scheduler system
- Enables elastic scaling patterns

## Trigger Types

### `on_workflow_start`

Triggered once when the workflow begins execution.

**When it fires:** After workflow initialization, when job execution starts

**Example:**
```yaml
- trigger_type: "on_workflow_start"
  action_type: "run_commands"
  commands:
    - "echo 'Starting workflow' | tee workflow.log"
    - "mkdir -p output checkpoints temp"
```

**Best Practices:**
- Use for one-time setup operations
- Create directory structures
- Initialize logging
- Check environment prerequisites

### `on_workflow_complete`

Triggered once when all jobs reach terminal states (completed/failed/canceled).

**When it fires:** After all jobs are done, before workflow shutdown

**Example:**
```yaml
- trigger_type: "on_workflow_complete"
  action_type: "run_commands"
  commands:
    - "tar -czf results.tar.gz output/"
    - "aws s3 cp results.tar.gz s3://bucket/"
    - "rm -rf temp/"
```

**Best Practices:**
- Archive final results
- Upload to remote storage
- Send completion notifications
- Cleanup temporary files
- Generate summary reports

### `on_jobs_ready`

Triggered when ALL specified jobs reach the "ready" status.

**When it fires:** When all jobs matching the patterns are ready to execute

**Example:**
```yaml
- trigger_type: "on_jobs_ready"
  action_type: "schedule_nodes"
  job_name_regexes: ["train_.*"]
  scheduler_name: "gpu_cluster"
  scheduler_type: "slurm"
  num_allocations: 4
```

**Job Selection:**
- `job_name_patterns`: List of exact job names
- `job_name_regexes`: List of regex patterns
- Can use both together (union of matches)

**Best Practices:**
- Use for just-in-time resource allocation
- Trigger notifications before expensive operations
- Start monitoring/logging for job phases

### `on_jobs_complete`

Triggered when ALL specified jobs reach terminal states.

**When it fires:** When all matching jobs are done (completed/failed/canceled)

**Example:**
```yaml
- trigger_type: "on_jobs_complete"
  action_type: "run_commands"
  job_name_regexes: ["preprocess_.*"]
  commands:
    - "echo 'Preprocessing complete'"
    - "rm -rf raw_data/"
```

**Best Practices:**
- Clean up intermediate files
- Archive phase results
- Trigger next phase notifications
- Free up storage space

## Job Selection Patterns

### Exact Job Names

Use `job_name_patterns` for exact matches:

```yaml
- trigger_type: "on_jobs_complete"
  action_type: "run_commands"
  job_name_patterns: ["job1", "job2", "job3"]
  commands:
    - "echo 'Specific jobs complete'"
```

### Regular Expressions

Use `job_name_regexes` for pattern matching:

```yaml
- trigger_type: "on_jobs_ready"
  action_type: "schedule_nodes"
  job_name_regexes: ["train_model_[0-9]+", "eval_.*"]
  scheduler_name: "gpu_cluster"
  scheduler_type: "slurm"
  num_allocations: 2
```

**Common Patterns:**
- `"train_.*"` - All jobs starting with "train_"
- `"model_[0-9]+"` - Jobs like "model_1", "model_2", etc.
- `".*_stage1"` - All jobs ending with "_stage1"
- `"job_(a|b|c)"` - Jobs named "job_a", "job_b", or "job_c"

### Combining Patterns

You can use both together:

```yaml
job_name_patterns: ["important_job"]
job_name_regexes: ["batch_.*"]
```

This will trigger when both "important_job" AND all jobs matching "batch_.*" are ready/complete.

## Complete Examples

### Example 1: Simple Setup and Cleanup

See [`workflow_actions_simple.yaml`](./workflow_actions_simple.yaml)

**Features:**
- Workspace initialization on start
- Result archiving on completion
- Temporary file cleanup

**Run:**
```bash
torc-client workflows create-from-spec examples/workflow_actions_simple.yaml
torc-client workflows start <workflow_id>
torc-job-runner <workflow_id>
```

### Example 2: ML Training with Auto-Scaling

See [`workflow_actions_ml_training.yaml`](./workflow_actions_ml_training.yaml)

**Features:**
- Dynamic GPU allocation when training jobs are ready
- Model archiving after training completes
- S3 upload on workflow completion
- Multiple action phases

**Key Pattern:**
```yaml
# Allocate GPUs just-in-time
- trigger_type: "on_jobs_ready"
  action_type: "schedule_nodes"
  job_name_regexes: ["train_model_.*"]
  scheduler_name: "gpu_cluster"
  num_allocations: 2
```

### Example 3: Data Pipeline with Cleanup

See [`workflow_actions_data_pipeline.yaml`](./workflow_actions_data_pipeline.yaml)

**Features:**
- Progressive cleanup of intermediate data
- Phase-based logging
- Storage optimization
- Notification integration

**Key Pattern:**
```yaml
# Clean up after each phase
- trigger_type: "on_jobs_complete"
  action_type: "run_commands"
  job_name_regexes: ["validate_.*"]
  commands:
    - "rm -rf raw/*.tar.gz"  # Free space after validation
```

## Best Practices

### 1. Action Idempotency

Actions should be safe to run multiple times (in case of retries):

**Good:**
```yaml
commands:
  - "mkdir -p output"  # Won't fail if exists
  - "rm -rf temp || true"  # Won't fail if doesn't exist
```

**Avoid:**
```yaml
commands:
  - "mkdir output"  # Fails if exists
  - "rm -rf temp"  # Fails if doesn't exist
```

### 2. Error Handling

Use shell error handling for robustness:

```yaml
commands:
  - "aws s3 cp results/ s3://bucket/ --recursive || echo 'Upload failed, continuing...'"
  - "curl -X POST $WEBHOOK || echo 'Notification failed'"
```

### 3. Logging

Always log actions for debugging:

```yaml
commands:
  - "echo '[ACTION] Starting cleanup at $(date)' | tee -a workflow.log"
  - "rm -rf temp"
  - "echo '[ACTION] Cleanup complete' | tee -a workflow.log"
```

### 4. Resource Allocation Timing

For `schedule_nodes`, consider job startup time:

```yaml
# Allocate nodes early so they're ready when jobs start
- trigger_type: "on_jobs_ready"
  action_type: "schedule_nodes"
  job_name_regexes: ["compute_.*"]
  num_allocations: 10
```

### 5. Cleanup Ordering

Clean up in reverse dependency order:

```yaml
# 1. Clean intermediate results after they're consumed
- trigger_type: "on_jobs_complete"
  job_name_regexes: ["phase1_.*"]
  commands: ["rm -rf phase1_intermediate/"]

# 2. Final cleanup after everything
- trigger_type: "on_workflow_complete"
  commands: ["rm -rf temp/ cache/"]
```

## Debugging Actions

### Check Action Status

```bash
# List all actions for a workflow
curl http://localhost:8080/torc-service/v1/workflows/<workflow_id>/actions

# Check pending actions
curl http://localhost:8080/torc-service/v1/workflows/<workflow_id>/actions/pending
```

### View Action Execution

Actions are executed by JobRunners. Check the job runner logs:

```bash
# Look for action-related log messages
RUST_LOG=info torc-job-runner <workflow_id>
```

You'll see messages like:
```
INFO Executing action 1 (trigger: on_workflow_start)
INFO Executing command: mkdir -p output
INFO Command output: ...
```

### Common Issues

**Action never triggers:**
- Check that trigger condition is actually met
- Verify job name patterns match actual job names
- Ensure action wasn't already executed (check `executed` field)

**Command fails:**
- Check command syntax (test locally first)
- Verify file paths relative to output directory
- Check for required environment variables
- Look at stderr in job runner logs

**schedule_nodes doesn't work:**
- Verify scheduler configuration exists
- Check scheduler_name matches slurm_schedulers name
- Ensure compute resources are available

## Advanced Patterns

### Multi-Stage Pipeline

```yaml
actions:
  # Stage 1: Download
  - trigger_type: "on_jobs_ready"
    job_name_regexes: ["download_.*"]
    action_type: "run_commands"
    commands: ["echo 'Download phase starting'"]

  # Stage 2: Process (allocate big nodes)
  - trigger_type: "on_jobs_ready"
    job_name_regexes: ["process_.*"]
    action_type: "schedule_nodes"
    scheduler_name: "large_mem"
    num_allocations: 5

  # Stage 3: Cleanup after process
  - trigger_type: "on_jobs_complete"
    job_name_regexes: ["process_.*"]
    action_type: "run_commands"
    commands: ["rm -rf downloads/"]
```

### Conditional Notifications

```yaml
- trigger_type: "on_workflow_complete"
  action_type: "run_commands"
  commands:
    - |
      if [ -f errors.log ]; then
        curl -X POST $WEBHOOK -d '{"status":"completed_with_errors"}'
      else
        curl -X POST $WEBHOOK -d '{"status":"success"}'
      fi
```

### Progressive Scaling

```yaml
# Allocate initial nodes
- trigger_type: "on_jobs_ready"
  job_name_regexes: ["batch_.*"]
  action_type: "schedule_nodes"
  scheduler_name: "cluster"
  num_allocations: 5

# Allocate more nodes after first batch completes
- trigger_type: "on_jobs_complete"
  job_name_patterns: ["batch_0", "batch_1", "batch_2"]
  action_type: "schedule_nodes"
  scheduler_name: "cluster"
  num_allocations: 10
```

## Limitations and Considerations

1. **Execution Guarantee:** Actions are executed at-most-once per workflow (atomic claiming prevents duplicates)

2. **No Rollback:** Failed actions don't roll back the workflow - workflow continues

3. **Compute Node Execution:** Actions run on compute nodes, not the submission node

4. **Timing:** Actions trigger when conditions are first met - not continuously

5. **Dependencies:** Actions don't have dependencies on each other (use job dependencies instead)

## API Reference

For programmatic action management:

```bash
# Create an action
POST /workflows/{workflow_id}/actions
{
  "workflow_id": 1,
  "trigger_type": "on_workflow_start",
  "action_type": "run_commands",
  "action_config": "{\"commands\":[\"echo hello\"]}",
  "job_ids": null
}

# Get all actions
GET /workflows/{workflow_id}/actions

# Get pending actions
GET /workflows/{workflow_id}/actions/pending

# Claim an action (used by JobRunner)
POST /workflows/{workflow_id}/actions/{action_id}/claim
{
  "compute_node_id": 5
}
```

## Further Reading

- [Main README](./README.md) - General Torc examples
- [Resource Monitoring](./RESOURCE_MONITORING_README.md) - Resource tracking
- [Parameterized Jobs](./hundred_jobs_parameterized.yaml) - Job parameters
- [Workflow Specification](../../CLAUDE.md) - Full workflow spec reference
