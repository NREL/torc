CREATE TABLE compute_node(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
    ,workflow_id INTEGER NOT NULL
    ,hostname TEXT NOT NULL
    ,pid INTEGER NOT NULL
    ,start_time TEXT NOT NULL
    ,duration_seconds REAL NULL
    ,is_active INTEGER NULL
    ,num_cpus INTEGER NOT NULL
    ,memory_gb REAL NOT NULL
    ,num_gpus INTEGER NOT NULL
    ,num_nodes INTEGER NOT NULL
    ,time_limit TEXT NULL
    ,scheduler_config_id INTEGER NULL
    ,compute_node_type TEXT NOT NULL
    ,scheduler TEXT NULL
    ,FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);
