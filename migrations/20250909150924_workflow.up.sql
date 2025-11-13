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
