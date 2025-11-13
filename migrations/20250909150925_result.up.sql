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
