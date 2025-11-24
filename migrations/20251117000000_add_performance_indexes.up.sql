-- Add indexes to dramatically improve job completion performance
-- These indexes are critical for workflows with large dependency graphs

-- Index on blocked_by_job_id for finding jobs that are blocked by a completed job
-- This is the primary lookup in unblock_jobs_waiting_for()
CREATE INDEX idx_job_blocked_by_blocked_by_job_id ON job_blocked_by(blocked_by_job_id);

-- Composite index on (workflow_id, blocked_by_job_id) for combined filtering
-- This covers both WHERE clauses in the unblock_jobs_waiting_for query
-- Also supports queries filtering on workflow_id alone via leftmost prefix
CREATE INDEX idx_job_blocked_by_workflow_blocked_by ON job_blocked_by(workflow_id, blocked_by_job_id);

-- Index on job status for checking if blocking jobs are complete
-- Used heavily in the EXISTS subquery
CREATE INDEX idx_job_status ON job(status);

-- Composite index on (workflow_id, status) for combined workflow+status queries
CREATE INDEX idx_job_workflow_status ON job(workflow_id, status);
