CREATE TABLE job_internal (
    job_id INTEGER PRIMARY KEY NOT NULL,
    input_hash TEXT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE
);
