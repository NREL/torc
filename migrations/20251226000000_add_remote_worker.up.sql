-- Add remote_worker table for storing remote worker configurations per workflow
CREATE TABLE remote_worker (
    worker TEXT NOT NULL,
    workflow_id INTEGER NOT NULL,
    PRIMARY KEY (worker, workflow_id),
    FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- Index for efficient lookup by workflow_id
CREATE INDEX idx_remote_worker_workflow_id ON remote_worker(workflow_id);
