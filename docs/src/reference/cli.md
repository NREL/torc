# CLI Reference

This documentation is automatically generated from the CLI help text.

To regenerate, run:
```bash
cargo run --bin generate-cli-docs --features "client,tui,plot_resources"
```

# Command-Line Help for `torc`

This document contains the help content for the `torc` command-line program.

**Command Overview:**

- [CLI Reference](#cli-reference)
- [Command-Line Help for `torc`](#command-line-help-for-torc)
  - [`torc`](#torc)
          - [**Subcommands:**](#subcommands)
          - [**Options:**](#options)
  - [`torc run`](#torc-run)
          - [**Arguments:**](#arguments)
          - [**Options:**](#options-1)
  - [`torc submit`](#torc-submit)
          - [**Arguments:**](#arguments-1)
          - [**Options:**](#options-2)
  - [`torc submit-slurm`](#torc-submit-slurm)
          - [**Arguments:**](#arguments-2)
          - [**Options:**](#options-3)
  - [`torc watch`](#torc-watch)
          - [**Arguments:**](#arguments-3)
          - [**Options:**](#options-4)
  - [`torc workflows`](#torc-workflows)
          - [**Subcommands:**](#subcommands-1)
  - [`torc workflows create`](#torc-workflows-create)
          - [**Arguments:**](#arguments-4)
          - [**Options:**](#options-5)
  - [`torc workflows create-slurm`](#torc-workflows-create-slurm)
          - [**Arguments:**](#arguments-5)
          - [**Options:**](#options-6)
  - [`torc workflows new`](#torc-workflows-new)
          - [**Options:**](#options-7)
  - [`torc workflows list`](#torc-workflows-list)
          - [**Options:**](#options-8)
  - [`torc workflows get`](#torc-workflows-get)
          - [**Arguments:**](#arguments-6)
          - [**Options:**](#options-9)
  - [`torc workflows update`](#torc-workflows-update)
          - [**Arguments:**](#arguments-7)
          - [**Options:**](#options-10)
  - [`torc workflows cancel`](#torc-workflows-cancel)
          - [**Arguments:**](#arguments-8)
  - [`torc workflows delete`](#torc-workflows-delete)
          - [**Arguments:**](#arguments-9)
          - [**Options:**](#options-11)
  - [`torc workflows archive`](#torc-workflows-archive)
          - [**Arguments:**](#arguments-10)
  - [`torc workflows submit`](#torc-workflows-submit)
          - [**Arguments:**](#arguments-11)
          - [**Options:**](#options-12)
  - [`torc workflows run`](#torc-workflows-run)
          - [**Arguments:**](#arguments-12)
          - [**Options:**](#options-13)
  - [`torc workflows initialize`](#torc-workflows-initialize)
          - [**Arguments:**](#arguments-13)
          - [**Options:**](#options-14)
  - [`torc workflows reinitialize`](#torc-workflows-reinitialize)
          - [**Arguments:**](#arguments-14)
          - [**Options:**](#options-15)
  - [`torc workflows status`](#torc-workflows-status)
          - [**Arguments:**](#arguments-15)
          - [**Options:**](#options-16)
  - [`torc workflows reset-status`](#torc-workflows-reset-status)
          - [**Arguments:**](#arguments-16)
          - [**Options:**](#options-17)
  - [`torc workflows execution-plan`](#torc-workflows-execution-plan)
          - [**Arguments:**](#arguments-17)
  - [`torc workflows list-actions`](#torc-workflows-list-actions)
          - [**Arguments:**](#arguments-18)
          - [**Options:**](#options-18)
  - [`torc workflows is-complete`](#torc-workflows-is-complete)
          - [**Arguments:**](#arguments-19)
  - [`torc compute-nodes`](#torc-compute-nodes)
          - [**Subcommands:**](#subcommands-2)
  - [`torc compute-nodes get`](#torc-compute-nodes-get)
          - [**Arguments:**](#arguments-20)
  - [`torc compute-nodes list`](#torc-compute-nodes-list)
          - [**Arguments:**](#arguments-21)
          - [**Options:**](#options-19)
  - [`torc files`](#torc-files)
          - [**Subcommands:**](#subcommands-3)
  - [`torc files create`](#torc-files-create)
          - [**Arguments:**](#arguments-22)
          - [**Options:**](#options-20)
  - [`torc files list`](#torc-files-list)
          - [**Arguments:**](#arguments-23)
          - [**Options:**](#options-21)
  - [`torc files get`](#torc-files-get)
          - [**Arguments:**](#arguments-24)
  - [`torc files update`](#torc-files-update)
          - [**Arguments:**](#arguments-25)
          - [**Options:**](#options-22)
  - [`torc files delete`](#torc-files-delete)
          - [**Arguments:**](#arguments-26)
  - [`torc files list-required-existing`](#torc-files-list-required-existing)
          - [**Arguments:**](#arguments-27)
  - [`torc jobs`](#torc-jobs)
          - [**Subcommands:**](#subcommands-4)
  - [`torc jobs create`](#torc-jobs-create)
          - [**Arguments:**](#arguments-28)
          - [**Options:**](#options-23)
  - [`torc jobs create-from-file`](#torc-jobs-create-from-file)
          - [**Arguments:**](#arguments-29)
          - [**Options:**](#options-24)
  - [`torc jobs list`](#torc-jobs-list)
          - [**Arguments:**](#arguments-30)
          - [**Options:**](#options-25)
  - [`torc jobs get`](#torc-jobs-get)
          - [**Arguments:**](#arguments-31)
  - [`torc jobs update`](#torc-jobs-update)
          - [**Arguments:**](#arguments-32)
          - [**Options:**](#options-26)
  - [`torc jobs delete`](#torc-jobs-delete)
          - [**Arguments:**](#arguments-33)
  - [`torc jobs delete-all`](#torc-jobs-delete-all)
          - [**Arguments:**](#arguments-34)
  - [`torc jobs list-resource-requirements`](#torc-jobs-list-resource-requirements)
          - [**Arguments:**](#arguments-35)
          - [**Options:**](#options-27)
  - [`torc job-dependencies`](#torc-job-dependencies)
          - [**Subcommands:**](#subcommands-5)
  - [`torc job-dependencies job-job`](#torc-job-dependencies-job-job)
          - [**Arguments:**](#arguments-36)
          - [**Options:**](#options-28)
  - [`torc job-dependencies job-file`](#torc-job-dependencies-job-file)
          - [**Arguments:**](#arguments-37)
          - [**Options:**](#options-29)
  - [`torc job-dependencies job-user-data`](#torc-job-dependencies-job-user-data)
          - [**Arguments:**](#arguments-38)
          - [**Options:**](#options-30)
  - [`torc resource-requirements`](#torc-resource-requirements)
          - [**Subcommands:**](#subcommands-6)
  - [`torc resource-requirements create`](#torc-resource-requirements-create)
          - [**Arguments:**](#arguments-39)
          - [**Options:**](#options-31)
  - [`torc resource-requirements list`](#torc-resource-requirements-list)
          - [**Arguments:**](#arguments-40)
          - [**Options:**](#options-32)
  - [`torc resource-requirements get`](#torc-resource-requirements-get)
          - [**Arguments:**](#arguments-41)
  - [`torc resource-requirements update`](#torc-resource-requirements-update)
          - [**Arguments:**](#arguments-42)
          - [**Options:**](#options-33)
  - [`torc resource-requirements delete`](#torc-resource-requirements-delete)
          - [**Arguments:**](#arguments-43)
  - [`torc events`](#torc-events)
          - [**Subcommands:**](#subcommands-7)
  - [`torc events create`](#torc-events-create)
          - [**Arguments:**](#arguments-44)
          - [**Options:**](#options-34)
  - [`torc events list`](#torc-events-list)
          - [**Arguments:**](#arguments-45)
          - [**Options:**](#options-35)
  - [`torc events monitor`](#torc-events-monitor)
          - [**Arguments:**](#arguments-46)
          - [**Options:**](#options-36)
  - [`torc events get-latest-event`](#torc-events-get-latest-event)
          - [**Arguments:**](#arguments-47)
  - [`torc events delete`](#torc-events-delete)
          - [**Arguments:**](#arguments-48)
  - [`torc results`](#torc-results)
          - [**Subcommands:**](#subcommands-8)
  - [`torc results list`](#torc-results-list)
          - [**Arguments:**](#arguments-49)
          - [**Options:**](#options-37)
  - [`torc results get`](#torc-results-get)
          - [**Arguments:**](#arguments-50)
  - [`torc results delete`](#torc-results-delete)
          - [**Arguments:**](#arguments-51)
  - [`torc user-data`](#torc-user-data)
          - [**Subcommands:**](#subcommands-9)
  - [`torc user-data create`](#torc-user-data-create)
          - [**Arguments:**](#arguments-52)
          - [**Options:**](#options-38)
  - [`torc user-data list`](#torc-user-data-list)
          - [**Arguments:**](#arguments-53)
          - [**Options:**](#options-39)
  - [`torc user-data get`](#torc-user-data-get)
          - [**Arguments:**](#arguments-54)
  - [`torc user-data update`](#torc-user-data-update)
          - [**Arguments:**](#arguments-55)
          - [**Options:**](#options-40)
  - [`torc user-data delete`](#torc-user-data-delete)
          - [**Arguments:**](#arguments-56)
  - [`torc user-data delete-all`](#torc-user-data-delete-all)
          - [**Arguments:**](#arguments-57)
  - [`torc user-data list-missing`](#torc-user-data-list-missing)
          - [**Arguments:**](#arguments-58)
  - [`torc slurm`](#torc-slurm)
          - [**Subcommands:**](#subcommands-10)
  - [`torc slurm create`](#torc-slurm-create)
          - [**Arguments:**](#arguments-59)
          - [**Options:**](#options-41)
  - [`torc slurm update`](#torc-slurm-update)
          - [**Arguments:**](#arguments-60)
          - [**Options:**](#options-42)
  - [`torc slurm list`](#torc-slurm-list)
          - [**Arguments:**](#arguments-61)
          - [**Options:**](#options-43)
  - [`torc slurm get`](#torc-slurm-get)
          - [**Arguments:**](#arguments-62)
  - [`torc slurm delete`](#torc-slurm-delete)
          - [**Arguments:**](#arguments-63)
  - [`torc slurm schedule-nodes`](#torc-slurm-schedule-nodes)
          - [**Arguments:**](#arguments-64)
          - [**Options:**](#options-44)
  - [`torc slurm parse-logs`](#torc-slurm-parse-logs)
          - [**Arguments:**](#arguments-65)
          - [**Options:**](#options-45)
  - [`torc slurm sacct`](#torc-slurm-sacct)
          - [**Arguments:**](#arguments-66)
          - [**Options:**](#options-46)
  - [`torc slurm generate`](#torc-slurm-generate)
          - [**Arguments:**](#arguments-67)
          - [**Options:**](#options-47)
  - [`torc slurm regenerate`](#torc-slurm-regenerate)
          - [**Arguments:**](#arguments-68)
          - [**Options:**](#options-48)
  - [`torc scheduled-compute-nodes`](#torc-scheduled-compute-nodes)
          - [**Subcommands:**](#subcommands-11)
  - [`torc scheduled-compute-nodes get`](#torc-scheduled-compute-nodes-get)
          - [**Arguments:**](#arguments-69)
  - [`torc scheduled-compute-nodes list`](#torc-scheduled-compute-nodes-list)
          - [**Arguments:**](#arguments-70)
          - [**Options:**](#options-49)
  - [`torc scheduled-compute-nodes list-jobs`](#torc-scheduled-compute-nodes-list-jobs)
          - [**Arguments:**](#arguments-71)
  - [`torc hpc`](#torc-hpc)
          - [**Subcommands:**](#subcommands-12)
  - [`torc hpc list`](#torc-hpc-list)
  - [`torc hpc detect`](#torc-hpc-detect)
  - [`torc hpc show`](#torc-hpc-show)
          - [**Arguments:**](#arguments-72)
  - [`torc hpc partitions`](#torc-hpc-partitions)
          - [**Arguments:**](#arguments-73)
          - [**Options:**](#options-50)
  - [`torc hpc match`](#torc-hpc-match)
          - [**Options:**](#options-51)
  - [`torc reports`](#torc-reports)
          - [**Subcommands:**](#subcommands-13)
  - [`torc reports check-resource-utilization`](#torc-reports-check-resource-utilization)
          - [**Arguments:**](#arguments-74)
          - [**Options:**](#options-52)
  - [`torc reports results`](#torc-reports-results)
          - [**Arguments:**](#arguments-75)
          - [**Options:**](#options-53)
  - [`torc reports summary`](#torc-reports-summary)
          - [**Arguments:**](#arguments-76)
  - [`torc config`](#torc-config)
          - [**Subcommands:**](#subcommands-14)
  - [`torc config show`](#torc-config-show)
          - [**Options:**](#options-54)
  - [`torc config paths`](#torc-config-paths)
  - [`torc config init`](#torc-config-init)
          - [**Options:**](#options-55)
  - [`torc config validate`](#torc-config-validate)
  - [`torc tui`](#torc-tui)
          - [**Options:**](#options-56)
  - [`torc plot-resources`](#torc-plot-resources)
          - [**Arguments:**](#arguments-77)
          - [**Options:**](#options-57)
  - [`torc completions`](#torc-completions)
          - [**Arguments:**](#arguments-78)

## `torc`

Torc workflow orchestration system

**Usage:** `torc [OPTIONS] <COMMAND>`

###### **Subcommands:**

* `run` — Run a workflow locally (create from spec file or run existing workflow by ID)
* `submit` — Submit a workflow to scheduler (create from spec file or submit existing workflow by ID)
* `submit-slurm` — Submit a workflow to Slurm with auto-generated schedulers
* `watch` — Watch a workflow and automatically recover from failures
* `workflows` — Workflow management commands
* `compute-nodes` — Compute node management commands
* `files` — File management commands
* `jobs` — Job management commands
* `job-dependencies` — Job dependency and relationship queries
* `resource-requirements` — Resource requirements management commands
* `events` — Event management commands
* `results` — Result management commands
* `user-data` — User data management commands
* `slurm` — Slurm scheduler commands
* `scheduled-compute-nodes` — Scheduled compute node management commands
* `hpc` — HPC system profiles and partition information
* `reports` — Generate reports and analytics
* `config` — Manage configuration files and settings
* `tui` — Interactive terminal UI for managing workflows
* `plot-resources` — Generate interactive HTML plots from resource monitoring data
* `completions` — Generate shell completions

###### **Options:**

* `--log-level <LOG_LEVEL>` — Log level (error, warn, info, debug, trace)
* `-f`, `--format <FORMAT>` — Output format (table or json)

  Default value: `table`
* `--url <URL>` — URL of torc server
* `--username <USERNAME>` — Username for basic authentication
* `--password <PASSWORD>` — Password for basic authentication (will prompt if username provided but password not)



## `torc run`

Run a workflow locally (create from spec file or run existing workflow by ID)

**Usage:** `torc run [OPTIONS] <WORKFLOW_SPEC_OR_ID>`

###### **Arguments:**

* `<WORKFLOW_SPEC_OR_ID>` — Path to workflow spec file (JSON/JSON5/YAML) or workflow ID

###### **Options:**

* `--max-parallel-jobs <MAX_PARALLEL_JOBS>` — Maximum number of parallel jobs to run concurrently
* `--num-cpus <NUM_CPUS>` — Number of CPUs available
* `--memory-gb <MEMORY_GB>` — Memory in GB
* `--num-gpus <NUM_GPUS>` — Number of GPUs available
* `-p`, `--poll-interval <POLL_INTERVAL>` — Job completion poll interval in seconds
* `-o`, `--output-dir <OUTPUT_DIR>` — Output directory for jobs
* `--skip-checks` — Skip validation checks (e.g., scheduler node requirements). Use with caution

  Default value: `false`



## `torc submit`

Submit a workflow to scheduler (create from spec file or submit existing workflow by ID)

Requires workflow to have an on_workflow_start action with schedule_nodes. For Slurm workflows without pre-configured schedulers, use `submit-slurm` instead.

**Usage:** `torc submit [OPTIONS] <WORKFLOW_SPEC_OR_ID>`

###### **Arguments:**

* `<WORKFLOW_SPEC_OR_ID>` — Path to workflow spec file (JSON/JSON5/YAML) or workflow ID

###### **Options:**

* `-i`, `--ignore-missing-data` — Ignore missing data (defaults to false)

  Default value: `false`
* `--skip-checks` — Skip validation checks (e.g., scheduler node requirements). Use with caution

  Default value: `false`



## `torc submit-slurm`

Submit a workflow to Slurm with auto-generated schedulers

Automatically generates Slurm schedulers based on job resource requirements and HPC profile.

WARNING: This command uses heuristics to generate schedulers and workflow actions. For complex workflows with unusual dependency patterns, the generated configuration may not be optimal and could waste allocation time.

RECOMMENDED: Preview the generated configuration first with:

torc slurm generate --account <account> workflow.yaml

Review the schedulers and actions to ensure they are appropriate for your workflow before submitting. You can save the output and submit manually:

torc slurm generate --account <account> -o workflow_with_schedulers.yaml workflow.yaml torc submit workflow_with_schedulers.yaml

**Usage:** `torc submit-slurm [OPTIONS] --account <ACCOUNT> <WORKFLOW_SPEC>`

###### **Arguments:**

* `<WORKFLOW_SPEC>` — Path to workflow spec file (JSON/JSON5/YAML/KDL)

###### **Options:**

* `--account <ACCOUNT>` — Slurm account to use for allocations
* `--hpc-profile <HPC_PROFILE>` — HPC profile to use (auto-detected if not specified)
* `--single-allocation` — Bundle all nodes into a single Slurm allocation per scheduler

   By default, creates one Slurm allocation per node (N×1 mode), which allows jobs to start as nodes become available and provides better fault tolerance.

   With this flag, creates one large allocation with all nodes (1×N mode), which requires all nodes to be available simultaneously but uses a single sbatch.
* `-i`, `--ignore-missing-data` — Ignore missing data (defaults to false)

  Default value: `false`
* `--skip-checks` — Skip validation checks (e.g., scheduler node requirements). Use with caution

  Default value: `false`



## `torc watch`

Watch a workflow and automatically recover from failures

Monitors a workflow until completion. With --auto-recover, automatically diagnoses failures, adjusts resource requirements, and resubmits jobs.

Recovery heuristics: - OOM (out of memory): Increase memory by --memory-multiplier (default 1.5x) - Timeout: Increase runtime by --runtime-multiplier (default 1.5x) - Other failures: Retry without changes (transient errors)

Without --auto-recover, reports failures and exits for manual intervention or AI-assisted recovery via the MCP server.

**Usage:** `torc watch [OPTIONS] <WORKFLOW_ID>`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID to watch

###### **Options:**

* `-p`, `--poll-interval <POLL_INTERVAL>` — Poll interval in seconds

  Default value: `60`
* `--auto-recover` — Enable automatic failure recovery
* `--max-retries <MAX_RETRIES>` — Maximum number of recovery attempts

  Default value: `3`
* `--memory-multiplier <MEMORY_MULTIPLIER>` — Memory multiplier for OOM failures (default: 1.5 = 50% increase)

  Default value: `1.5`
* `--runtime-multiplier <RUNTIME_MULTIPLIER>` — Runtime multiplier for timeout failures (default: 1.5 = 50% increase)

  Default value: `1.5`
* `--retry-unknown` — Retry jobs with unknown failure causes (not OOM or timeout)

   By default, only jobs that failed due to OOM or timeout are retried (with increased resources). Jobs with unknown failure causes are skipped since they likely have script or data bugs that won't be fixed by retrying.

   Enable this flag to also retry jobs with unknown failures (e.g., to handle transient errors like network issues or filesystem glitches).
* `--recovery-hook <RECOVERY_HOOK>` — Custom recovery hook command for unknown failures

   When jobs fail with unknown causes (not OOM or timeout), this command is executed before resetting jobs for retry. Use this to run custom recovery logic, such as adjusting Spark cluster sizes or fixing configuration issues.

   The workflow ID is passed as both an argument and environment variable: - Argument: `<command> <workflow_id>` - Environment: `TORC_WORKFLOW_ID=<workflow_id>`

   Example: --recovery-hook "bash fix-spark-cluster.sh"
* `-o`, `--output-dir <OUTPUT_DIR>` — Output directory for job files

  Default value: `output`
* `--show-job-counts` — Show job counts by status during polling

   WARNING: This option queries all jobs on each poll, which can cause high server load for large workflows. Only use for debugging or small workflows.



## `torc workflows`

Workflow management commands

**Usage:** `torc workflows <COMMAND>`

###### **Subcommands:**

* `create` — Create a workflow from a specification file (supports JSON, JSON5, YAML, and KDL formats)
* `create-slurm` — Create a workflow with auto-generated Slurm schedulers
* `new` — Create a new empty workflow
* `list` — List workflows
* `get` — Get a specific workflow by ID
* `update` — Update an existing workflow
* `cancel` — Cancel a workflow and all associated Slurm jobs
* `delete` — Delete one or more workflows
* `archive` — Archive or unarchive one or more workflows
* `submit` — Submit a workflow: initialize if needed and schedule nodes for on_workflow_start actions This command requires the workflow to have an on_workflow_start action with schedule_nodes
* `run` — Run a workflow locally on the current node
* `initialize` — Initialize a workflow, including all job statuses
* `reinitialize` — Reinitialize a workflow. This will reinitialize all jobs with a status of canceled, submitting, pending, or terminated. Jobs with a status of done will also be reinitialized if an input_file or user_data record has changed
* `status` — Get workflow status
* `reset-status` — Reset workflow and job status
* `execution-plan` — Show the execution plan for a workflow specification or existing workflow
* `list-actions` — List workflow actions and their statuses (useful for debugging action triggers)
* `is-complete` — Check if a workflow is complete



## `torc workflows create`

Create a workflow from a specification file (supports JSON, JSON5, YAML, and KDL formats)

**Usage:** `torc workflows create [OPTIONS] --user <USER> <FILE>`

###### **Arguments:**

* `<FILE>` — Path to specification file containing WorkflowSpec

   Supported formats: - JSON (.json): Standard JSON format - JSON5 (.json5): JSON with comments and trailing commas - YAML (.yaml, .yml): Human-readable YAML format - KDL (.kdl): KDL document format

   Format is auto-detected from file extension, with fallback parsing attempted

###### **Options:**

* `-u`, `--user <USER>` — User that owns the workflow (defaults to USER environment variable)
* `--no-resource-monitoring` — Disable resource monitoring (default: enabled with summary granularity and 5s sample rate)

  Default value: `false`
* `--skip-checks` — Skip validation checks (e.g., scheduler node requirements). Use with caution

  Default value: `false`
* `--dry-run` — Validate the workflow specification without creating it (dry-run mode) Returns a summary of what would be created including job count after parameter expansion



## `torc workflows create-slurm`

Create a workflow with auto-generated Slurm schedulers

Automatically generates Slurm schedulers based on job resource requirements and HPC profile. For Slurm workflows without pre-configured schedulers.

**Usage:** `torc workflows create-slurm [OPTIONS] --account <ACCOUNT> --user <USER> <FILE>`

###### **Arguments:**

* `<FILE>` — Path to specification file containing WorkflowSpec

###### **Options:**

* `--account <ACCOUNT>` — Slurm account to use for allocations
* `--hpc-profile <HPC_PROFILE>` — HPC profile to use (auto-detected if not specified)
* `--single-allocation` — Bundle all nodes into a single Slurm allocation per scheduler

   By default, creates one Slurm allocation per node (N×1 mode), which allows jobs to start as nodes become available and provides better fault tolerance.

   With this flag, creates one large allocation with all nodes (1×N mode), which requires all nodes to be available simultaneously but uses a single sbatch.
* `-u`, `--user <USER>` — User that owns the workflow (defaults to USER environment variable)
* `--no-resource-monitoring` — Disable resource monitoring (default: enabled with summary granularity and 5s sample rate)

  Default value: `false`
* `--skip-checks` — Skip validation checks (e.g., scheduler node requirements). Use with caution

  Default value: `false`
* `--dry-run` — Validate the workflow specification without creating it (dry-run mode)



## `torc workflows new`

Create a new empty workflow

**Usage:** `torc workflows new [OPTIONS] --name <NAME> --user <USER>`

###### **Options:**

* `-n`, `--name <NAME>` — Name of the workflow
* `-d`, `--description <DESCRIPTION>` — Description of the workflow
* `-u`, `--user <USER>` — User that owns the workflow (defaults to USER environment variable)



## `torc workflows list`

List workflows

**Usage:** `torc workflows list [OPTIONS]`

###### **Options:**

* `-u`, `--user <USER>` — User to filter by (defaults to USER environment variable)
* `--all-users` — List workflows for all users (overrides --user)
* `-l`, `--limit <LIMIT>` — Maximum number of workflows to return

  Default value: `10000`
* `--offset <OFFSET>` — Offset for pagination (0-based)

  Default value: `0`
* `--sort-by <SORT_BY>` — Field to sort by
* `--reverse-sort` — Reverse sort order
* `--archived-only` — Show only archived workflows

  Default value: `false`
* `--include-archived` — Include both archived and non-archived workflows

  Default value: `false`



## `torc workflows get`

Get a specific workflow by ID

**Usage:** `torc workflows get [OPTIONS] [ID]`

###### **Arguments:**

* `<ID>` — ID of the workflow to get (optional - will prompt if not provided)

###### **Options:**

* `-u`, `--user <USER>` — User to filter by (defaults to USER environment variable)



## `torc workflows update`

Update an existing workflow

**Usage:** `torc workflows update [OPTIONS] [ID]`

###### **Arguments:**

* `<ID>` — ID of the workflow to update (optional - will prompt if not provided)

###### **Options:**

* `-n`, `--name <NAME>` — Name of the workflow
* `-d`, `--description <DESCRIPTION>` — Description of the workflow
* `--owner-user <OWNER_USER>` — User that owns the workflow



## `torc workflows cancel`

Cancel a workflow and all associated Slurm jobs

**Usage:** `torc workflows cancel [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — ID of the workflow to cancel (optional - will prompt if not provided)



## `torc workflows delete`

Delete one or more workflows

**Usage:** `torc workflows delete [OPTIONS] [IDS]...`

###### **Arguments:**

* `<IDS>` — IDs of workflows to remove (optional - will prompt if not provided)

###### **Options:**

* `--no-prompts` — Skip confirmation prompt
* `--force` — Force deletion even if workflow belongs to a different user



## `torc workflows archive`

Archive or unarchive one or more workflows

**Usage:** `torc workflows archive <IS_ARCHIVED> [WORKFLOW_IDS]...`

###### **Arguments:**

* `<IS_ARCHIVED>` — Set to true to archive, false to unarchive
* `<WORKFLOW_IDS>` — IDs of workflows to archive/unarchive (if empty, will prompt for selection)



## `torc workflows submit`

Submit a workflow: initialize if needed and schedule nodes for on_workflow_start actions This command requires the workflow to have an on_workflow_start action with schedule_nodes

**Usage:** `torc workflows submit [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — ID of the workflow to submit (optional - will prompt if not provided)

###### **Options:**

* `--force` — If false, fail the operation if missing data is present (defaults to false)

  Default value: `false`



## `torc workflows run`

Run a workflow locally on the current node

**Usage:** `torc workflows run [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — ID of the workflow to run (optional - will prompt if not provided)

###### **Options:**

* `-p`, `--poll-interval <POLL_INTERVAL>` — Poll interval in seconds for checking job completion

  Default value: `5.0`
* `--max-parallel-jobs <MAX_PARALLEL_JOBS>` — Maximum number of parallel jobs to run (defaults to available CPUs)
* `--output-dir <OUTPUT_DIR>` — Output directory for job logs and results

  Default value: `output`



## `torc workflows initialize`

Initialize a workflow, including all job statuses

**Usage:** `torc workflows initialize [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — ID of the workflow to start (optional - will prompt if not provided)

###### **Options:**

* `--force` — If false, fail the operation if missing data is present (defaults to false)

  Default value: `false`
* `--no-prompts` — Skip confirmation prompt
* `--dry-run` — Perform a dry run without making changes



## `torc workflows reinitialize`

Reinitialize a workflow. This will reinitialize all jobs with a status of canceled, submitting, pending, or terminated. Jobs with a status of done will also be reinitialized if an input_file or user_data record has changed

**Usage:** `torc workflows reinitialize [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — ID of the workflow to reinitialize (optional - will prompt if not provided)

###### **Options:**

* `--force` — If false, fail the operation if missing data is present (defaults to false)

  Default value: `false`
* `--dry-run` — Perform a dry run without making changes



## `torc workflows status`

Get workflow status

**Usage:** `torc workflows status [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — ID of the workflow to get status for (optional - will prompt if not provided)

###### **Options:**

* `-u`, `--user <USER>` — User to filter by (defaults to USER environment variable)



## `torc workflows reset-status`

Reset workflow and job status

**Usage:** `torc workflows reset-status [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — ID of the workflow to reset status for (optional - will prompt if not provided)

###### **Options:**

* `--failed-only` — Only reset failed jobs

  Default value: `false`
* `-r`, `--reinitialize` — Reinitialize the workflow after resetting status

  Default value: `false`
* `--force` — Force reset even if there are active jobs (ignores running/pending jobs check)

  Default value: `false`
* `--no-prompts` — Skip confirmation prompt



## `torc workflows execution-plan`

Show the execution plan for a workflow specification or existing workflow

**Usage:** `torc workflows execution-plan <SPEC_OR_ID>`

###### **Arguments:**

* `<SPEC_OR_ID>` — Path to specification file OR workflow ID



## `torc workflows list-actions`

List workflow actions and their statuses (useful for debugging action triggers)

**Usage:** `torc workflows list-actions [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — ID of the workflow to show actions for (optional - will prompt if not provided)

###### **Options:**

* `-u`, `--user <USER>` — User to filter by when selecting workflow interactively (defaults to USER environment variable)



## `torc workflows is-complete`

Check if a workflow is complete

**Usage:** `torc workflows is-complete [ID]`

###### **Arguments:**

* `<ID>` — ID of the workflow to check (optional - will prompt if not provided)



## `torc compute-nodes`

Compute node management commands

**Usage:** `torc compute-nodes <COMMAND>`

###### **Subcommands:**

* `get` — Get a specific compute node by ID
* `list` — List compute nodes for a workflow



## `torc compute-nodes get`

Get a specific compute node by ID

**Usage:** `torc compute-nodes get <ID>`

###### **Arguments:**

* `<ID>` — ID of the compute node



## `torc compute-nodes list`

List compute nodes for a workflow

**Usage:** `torc compute-nodes list [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — List compute nodes for this workflow (optional - will prompt if not provided)

###### **Options:**

* `-l`, `--limit <LIMIT>` — Maximum number of compute nodes to return

  Default value: `10000`
* `-o`, `--offset <OFFSET>` — Offset for pagination (0-based)

  Default value: `0`
* `-s`, `--sort-by <SORT_BY>` — Field to sort by
* `-r`, `--reverse-sort` — Reverse sort order

  Default value: `false`
* `--scheduled-compute-node <SCHEDULED_COMPUTE_NODE>` — Filter by scheduled compute node ID



## `torc files`

File management commands

**Usage:** `torc files <COMMAND>`

###### **Subcommands:**

* `create` — Create a new file
* `list` — List files
* `get` — Get a specific file by ID
* `update` — Update an existing file
* `delete` — Delete a file
* `list-required-existing` — List required existing files for a workflow



## `torc files create`

Create a new file

**Usage:** `torc files create --name <NAME> --path <PATH> [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Create the file in this workflow

###### **Options:**

* `-n`, `--name <NAME>` — Name of the job
* `-p`, `--path <PATH>` — Path of the file



## `torc files list`

List files

**Usage:** `torc files list [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — List files for this workflow (optional - will prompt if not provided)

###### **Options:**

* `--produced-by-job-id <PRODUCED_BY_JOB_ID>` — Filter by job ID that produced the files
* `-l`, `--limit <LIMIT>` — Maximum number of files to return

  Default value: `10000`
* `--offset <OFFSET>` — Offset for pagination (0-based)

  Default value: `0`
* `--sort-by <SORT_BY>` — Field to sort by
* `--reverse-sort` — Reverse sort order



## `torc files get`

Get a specific file by ID

**Usage:** `torc files get <ID>`

###### **Arguments:**

* `<ID>` — ID of the file to get



## `torc files update`

Update an existing file

**Usage:** `torc files update [OPTIONS] <ID>`

###### **Arguments:**

* `<ID>` — ID of the file to update

###### **Options:**

* `-n`, `--name <NAME>` — Name of the file
* `-p`, `--path <PATH>` — Path of the file



## `torc files delete`

Delete a file

**Usage:** `torc files delete <ID>`

###### **Arguments:**

* `<ID>` — ID of the file to remove



## `torc files list-required-existing`

List required existing files for a workflow

**Usage:** `torc files list-required-existing [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — List required existing files for this workflow (optional - will prompt if not provided)



## `torc jobs`

Job management commands

**Usage:** `torc jobs <COMMAND>`

###### **Subcommands:**

* `create` — Create a new job
* `create-from-file` — Create multiple jobs from a text file containing one command per line
* `list` — List jobs
* `get` — Get a specific job by ID
* `update` — Update an existing job
* `delete` — Delete one or more jobs
* `delete-all` — Delete all jobs for a workflow
* `list-resource-requirements` — List jobs with their resource requirements



## `torc jobs create`

Create a new job

**Usage:** `torc jobs create [OPTIONS] --name <NAME> --command <COMMAND> [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Create the job in this workflow

###### **Options:**

* `-n`, `--name <NAME>` — Name of the job
* `-c`, `--command <COMMAND>` — Command to execute
* `-r`, `--resource-requirements-id <RESOURCE_REQUIREMENTS_ID>` — Resource requirements ID for this job
* `-b`, `--blocking-job-ids <BLOCKING_JOB_IDS>` — Job IDs that block this job
* `-i`, `--input-file-ids <INPUT_FILE_IDS>` — Input files needed by this job
* `-o`, `--output-file-ids <OUTPUT_FILE_IDS>` — Output files produced by this job



## `torc jobs create-from-file`

Create multiple jobs from a text file containing one command per line

This command reads a text file where each line contains a job command. Lines starting with '#' are treated as comments and ignored. Empty lines are also ignored.

Jobs will be named sequentially as job1, job2, job3, etc., starting from the current job count + 1 to avoid naming conflicts.

All jobs created will share the same resource requirements, which are automatically created and assigned.

Example: torc jobs create-from-file 123 batch_jobs.txt --cpus-per-job 4 --memory-per-job 8g

**Usage:** `torc jobs create-from-file [OPTIONS] <WORKFLOW_ID> <FILE>`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID to create jobs for
* `<FILE>` — Path to text file containing job commands (one per line)

   File format: - One command per line - Lines starting with # are comments (ignored) - Empty lines are ignored

   Example file content: # Data processing jobs python process.py --batch 1 python process.py --batch 2 python process.py --batch 3

###### **Options:**

* `--cpus-per-job <CPUS_PER_JOB>` — Number of CPUs per job

  Default value: `1`
* `--memory-per-job <MEMORY_PER_JOB>` — Memory per job (e.g., "1m", "2g", "16g")

  Default value: `1m`
* `--runtime-per-job <RUNTIME_PER_JOB>` — Runtime per job (ISO 8601 duration format)

   Examples: P0DT1M    = 1 minute P0DT30M   = 30 minutes P0DT2H    = 2 hours P1DT0H    = 1 day

  Default value: `P0DT1M`



## `torc jobs list`

List jobs

**Usage:** `torc jobs list [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — List jobs for this workflow (optional - will prompt if not provided)

###### **Options:**

* `-s`, `--status <STATUS>` — User to filter by (defaults to USER environment variable)
* `--upstream-job-id <UPSTREAM_JOB_ID>` — Filter by upstream job ID (jobs that depend on this job)
* `-l`, `--limit <LIMIT>` — Maximum number of jobs to return

  Default value: `10000`
* `--offset <OFFSET>` — Offset for pagination (0-based)

  Default value: `0`
* `--sort-by <SORT_BY>` — Field to sort by
* `--reverse-sort` — Reverse sort order
* `--include-relationships` — Include job relationships (depends_on_job_ids, input/output file/user_data IDs) - slower but more complete



## `torc jobs get`

Get a specific job by ID

**Usage:** `torc jobs get <ID>`

###### **Arguments:**

* `<ID>` — ID of the job to get



## `torc jobs update`

Update an existing job

**Usage:** `torc jobs update [OPTIONS] <ID>`

###### **Arguments:**

* `<ID>` — ID of the job to update

###### **Options:**

* `-n`, `--name <NAME>` — Name of the job
* `-c`, `--command <COMMAND>` — Command to execute



## `torc jobs delete`

Delete one or more jobs

**Usage:** `torc jobs delete [IDS]...`

###### **Arguments:**

* `<IDS>` — IDs of the jobs to remove



## `torc jobs delete-all`

Delete all jobs for a workflow

**Usage:** `torc jobs delete-all [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID to delete all jobs from (optional - will prompt if not provided)



## `torc jobs list-resource-requirements`

List jobs with their resource requirements

**Usage:** `torc jobs list-resource-requirements [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID to list jobs from (optional - will prompt if not provided)

###### **Options:**

* `-j`, `--job-id <JOB_ID>` — Filter by specific job ID



## `torc job-dependencies`

Job dependency and relationship queries

**Usage:** `torc job-dependencies <COMMAND>`

###### **Subcommands:**

* `job-job` — List job-to-job dependencies for a workflow
* `job-file` — List job-file relationships for a workflow
* `job-user-data` — List job-user_data relationships for a workflow



## `torc job-dependencies job-job`

List job-to-job dependencies for a workflow

**Usage:** `torc job-dependencies job-job [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — ID of the workflow (optional - will prompt if not provided)

###### **Options:**

* `-l`, `--limit <LIMIT>` — Maximum number of dependencies to return

  Default value: `10000`
* `--offset <OFFSET>` — Offset for pagination (0-based)

  Default value: `0`



## `torc job-dependencies job-file`

List job-file relationships for a workflow

**Usage:** `torc job-dependencies job-file [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — ID of the workflow (optional - will prompt if not provided)

###### **Options:**

* `-l`, `--limit <LIMIT>` — Maximum number of relationships to return

  Default value: `10000`
* `--offset <OFFSET>` — Offset for pagination (0-based)

  Default value: `0`



## `torc job-dependencies job-user-data`

List job-user_data relationships for a workflow

**Usage:** `torc job-dependencies job-user-data [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — ID of the workflow (optional - will prompt if not provided)

###### **Options:**

* `-l`, `--limit <LIMIT>` — Maximum number of relationships to return

  Default value: `10000`
* `--offset <OFFSET>` — Offset for pagination (0-based)

  Default value: `0`



## `torc resource-requirements`

Resource requirements management commands

**Usage:** `torc resource-requirements <COMMAND>`

###### **Subcommands:**

* `create` — Create new resource requirements
* `list` — List resource requirements
* `get` — Get a specific resource requirement by ID
* `update` — Update existing resource requirements
* `delete` — Delete resource requirements



## `torc resource-requirements create`

Create new resource requirements

**Usage:** `torc resource-requirements create [OPTIONS] --name <NAME> [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Create resource requirements in this workflow

###### **Options:**

* `-n`, `--name <NAME>` — Name of the resource requirements
* `--num-cpus <NUM_CPUS>` — Number of CPUs required

  Default value: `1`
* `--num-gpus <NUM_GPUS>` — Number of GPUs required

  Default value: `0`
* `--num-nodes <NUM_NODES>` — Number of nodes required

  Default value: `1`
* `-m`, `--memory <MEMORY>` — Amount of memory required (e.g., "20g")

  Default value: `1m`
* `-r`, `--runtime <RUNTIME>` — Maximum runtime in ISO 8601 duration format (e.g., "P0DT1H")

  Default value: `P0DT1M`



## `torc resource-requirements list`

List resource requirements

**Usage:** `torc resource-requirements list [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — List resource requirements for this workflow (optional - will prompt if not provided)

###### **Options:**

* `-l`, `--limit <LIMIT>` — Maximum number of resource requirements to return

  Default value: `10000`
* `--offset <OFFSET>` — Offset for pagination (0-based)

  Default value: `0`
* `--sort-by <SORT_BY>` — Field to sort by
* `--reverse-sort` — Reverse sort order



## `torc resource-requirements get`

Get a specific resource requirement by ID

**Usage:** `torc resource-requirements get <ID>`

###### **Arguments:**

* `<ID>` — ID of the resource requirement to get



## `torc resource-requirements update`

Update existing resource requirements

**Usage:** `torc resource-requirements update [OPTIONS] <ID>`

###### **Arguments:**

* `<ID>` — ID of the resource requirement to update

###### **Options:**

* `-n`, `--name <NAME>` — Name of the resource requirements
* `--num-cpus <NUM_CPUS>` — Number of CPUs required
* `--num-gpus <NUM_GPUS>` — Number of GPUs required
* `--num-nodes <NUM_NODES>` — Number of nodes required
* `--memory <MEMORY>` — Amount of memory required (e.g., "20g")
* `--runtime <RUNTIME>` — Maximum runtime (e.g., "1h", "30m")



## `torc resource-requirements delete`

Delete resource requirements

**Usage:** `torc resource-requirements delete <ID>`

###### **Arguments:**

* `<ID>` — ID of the resource requirement to remove



## `torc events`

Event management commands

**Usage:** `torc events <COMMAND>`

###### **Subcommands:**

* `create` — Create a new event
* `list` — List events for a workflow
* `monitor` — Monitor events for a workflow in real-time
* `get-latest-event` — Get the latest event for a workflow
* `delete` — Delete an event



## `torc events create`

Create a new event

**Usage:** `torc events create --data <DATA> [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Create the event in this workflow

###### **Options:**

* `-d`, `--data <DATA>` — JSON data for the event



## `torc events list`

List events for a workflow

**Usage:** `torc events list [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — List events for this workflow (optional - will prompt if not provided)

###### **Options:**

* `-c`, `--category <CATEGORY>` — Filter events by category
* `-l`, `--limit <LIMIT>` — Maximum number of events to return

  Default value: `10000`
* `-o`, `--offset <OFFSET>` — Offset for pagination (0-based)

  Default value: `0`
* `-s`, `--sort-by <SORT_BY>` — Field to sort by
* `-r`, `--reverse-sort` — Reverse sort order

  Default value: `false`



## `torc events monitor`

Monitor events for a workflow in real-time

**Usage:** `torc events monitor [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Monitor events for this workflow (optional - will prompt if not provided)

###### **Options:**

* `-d`, `--duration <DURATION>` — Duration to monitor in minutes (default: infinite)
* `-p`, `--poll-interval <POLL_INTERVAL>` — Poll interval in seconds (default: 60)

  Default value: `60`
* `-c`, `--category <CATEGORY>` — Filter events by category



## `torc events get-latest-event`

Get the latest event for a workflow

**Usage:** `torc events get-latest-event [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Get the latest event for this workflow (optional - will prompt if not provided)



## `torc events delete`

Delete an event

**Usage:** `torc events delete <ID>`

###### **Arguments:**

* `<ID>` — ID of the event to remove



## `torc results`

Result management commands

**Usage:** `torc results <COMMAND>`

###### **Subcommands:**

* `list` — List results
* `get` — Get a specific result by ID
* `delete` — Delete a result



## `torc results list`

List results

**Usage:** `torc results list [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — List results for this workflow (optional - will prompt if not provided). By default, only lists results for the latest run of the workflow

###### **Options:**

* `-j`, `--job-id <JOB_ID>` — List results for this job
* `-r`, `--run-id <RUN_ID>` — List results for this run_id
* `--return-code <RETURN_CODE>` — Filter by return code
* `--failed` — Show only failed jobs (non-zero return code)
* `-s`, `--status <STATUS>` — Filter by job status (uninitialized, blocked, canceled, terminated, done, ready, scheduled, running, pending, disabled)
* `-l`, `--limit <LIMIT>` — Maximum number of results to return

  Default value: `10000`
* `--offset <OFFSET>` — Offset for pagination (0-based)

  Default value: `0`
* `--sort-by <SORT_BY>` — Field to sort by
* `--reverse-sort` — Reverse sort order
* `--all-runs` — Show all historical results (default: false, only shows current results)
* `--compute-node <COMPUTE_NODE>` — Filter by compute node ID



## `torc results get`

Get a specific result by ID

**Usage:** `torc results get <ID>`

###### **Arguments:**

* `<ID>` — ID of the result to get



## `torc results delete`

Delete a result

**Usage:** `torc results delete <ID>`

###### **Arguments:**

* `<ID>` — ID of the result to remove



## `torc user-data`

User data management commands

**Usage:** `torc user-data <COMMAND>`

###### **Subcommands:**

* `create` — Create a new user data record
* `list` — List user data records
* `get` — Get a specific user data record
* `update` — Update a user data record
* `delete` — Delete a user data record
* `delete-all` — Delete all user data records for a workflow
* `list-missing` — List missing user data for a workflow



## `torc user-data create`

Create a new user data record

**Usage:** `torc user-data create [OPTIONS] --name <NAME> [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID

###### **Options:**

* `-n`, `--name <NAME>` — Name of the data object
* `-d`, `--data <DATA>` — JSON data content
* `--ephemeral` — Whether the data is ephemeral (cleared between runs)
* `--consumer-job-id <CONSUMER_JOB_ID>` — Consumer job ID (optional)
* `--producer-job-id <PRODUCER_JOB_ID>` — Producer job ID (optional)



## `torc user-data list`

List user data records

**Usage:** `torc user-data list [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID (if not provided, will be selected interactively)

###### **Options:**

* `-l`, `--limit <LIMIT>` — Maximum number of records to return

  Default value: `50`
* `-o`, `--offset <OFFSET>` — Number of records to skip

  Default value: `0`
* `--sort-by <SORT_BY>` — Field to sort by
* `--reverse-sort` — Reverse sort order
* `--name <NAME>` — Filter by name
* `--is-ephemeral <IS_EPHEMERAL>` — Filter by ephemeral status

  Possible values: `true`, `false`

* `--consumer-job-id <CONSUMER_JOB_ID>` — Filter by consumer job ID
* `--producer-job-id <PRODUCER_JOB_ID>` — Filter by producer job ID



## `torc user-data get`

Get a specific user data record

**Usage:** `torc user-data get <ID>`

###### **Arguments:**

* `<ID>` — User data record ID



## `torc user-data update`

Update a user data record

**Usage:** `torc user-data update [OPTIONS] <ID>`

###### **Arguments:**

* `<ID>` — User data record ID

###### **Options:**

* `-n`, `--name <NAME>` — New name for the data object
* `-d`, `--data <DATA>` — New JSON data content
* `--ephemeral <EPHEMERAL>` — Update ephemeral status

  Possible values: `true`, `false`




## `torc user-data delete`

Delete a user data record

**Usage:** `torc user-data delete <ID>`

###### **Arguments:**

* `<ID>` — User data record ID



## `torc user-data delete-all`

Delete all user data records for a workflow

**Usage:** `torc user-data delete-all <WORKFLOW_ID>`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID



## `torc user-data list-missing`

List missing user data for a workflow

**Usage:** `torc user-data list-missing <WORKFLOW_ID>`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID



## `torc slurm`

Slurm scheduler commands

**Usage:** `torc slurm <COMMAND>`

###### **Subcommands:**

* `create` — Add a Slurm config to the database
* `update` — Modify a Slurm config in the database
* `list` — Show the current Slurm configs in the database
* `get` — Get a specific Slurm config by ID
* `delete` — Delete a Slurm config by ID
* `schedule-nodes` — Schedule compute nodes using Slurm
* `parse-logs` — Parse Slurm log files for known error messages
* `sacct` — Call sacct for scheduled compute nodes and display summary
* `generate` — Generate Slurm schedulers for a workflow based on job resource requirements
* `regenerate` — Regenerate Slurm schedulers for an existing workflow based on pending jobs



## `torc slurm create`

Add a Slurm config to the database

**Usage:** `torc slurm create [OPTIONS] --name <NAME> --account <ACCOUNT> [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID

###### **Options:**

* `-n`, `--name <NAME>` — Name of config
* `-a`, `--account <ACCOUNT>` — HPC account
* `-g`, `--gres <GRES>` — Request nodes that have at least this number of GPUs. Ex: 'gpu:2'
* `-m`, `--mem <MEM>` — Request nodes that have at least this amount of memory. Ex: '180G'
* `-N`, `--nodes <NODES>` — Number of nodes to use for each job

  Default value: `1`
* `-p`, `--partition <PARTITION>` — HPC partition. Default is determined by the scheduler
* `-q`, `--qos <QOS>` — Controls priority of the jobs

  Default value: `normal`
* `-t`, `--tmp <TMP>` — Request nodes that have at least this amount of storage scratch space
* `-W`, `--walltime <WALLTIME>` — Slurm job walltime

  Default value: `04:00:00`
* `-e`, `--extra <EXTRA>` — Add extra Slurm parameters, for example --extra='--reservation=my-reservation'



## `torc slurm update`

Modify a Slurm config in the database

**Usage:** `torc slurm update [OPTIONS] <SCHEDULER_ID>`

###### **Arguments:**

* `<SCHEDULER_ID>`

###### **Options:**

* `-N`, `--name <NAME>` — Name of config
* `-a`, `--account <ACCOUNT>` — HPC account
* `-g`, `--gres <GRES>` — Request nodes that have at least this number of GPUs. Ex: 'gpu:2'
* `-m`, `--mem <MEM>` — Request nodes that have at least this amount of memory. Ex: '180G'
* `-n`, `--nodes <NODES>` — Number of nodes to use for each job
* `-p`, `--partition <PARTITION>` — HPC partition
* `-q`, `--qos <QOS>` — Controls priority of the jobs
* `-t`, `--tmp <TMP>` — Request nodes that have at least this amount of storage scratch space
* `--walltime <WALLTIME>` — Slurm job walltime
* `-e`, `--extra <EXTRA>` — Add extra Slurm parameters



## `torc slurm list`

Show the current Slurm configs in the database

**Usage:** `torc slurm list [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID

###### **Options:**

* `-l`, `--limit <LIMIT>` — Maximum number of configs to return

  Default value: `10000`
* `--offset <OFFSET>` — Offset for pagination (0-based)

  Default value: `0`



## `torc slurm get`

Get a specific Slurm config by ID

**Usage:** `torc slurm get <ID>`

###### **Arguments:**

* `<ID>` — ID of the Slurm config to get



## `torc slurm delete`

Delete a Slurm config by ID

**Usage:** `torc slurm delete <ID>`

###### **Arguments:**

* `<ID>` — ID of the Slurm config to delete



## `torc slurm schedule-nodes`

Schedule compute nodes using Slurm

**Usage:** `torc slurm schedule-nodes [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID

###### **Options:**

* `-j`, `--job-prefix <JOB_PREFIX>` — Job prefix for the Slurm job names

  Default value: `worker`
* `--keep-submission-scripts` — Keep submission scripts after job submission

  Default value: `false`
* `-m`, `--max-parallel-jobs <MAX_PARALLEL_JOBS>` — Maximum number of parallel jobs
* `-n`, `--num-hpc-jobs <NUM_HPC_JOBS>` — Number of HPC jobs to submit

  Default value: `1`
* `-o`, `--output <OUTPUT>` — Output directory for job output files

  Default value: `output`
* `-p`, `--poll-interval <POLL_INTERVAL>` — Poll interval in seconds

  Default value: `60`
* `--scheduler-config-id <SCHEDULER_CONFIG_ID>` — Scheduler config ID
* `--start-one-worker-per-node` — Start one worker per node

  Default value: `false`



## `torc slurm parse-logs`

Parse Slurm log files for known error messages

**Usage:** `torc slurm parse-logs [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID

###### **Options:**

* `-o`, `--output-dir <OUTPUT_DIR>` — Output directory containing Slurm log files

  Default value: `output`
* `--errors-only` — Only show errors (skip warnings)

  Default value: `false`



## `torc slurm sacct`

Call sacct for scheduled compute nodes and display summary

**Usage:** `torc slurm sacct [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID

###### **Options:**

* `-o`, `--output-dir <OUTPUT_DIR>` — Output directory for sacct JSON files (only used with --save-json)

  Default value: `output`
* `--save-json` — Save full JSON output to files in addition to displaying summary

  Default value: `false`



## `torc slurm generate`

Generate Slurm schedulers for a workflow based on job resource requirements

**Usage:** `torc slurm generate [OPTIONS] --account <ACCOUNT> <WORKFLOW_FILE>`

###### **Arguments:**

* `<WORKFLOW_FILE>` — Path to workflow specification file (YAML, JSON, JSON5, or KDL)

###### **Options:**

* `--account <ACCOUNT>` — Slurm account to use
* `--profile <PROFILE>` — HPC profile to use (if not specified, tries to detect current system)
* `-o`, `--output <OUTPUT>` — Output file path (if not specified, prints to stdout)
* `--single-allocation` — Bundle all nodes into a single Slurm allocation per scheduler

   By default, creates one Slurm allocation per node (N×1 mode), which allows jobs to start as nodes become available and provides better fault tolerance.

   With this flag, creates one large allocation with all nodes (1×N mode), which requires all nodes to be available simultaneously but uses a single sbatch.
* `--no-actions` — Don't add workflow actions for scheduling nodes
* `--force` — Force overwrite of existing schedulers in the workflow



## `torc slurm regenerate`

Regenerate Slurm schedulers for an existing workflow based on pending jobs

Analyzes jobs that are uninitialized, ready, or blocked and generates new Slurm schedulers to run them. Uses existing scheduler configurations as defaults for account, partition, and other settings.

This is useful for recovery after job failures: update job resources, reset failed jobs, then regenerate schedulers to submit new allocations.

**Usage:** `torc slurm regenerate [OPTIONS] <WORKFLOW_ID>`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID

###### **Options:**

* `--account <ACCOUNT>` — Slurm account to use (defaults to account from existing schedulers)
* `--profile <PROFILE>` — HPC profile to use (if not specified, tries to detect current system)
* `--single-allocation` — Bundle all nodes into a single Slurm allocation per scheduler
* `--submit` — Submit the generated allocations immediately
* `-o`, `--output-dir <OUTPUT_DIR>` — Output directory for job output files (used when submitting)

  Default value: `output`
* `-p`, `--poll-interval <POLL_INTERVAL>` — Poll interval in seconds (used when submitting)

  Default value: `60`



## `torc scheduled-compute-nodes`

Scheduled compute node management commands

**Usage:** `torc scheduled-compute-nodes <COMMAND>`

###### **Subcommands:**

* `get` — Get a scheduled compute node by ID
* `list` — List scheduled compute nodes for a workflow
* `list-jobs` — List jobs that ran under a scheduled compute node



## `torc scheduled-compute-nodes get`

Get a scheduled compute node by ID

**Usage:** `torc scheduled-compute-nodes get <ID>`

###### **Arguments:**

* `<ID>` — ID of the scheduled compute node



## `torc scheduled-compute-nodes list`

List scheduled compute nodes for a workflow

**Usage:** `torc scheduled-compute-nodes list [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — List scheduled compute nodes for this workflow (optional - will prompt if not provided)

###### **Options:**

* `-l`, `--limit <LIMIT>` — Maximum number of scheduled compute nodes to return

  Default value: `10000`
* `-o`, `--offset <OFFSET>` — Offset for pagination (0-based)

  Default value: `0`
* `-s`, `--sort-by <SORT_BY>` — Field to sort by
* `-r`, `--reverse-sort` — Reverse sort order

  Default value: `false`
* `--scheduler-id <SCHEDULER_ID>` — Filter by scheduler ID
* `--scheduler-config-id <SCHEDULER_CONFIG_ID>` — Filter by scheduler config ID
* `--status <STATUS>` — Filter by status



## `torc scheduled-compute-nodes list-jobs`

List jobs that ran under a scheduled compute node

**Usage:** `torc scheduled-compute-nodes list-jobs <ID>`

###### **Arguments:**

* `<ID>` — ID of the scheduled compute node



## `torc hpc`

HPC system profiles and partition information

**Usage:** `torc hpc <COMMAND>`

###### **Subcommands:**

* `list` — List known HPC system profiles
* `detect` — Detect the current HPC system
* `show` — Show details of an HPC profile
* `partitions` — Show partitions for an HPC profile
* `match` — Find partitions matching resource requirements



## `torc hpc list`

List known HPC system profiles

**Usage:** `torc hpc list`



## `torc hpc detect`

Detect the current HPC system

**Usage:** `torc hpc detect`



## `torc hpc show`

Show details of an HPC profile

**Usage:** `torc hpc show <NAME>`

###### **Arguments:**

* `<NAME>` — Profile name (e.g., "kestrel")



## `torc hpc partitions`

Show partitions for an HPC profile

**Usage:** `torc hpc partitions [OPTIONS] [NAME]`

###### **Arguments:**

* `<NAME>` — Profile name (e.g., "kestrel"). If not specified, tries to detect current system

###### **Options:**

* `--gpu` — Filter to GPU partitions only
* `--cpu` — Filter to CPU-only partitions
* `--shared` — Filter to shared partitions



## `torc hpc match`

Find partitions matching resource requirements

**Usage:** `torc hpc match [OPTIONS]`

###### **Options:**

* `--cpus <CPUS>` — Number of CPUs required

  Default value: `1`
* `--memory <MEMORY>` — Memory required (e.g., "100g", "512m", or MB as number)

  Default value: `1g`
* `--walltime <WALLTIME>` — Wall time required (e.g., "4:00:00", "2-00:00:00")

  Default value: `1:00:00`
* `--gpus <GPUS>` — Number of GPUs required
* `--profile <PROFILE>` — Profile name (if not specified, tries to detect current system)



## `torc reports`

Generate reports and analytics

**Usage:** `torc reports <COMMAND>`

###### **Subcommands:**

* `check-resource-utilization` — Check resource utilization and report jobs that exceeded their specified requirements
* `results` — Generate a comprehensive JSON report of job results including all log file paths
* `summary` — Generate a summary of workflow results (requires workflow to be complete)



## `torc reports check-resource-utilization`

Check resource utilization and report jobs that exceeded their specified requirements

**Usage:** `torc reports check-resource-utilization [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID to analyze (optional - will prompt if not provided)

###### **Options:**

* `-r`, `--run-id <RUN_ID>` — Run ID to analyze (optional - analyzes latest run if not provided)
* `-a`, `--all` — Show all jobs (default: only show jobs that exceeded requirements)
* `--include-failed` — Include failed and terminated jobs in the analysis (for recovery diagnostics)



## `torc reports results`

Generate a comprehensive JSON report of job results including all log file paths

**Usage:** `torc reports results [OPTIONS] [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID to analyze (optional - will prompt if not provided)

###### **Options:**

* `-o`, `--output-dir <OUTPUT_DIR>` — Output directory (where job logs are stored, passed in `torc run` and `torc submit`)

  Default value: `output`
* `--all-runs` — Include all runs for each job (default: only latest run)



## `torc reports summary`

Generate a summary of workflow results (requires workflow to be complete)

**Usage:** `torc reports summary [WORKFLOW_ID]`

###### **Arguments:**

* `<WORKFLOW_ID>` — Workflow ID to summarize (optional - will prompt if not provided)



## `torc config`

Manage configuration files and settings

**Usage:** `torc config <COMMAND>`

###### **Subcommands:**

* `show` — Show the effective configuration (merged from all sources)
* `paths` — Show configuration file paths
* `init` — Initialize a configuration file with defaults
* `validate` — Validate the current configuration



## `torc config show`

Show the effective configuration (merged from all sources)

**Usage:** `torc config show [OPTIONS]`

###### **Options:**

* `-f`, `--format <FORMAT>` — Output format (toml or json)

  Default value: `toml`



## `torc config paths`

Show configuration file paths

**Usage:** `torc config paths`



## `torc config init`

Initialize a configuration file with defaults

**Usage:** `torc config init [OPTIONS]`

###### **Options:**

* `--system` — Create system-wide config (/etc/torc/config.toml)
* `--user` — Create user config (~/.config/torc/config.toml)
* `--local` — Create project-local config (./torc.toml)
* `-f`, `--force` — Force overwrite if file exists



## `torc config validate`

Validate the current configuration

**Usage:** `torc config validate`



## `torc tui`

Interactive terminal UI for managing workflows

**Usage:** `torc tui [OPTIONS]`

###### **Options:**

* `--standalone` — Start in standalone mode: automatically start a torc-server
* `--port <PORT>` — Port for the server in standalone mode (default: 8080)

  Default value: `8080`
* `--database <DATABASE>` — Database path for standalone mode



## `torc plot-resources`

Generate interactive HTML plots from resource monitoring data

**Usage:** `torc plot-resources [OPTIONS] <DB_PATHS>...`

###### **Arguments:**

* `<DB_PATHS>` — Path to the resource metrics database file(s)

###### **Options:**

* `-o`, `--output-dir <OUTPUT_DIR>` — Output directory for generated plots (default: current directory)

  Default value: `.`
* `-j`, `--job-ids <JOB_IDS>` — Only plot specific job IDs (comma-separated)
* `-p`, `--prefix <PREFIX>` — Prefix for output filenames

  Default value: `resource_plot`
* `-f`, `--format <FORMAT>` — Output format: html or json

  Default value: `html`



## `torc completions`

Generate shell completions

**Usage:** `torc completions <SHELL>`

###### **Arguments:**

* `<SHELL>` — The shell to generate completions for

  Possible values: `bash`, `elvish`, `fish`, `powershell`, `zsh`




<hr/>

<small><i>
    This document was generated automatically by
    <a href="https://crates.io/crates/clap-markdown"><code>clap-markdown</code></a>.
</i></small>
