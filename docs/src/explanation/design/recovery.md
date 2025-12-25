# Workflow Recovery

Torc provides mechanisms for recovering workflows when Slurm allocations are preempted or fail
before completing all jobs. The `torc slurm regenerate` command creates new schedulers and
allocations for pending jobs.

## The Recovery Problem

When running workflows on Slurm, allocations can fail or be preempted before all jobs complete. This
leaves workflows in a partial state with:

1. **Ready/uninitialized jobs** - Jobs that were waiting to run but never got scheduled
2. **Blocked jobs** - Jobs whose dependencies haven't completed yet

Simply creating new Slurm schedulers and submitting allocations isn't enough because:

1. **Duplicate allocations**: If the workflow had `on_workflow_start` actions to schedule nodes,
   those actions would fire again when the workflow is reinitialized, creating duplicate allocations
2. **Missing allocations for blocked jobs**: Blocked jobs will eventually become ready, but there's
   no mechanism to schedule new allocations for them

## Recovery Actions

The recovery system uses **ephemeral recovery actions** to solve these problems.

### How It Works

When `torc slurm regenerate` runs:

```mermaid
flowchart TD
    A[torc slurm regenerate] --> B[Fetch pending jobs]
    B --> C{Has pending jobs?}
    C -->|No| D[Exit - nothing to do]
    C -->|Yes| E[Build WorkflowGraph from pending jobs]
    E --> F[Mark existing schedule_nodes actions as executed]
    F --> G[Group jobs using scheduler_groups]
    G --> H[Create schedulers for each group]
    H --> I[Update jobs with scheduler assignments]
    I --> J[Create on_jobs_ready recovery actions for deferred groups]
    J --> K{Submit allocations?}
    K -->|Yes| L[Submit Slurm allocations]
    K -->|No| M[Done]
    L --> M
```

### Step 1: Mark Existing Actions as Executed

All existing `schedule_nodes` actions are marked as executed using the `claim_action` API. This
prevents them from firing again and creating duplicate allocations:

```mermaid
sequenceDiagram
    participant R as regenerate
    participant S as Server
    participant A as workflow_action table

    R->>S: get_workflow_actions(workflow_id)
    S-->>R: [action1, action2, ...]

    loop For each schedule_nodes action
        R->>S: claim_action(action_id)
        S->>A: UPDATE executed=1, executed_at=NOW()
    end
```

### Step 2: Group Jobs Using WorkflowGraph

The system builds a `WorkflowGraph` from pending jobs and uses `scheduler_groups()` to group them by
`(resource_requirements, has_dependencies)`. This aligns with the behavior of
`torc workflows create-slurm`:

- **Jobs without dependencies**: Can be scheduled immediately with `on_workflow_start`
- **Jobs with dependencies** (deferred): Need `on_jobs_ready` recovery actions to schedule when they
  become ready

```mermaid
flowchart TD
    subgraph "Pending Jobs"
        A[Job A: no deps, rr=default]
        B[Job B: no deps, rr=default]
        C[Job C: depends on A, rr=default]
        D[Job D: no deps, rr=gpu]
    end

    subgraph "Scheduler Groups"
        G1[Group 1: default, no deps<br/>Jobs: A, B]
        G2[Group 2: default, has deps<br/>Jobs: C]
        G3[Group 3: gpu, no deps<br/>Jobs: D]
    end

    A --> G1
    B --> G1
    C --> G2
    D --> G3
```

### Step 3: Create Recovery Actions for Deferred Groups

For groups with `has_dependencies = true`, the system creates `on_jobs_ready` recovery actions.
These actions:

- Have `is_recovery = true` to mark them as ephemeral
- Use a `_deferred` suffix in the scheduler name
- Trigger when the blocked jobs become ready
- Schedule additional Slurm allocations for those jobs

```mermaid
flowchart LR
    subgraph "Original Workflow"
        A[Job A: blocked] --> C[Job C: blocked]
        B[Job B: blocked] --> C
    end

    subgraph "Recovery Actions"
        RA[on_jobs_ready: schedule_nodes<br/>job_ids: [A, B]<br/>is_recovery: true]
        RC[on_jobs_ready: schedule_nodes<br/>job_ids: [C]<br/>is_recovery: true]
    end
```

## Recovery Action Lifecycle

Recovery actions are ephemeral - they exist only during the recovery period:

```mermaid
stateDiagram-v2
    [*] --> Created: regenerate creates action
    Created --> Executed: Jobs become ready<br/>action triggers
    Executed --> Deleted: Workflow reinitialized
    Created --> Deleted: Workflow reinitialized
```

When a workflow is reinitialized (e.g., after resetting jobs), all recovery actions are deleted and
original actions are reset to their initial state. This ensures a clean slate for the next run.

## Database Schema

Recovery actions are tracked using the `is_recovery` column in the `workflow_action` table:

| Column        | Type    | Description                            |
| ------------- | ------- | -------------------------------------- |
| `is_recovery` | INTEGER | 0 = normal action, 1 = recovery action |

### Behavior Differences

| Operation                           | Normal Actions        | Recovery Actions        |
| ----------------------------------- | --------------------- | ----------------------- |
| On `reset_actions_for_reinitialize` | Reset `executed` to 0 | Deleted entirely        |
| Created by                          | Workflow spec         | `torc slurm regenerate` |
| Purpose                             | Configured behavior   | Temporary recovery      |

## Usage

```bash
# Regenerate schedulers for pending jobs
torc slurm regenerate <workflow_id> --account <account>

# With automatic submission
torc slurm regenerate <workflow_id> --account <account> --submit

# Using a specific HPC profile
torc slurm regenerate <workflow_id> --account <account> --profile kestrel
```

## Implementation Details

The recovery logic is implemented in:

- `src/client/commands/slurm.rs`: `handle_regenerate` function
- `src/client/workflow_graph.rs`: `WorkflowGraph::from_jobs()` and `scheduler_groups()` methods
- `src/server/api/workflow_actions.rs`: `reset_actions_for_reinitialize` function
- `migrations/20251225000000_add_is_recovery_to_workflow_action.up.sql`: Schema migration

Key implementation notes:

1. **WorkflowGraph construction**: A `WorkflowGraph` is built from pending jobs using `from_jobs()`,
   which reconstructs the dependency structure from `depends_on_job_ids`
2. **Scheduler grouping**: Jobs are grouped using `scheduler_groups()` by
   `(resource_requirements, has_dependencies)`, matching `create-slurm` behavior
3. **Deferred schedulers**: Groups with dependencies get a `_deferred` suffix in the scheduler name
4. **Allocation calculation**: Number of allocations is based on job count and resources per node
5. **Recovery actions**: Only deferred groups (jobs with dependencies) get `on_jobs_ready` recovery
   actions
