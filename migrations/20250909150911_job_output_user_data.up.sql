CREATE TABLE job_output_user_data (
  job_id INTEGER NOT NULL,
  user_data_id INTEGER NOT NULL,
  PRIMARY KEY (job_id, user_data_id),
  FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE,
  FOREIGN KEY (user_data_id) REFERENCES user_data(id) ON DELETE CASCADE
);
