# Resource Management

## Defining Resource Requirements

Resource requirements specify the compute resources needed for each job:

```yaml
resource_requirements:
  - name: small
    num_cpus: 2
    num_gpus: 0
    num_nodes: 1
    memory: 4g
    runtime: PT30M

  - name: large
    num_cpus: 16
    num_gpus: 2
    num_nodes: 1
    memory: 128g
    runtime: PT8H
```

## Resource Formats

### Memory

String format with suffix:
- `1m` - 1 megabyte
- `2g` - 2 gigabytes
- `512k` - 512 kilobytes

Examples:
```yaml
memory: 1g      # 1 GB
memory: 512m    # 512 MB
memory: 16g     # 16 GB
```

### Runtime

ISO 8601 duration format:
- `PT30M` - 30 minutes
- `PT2H` - 2 hours
- `P1DT12H` - 1.5 days

Examples:
```yaml
runtime: PT10M      # 10 minutes
runtime: PT4H       # 4 hours
runtime: P1D        # 1 day
```

## Job Allocation Strategies

Torc supports two different strategies for allocating jobs to runners:

### Resource-Based Allocation (Default)

**When to use**: You have jobs with varying resource requirements and want intelligent resource management.

**Configuration**: Run the job runner WITHOUT `--max-parallel-jobs`:

```bash
torc run-jobs $WORKFLOW_ID \
  --num-cpus 32 \
  --memory-gb 256 \
  --num-gpus 4
```

**Behavior**:
- The server considers each job's resource requirements (CPU, memory, GPU)
- Only returns jobs that fit within available compute node resources
- Prevents resource over-subscription
- Enables efficient packing of heterogeneous workloads

**Requirements**: Jobs must define resource requirements in the workflow specification.

### Simple Queue-Based Allocation

**When to use**: Jobs have similar resource needs, or you want simple parallelism control without resource tracking overhead.

**Configuration**: Run the job runner WITH `--max-parallel-jobs`:

```bash
torc run-jobs $WORKFLOW_ID \
  --max-parallel-jobs 10 \
  --output-dir ./results
```

**Behavior**:
- The server returns the next N ready jobs from the queue (up to the limit)
- Ignores job resource requirements completely
- Only limits the number of concurrent jobs running
- Simpler and faster (no resource calculation overhead)

**Use case**: Homogeneous workloads, simple task queues, or when resource requirements are not critical.

## Resource Tracking

When using resource-based allocation (default), the job runner tracks available resources:
- Number of CPUs in use
- Memory allocated to running jobs
- GPUs in use
- Number of jobs running per node

When requesting jobs from the server, the runner only accepts jobs that fit within available resources.

## Configuring Compute Nodes

Register compute nodes with the server:

```bash
torc compute-nodes create \
  --workflow-id $WORKFLOW_ID \
  --hostname $(hostname) \
  --num-cpus 32 \
  --memory "256g" \
  --num-gpus 8 \
  --is-active true
```

The job runner can automatically detect local resources or use registered nodes for tracking.

## Resource Over-Subscription

By default, Torc prevents resource over-subscription. To allow it:

```yaml
resource_requirements:
  - name: oversubscribe
    num_cpus: 64      # More than physically available
    memory: 512g
    allow_oversubscribe: true
```

Use with caution - may cause performance degradation or out-of-memory errors.
