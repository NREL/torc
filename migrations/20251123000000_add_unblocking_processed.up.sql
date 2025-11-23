-- Add unblocking_processed flag to job table
-- This flag tracks whether the background task has processed job completion
-- to unblock downstream dependent jobs

ALTER TABLE job ADD COLUMN unblocking_processed INTEGER NOT NULL DEFAULT 0;

-- Create composite index for efficient queries by background unblocking task
-- Index only covers completed jobs (done=6, canceled=7, terminated=8) that need processing
CREATE INDEX idx_job_unblocking_pending
ON job(workflow_id, status, unblocking_processed)
WHERE status IN (6, 7, 8) AND unblocking_processed = 0;

-- Also create an index for finding workflows with pending unblocks
CREATE INDEX idx_job_workflow_unblocking
ON job(workflow_id)
WHERE status IN (6, 7, 8) AND unblocking_processed = 0;
