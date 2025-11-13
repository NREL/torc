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
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE,
  FOREIGN KEY (resource_requirements_id) REFERENCES resource_requirements(id) ON DELETE CASCADE
);
