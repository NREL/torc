-- ============================================================================
-- ADD FAILURE HANDLERS
-- ============================================================================
-- This migration adds support for configurable job failure handlers that can
-- automatically retry jobs based on specific exit codes, with optional
-- recovery scripts.
--
-- Schema Version: 2026-01-10
-- ============================================================================

-- ----------------------------------------------------------------------------
-- failure_handler: Configurable failure handling rules for jobs
-- ----------------------------------------------------------------------------
-- Each failure handler contains rules that specify:
-- - exit_codes: List of exit codes that trigger this rule
-- - recovery_script: Optional script to run before retrying
-- - max_retries: Maximum number of retry attempts
--
-- Rules are stored as JSON for flexibility:
-- [{"exit_codes": [128, 129], "recovery_script": "./fix.sh", "max_retries": 3}]
-- ----------------------------------------------------------------------------
CREATE TABLE failure_handler (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  rules TEXT NOT NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

CREATE INDEX idx_failure_handler_workflow_id ON failure_handler(workflow_id);

-- ----------------------------------------------------------------------------
-- Add failure_handler_id to job table
-- ----------------------------------------------------------------------------
-- Jobs can optionally reference a failure handler for automatic retry behavior
ALTER TABLE job ADD COLUMN failure_handler_id INTEGER REFERENCES failure_handler(id) ON DELETE SET NULL;

-- ----------------------------------------------------------------------------
-- Add attempt_id to job table
-- ----------------------------------------------------------------------------
-- Tracks which attempt this job is on (starts at 1, increments on each retry)
ALTER TABLE job ADD COLUMN attempt_id INTEGER NOT NULL DEFAULT 1;

-- ----------------------------------------------------------------------------
-- Recreate result table with attempt_id
-- ----------------------------------------------------------------------------
-- SQLite doesn't support modifying UNIQUE constraints, so we recreate the table
-- The new constraint is UNIQUE(job_id, run_id, attempt_id) to allow multiple
-- results for the same job across retry attempts.

-- Step 1: Create new table with updated schema
CREATE TABLE result_new (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  job_id INTEGER NOT NULL,
  run_id INTEGER NOT NULL,
  attempt_id INTEGER NOT NULL DEFAULT 1,
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
  UNIQUE(job_id, run_id, attempt_id)
);

-- Step 2: Copy existing data (with default attempt_id = 1)
INSERT INTO result_new (id, workflow_id, job_id, run_id, attempt_id, compute_node_id,
                        return_code, exec_time_minutes, completion_time, status,
                        peak_memory_bytes, avg_memory_bytes, peak_cpu_percent, avg_cpu_percent)
SELECT id, workflow_id, job_id, run_id, 1, compute_node_id,
       return_code, exec_time_minutes, completion_time, status,
       peak_memory_bytes, avg_memory_bytes, peak_cpu_percent, avg_cpu_percent
FROM result;

-- Step 3: Drop old table
DROP TABLE result;

-- Step 4: Rename new table
ALTER TABLE result_new RENAME TO result;

-- Step 5: Recreate indexes that were on the original table
CREATE INDEX idx_result_job_id ON result(job_id);
CREATE INDEX idx_result_workflow_id ON result(workflow_id);
