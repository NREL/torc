# Workflow Reinitialization

Reinitialization allows workflows to be rerun when inputs change.

## Reinitialize Process

1. **Bump run_id** - Increments workflow run counter.
2. **Reset workflow status** - Clears previous run state.
3. **Process changed files** - Detects file modifications via `st_mtime`.
4. **Process changed user_data** - Computes input hashes and detects changes.
5. **Mark jobs for rerun** - Sets affected jobs to `uninitialized`.
6. **Re-initialize jobs** - Re-evaluates dependencies and marks jobs `ready`/`blocked`.

## Input Change Detection

The `process_changed_job_inputs` endpoint implements hash-based change detection:

1. For each job, compute SHA256 hash of all input parameters. **Note**: files are tracked by
   modification times, not hashes. User data records are hashed.
2. Compare to stored hash in the database.
3. If hash differs, mark job as `uninitialized`.
4. All updates happen in a single database transaction (all-or-none).

After jobs are marked `uninitialized`, calling `initialize_jobs` re-evaluates the dependency graph:
- Jobs with satisfied dependencies → `ready`
- Jobs waiting on dependencies → `blocked`

## Use Cases

- **Development iteration** - Modify input files and re-run affected jobs
- **Parameter updates** - Change configuration and re-execute
- **Failed job recovery** - Fix issues and re-run without starting from scratch
- **Incremental computation** - Only re-run jobs affected by changes
