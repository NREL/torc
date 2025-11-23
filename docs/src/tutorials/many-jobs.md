# Tutorial 1: Many Independent Jobs

**Goal**: Create a workflow with 100 independent parallel jobs.

**Use Case**: Parameter sweeps, Monte Carlo simulations, batch processing.

## Step 1: Start the Torc server
```console
torc-server
```
By default, the server will listen on port 8080, making the default API URL for the client
`http://localhost:8080/torc-service/v1`. If you change the port, set the environment variable
`TORC_API_URL` to the new URL.

This step is unnecessary if you use default values. This assumes a custom port of 8100.
```console
export TORC_API_URL="http://localhost:8100/torc-service/v1"
```

## Step 1: Create Workflow Specification

Save as `hundred_jobs.yaml`:

```yaml
name: hundred_jobs_parallel
description: 100 independent jobs that can run in parallel

jobs:
  - name: job_{i:03d}
    command: |
      echo "Running job {i}"
      sleep $((RANDOM % 10 + 1))
      echo "Job {i} completed"
    resource_requirements: minimal
    parameters:
      i: "1:100"

resource_requirements:
  - name: minimal
    num_cpus: 1
    num_gpus: 0
    num_nodes: 1
    memory: 1g
    runtime: PT5M
```

## Step 2: Create and run the workflow

```bash
# Run the workflow
torc workflows run hundred_jobs.yaml

# Note that it will print the workflow ID to the console.

# When complete, check the results.
torc results list <workflow_id>
```

The runner will:
- Pull ready jobs from the server
- Execute them in parallel (respecting resource limits)
- Report results back to the server
