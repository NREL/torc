# Test Workflows

This directory contains workflow specifications for testing Torc features.
These are not intended for end users - they are for development and testing purposes.

## Workflows

### slurm_oom_test.yaml

Tests Slurm debugging features by intentionally triggering an Out-of-Memory (OOM) condition.

**Purpose:** Verify that the following tools correctly detect and report OOM failures:
- `torc slurm parse-logs` - Should find OOM-related errors in Slurm logs
- `torc slurm sacct` - Should show `OUT_OF_MEMORY` state in the summary table
- torc-dash Debugging tab - Should display the errors in the web UI
- torc TUI - Should allow viewing Slurm logs with 'l' key

**Usage:**
```bash
# Set your Slurm account (or the workflow will use 'default')
export SLURM_ACCOUNT=myaccount
export SLURM_PARTITION=standard
export SLURM_QOS=normal

# Create and submit the workflow
torc workflows create tests/workflows/slurm_oom_test.yaml
torc slurm schedule-nodes <workflow_id>

# Wait for job to fail (check with: squeue -u $USER)

# Test the debugging tools
torc slurm parse-logs <workflow_id>
torc slurm sacct <workflow_id>

# Or use the dashboard
torc-dash --standalone
# Navigate to Debugging tab
```

**Expected Results:**
- Job should fail within ~2-5 minutes after starting
- `parse-logs` should detect "oom-kill" or "out of memory" patterns
- `sacct` should show state as `OUT_OF_MEMORY` or `FAILED`
- Exit code should be non-zero (typically 137 for SIGKILL or 9 for OOM)
