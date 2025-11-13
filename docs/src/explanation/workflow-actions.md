# Workflow Actions

Workflow actions enable automatic execution of commands and resource allocation in response to workflow lifecycle events. Actions provide hooks for setup, teardown, monitoring, and dynamic resource management throughout workflow execution.

## Overview

Actions consist of three components:

1. **Trigger** - The condition that activates the action
2. **Action Type** - The operation to perform
3. **Configuration** - Parameters specific to the action

```yaml
actions:
  - trigger_type: "on_workflow_start"
    action_type: "run_commands"
    commands:
      - "mkdir -p output logs"
      - "echo 'Workflow started' > logs/status.txt"
```

## Trigger Types

### Workflow Lifecycle Triggers

#### `on_workflow_start`

Executes once when the workflow is initialized.

**When it fires**: During `initialize_jobs` after jobs are transitioned from uninitialized to ready/blocked states.

**Typical use cases**:
- Creating directory structures
- Copying initial data

```yaml
- trigger_type: "on_workflow_start"
  action_type: "run_commands"
  commands:
    - "mkdir -p output checkpoints temp"
    - "echo 'Workflow started at $(date)' > workflow.log"
```

#### `on_workflow_complete`

Executes once when all jobs reach terminal states (completed, failed, or canceled).

**When it fires**: After the last job completes, as detected by the job runner.

**Typical use cases**:
- Archiving final results
- Uploading to remote storage
- Cleanup of temporary files
- Generating summary reports

```yaml
- trigger_type: "on_workflow_complete"
  action_type: "run_commands"
  commands:
    - "tar -czf results.tar.gz output/"
    - "aws s3 cp results.tar.gz s3://bucket/results/"
    - "rm -rf temp/"
```

### Job-Based Triggers

#### `on_jobs_ready`

Executes when **all** specified jobs transition to the "ready" state.

**When it fires**: When the last specified job becomes ready to execute (all dependencies satisfied).

**Typical use cases**:
- Just-in-time resource allocation
- Starting phase-specific monitoring
- Pre-computation setup
- Notifications before expensive operations

```yaml
- trigger_type: "on_jobs_ready"
  action_type: "schedule_nodes"
  job_names: ["train_model_001", "train_model_002", "train_model_003"]
  scheduler_name: "gpu_cluster"
  scheduler_type: "slurm"
  num_allocations: 2
```

**Important**: The action triggers only when **all** matching jobs are ready, not individually as each job becomes ready.

#### `on_jobs_complete`

Executes when **all** specified jobs reach terminal states (completed, failed, or canceled).

**When it fires**: When the last specified job finishes execution.

**Typical use cases**:
- Cleaning up intermediate files
- Archiving phase results
- Freeing storage space
- Phase-specific reporting

```yaml
- trigger_type: "on_jobs_complete"
  action_type: "run_commands"
  job_names: ["preprocess_1", "preprocess_2", "preprocess_3"]
  commands:
    - "echo 'Preprocessing phase complete' >> workflow.log"
    - "rm -rf raw_data/"
```

### Worker Lifecycle Triggers

Worker lifecycle triggers are **persistent by default**, meaning they execute once per worker (job runner), not once per workflow.

#### `on_worker_start`

Executes when each worker (job runner) starts.

**When it fires**: After a job runner starts and checks for workflow actions, before claiming any jobs.

**Typical use cases**:
- Worker-specific initialization
- Setting up worker-local logging
- Initializing worker-specific resources
- Recording worker startup metrics

```yaml
- trigger_type: "on_worker_start"
  action_type: "run_commands"
  persistent: true  # Each worker executes this
  commands:
    - "echo 'Worker started on $(hostname) at $(date)' >> worker.log"
    - "mkdir -p worker_temp"
```

#### `on_worker_complete`

Executes when each worker completes (exits the main loop).

**When it fires**: After a worker finishes processing jobs and before it shuts down.

**Typical use cases**:
- Worker-specific cleanup
- Uploading worker-specific logs
- Recording worker completion metrics
- Cleaning up worker-local resources

```yaml
- trigger_type: "on_worker_complete"
  action_type: "run_commands"
  persistent: true  # Each worker executes this
  commands:
    - "echo 'Worker completed on $(hostname) at $(date)' >> worker.log"
    - "rm -rf worker_temp"
```

## Job Selection

For `on_jobs_ready` and `on_jobs_complete` triggers, specify which jobs to monitor.

### Exact Job Names

```yaml
- trigger_type: "on_jobs_complete"
  action_type: "run_commands"
  job_names: ["job1", "job2", "job3"]
  commands:
    - "echo 'Specific jobs complete'"
```

### Regular Expressions

```yaml
- trigger_type: "on_jobs_ready"
  action_type: "schedule_nodes"
  job_name_regexes: ["train_model_[0-9]+", "eval_.*"]
  scheduler_name: "gpu_cluster"
  scheduler_type: "slurm"
  num_allocations: 2
```

**Common regex patterns**:
- `"train_.*"` - All jobs starting with "train_"
- `"model_[0-9]+"` - Jobs like "model_1", "model_2"
- `".*_stage1"` - All jobs ending with "_stage1"
- `"job_(a|b|c)"` - Jobs "job_a", "job_b", or "job_c"

### Combining Selection Methods

You can use both together - the action triggers when **all** matching jobs meet the condition:

```yaml
job_names: ["critical_job"]
job_name_regexes: ["batch_.*"]
# Triggers when "critical_job" AND all "batch_*" jobs are ready/complete
```

## Action Types

### `run_commands`

Execute shell commands sequentially on a compute node.

**Configuration**:
```yaml
- trigger_type: "on_workflow_complete"
  action_type: "run_commands"
  commands:
    - "tar -czf results.tar.gz output/"
    - "aws s3 cp results.tar.gz s3://bucket/"
```

**Execution details**:
- Commands run in the workflow's output directory
- Commands execute sequentially (one after another)
- If a command fails, the action fails (but workflow continues)
- Commands run on compute nodes, not the submission node
- Uses the shell environment of the job runner process

### `schedule_nodes`

Dynamically allocate compute resources from a Slurm scheduler.

**Configuration**:
```yaml
- trigger_type: "on_jobs_ready"
  action_type: "schedule_nodes"
  job_names: ["train_model_1", "train_model_2"]
  scheduler_name: "gpu_cluster"
  scheduler_type: "slurm"
  num_allocations: 2
  start_one_worker_per_node: true
  max_parallel_jobs: 8
```

**Parameters**:
- `scheduler_name` (required) - Name of Slurm scheduler configuration (must exist in `slurm_schedulers`)
- `scheduler_type` (required) - Must be "slurm"
- `num_allocations` (required) - Number of Slurm allocation requests to submit
- `start_one_worker_per_node` (optional) - Start one job runner per node (default: false)
- `start_server_on_head_node` (optional) - Start torc-server on head node (default: false)
- `max_parallel_jobs` (optional) - Maximum concurrent jobs per runner

**Use cases**:
- Auto-scaling for large job arrays
- Just-in-time resource allocation
- Cost optimization (allocate only when needed)
- Separating workflow phases with different resource requirements

## Complete Examples

### Example 1: Simple Setup and Cleanup

```yaml
name: "Data Processing Workflow"
user: "researcher"

jobs:
  - name: "download_data"
    command: "wget https://example.com/data.tar.gz && tar -xzf data.tar.gz"

  - name: "process_data"
    command: "python process.py"
    blocked_by_job_names: ["download_data"]

  - name: "analyze_results"
    command: "python analyze.py"
    blocked_by_job_names: ["process_data"]

actions:
  - trigger_type: "on_workflow_start"
    action_type: "run_commands"
    commands:
      - "echo 'Workflow started at $(date)' > workflow.log"
      - "mkdir -p output temp logs"

  - trigger_type: "on_workflow_complete"
    action_type: "run_commands"
    commands:
      - "echo 'Workflow completed at $(date)' >> workflow.log"
      - "rm -rf temp"
      - "tar -czf results.tar.gz output/ workflow.log"
```

### Example 2: Dynamic GPU Allocation for ML Training

```yaml
name: "ML Training with Auto-Scaling"
user: "ml_team"

jobs:
  - name: "preprocess"
    command: "python preprocess.py"
    resource_requirements_name: "cpu_small"

  - name: "train_model_{model_id}"
    command: "python train.py --model {model_id}"
    resource_requirements_name: "gpu_large"
    blocked_by_job_names: ["preprocess"]
    parameters:
      model_id: "[1,2,3,4,5,6,7,8]"

  - name: "evaluate_{model_id}"
    command: "python evaluate.py --model {model_id}"
    resource_requirements_name: "cpu_medium"
    blocked_by_job_names: ["train_model_{model_id}"]
    parameters:
      model_id: "[1,2,3,4,5,6,7,8]"

resource_requirements:
  - name: "cpu_small"
    num_cpus: 2
    memory: "4g"
  - name: "cpu_medium"
    num_cpus: 4
    memory: "8g"
  - name: "gpu_large"
    num_cpus: 8
    num_gpus: 1
    memory: "32g"
    runtime: "PT4H"

slurm_schedulers:
  - name: "gpu_cluster"
    account: "ml_project"
    partition: "gpu"
    nodes: 2
    walltime: "04:00:00"
    gres: "gpu:1"

actions:
  # Allocate GPU nodes when training jobs are ready
  - trigger_type: "on_jobs_ready"
    action_type: "schedule_nodes"
    job_name_regexes: ["train_model_.*"]
    scheduler_name: "gpu_cluster"
    scheduler_type: "slurm"
    num_allocations: 2
    start_one_worker_per_node: true
    max_parallel_jobs: 4

  # Clean up after training
  - trigger_type: "on_jobs_complete"
    action_type: "run_commands"
    job_name_regexes: ["train_model_.*"]
    commands:
      - "tar -czf checkpoints.tar.gz checkpoints/"
      - "rm -rf checkpoints/"

  # Archive final results
  - trigger_type: "on_workflow_complete"
    action_type: "run_commands"
    commands:
      - "python summarize_results.py"
      - "tar -czf final_results.tar.gz output/ models/"
```

### Example 4: Multi-Stage Pipeline with Progressive Cleanup

```yaml
name: "ETL Pipeline"
user: "data_engineer"

jobs:
  - name: "extract_{source}"
    command: "python extract.py {source}"
    parameters:
      source: "['db1', 'db2', 'db3']"

  - name: "transform_{source}"
    command: "python transform.py {source}"
    blocked_by_job_names: ["extract_{source}"]
    parameters:
      source: "['db1', 'db2', 'db3']"

  - name: "load_{source}"
    command: "python load.py {source}"
    blocked_by_job_names: ["transform_{source}"]
    parameters:
      source: "['db1', 'db2', 'db3']"

actions:
  - trigger_type: "on_workflow_start"
    action_type: "run_commands"
    commands:
      - "mkdir -p raw transformed loaded logs"
      - "echo 'Pipeline started at $(date)' > logs/pipeline.log"

  # Clean raw data after transformation
  - trigger_type: "on_jobs_complete"
    action_type: "run_commands"
    job_name_regexes: ["transform_.*"]
    commands:
      - "echo 'Transform complete, cleaning raw data' >> logs/pipeline.log"
      - "rm -rf raw/"

  # Archive transformed data after loading
  - trigger_type: "on_jobs_complete"
    action_type: "run_commands"
    job_name_regexes: ["load_.*"]
    commands:
      - "tar -czf archives/transformed_$(date +%Y%m%d).tar.gz transformed/"
      - "rm -rf transformed/"

  - trigger_type: "on_workflow_complete"
    action_type: "run_commands"
    commands:
      - "echo 'Pipeline completed at $(date)' >> logs/pipeline.log"
      - "python generate_report.py"
```

## Best Practices

### 1. Include Error Handling

Use shell error handling for robustness:

```yaml
commands:
  - "aws s3 cp results/ s3://bucket/ --recursive || echo 'WARNING: Upload failed'"
  - "python notify.py || logger 'Notification failed'"
```

### 2. Always Log Actions

Add logging for debugging and auditing:

```yaml
commands:
  - "echo '[ACTION] Starting cleanup at $(date)' | tee -a workflow.log"
  - "rm -rf temp/"
  - "echo '[ACTION] Cleanup complete' | tee -a workflow.log"
```

### 3. Plan Resource Allocation Timing

For `schedule_nodes`, allocate resources when jobs become ready, not when they start running:

```yaml
- trigger_type: "on_jobs_ready"  # Allocate early
  action_type: "schedule_nodes"
  job_name_regexes: ["compute_.*"]
  num_allocations: 10
```

This allows Slurm allocations to be pending/starting while other jobs run, minimizing idle time.

### 4. Use Worker Actions for Per-Worker Operations

If you need operations per worker (not per workflow), use persistent worker actions:

```yaml
# Good: Each worker cleans up its own temp directory
- trigger_type: "on_worker_complete"
  action_type: "run_commands"
  persistent: true
  commands:
    - "rm -rf /tmp/worker_$$_temp"

# Avoid: Single workflow cleanup won't run on all workers
- trigger_type: "on_workflow_complete"
  action_type: "run_commands"
  commands:
    - "rm -rf /tmp/worker_*_temp"  # Only runs on one worker
```

### 5. Clean Up in Dependency Order

```yaml
# Clean intermediate results after downstream jobs complete
- trigger_type: "on_jobs_complete"
  job_name_regexes: ["phase2_.*"]
  commands: ["rm -rf phase1_output/"]

# Final cleanup after everything
- trigger_type: "on_workflow_complete"
  commands: ["rm -rf temp/ cache/"]
```

## Execution Model

### Action Claiming and Execution

1. **Atomic Claiming**: Actions are claimed atomically by workers to prevent duplicate execution
2. **Non-Persistent Actions**: Execute once per workflow (first worker to claim executes)
3. **Persistent Actions**: Can be claimed and executed by multiple workers
4. **Trigger Counting**: Job-based triggers increment a counter as jobs transition; action becomes pending when count reaches threshold
5. **Immediate Availability**: Worker lifecycle actions are immediately available after workflow initialization

### Action Lifecycle

```
[Workflow Created]
    ↓
[initialize_jobs called]
    ↓
├─→ on_workflow_start actions become pending
├─→ on_worker_start actions become pending (persistent)
├─→ on_worker_complete actions become pending (persistent)
└─→ on_jobs_ready actions wait for job transitions
    ↓
[Worker Claims and Executes Actions]
    ↓
[Jobs Execute]
    ↓
[Jobs Complete]
    ↓
├─→ on_jobs_complete actions become pending when all specified jobs complete
└─→ on_workflow_complete actions become pending when all jobs complete
    ↓
[Workers Exit]
    ↓
[on_worker_complete actions execute per worker]
```

### Important Characteristics

1. **No Rollback**: Failed actions don't affect workflow execution
2. **Compute Node Execution**: Actions run on compute nodes via job runners
3. **One-Time Triggers**: Non-persistent actions trigger once when conditions are first met
4. **No Inter-Action Dependencies**: Actions don't depend on other actions
5. **Concurrent Workers**: Multiple workers can execute different actions simultaneously

## Limitations

1. **No Action Dependencies**: Actions cannot depend on other actions completing
2. **No Conditional Execution**: Actions cannot have conditional logic (use multiple actions with different job selections instead)
3. **No Action Retries**: Failed actions are not automatically retried
4. **Single Action Type**: Each action has one action_type (cannot combine run_commands and schedule_nodes)
5. **No Dynamic Job Selection**: Job names/patterns are fixed at action creation time

For complex workflows requiring these features, consider:
- Using job dependencies to order operations
- Creating separate jobs for conditional logic
- Implementing retry logic within command scripts
- Creating multiple actions for different scenarios
