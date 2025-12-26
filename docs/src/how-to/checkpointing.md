# How to Checkpoint a Job During Wall-Time Timeout

When running jobs on HPC systems like Slurm, your job may be terminated when the allocated wall-time
expires. Torc supports **graceful termination**, allowing jobs to save checkpoints before exiting.
This guide explains how to configure Slurm and your jobs to handle wall-time timeouts gracefully.

## Overview

When Slurm is about to reach wall-time, it can be configured to send a SIGTERM signal to the Torc
worker process. Torc then:

1. Sends SIGTERM to jobs with `supports_termination: true`
2. Sends SIGKILL to jobs with `supports_termination: false` (or unset)
3. Waits for all processes to exit
4. Reports job status as `terminated` to the server

Jobs that support termination can catch SIGTERM and perform cleanup operations like saving
checkpoints, flushing buffers, or releasing resources.

## Enabling Graceful Termination

### Configuring Slurm to Send a Signal Before Timeout

By default, Slurm does **not** send any signal before the job's end time. When the wall-time limit
is reached, Slurm immediately terminates all processes. To receive a warning signal before timeout,
you must explicitly configure it using the `--signal` option in the `extra` field of your Slurm
scheduler specification:

```yaml
slurm_schedulers:
  - name: gpu_scheduler
    account: my_project
    partition: gpu
    nodes: 1
    walltime: "04:00:00"
    extra: "--signal=B:TERM@300"  # Send SIGTERM to batch script 300 seconds before timeout
```

The `--signal` option format is `[B:]<sig_num>[@sig_time]`:

- `B:` prefix sends the signal only to the batch shell (by default, all job steps are signaled but
  not the batch shell itself)
- `sig_num` is the signal name or number (e.g., `TERM`, `USR1`, `10`)
- `sig_time` is seconds before the time limit to send the signal (default: 60 if not specified)

Note: Due to Slurm's event handling resolution, the signal may be sent up to 60 seconds earlier than
specified.

To enable graceful termination for a job, set `supports_termination: true` in your job
specification:

### Configuring a Torc job to be terminated gracefully

```yaml
jobs:
  - name: training_job
    command: python train.py --checkpoint-dir /scratch/checkpoints
    supports_termination: true
    resource_requirements:
      num_cpus: 4
      memory: 16g
      runtime: PT2H
```

## Writing a Job That Handles SIGTERM

Your job script must catch SIGTERM and save its state. Here's a Python example:

```python
import signal
import sys
import pickle

# Global state
checkpoint_path = "/scratch/checkpoints/model.pkl"
model_state = None

def save_checkpoint():
    """Save current model state to disk."""
    print("Saving checkpoint...")
    with open(checkpoint_path, 'wb') as f:
        pickle.dump(model_state, f)
    print(f"Checkpoint saved to {checkpoint_path}")

def handle_sigterm(signum, frame):
    """Handle SIGTERM by saving checkpoint and exiting."""
    print("Received SIGTERM - saving checkpoint before exit")
    save_checkpoint()
    sys.exit(0)  # Exit cleanly after saving

# Register the signal handler
signal.signal(signal.SIGTERM, handle_sigterm)

# Main training loop
def train():
    global model_state
    for epoch in range(1000):
        # Training logic here...
        model_state = {"epoch": epoch, "weights": [...]}

        # Optionally save periodic checkpoints
        if epoch % 100 == 0:
            save_checkpoint()

if __name__ == "__main__":
    train()
```

### Bash Script Example

For shell scripts, use `trap` to catch SIGTERM:

```bash
#!/bin/bash

CHECKPOINT_FILE="/scratch/checkpoints/progress.txt"

# Function to save checkpoint
save_checkpoint() {
    echo "Saving checkpoint at iteration $ITERATION"
    echo "$ITERATION" > "$CHECKPOINT_FILE"
}

# Trap SIGTERM and save checkpoint
trap 'save_checkpoint; exit 0' SIGTERM

# Load checkpoint if exists
if [ -f "$CHECKPOINT_FILE" ]; then
    ITERATION=$(cat "$CHECKPOINT_FILE")
    echo "Resuming from iteration $ITERATION"
else
    ITERATION=0
fi

# Main loop
while [ $ITERATION -lt 1000 ]; do
    # Do work...
    ITERATION=$((ITERATION + 1))
    sleep 1
done
```

### Complete Workflow Example

```yaml
name: ml_training_workflow
user: researcher

jobs:
  - name: preprocess
    command: python preprocess.py
    supports_termination: false  # Quick job, no checkpointing needed

  - name: train_model
    command: python train.py --checkpoint-dir /scratch/checkpoints
    supports_termination: true   # Long job, needs checkpointing
    depends_on:
      - preprocess
    resource_requirements:
      num_cpus: 8
      memory: 32g
      num_gpus: 1
      runtime: PT4H

  - name: evaluate
    command: python evaluate.py
    supports_termination: true
    depends_on:
      - train_model

slurm_schedulers:
  - name: gpu_scheduler
    account: my_project
    partition: gpu
    nodes: 1
    walltime: "04:00:00"
    extra: "--signal=B:TERM@300"  # Send SIGTERM to batch script 300 seconds before timeout

actions:
  - trigger_type: on_workflow_start
    action_type: schedule_nodes
    scheduler: gpu_scheduler
    scheduler_type: slurm
    num_allocations: 1
```

## Restarting After Termination

When a job is terminated due to wall-time, it will have status `terminated`. To continue the
workflow:

1. **Re-submit the workflow** to allocate new compute time:
   ```bash
   torc workflows submit $WORKFLOW_ID
   ```

2. **Reinitialize terminated jobs** to make them ready again:
   ```bash
   torc workflows reinitialize $WORKFLOW_ID
   ```

Your job script should detect existing checkpoints and resume from where it left off.

## Best Practices

### 1. Verify Checkpoint Integrity

Add validation to ensure checkpoints are complete:

```python
def save_checkpoint():
    temp_path = checkpoint_path + ".tmp"
    with open(temp_path, 'wb') as f:
        pickle.dump(model_state, f)
    # Atomic rename ensures complete checkpoint
    os.rename(temp_path, checkpoint_path)
```

### 2. Handle Multiple Termination Signals

Some systems send multiple signals. Ensure your handler is idempotent:

```python
checkpoint_saved = False

def handle_sigterm(signum, frame):
    global checkpoint_saved
    if not checkpoint_saved:
        save_checkpoint()
        checkpoint_saved = True
    sys.exit(0)
```

### 3. Test Locally

Test your SIGTERM handling locally before running on the cluster:

```bash
# Start your job
python train.py &
PID=$!

# Wait a bit, then send SIGTERM
sleep 10
kill -TERM $PID

# Verify checkpoint was saved
ls -la /scratch/checkpoints/
```

## Troubleshooting

### Job Killed Without Checkpointing

**Symptoms:** Job status is `terminated` but no checkpoint was saved.

**Causes:**

- `supports_termination` not set to `true`
- Signal handler not registered before training started
- Checkpoint save took longer than the buffer time

**Solutions:**

- Verify `supports_termination: true` in job spec
- Register signal handlers early in your script

### Checkpoint File Corrupted

**Symptoms:** Job fails to load checkpoint on restart.

**Causes:**

- Job was killed during checkpoint write
- Disk space exhausted

**Solutions:**

- Use atomic file operations (write to temp, then rename)
- Check available disk space before checkpointing
- Implement checkpoint validation on load

### Job Doesn't Receive SIGTERM

**Symptoms:** Job runs until hard kill with no graceful shutdown.

**Causes:**

- Job running in a subprocess that doesn't forward signals
- Container or wrapper script intercepting signals

**Solutions:**

- Use `exec` in wrapper scripts to replace the shell
- Configure signal forwarding in containers
- Run the job directly without wrapper scripts

## See Also

- [Working with Slurm](./slurm.md) - General Slurm configuration
- [Managing Resources](./resources.md) - Resource requirements configuration
- [Debugging Workflows](./debugging.md) - Troubleshooting workflow issues
- [Slurm sbatch --signal option](https://slurm.schedmd.com/sbatch.html#OPT_signal) - Customize which
  signal is sent and when before wall-time timeout
