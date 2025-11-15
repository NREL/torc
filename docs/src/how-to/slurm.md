# Working with Slurm

## Torc server
- **External server**: A single member of your team allocates a shared server in
  the HPC environment to host a Torc server. This is recommended if your
  operations team provides this capability. The Torc server must be running on a
  network accessible to compute nodes. There are three ways of running it:
- **Login node**: By default, the server runs single-threaded. If you have small
  job counts and each job runs a long time, the overhead on the login node will
  be minimal. However, if you allocate hundreds of nodes with many thousands of
  short jobs, the Torc server process may exceed allowed resource limits. Check
  with your operations team if you have doubts.
- **Slurm head node**: Create the workflow while running the Torc server on the
  login node. Start the workflow with `start_server_on_head_node` set to true.
  Shut down the server. Torc will configure the job to start the server upon
  being granted the allocation.

## Basic Slurm Configuration

Define a Slurm scheduler in your workflow spec:

```yaml
slurm_schedulers:
  - name: my_cluster
    partition: compute
    account: my_project
    extra_sbatch_args: "--reservation=my_reservation"
```

Then reference it in jobs:

```yaml
jobs:
  - name: compute_job
    command: ./run_simulation
    resource_requirements_name: gpu_node
    slurm_scheduler_name: my_cluster
```

## Scheduling Compute Nodes

Four main approaches for running Torc workers on Slurm:

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

### Approach 4: Server on Head Node

For HPC environments where a persistent Torc server is not available, you can
start the server dynamically on the head node of your Slurm allocation:

```yaml
slurm_schedulers:
  - name: "work_scheduler"
    account: "my_account"
    nodes: 10
    walltime: "04:00:00"
```

```bash
torc slurm schedule-nodes <workflow_id> \
  --scheduler-config-id <config_id> \
  --num-hpc-jobs 1 \
  --start-server-on-head-node \
  --start-one-worker-per-node
```

**What happens:**
1. Torc server starts on the head node (`SLURM_NODEID=0`)
2. Server listens on `http://$(hostname):8080`
3. All workers connect to the head node's server
4. Server and workers run within the same Slurm allocation

**When to use:**
- No persistent Torc server infrastructure available
- Self-contained workflow execution needed
- Running on clusters without external network access
- Development and testing on HPC systems

**Benefits:**
- No external server infrastructure required
- Self-contained execution within allocation
- Works on air-gapped clusters
- Server lifecycle matches job allocation

**Drawbacks:**
- Head node resources used for server
- Server stops when allocation ends
- Cannot submit new work from outside the allocation
