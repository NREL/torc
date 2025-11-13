CREATE TABLE job_blocked_by (
  job_id INTEGER NOT NULL,
  blocked_by_job_id INTEGER NOT NULL,
  workflow_id INTEGER NOT NULL,
  PRIMARY KEY (job_id, blocked_by_job_id),
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (blocked_by_job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);
