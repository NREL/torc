# Working with Slurm

## Torc server
- **External server**: A single member of your team allocates a shared server in
  the HPC environment to host a Torc server. This is recommended if your
  operations team provides this capability. The Torc server must be running on a
  network accessible to compute nodes.
- **Login node**: By default, the server runs single-threaded. If you have small
  job counts and each job runs a long time, the overhead on the login node will
  be minimal. However, if you allocate hundreds of nodes with many thousands of
  short jobs, the Torc server process may exceed allowed resource limits. Check
  with your operations team if you have doubts.


## Basic Slurm Configuration

Define a Slurm scheduler in your workflow spec that matches your jobs' resource requirements:

```yaml
slurm_schedulers:
  - name: standard
    account: my_project
    nodes: 1
    walltime: 12:00:00
```

Then define an action to schedule the node on workflow start:
```yaml
  - trigger_type: "on_workflow_start"
    action_type: "schedule_nodes"
    scheduler: "setup_scheduler"
    scheduler_type: "slurm"
    num_allocations: 1
```

Start the workflow with the workflow specification or create it and then pass the ID.
```bash
torc submit <workflow_spec>
```

When Slurm allocates the node, a Torc worker will start pulling appropriate jobs from the database.

## Scheduling Compute Nodes

Three main approaches for running Torc workers on Slurm:

### Approach 1: Many Single-Node Allocations

Submit multiple Slurm jobs, each with its own Torc worker:

```yaml
slurm_schedulers:
  - name: "work_scheduler"
    account: "my_account"
    nodes: 1
    walltime: "04:00:00"
```

```bash
torc slurm schedule-nodes -n 10 $WORKFLOW_ID
```

**When to use:**
- Jobs have diverse resource requirements
- Want independent time limits per job
- Need fine-grained control over resource allocation
- Cluster has low queue wait times

**Benefits:**
- Maximum flexibility in job scheduling
- Each job gets independent time limit
- Better resource matching (no wasted nodes)
- Fault isolation (one job failure doesn't affect others)

**Drawbacks:**
- More Slurm queue time (multiple jobs to schedule)
- Higher Slurm scheduler overhead
- Potential for queue backlog on busy clusters

### Approach 2: Multi-node Allocation, One Worker Per Node

Launch multiple workers, one per node:

```yaml
slurm_schedulers:
  - name: "work_scheduler"
    account: "my_account"
    nodes: 10
    walltime: "04:00:00"
```

```bash
torc slurm schedule-nodes -n 1 $WORKFLOW_ID --start-one-worker-per-node
```

**Benefits:**
- Slurm typically prioritizes jobs with higher node counts
- Efficient for workflows with many jobs having similar resource requirements

**Drawbacks:**
- All Torc jobs share the same Slurm allocation time limit
- Wasted resources if some jobs run much longer than others

### Approach 3: One Worker Per Slurm Allocation

Submit a single Slurm job that runs the Torc worker on the head node.

```yaml
slurm_schedulers:
  - name: "work_scheduler"
    account: "my_account"
    nodes: 10
    walltime: "04:00:00"
```
```bash
torc slurm schedule-nodes -n 1 $WORKFLOW_ID
```

**Benefits:**
- Your job has full control over all compute nodes in the allocation.

**Drawbacks:**
- Complexity: your code must find all compute nodes and coordinate worker startup.
