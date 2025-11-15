# Job Runners

Job runners are worker processes that execute jobs on compute resources.

## Job Runner Modes

1. **Local Runner** (`torc run-jobs`) - Runs jobs on local machine with resource tracking
2. **Slurm Runner** (`torc-slurm-job-runner`) - Submits jobs to Slurm clusters

## Job Allocation Strategies

The job runner supports two different strategies for retrieving and executing jobs:

### Resource-Based Allocation (Default)

**Used when**: `--max-parallel-jobs` is NOT specified

**Behavior**:
- Retrieves jobs from the server via `GET /workflows/{id}/claim_jobs_based_on_resources`
- Server filters jobs based on available compute node resources (CPU, memory, GPU)
- Only returns jobs that fit within the current resource capacity
- Prevents resource over-subscription and ensures jobs have required resources
- Defaults to requiring one CPU for each job.

**Use case**: When you have heterogeneous jobs with different resource requirements and want
intelligent resource management.

**Example**:
```yaml
resource_requirements:
  - name: "work_resources"
    num_cpus: 32
    memory: "200g"
    runtime: "PT4H"
    num_nodes: 1
    
jobs:
  - name: "work1"
    command: bash my_script.sh
    resource_requirements_name: work_resources  
```

### Simple Queue-Based Allocation

**Used when**: `--max-parallel-jobs` is specified

**Behavior**:
- Retrieves jobs from the server via `GET /workflows/{id}/claim_next_jobs`
- Server returns the next N ready jobs from the queue (up to the specified limit)
- Ignores job resource requirements completely
- Simply limits the number of concurrent jobs

**Use case**: When all jobs have similar resource needs or when the resource bottleneck is not
tracked by Torc, such as network or storage I/O.

**Example**:
```bash
torc run-jobs $WORKFLOW_ID \
  --max-parallel-jobs 10 \
  --output-dir ./results
```

## Job Runner Workflow

The job runner executes a continuous loop with these steps:

1. **Check workflow status** - Poll server to check if workflow is complete or canceled
2. **Monitor running jobs** - Check status of currently executing jobs
3. **Execute workflow actions** - Check for and execute any pending workflow actions
4. **Claim new jobs** - Request ready jobs from server based on allocation strategy:
   - Resource-based: `GET /workflows/{id}/claim_jobs_based_on_resources`
   - Queue-based: `GET /workflows/{id}/claim_next_jobs`
5. **Start jobs** - For each claimed job:
   - Call `POST /jobs/{id}/start_job` to mark job as started in database
   - Execute job command using `AsyncCliCommand` (non-blocking subprocess)
   - Track stdout/stderr output to files
6. **Complete jobs** - When running jobs finish:
   - Call `POST /jobs/{id}/complete_job` with exit code and result
   - Server updates job status and automatically marks dependent jobs as ready
7. **Sleep and repeat** - Wait for job completion poll interval, then repeat loop

The runner continues until the workflow is complete or canceled.

## Resource Management (Resource-Based Allocation Only)

When using resource-based allocation (default), the local job runner tracks:
- Number of CPUs in use
- Memory allocated to running jobs
- GPUs in use
- Job runtime limits

When a ready job is retrieved, the runner checks if sufficient resources are available before executing it.
