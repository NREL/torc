# Slurm Staged Pipeline Example

This example demonstrates a complete three-stage Slurm pipeline with automated scheduling and resource monitoring.

## Pipeline Architecture

The workflow consists of three stages that execute sequentially with automatic scheduling:

### Stage 1: Setup (4 hours)
- **Job**: `setup`
- **Resources**: 16 CPUs, 64 GB memory, 1 node
- **Output**: 10 input data files (1 GB each)
- **Trigger**: Launches automatically when workflow starts (`on_workflow_start`)

### Stage 2: Work (8 hours each, parallel)
- **Jobs**: `work_001` through `work_010` (10 parallel jobs)
- **Resources**: 32 CPUs, 300 GB memory per job, 1 node each
- **Input**: One input file per job
- **Output**: One output file per job (512 MB each)
- **Trigger**: Launches automatically when all jobs are ready (`when_jobs_ready`)

### Stage 3: Post-processing (1 hour)
- **Job**: `postprocess`
- **Resources**: 8 CPUs, 32 GB memory, 1 node
- **Input**: All 10 output files from work stage
- **Output**: Single aggregated results file
- **Trigger**: Launches automatically when all work jobs complete (`when_jobs_complete`)

## Features Demonstrated

1. **Multi-stage Pipeline**: Three distinct computational stages with different resource requirements
2. **Automated Scheduling**: Scheduling rules automatically trigger compute node allocation for each stage
3. **Resource Monitoring**: Time-series monitoring of CPU, memory, and disk I/O metrics
4. **File Dependencies**: Implicit job dependencies through input/output file relationships
5. **Slurm Integration**: Separate Slurm scheduler configurations for each stage
6. **Large Memory Jobs**: Work jobs demonstrate high-memory requirements (300 GB)

## Prerequisites

Before running this workflow, you need to create compute node allocations for the three stages:

```bash
# Create allocation for setup stage (1 node for 4 hours)
curl -X POST http://localhost:8080/torc-service/v1/compute_node_allocations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "setup_allocation",
    "cluster_name": "your_cluster",
    "partition": "standard",
    "num_nodes": 1,
    "num_cpus_per_node": 16,
    "memory_per_node_gb": 64,
    "runtime": "PT4H"
  }'
# Note the returned ID (should be 1)

# Create allocation for work stage (10 nodes for 8 hours)
curl -X POST http://localhost:8080/torc-service/v1/compute_node_allocations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "work_allocation",
    "cluster_name": "your_cluster",
    "partition": "himem",
    "num_nodes": 10,
    "num_cpus_per_node": 32,
    "memory_per_node_gb": 300,
    "runtime": "PT8H"
  }'
# Note the returned ID (should be 2)

# Create allocation for postprocess stage (1 node for 1 hour)
curl -X POST http://localhost:8080/torc-service/v1/compute_node_allocations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "postprocess_allocation",
    "cluster_name": "your_cluster",
    "partition": "standard",
    "num_nodes": 1,
    "num_cpus_per_node": 8,
    "memory_per_node_gb": 32,
    "runtime": "PT1H"
  }'
# Note the returned ID (should be 3)
```

## Usage

### 1. Create the workflow from the specification

```bash
torc-client workflows create-from-spec slurm_staged_pipeline.yaml
```

This will output the workflow ID. Save this for the next steps.

### 2. Start the workflow

```bash
# Start the workflow (activates scheduling rules)
torc-client workflows start <workflow_id>
```

This command will:
- Reset the workflow status
- Initialize job dependencies
- Activate all scheduling rules
- Create the first active trigger (`on_workflow_start`)

### 3. Monitor workflow progress

```bash
# Check workflow status
torc-client workflows status <workflow_id>

# List jobs and their statuses
torc-client jobs list <workflow_id>

# View active triggers
torc-client workflows <workflow_id> active-triggers list

# View scheduling rules
torc-client workflows <workflow_id> scheduling-rules list

# View resource monitoring data
torc-client resource-monitoring list <workflow_id>
```

## Automated Execution Flow

Once started, the workflow executes automatically:

1. **T=0**: `on_workflow_start` trigger fires
   - Compute nodes allocated for setup stage
   - JobRunner(s) launched on allocated nodes
   - Setup job executes (4 hours)

2. **T=4h**: Setup job completes, all work jobs become ready
   - `when_jobs_ready` trigger fires
   - Compute nodes allocated for work stage (10 nodes)
   - JobRunner(s) launched on allocated nodes
   - 10 work jobs execute in parallel (8 hours)

3. **T=12h**: All work jobs complete
   - `when_jobs_complete` trigger fires
   - Compute nodes allocated for postprocess stage
   - JobRunner launched on allocated node
   - Postprocess job executes (1 hour)

4. **T=13h**: Pipeline completes
   - Final results file created
   - All resources released

## Resource Monitoring

The workflow includes time-series resource monitoring with 30-second sampling:

- **CPU utilization** (`cpu_percent`)
- **Memory usage** (`memory_bytes`, `memory_percent`)

View monitoring data:

```bash
# Get all monitoring data for the workflow
torc-client resource-monitoring list <workflow_id>

# Filter by job
torc-client resource-monitoring list <workflow_id> --job-id <job_id>

# Filter by metric type
torc-client resource-monitoring list <workflow_id> --metric-type cpu_percent
```

## Customization

### Adjust Resource Requirements

Edit the `resource_requirements` section:

```yaml
resource_requirements:
  - name: "work_resources"
    num_cpus: 64        # Increase CPUs
    memory: "500g"      # Increase memory
    runtime: "PT12H"    # Extend runtime
    num_nodes: 1
```

### Add More Work Jobs

Use parameterization to generate additional work jobs:

```yaml
jobs:
  - name: "work_{i}"
    command: |
      #!/bin/bash
      # ... processing logic ...
    scheduler_name: "work_scheduler"
    resource_requirements_name: "work_resources"
    blocked_by_job_names: ["setup"]
    input_file_names: ["input_{i}"]
    output_file_names: ["output_{i}"]
    parameters:
      i: "1:20"  # Creates work_001 through work_020
```

### Modify Scheduling Behavior

Update `scheduling_rules` to change when compute nodes are allocated:

```yaml
scheduling_rules:
  # Launch work stage immediately at workflow start (not waiting for setup)
  - trigger_type: "on_workflow_start"
    start_server_on_head_node: true
    start_one_worker_per_node: true
```

## Troubleshooting

### Jobs Not Starting

1. Verify scheduling rules are active:
   ```bash
   torc-client workflows <workflow_id> scheduling-rules list
   ```
   Rules should show status `active` after workflow start.

2. Check for active triggers:
   ```bash
   torc-client workflows <workflow_id> active-triggers list
   ```

3. Verify compute node allocations exist and IDs match:
   ```bash
   curl http://localhost:8080/torc-service/v1/compute_node_allocations
   ```

### Missing Files

Ensure the scratch directory exists and is accessible:
```bash
mkdir -p /scratch/pipeline
chmod 777 /scratch/pipeline
```

### High Memory Jobs Failing

Verify Slurm partition supports 300 GB memory allocations:
```bash
sinfo -o "%P %N %m"
```

Use a partition with sufficient memory (e.g., `himem` instead of `standard`).

## Performance Considerations

- **Parallel Execution**: 10 work jobs run simultaneously, requiring 10 compute nodes
- **Total Compute Time**: ~13 hours (4h setup + 8h work + 1h postprocess)
- **Peak Resource Usage**: 320 CPUs, 3 TB memory (during work stage)
- **Data Volume**: ~6 GB total (10 GB input + 5 GB intermediate + 1 GB final)

## See Also

- [Resource Monitoring README](RESOURCE_MONITORING_README.md)
- [Workflow Specification Guide](../README.md)
- [Slurm Integration Documentation](../../docs/SLURM.md)
