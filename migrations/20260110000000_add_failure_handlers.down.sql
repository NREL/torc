-- ============================================================================
-- REMOVE FAILURE HANDLERS
-- ============================================================================
-- This migration removes failure handler support by reversing the changes.
--
-- Note: SQLite doesn't support DROP COLUMN directly. We recreate the result
-- table to restore the original schema, but the job table columns
-- (failure_handler_id, attempt_id) will remain as orphaned columns.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Recreate result table with original schema
-- ----------------------------------------------------------------------------
-- Step 1: Create table with original schema
CREATE TABLE result_old (
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

-- Step 2: Copy data (only keeping first attempt for each job/run)
INSERT INTO result_old (id, workflow_id, job_id, run_id, compute_node_id,
                        return_code, exec_time_minutes, completion_time, status,
                        peak_memory_bytes, avg_memory_bytes, peak_cpu_percent, avg_cpu_percent)
SELECT id, workflow_id, job_id, run_id, compute_node_id,
       return_code, exec_time_minutes, completion_time, status,
       peak_memory_bytes, avg_memory_bytes, peak_cpu_percent, avg_cpu_percent
FROM result
WHERE attempt_id = 1 OR id IN (
  SELECT MIN(id) FROM result GROUP BY job_id, run_id
);

-- Step 3: Drop new table and indexes
DROP INDEX IF EXISTS idx_result_job_id;
DROP INDEX IF EXISTS idx_result_workflow_id;
DROP TABLE result;

-- Step 4: Rename old table
ALTER TABLE result_old RENAME TO result;

-- Step 5: Recreate original indexes
CREATE INDEX idx_result_job_id ON result(job_id);
CREATE INDEX idx_result_workflow_id ON result(workflow_id);

-- ----------------------------------------------------------------------------
-- Drop the failure_handler table and its index
-- ----------------------------------------------------------------------------
DROP INDEX IF EXISTS idx_failure_handler_workflow_id;
DROP TABLE IF EXISTS failure_handler;

-- Note: The following columns cannot be removed in SQLite without table recreation:
-- - job.failure_handler_id
-- - job.attempt_id
-- These columns will remain with NULL/default values after rollback.
