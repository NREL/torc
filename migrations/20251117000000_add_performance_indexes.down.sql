-- Revert performance indexes

DROP INDEX IF EXISTS idx_job_workflow_status;
DROP INDEX IF EXISTS idx_job_status;
DROP INDEX IF EXISTS idx_job_blocked_by_workflow_blocked_by;
DROP INDEX IF EXISTS idx_job_blocked_by_workflow_id;
DROP INDEX IF EXISTS idx_job_blocked_by_blocked_by_job_id;
