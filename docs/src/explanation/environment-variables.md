# Environment Variables

When Torc executes jobs, it automatically sets several environment variables that provide context about the job and enable communication with the Torc server. These variables are available to all job commands during execution.

## Variables Set During Job Execution

### TORC_WORKFLOW_ID

The unique identifier of the workflow that contains this job.

- **Type**: Integer (provided as string)
- **Example**: `"42"`
- **Use case**: Jobs can use this to query workflow information or to organize output files by workflow

```bash
# Example: Create a workflow-specific output directory
mkdir -p "/data/results/workflow_${TORC_WORKFLOW_ID}"
echo "Processing data..." > "/data/results/workflow_${TORC_WORKFLOW_ID}/output.txt"
```

### TORC_JOB_ID

The unique identifier of the currently executing job.

- **Type**: Integer (provided as string)
- **Example**: `"123"`
- **Use case**: Jobs can use this for logging, creating job-specific output files, or querying job metadata

```bash
# Example: Log job-specific information
echo "Job ${TORC_JOB_ID} started at $(date)" >> "/var/log/torc/job_${TORC_JOB_ID}.log"
```

### TORC_API_URL

The URL of the Torc API server that the job runner is communicating with.

- **Type**: String (URL)
- **Example**: `"http://localhost:8080/torc-service/v1"`
- **Use case**: Jobs can make API calls to the Torc server to query data, create files, update user data, or perform other operations

```bash
# Example: Query workflow information from within a job
curl -s "${TORC_API_URL}/workflows/${TORC_WORKFLOW_ID}" | jq '.name'

# Example: Create a file entry in Torc
curl -X POST "${TORC_API_URL}/files" \
  -H "Content-Type: application/json" \
  -d "{
    \"workflow_id\": ${TORC_WORKFLOW_ID},
    \"name\": \"result_${TORC_JOB_ID}\",
    \"path\": \"/data/results/output.txt\"
  }"
```

## Implementation Details

These environment variables are set by the job runner when spawning job processes. The implementation can be found in `src/client/async_cli_command.rs` in the `start()` method.

## Complete Example

Here's a complete example of a job that uses all three environment variables:

```yaml
name: "Environment Variables Demo"
user: "demo"

jobs:
  - name: "example_job"
    command: |
      #!/bin/bash
      set -e

      echo "=== Job Environment ==="
      echo "Workflow ID: ${TORC_WORKFLOW_ID}"
      echo "Job ID: ${TORC_JOB_ID}"
      echo "API URL: ${TORC_API_URL}"

      # Create job-specific output directory
      OUTPUT_DIR="/tmp/workflow_${TORC_WORKFLOW_ID}/job_${TORC_JOB_ID}"
      mkdir -p "${OUTPUT_DIR}"

      # Do some work
      echo "Processing data..." > "${OUTPUT_DIR}/status.txt"
      date >> "${OUTPUT_DIR}/status.txt"

      # Register the output file with Torc
      curl -X POST "${TORC_API_URL}/files" \
        -H "Content-Type: application/json" \
        -d "{
          \"workflow_id\": ${TORC_WORKFLOW_ID},
          \"name\": \"job_${TORC_JOB_ID}_output\",
          \"path\": \"${OUTPUT_DIR}/status.txt\"
        }"

      echo "Job completed successfully!"
```

## Notes

- All environment variables are set as strings, even numeric values like workflow and job IDs
- The `TORC_API_URL` includes the full base path to the API (e.g., `/torc-service/v1`)
- Jobs inherit all other environment variables from the job runner process
- These variables are available in both local and Slurm-scheduled job executions
