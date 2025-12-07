# Central Database

The SQLite database is the heart of Torc's coordination model. All workflow state lives in the database, enabling:

- **Stateless clients and workers** - All state persists in the database
- **Multiple concurrent workers** - Workers coordinate through database locks
- **Fault tolerance** - Workers can crash and restart; state is preserved
- **Workflow resumption** - Workflows can be stopped and restarted without losing progress

## Core Database Tables

- `workflow` - Top-level workflow records with name, user, description
- `workflow_status` - Workflow execution state (run_id, status)
- `job` - Individual computational tasks with commands and status
- `job_internal` - Internal job data (input hashes for change detection)
- `job_depends_on` - Explicit and implicit job dependencies
- `file` - File artifacts with paths and modification times
- `user_data` - JSON data artifacts for passing information between jobs
- `job_input_file`, `job_output_file` - Job-file relationships
- `job_input_user_data`, `job_output_user_data` - Job-user_data relationships
- `resource_requirements` - CPU, memory, GPU, runtime specifications
- `compute_node` - Available compute resources
- `scheduled_compute_node` - Compute nodes allocated to workflows
- `local_scheduler`, `slurm_scheduler` - Execution environment configurations
- `result` - Job execution results (exit code, stdout, stderr)
- `event` - Audit log of workflow events

## Foreign Key Cascades

The schema uses foreign key constraints with cascading deletes. Deleting a workflow automatically removes all associated jobs, files, events, and other related records, ensuring referential integrity.

## Concurrency Model

SQLite uses database-level locking with `BEGIN IMMEDIATE TRANSACTION` to prevent race conditions in critical sections, particularly during job allocation when multiple workers request jobs simultaneously.
