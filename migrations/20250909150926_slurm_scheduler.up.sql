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
