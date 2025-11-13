# Tutorial 1: Many Independent Jobs

**Goal**: Create a workflow with 100 independent parallel jobs.

**Use Case**: Parameter sweeps, Monte Carlo simulations, batch processing.

## Step 1: Create Workflow Specification

Save as `hundred_jobs.yaml`:

```yaml
name: hundred_jobs_parallel
user: myuser
description: 100 independent jobs that can run in parallel

jobs:
  - name: job_{i:03d}
    command: |
      echo "Running job {i}"
      sleep $((RANDOM % 10 + 1))
      echo "Job {i} completed"
    resource_requirements_name: minimal
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

## Step 2: Create and Start Workflow

```bash
# Set server URL
export TORC_BASE_URL="http://localhost:8080/torc-service/v1"

# Create workflow from spec
WORKFLOW_ID=$(torc-client workflows create-from-spec hundred_jobs.yaml \
  | jq -r '.id')

echo "Created workflow $WORKFLOW_ID"

# Initialize jobs (marks them ready)
torc-client workflows initialize-jobs $WORKFLOW_ID

# Check workflow status
torc-client workflows status $WORKFLOW_ID
```

## Step 3: Run Jobs Locally

```bash
# Start local job runner
torc-job-runner $WORKFLOW_ID
```

The runner will:
- Pull ready jobs from the server
- Execute them in parallel (respecting resource limits)
- Report results back to the server

## Step 4: Monitor Progress

In another terminal:

```bash
# Watch job counts by status
watch -n 5 'torc-client jobs list-by-status $WORKFLOW_ID | jq'

# View completed jobs
torc-client jobs list $WORKFLOW_ID --status completed | jq '.jobs[] | {name, status}'
```

## Expected Behavior

- All 100 jobs start in `ready` state (no dependencies)
- Runner executes jobs in parallel based on available CPUs
- Jobs complete independently
- Workflow finishes when all jobs reach `completed` status
