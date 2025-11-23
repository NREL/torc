-- Drop indexes
DROP INDEX IF EXISTS idx_job_unblocking_pending;
DROP INDEX IF EXISTS idx_job_workflow_unblocking;

-- Drop column
ALTER TABLE job DROP COLUMN unblocking_processed;
