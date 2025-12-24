# Recovery Hook Test

This test verifies that `torc watch --recovery-hook` correctly invokes a custom
recovery script when jobs fail with unknown causes.

## Workflow Description

- **5 work jobs** (`work_1` through `work_5`): Each requires 10GB memory and 30 CPUs
- **1 postprocess job**: Runs after all work jobs complete, requires 1GB memory and 1 CPU
- **work_3** is designed to fail on the first run because it expects a file that doesn't exist

## Test Procedure

### 1. Update the account in workflow.yaml

Replace `PLACEHOLDER_ACCOUNT` with your actual Slurm account:

```bash
sed -i 's/PLACEHOLDER_ACCOUNT/your_account/g' workflow.yaml
```

### 2. Submit the workflow

```bash
torc submit-slurm --account <your_account> workflow.yaml
```

Note the workflow ID from the output.

### 3. Run the watcher with recovery hook

```bash
export TORC_OUTPUT_DIR=output
torc watch <workflow_id> --auto-recover --recovery-hook "bash create_missing_file.sh"
```

### 4. Expected behavior

1. Jobs `work_1`, `work_2`, `work_4`, `work_5` complete successfully
2. Job `work_3` fails because `output/required_input.txt` doesn't exist
3. The watcher detects the failure as "unknown" (not OOM or timeout)
4. The recovery hook (`create_missing_file.sh`) is executed
5. The hook creates `output/required_input.txt`
6. Failed jobs are reset and the workflow is resubmitted
7. On retry, `work_3` finds the file and completes successfully
8. `postprocess` runs after all work jobs complete
9. Workflow completes successfully

## Files

- `workflow.yaml` - The workflow specification
- `create_missing_file.sh` - Recovery hook script that creates the missing file
- `README.md` - This file

## Verification

After the test completes successfully:

```bash
# Check workflow status
torc workflows status <workflow_id>

# Verify all jobs completed
torc jobs list <workflow_id>

# Check that the file was created
cat output/required_input.txt
```
