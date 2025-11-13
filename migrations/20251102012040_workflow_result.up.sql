CREATE TABLE workflow_result (
  workflow_id INTEGER NOT NULL,
  job_id INTEGER NOT NULL,
  result_id INTEGER NOT NULL,
  PRIMARY KEY (workflow_id, job_id),
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE,
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (result_id) REFERENCES result(id) ON DELETE CASCADE
);
