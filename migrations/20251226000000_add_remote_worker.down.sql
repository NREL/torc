-- Remove remote_worker table
DROP INDEX IF EXISTS idx_remote_worker_workflow_id;
DROP TABLE IF EXISTS remote_worker;
