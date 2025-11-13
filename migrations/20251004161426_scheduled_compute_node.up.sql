CREATE TABLE scheduled_compute_node(
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  scheduler_config_id INTEGER NOT NULL,
  scheduler_id INTEGER NOT NULL,
  scheduler_type TEXT NOT NULL,
  status TEXT NOT NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
)
