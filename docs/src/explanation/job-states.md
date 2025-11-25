# Job State Transitions

Jobs progress through a defined lifecycle:

```mermaid
stateDiagram-v2
    [*] --> uninitialized
    uninitialized --> ready: initialize_jobs called
    uninitialized --> blocked: initialize_jobs called<br/>(dependencies not met)

    ready --> pending: job runner claims job
    blocked --> ready: dependency completed
    pending --> running: job runner starts job

    running --> completed: exit code 0
    running --> failed: exit code != 0
    running --> canceled: explicit cancellation
    running --> terminated: explicit termination

    completed --> [*]
    failed --> [*]
    canceled --> [*]
    terminated --> [*]
```

## State Descriptions

- **uninitialized** (0) - Job created but dependencies not evaluated
- **blocked** (1) - Waiting for dependencies to complete
- **ready** (2) - All dependencies satisfied, ready for execution
- **pending** (3) - Job claimed by runner
- **running** (4) - Currently executing
- **completed** (5) - Finished successfully (exit code 0)
- **failed** (6) - Finished with error (exit code != 0)
- **canceled** (7) - Explicitly canceled by user or system
- **terminated** (8) - Explicitly terminated by user or system
- **disabled** (9) - Explicitly disabled by user

## Critical State Transitions

1. **initialize_jobs** - Evaluates all dependencies and sets jobs to `ready` or `blocked`
2. **manage_status_change** - Updates job status and triggers cascade effects:
   - When a job completes, checks if blocked jobs become ready
   - Updates workflow status when all jobs complete
   - Handles `cancel_on_blocking_job_failure` flag
