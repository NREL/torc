CREATE TABLE resource_requirements (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
  ,workflow_id INTEGER NOT NULL
  ,name TEXT NOT NULL
  ,num_cpus INTEGER NOT NULL DEFAULT 1
  ,num_gpus INTEGER NOT NULL DEFAULT 0
  ,num_nodes INTEGER NOT NULL DEFAULT 1
  ,memory TEXT NOT NULL DEFAULT '1m'
  ,runtime TEXT NOT NULL DEFAULT 'P0DT1M'
  -- These are used to speed-up queries and are not part of the data model.
  ,memory_bytes INTEGER NOT NULL
  ,runtime_s INTEGER NOT NULL
  ,FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);
