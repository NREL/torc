-- SQLite doesn't support DROP COLUMN directly
-- We need to recreate the table without the column

DROP INDEX IF EXISTS idx_job_internal_active_compute_node_id;

-- Create new table without the active_compute_node_id column
CREATE TABLE job_internal_new (
  job_id INTEGER PRIMARY KEY NOT NULL,
  input_hash TEXT NOT NULL,
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE
);

-- Copy data from old table
INSERT INTO job_internal_new (job_id, input_hash)
SELECT job_id, input_hash FROM job_internal;

-- Drop old table and rename new one
DROP TABLE job_internal;
ALTER TABLE job_internal_new RENAME TO job_internal;
