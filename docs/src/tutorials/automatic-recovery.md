# Tutorial: Automatic Failure Recovery

This tutorial shows how to use `torc watch` with automatic recovery to handle workflow failures without manual intervention.

## Learning Objectives

By the end of this tutorial, you will:

- Understand automatic vs manual recovery options
- Know how to configure automatic recovery heuristics
- Monitor workflows with automatic failure handling

## Prerequisites

- Torc installed with the client feature
- A running Torc server
- Workflows submitted to Slurm

## Automatic Recovery

The `torc watch` command can automatically recover from common failures:

```bash
torc watch 42 --auto-recover
```

This will:
1. Poll the workflow until completion
2. On failure, diagnose the cause (OOM, timeout, etc.)
3. Adjust resource requirements based on heuristics
4. Reset failed jobs and submit new Slurm allocations
5. Resume monitoring
6. Repeat until success or max retries exceeded

### Recovery Heuristics

| Failure Type | Detection | Default Action |
|--------------|-----------|----------------|
| Out of Memory | Peak memory > limit, exit code 137 | Increase memory by 1.5x |
| Timeout | Execution time near limit | Increase runtime by 1.5x |
| Unknown | Other exit codes | Retry without changes |

### Configuration Options

```bash
torc watch 42 --auto-recover \
  --max-retries 5 \           # Maximum recovery attempts (default: 3)
  --memory-multiplier 2.0 \   # Memory increase factor (default: 1.5)
  --runtime-multiplier 2.0 \  # Runtime increase factor (default: 1.5)
  --poll-interval 120 \       # Seconds between status checks (default: 60)
  --output-dir /scratch/output \
  --show-job-counts           # Display per-status job counts (optional, adds server load)
```

## Example: Complete Workflow

### 1. Submit a Workflow

```bash
torc submit-slurm --account myproject workflow.yaml
```

Output:
```
Created workflow 42 with 100 jobs
Submitted to Slurm with 10 allocations
```

### 2. Start Watching with Auto-Recovery

```bash
torc watch 42 --auto-recover --max-retries 3 --show-job-counts
```

> **Note:** The `--show-job-counts` flag is optional. Without it, the command polls
> silently until completion, which reduces server load for large workflows.

Output:
```
Watching workflow 42 (poll interval: 60s, auto-recover enabled, max retries: 3, job counts enabled)
  completed=0, running=10, pending=0, failed=0, blocked=90
  completed=25, running=10, pending=0, failed=0, blocked=65
  ...
  completed=95, running=0, pending=0, failed=5, blocked=0
Workflow 42 is complete

Workflow completed with failures:
  - Failed: 5
  - Canceled: 0
  - Terminated: 0
  - Completed: 95

Attempting automatic recovery (attempt 1/3)

Diagnosing failures...
Applying recovery heuristics...
  Job 107 (train_model_7): OOM detected, increasing memory 8g -> 12g
  Job 112 (train_model_12): OOM detected, increasing memory 8g -> 12g
  Job 123 (train_model_23): OOM detected, increasing memory 8g -> 12g
  Job 131 (train_model_31): OOM detected, increasing memory 8g -> 12g
  Job 145 (train_model_45): OOM detected, increasing memory 8g -> 12g
  Applied fixes: 5 OOM, 0 timeout

Resetting failed jobs...
Regenerating Slurm schedulers and submitting...

Recovery initiated. Resuming monitoring...

Watching workflow 42 (poll interval: 60s, auto-recover enabled, max retries: 3, job counts enabled)
  completed=95, running=5, pending=0, failed=0, blocked=0
  ...
Workflow 42 is complete

✓ Workflow completed successfully (100 jobs)
```

### 3. If Max Retries Exceeded

If failures persist after max retries:

```
Max retries (3) exceeded. Manual intervention required.
Use the Torc MCP server with your AI assistant to investigate.
```

At this point, you can use the MCP server with an AI assistant to investigate the root cause.

## Manual Recovery (Without --auto-recover)

Without the `--auto-recover` flag, `torc watch` simply monitors and reports:

```bash
torc watch 42
```

On failure, it exits with instructions:

```
Workflow completed with failures:
  - Failed: 5
  - Completed: 95

Auto-recovery disabled. To enable, use --auto-recover flag.
Or use the Torc MCP server with your AI assistant for manual recovery.
```

## When to Use Each Approach

### Use Automatic Recovery (`--auto-recover`) when:
- Running standard compute jobs with predictable failure modes
- You want hands-off operation
- OOM and timeout are the main failure types
- You have HPC allocation budget for retries

### Use Manual/AI-Assisted Recovery when:
- Failures have complex or unknown causes
- You need to investigate before retrying
- Resource increases aren't solving the problem
- You want to understand why jobs are failing

## Best Practices

### 1. Start with Conservative Resources

Set initial resource requests lower and let auto-recovery increase them:
- Jobs that succeed keep their original allocation
- Only failing jobs get increased resources
- Avoids wasting HPC resources on over-provisioned jobs

### 2. Set Reasonable Max Retries

```bash
--max-retries 3  # Good for most workflows
```

Too many retries can waste allocation time on jobs that will never succeed.

### 3. Use Appropriate Multipliers

For memory-bound jobs:
```bash
--memory-multiplier 2.0  # Double on OOM
```

For time-sensitive jobs where you want larger increases:
```bash
--runtime-multiplier 2.0  # Double runtime on timeout
```

### 4. Monitor Long-Running Workflows

**Always run `torc watch` inside tmux or screen** for long-running workflows. HPC workflows can run for hours or days, and you don't want to lose your monitoring session if:

- Your SSH connection drops
- Your laptop goes to sleep
- You need to disconnect and reconnect later

Using [tmux](https://github.com/tmux/tmux/wiki) (recommended):

```bash
# Start a new tmux session
tmux new -s torc-watch

# Run the watch command
torc watch 42 --auto-recover --poll-interval 300 --show-job-counts

# Detach from session: press Ctrl+b, then d
# Reattach later: tmux attach -t torc-watch
```

Using screen:
```bash
screen -S torc-watch
torc watch 42 --auto-recover --poll-interval 300 --show-job-counts
# Detach: Ctrl+a, then d
# Reattach: screen -r torc-watch
```

For very large workflows, omit `--show-job-counts` to reduce server load.

### 5. Check Resource Utilization Afterward

After completion, review actual usage:
```bash
torc reports check-resource-utilization 42
```

This helps tune future job specifications.

## Troubleshooting

### Jobs Keep Failing After Recovery

If jobs fail repeatedly with the same error:
1. Check if the error is resource-related (OOM/timeout)
2. Review job logs: `torc jobs logs <job_id>`
3. Check if there's a code bug
4. Use MCP server with AI assistant to investigate

### No Slurm Schedulers Generated

If `slurm regenerate` fails:
1. Ensure workflow was created with `--account` option
2. Check HPC profile is detected: `torc hpc detect`
3. Specify profile explicitly: `--profile kestrel`

### Resource Limits Too High

If jobs are requesting more resources than partitions allow:
1. Check partition limits: `torc hpc partitions <profile>`
2. Use smaller multipliers
3. Consider splitting jobs into smaller pieces

## Summary

The `torc watch --auto-recover` command provides:

- **Automatic OOM handling**: Detects memory issues and increases allocations
- **Automatic timeout handling**: Detects slow jobs and increases runtime
- **Configurable heuristics**: Adjust multipliers for your workload
- **Retry limits**: Prevent infinite retry loops
- **Graceful degradation**: Falls back to manual recovery when needed

For most HPC workflows, automatic recovery handles 80-90% of transient failures without human intervention.
