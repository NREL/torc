CREATE TABLE ready_queue (
    workflow_id INTEGER NOT NULL
    ,job_id INTEGER NOT NULL
    ,resource_requirements_id INTEGER NOT NULL
    ,PRIMARY KEY (workflow_id, job_id)
    ,FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
    ,FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE
    ,FOREIGN KEY (resource_requirements_id) REFERENCES resource_requirements(id) ON DELETE CASCADE
);
