# How to Generate Workflow Reports

This guide shows how to check workflow completion status and generate summary reports.

## Check if a Workflow is Complete

Before generating reports, verify that your workflow has finished:

```bash
torc workflows is-complete <workflow_id>
```

If you omit the workflow ID, you'll be prompted to select from your workflows:

```bash
torc workflows is-complete
```

Example output:

```
Workflow 42 completion status:
  Is Complete: true
  Is Canceled: false
  Needs Completion Script: false
```

For JSON output:

```bash
torc workflows is-complete <workflow_id> -f json
```

## Generate a Workflow Summary

Once a workflow is complete, generate a summary report:

```bash
torc reports summary <workflow_id>
```

If you omit the workflow ID, you'll be prompted to select from your workflows:

```bash
torc reports summary
```

Example output:

```
Workflow Summary
================

Workflow ID: 42
Name: data_processing_pipeline
User: jsmith

Job Status:
  Total Jobs: 100
  Completed:  95 ✓
  Failed:     5 ✗

Total Execution Time: 2h 30m 15s
```

If all jobs succeeded:

```
Workflow Summary
================

Workflow ID: 42
Name: simulation_run
User: jsmith

Job Status:
  Total Jobs: 50
  Completed:  50 ✓
  Failed:     0

Total Execution Time: 45m 30s

✓ All jobs completed successfully!
```

For JSON output (useful for scripting):

```bash
torc reports summary <workflow_id> -f json
```

```json
{
  "workflow_id": 42,
  "workflow_name": "data_processing_pipeline",
  "workflow_user": "jsmith",
  "is_complete": true,
  "total_jobs": 100,
  "completed_jobs": 95,
  "failed_jobs": 5,
  "canceled_jobs": 0,
  "other_jobs": 0,
  "total_exec_time_minutes": 150.25,
  "total_exec_time_formatted": "2h 30m 15s"
}
```

## Handle Incomplete Workflows

If you try to generate a summary for an incomplete workflow, the command will exit with an error:

```bash
$ torc reports summary 42
Error: Workflow 42 is not complete.
Wait for the workflow to finish before generating a summary.
```

To check workflow progress instead, use:

```bash
torc workflows status <workflow_id>
```

## Use in Scripts

Combine these commands in automation scripts:

```bash
#!/bin/bash
WORKFLOW_ID=$1

# Check completion status
if torc workflows is-complete "$WORKFLOW_ID" -f json | jq -e '.is_complete' > /dev/null; then
    echo "Workflow complete, generating summary..."
    torc reports summary "$WORKFLOW_ID" -f json > "summary_${WORKFLOW_ID}.json"
else
    echo "Workflow not yet complete"
    exit 1
fi
```

## Related Commands

- `torc workflows status <id>` - View current job status counts
- `torc results list <id>` - List individual job results
- `torc reports check-resource-utilization <id>` - Check for resource violations
- `torc reports results <id>` - Generate detailed results with log file paths

## Next Steps

- [Resource Monitoring](./resource-monitoring.md) - Track CPU and memory usage
- [Debugging Workflows](./debugging.md) - Troubleshoot failed jobs
