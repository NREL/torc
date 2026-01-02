# Working with Slurm

This guide covers advanced Slurm configuration for users who need fine-grained control over their
HPC workflows.

> **For most users**: See [Slurm Workflows](../explanation/slurm-workflows.md) for the recommended
> approach using `torc submit-slurm`. You don't need to manually configure schedulers or
> actions—Torc handles this automatically.

## When to Use Manual Configuration

Manual Slurm configuration is useful when you need:

- Custom Slurm directives (e.g., `--constraint`, `--exclusive`)
- Multi-node jobs with specific topology requirements
- Shared allocations across multiple jobs for efficiency
- Non-standard partition configurations
- Fine-tuned control over allocation timing

## Torc Server Requirements

The Torc server must be accessible from compute nodes:

- **External server** (Recommended): A team member allocates a shared server in the HPC environment.
  This is recommended if your operations team provides this capability.
- **Login node**: Suitable for small workflows. The server runs single-threaded by default. If you
  have many thousands of short jobs, check with your operations team about resource limits.

## Manual Scheduler Configuration

### Defining Slurm Schedulers

Define schedulers in your workflow specification:

```yaml
slurm_schedulers:
  - name: standard
    account: my_project
    nodes: 1
    walltime: "12:00:00"
    partition: compute
    mem: 64G

  - name: gpu_nodes
    account: my_project
    nodes: 1
    walltime: "08:00:00"
    partition: gpu
    gres: "gpu:4"
    mem: 256G
```

### Scheduler Fields

| Field             | Description                         | Required |
| ----------------- | ----------------------------------- | -------- |
| `name`            | Scheduler identifier                | Yes      |
| `account`         | Slurm account/allocation            | Yes      |
| `nodes`           | Number of nodes                     | Yes      |
| `walltime`        | Time limit (HH:MM:SS or D-HH:MM:SS) | Yes      |
| `partition`       | Slurm partition                     | No       |
| `mem`             | Memory per node                     | No       |
| `gres`            | Generic resources (e.g., GPUs)      | No       |
| `qos`             | Quality of Service                  | No       |
| `ntasks_per_node` | Tasks per node                      | No       |
| `tmp`             | Temporary disk space                | No       |
| `extra`           | Additional sbatch arguments         | No       |

### Defining Workflow Actions

Actions trigger scheduler allocations:

```yaml
actions:
  - trigger_type: on_workflow_start
    action_type: schedule_nodes
    scheduler: standard
    scheduler_type: slurm
    num_allocations: 1

  - trigger_type: on_jobs_ready
    action_type: schedule_nodes
    jobs: [train_model]
    scheduler: gpu_nodes
    scheduler_type: slurm
    num_allocations: 2
```

### Action Trigger Types

| Trigger                | Description                            |
| ---------------------- | -------------------------------------- |
| `on_workflow_start`    | Fires when workflow is submitted       |
| `on_jobs_ready`        | Fires when specified jobs become ready |
| `on_jobs_complete`     | Fires when specified jobs complete     |
| `on_workflow_complete` | Fires when all jobs complete           |

### Assigning Jobs to Schedulers

Reference schedulers in job definitions:

```yaml
jobs:
  - name: preprocess
    command: ./preprocess.sh
    scheduler: standard

  - name: train
    command: python train.py
    scheduler: gpu_nodes
    depends_on: [preprocess]
```

## Scheduling Strategies

### Strategy 1: Many Single-Node Allocations

Submit multiple Slurm jobs, each with its own Torc worker:

```yaml
slurm_schedulers:
  - name: work_scheduler
    account: my_account
    nodes: 1
    walltime: "04:00:00"

actions:
  - trigger_type: on_workflow_start
    action_type: schedule_nodes
    scheduler: work_scheduler
    scheduler_type: slurm
    num_allocations: 10
```

**When to use:**

- Jobs have diverse resource requirements
- Want independent time limits per job
- Cluster has low queue wait times

**Benefits:**

- Maximum scheduling flexibility
- Independent time limits per allocation
- Fault isolation

**Drawbacks:**

- More Slurm queue overhead
- Multiple jobs to schedule

### Strategy 2: Multi-Node Allocation, One Worker Per Node

Launch multiple workers within a single allocation:

```yaml
slurm_schedulers:
  - name: work_scheduler
    account: my_account
    nodes: 10
    walltime: "04:00:00"

actions:
  - trigger_type: on_workflow_start
    action_type: schedule_nodes
    scheduler: work_scheduler
    scheduler_type: slurm
    num_allocations: 1
    start_one_worker_per_node: true
```

**When to use:**

- Many jobs with similar requirements
- Want faster queue scheduling (larger jobs often prioritized)

**Benefits:**

- Single queue wait
- Often prioritized by Slurm scheduler

**Drawbacks:**

- Shared time limit for all workers
- Less flexibility

### Strategy 3: Single Worker Per Allocation

One Torc worker handles all nodes:

```yaml
slurm_schedulers:
  - name: work_scheduler
    account: my_account
    nodes: 10
    walltime: "04:00:00"

actions:
  - trigger_type: on_workflow_start
    action_type: schedule_nodes
    scheduler: work_scheduler
    scheduler_type: slurm
    num_allocations: 1
```

**When to use:**

- Your application manages node coordination
- Need full control over compute resources

## Staged Allocations

For pipelines with distinct phases, stage allocations to avoid wasted resources:

```yaml
slurm_schedulers:
  - name: preprocess_sched
    account: my_project
    nodes: 2
    walltime: "01:00:00"

  - name: compute_sched
    account: my_project
    nodes: 20
    walltime: "08:00:00"

  - name: postprocess_sched
    account: my_project
    nodes: 1
    walltime: "00:30:00"

actions:
  # Preprocessing starts immediately
  - trigger_type: on_workflow_start
    action_type: schedule_nodes
    scheduler: preprocess_sched
    scheduler_type: slurm
    num_allocations: 1

  # Compute nodes allocated when compute jobs are ready
  - trigger_type: on_jobs_ready
    action_type: schedule_nodes
    jobs: [compute_step]
    scheduler: compute_sched
    scheduler_type: slurm
    num_allocations: 1
    start_one_worker_per_node: true

  # Postprocessing allocated when those jobs are ready
  - trigger_type: on_jobs_ready
    action_type: schedule_nodes
    jobs: [postprocess]
    scheduler: postprocess_sched
    scheduler_type: slurm
    num_allocations: 1
```

> **Note**: The `torc submit-slurm` command handles this automatically by analyzing job
> dependencies.

## Custom Slurm Directives

Use the `extra` field for additional sbatch arguments:

```yaml
slurm_schedulers:
  - name: exclusive_nodes
    account: my_project
    nodes: 4
    walltime: "04:00:00"
    extra: "--exclusive --constraint=skylake"
```

## Submitting Workflows

### With Manual Configuration

```bash
# Submit workflow with pre-defined schedulers and actions
torc submit workflow.yaml
```

### Scheduling Additional Nodes

Add more allocations to a running workflow:

```bash
torc slurm schedule-nodes -n 5 $WORKFLOW_ID
```

## Debugging

### Check Slurm Job Status

```bash
squeue --me
```

### View Torc Worker Logs

Workers log to the Slurm output file. Check:

```bash
cat slurm-<jobid>.out
```

### Verify Server Connectivity

From a compute node:

```bash
curl $TORC_API_URL/health
```

## See Also

- [Slurm Workflows](../explanation/slurm-workflows.md) — Simplified workflow approach
- [HPC Profiles](./hpc-profiles.md) — Automatic partition matching
- [Workflow Actions](../explanation/workflow-actions.md) — Action system details
- [Debugging Slurm Workflows](./debugging-slurm.md) — Troubleshooting guide
