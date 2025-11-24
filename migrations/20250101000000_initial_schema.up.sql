-- ============================================================================
-- TORC CONSOLIDATED SCHEMA
-- ============================================================================
-- This migration represents the complete consolidated schema for the Torc
-- distributed workflow orchestration system. It includes all tables, indexes,
-- and foreign key constraints from the original incremental migrations.
--
-- Schema Version: 2025-01-01
-- ============================================================================

-- ============================================================================
-- CORE TABLES
-- ============================================================================
-- These tables represent the primary entities in the Torc system:
-- workflows, jobs, files, and user data.

-- ----------------------------------------------------------------------------
-- workflow_status: Status tracking for workflows
-- ----------------------------------------------------------------------------
CREATE TABLE workflow_status (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  run_id INTGEGER NOT NULL DEFAULT 1,
  has_detected_need_to_run_completion_script INTEGER NOT NULL DEFAULT 0,
  is_canceled INTEGER NOT NULL DEFAULT 0,
  is_archived INTEGER NOT NULL DEFAULT 0
);

-- ----------------------------------------------------------------------------
-- workflow: Top-level container for computational workflows
-- ----------------------------------------------------------------------------
CREATE TABLE workflow (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT NULL,
  user TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  is_archived INTEGER NOT NULL DEFAULT 0,
  compute_node_expiration_buffer_seconds INTEGER NOT NULL DEFAULT 60,
  compute_node_wait_for_new_jobs_seconds INTEGER NOT NULL DEFAULT 0,
  compute_node_ignore_workflow_completion INTEGER NOT NULL DEFAULT 0,
  compute_node_wait_for_healthy_database_minutes INTEGER NOT NULL DEFAULT 20,
  jobs_sort_method TEXT NOT NULL DEFAULT 'gpus_runtime_memory',
  status_id INTEGER NOT NULL,
  resource_monitor_config TEXT NULL,
  FOREIGN KEY (status_id) REFERENCES workflow_status(id)
);

-- ----------------------------------------------------------------------------
-- resource_requirements: Resource specifications for jobs
-- ----------------------------------------------------------------------------
CREATE TABLE resource_requirements (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  num_cpus INTEGER NOT NULL DEFAULT 1,
  num_gpus INTEGER NOT NULL DEFAULT 0,
  num_nodes INTEGER NOT NULL DEFAULT 1,
  memory TEXT NOT NULL DEFAULT '1m',
  runtime TEXT NOT NULL DEFAULT 'P0DT1M',
  -- Computed fields for query optimization
  memory_bytes INTEGER NOT NULL,
  runtime_s INTEGER NOT NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- job: Individual computational tasks within workflows
-- ----------------------------------------------------------------------------
CREATE TABLE job (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  command TEXT NOT NULL,
  cancel_on_blocking_job_failure NOT NULL DEFAULT true,
  supports_termination NOT NULL DEFAULT false,
  resource_requirements_id INTEGER NULL,
  invocation_script TEXT NULL,
  status INTEGER NOT NULL,
  scheduler_id INTEGER NULL,
  scheduler_type TEXT NULL,
  schedule_compute_nodes JSON NULL,
  -- Unblocking flag: tracks if background task has processed job completion
  unblocking_processed INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE,
  FOREIGN KEY (resource_requirements_id) REFERENCES resource_requirements(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- job_internal: Internal job metadata (input hashing)
-- ----------------------------------------------------------------------------
CREATE TABLE job_internal (
  job_id INTEGER PRIMARY KEY NOT NULL,
  input_hash TEXT NOT NULL,
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- file: File artifacts managed by the workflow
-- ----------------------------------------------------------------------------
CREATE TABLE file (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  path TEXT NOT NULL,
  st_mtime REAL NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- user_data: User-defined data artifacts
-- ----------------------------------------------------------------------------
CREATE TABLE user_data (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  is_ephemeral INTEGER NOT NULL,
  data JSON NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- ============================================================================
-- RELATIONSHIP TABLES
-- ============================================================================
-- These junction tables establish many-to-many relationships between
-- jobs, files, and user data, creating the dependency graph.

-- ----------------------------------------------------------------------------
-- job_blocked_by: Explicit job dependencies
-- ----------------------------------------------------------------------------
CREATE TABLE job_blocked_by (
  job_id INTEGER NOT NULL,
  blocked_by_job_id INTEGER NOT NULL,
  workflow_id INTEGER NOT NULL,
  PRIMARY KEY (job_id, blocked_by_job_id),
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (blocked_by_job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- job_input_file: Files consumed by jobs
-- ----------------------------------------------------------------------------
CREATE TABLE job_input_file (
  job_id INTEGER NOT NULL,
  file_id INTEGER NOT NULL,
  workflow_id INTEGER NOT NULL,
  PRIMARY KEY (job_id, file_id),
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (file_id) REFERENCES file(id) ON DELETE CASCADE,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- job_output_file: Files produced by jobs
-- ----------------------------------------------------------------------------
CREATE TABLE job_output_file (
  job_id INTEGER NOT NULL,
  file_id INTEGER NOT NULL,
  workflow_id INTEGER NOT NULL,
  PRIMARY KEY (job_id, file_id),
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (file_id) REFERENCES file(id) ON DELETE CASCADE,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- job_input_user_data: User data consumed by jobs
-- ----------------------------------------------------------------------------
CREATE TABLE job_input_user_data (
  job_id INTEGER NOT NULL,
  user_data_id INTEGER NOT NULL,
  PRIMARY KEY (job_id, user_data_id),
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (user_data_id) REFERENCES user_data(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- job_output_user_data: User data produced by jobs
-- ----------------------------------------------------------------------------
CREATE TABLE job_output_user_data (
  job_id INTEGER NOT NULL,
  user_data_id INTEGER NOT NULL,
  PRIMARY KEY (job_id, user_data_id),
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (user_data_id) REFERENCES user_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- SCHEDULER CONFIGURATION TABLES
-- ============================================================================
-- These tables define scheduler configurations for job execution.

-- ----------------------------------------------------------------------------
-- local_scheduler: Local execution configuration
-- ----------------------------------------------------------------------------
CREATE TABLE local_scheduler (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  memory TEXT NOT NULL,
  num_cpus INTEGER NOT NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- slurm_scheduler: SLURM cluster execution configuration
-- ----------------------------------------------------------------------------
CREATE TABLE slurm_scheduler (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  account TEXT NOT NULL,
  gres TEXT NULL,
  mem TEXT NULL,
  nodes INTEGER NULL,
  ntasks_per_node INTEGER NULL,
  partition TEXT NULL,
  qos TEXT NULL,
  tmp TEXT NULL,
  walltime TEXT NOT NULL,
  extra TEXT NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- ============================================================================
-- EXECUTION AND MONITORING TABLES
-- ============================================================================
-- These tables track workflow execution, compute resources, and results.

-- ----------------------------------------------------------------------------
-- compute_node: Available compute resources
-- ----------------------------------------------------------------------------
CREATE TABLE compute_node(
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  hostname TEXT NOT NULL,
  pid INTEGER NOT NULL,
  start_time TEXT NOT NULL,
  duration_seconds REAL NULL,
  is_active INTEGER NULL,
  num_cpus INTEGER NOT NULL,
  memory_gb REAL NOT NULL,
  num_gpus INTEGER NOT NULL,
  num_nodes INTEGER NOT NULL,
  time_limit TEXT NULL,
  scheduler_config_id INTEGER NULL,
  compute_node_type TEXT NOT NULL,
  scheduler TEXT NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- scheduled_compute_node: Scheduled compute resource allocations
-- ----------------------------------------------------------------------------
CREATE TABLE scheduled_compute_node(
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  scheduler_config_id INTEGER NOT NULL,
  scheduler_id INTEGER NOT NULL,
  scheduler_type TEXT NOT NULL,
  status TEXT NOT NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- result: Job execution results and metrics
-- ----------------------------------------------------------------------------
CREATE TABLE result (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  job_id INTEGER NOT NULL,
  run_id INTEGER NOT NULL,
  compute_node_id INTEGER NOT NULL,
  return_code INTEGER NOT NULL,
  exec_time_minutes REAL NOT NULL,
  completion_time TEXT NOT NULL,
  status INTEGER NOT NULL,
  peak_memory_bytes INTEGER NULL,
  avg_memory_bytes INTEGER NULL,
  peak_cpu_percent REAL NULL,
  avg_cpu_percent REAL NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE,
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (compute_node_id) REFERENCES compute_node(id) ON DELETE CASCADE,
  UNIQUE(job_id, run_id)
);

-- ----------------------------------------------------------------------------
-- workflow_result: Latest result for each job in a workflow
-- ----------------------------------------------------------------------------
CREATE TABLE workflow_result (
  workflow_id INTEGER NOT NULL,
  job_id INTEGER NOT NULL,
  result_id INTEGER NOT NULL,
  PRIMARY KEY (workflow_id, job_id),
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE,
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (result_id) REFERENCES result(id) ON DELETE CASCADE
);

-- ============================================================================
-- AUXILIARY TABLES
-- ============================================================================
-- These tables support workflow actions and event logging.

-- ----------------------------------------------------------------------------
-- workflow_action: Workflow lifecycle actions and triggers
-- ----------------------------------------------------------------------------
CREATE TABLE workflow_action (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  trigger_type TEXT NOT NULL,
  action_type TEXT NOT NULL,
  action_config TEXT NOT NULL,
  job_ids TEXT NULL,
  trigger_count INTEGER NOT NULL DEFAULT 0,
  required_triggers INTEGER NOT NULL DEFAULT 1,
  executed INTEGER NOT NULL DEFAULT 0,
  executed_at TEXT NULL,
  executed_by INTEGER NULL,
  persistent INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE,
  FOREIGN KEY (executed_by) REFERENCES compute_node(id) ON DELETE SET NULL
);

-- ----------------------------------------------------------------------------
-- event: Workflow event log
-- ----------------------------------------------------------------------------
CREATE TABLE event (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  timestamp TEXT NOT NULL,
  data TEXT NOT NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================
-- These indexes are critical for query performance, especially in workflows
-- with large dependency graphs. They dramatically improve job completion
-- and unblocking operations.

-- ----------------------------------------------------------------------------
-- Dependency Graph Indexes
-- ----------------------------------------------------------------------------
-- Index for finding jobs blocked by a specific job (primary unblocking lookup)
CREATE INDEX idx_job_blocked_by_blocked_by_job_id ON job_blocked_by(blocked_by_job_id);

-- Composite index for combined workflow + blocking job filtering
-- Also supports workflow_id-only queries via leftmost prefix
CREATE INDEX idx_job_blocked_by_workflow_blocked_by ON job_blocked_by(workflow_id, blocked_by_job_id);

-- ----------------------------------------------------------------------------
-- Job Status Indexes
-- ----------------------------------------------------------------------------
-- Index for checking job status (heavily used in dependency resolution)
CREATE INDEX idx_job_status ON job(status);

-- Composite index for combined workflow + status queries
CREATE INDEX idx_job_workflow_status ON job(workflow_id, status);

-- ----------------------------------------------------------------------------
-- Background Unblocking Task Indexes
-- ----------------------------------------------------------------------------
-- Partial index for finding completed jobs pending unblocking processing
-- Only indexes rows where status is done/canceled/terminated and not yet processed
CREATE INDEX idx_job_unblocking_pending
ON job(workflow_id, status, unblocking_processed)
WHERE status IN (6, 7, 8) AND unblocking_processed = 0;

-- Partial index for finding workflows with pending unblocks
CREATE INDEX idx_job_workflow_unblocking
ON job(workflow_id)
WHERE status IN (6, 7, 8) AND unblocking_processed = 0;
