-- Remove is_recovery column from workflow_action table
-- SQLite doesn't support DROP COLUMN directly, so we need to recreate the table

-- Create a new table without is_recovery
CREATE TABLE workflow_action_new (
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

-- Copy data (excluding recovery actions since they shouldn't exist after downgrade)
INSERT INTO workflow_action_new (id, workflow_id, trigger_type, action_type, action_config, job_ids, trigger_count, required_triggers, executed, executed_at, executed_by, persistent)
SELECT id, workflow_id, trigger_type, action_type, action_config, job_ids, trigger_count, required_triggers, executed, executed_at, executed_by, persistent
FROM workflow_action
WHERE is_recovery = 0;

-- Drop the old table
DROP TABLE workflow_action;

-- Rename the new table
ALTER TABLE workflow_action_new RENAME TO workflow_action;
