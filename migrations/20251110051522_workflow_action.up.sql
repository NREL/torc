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
