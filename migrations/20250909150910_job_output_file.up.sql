CREATE TABLE job_output_file (
  job_id INTEGER NOT NULL,
  file_id INTEGER NOT NULL,
  workflow_id INTEGER NOT NULL,
  PRIMARY KEY (job_id, file_id),
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (file_id) REFERENCES file(id) ON DELETE CASCADE,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);
