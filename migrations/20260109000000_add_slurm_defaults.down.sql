-- Remove slurm_defaults column from workflow table
-- SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
-- Note: This migration assumes no other columns have been added after slurm_defaults

-- Create temporary table without slurm_defaults
CREATE TABLE workflow_backup (
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
  compute_node_min_time_for_new_jobs_seconds INTEGER NOT NULL DEFAULT 300,
  jobs_sort_method TEXT NOT NULL DEFAULT 'gpus_runtime_memory',
  status_id INTEGER NOT NULL,
  resource_monitor_config TEXT NULL,
  FOREIGN KEY (status_id) REFERENCES workflow_status(id)
);

-- Copy data
INSERT INTO workflow_backup (
  id, name, description, user, timestamp, is_archived,
  compute_node_expiration_buffer_seconds, compute_node_wait_for_new_jobs_seconds,
  compute_node_ignore_workflow_completion, compute_node_wait_for_healthy_database_minutes,
  compute_node_min_time_for_new_jobs_seconds, jobs_sort_method, status_id, resource_monitor_config
)
SELECT
  id, name, description, user, timestamp, is_archived,
  compute_node_expiration_buffer_seconds, compute_node_wait_for_new_jobs_seconds,
  compute_node_ignore_workflow_completion, compute_node_wait_for_healthy_database_minutes,
  compute_node_min_time_for_new_jobs_seconds, jobs_sort_method, status_id, resource_monitor_config
FROM workflow;

-- Drop original table
DROP TABLE workflow;

-- Rename backup to original
ALTER TABLE workflow_backup RENAME TO workflow;

-- Recreate indexes
CREATE INDEX IF NOT EXISTS idx_workflow_name ON workflow(name);
CREATE INDEX IF NOT EXISTS idx_workflow_user ON workflow(user);
CREATE INDEX IF NOT EXISTS idx_workflow_is_archived ON workflow(is_archived);
