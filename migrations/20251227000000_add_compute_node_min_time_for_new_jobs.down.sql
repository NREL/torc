-- Remove compute_node_min_time_for_new_jobs_seconds column from workflow table
ALTER TABLE workflow DROP COLUMN compute_node_min_time_for_new_jobs_seconds;
