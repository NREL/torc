-- Add compute_node_min_time_for_new_jobs_seconds column to workflow table
-- This specifies the minimum remaining time (in seconds) a compute node must have
-- before it will request new jobs. Default is 300 seconds (5 minutes).
ALTER TABLE workflow ADD COLUMN compute_node_min_time_for_new_jobs_seconds INTEGER NOT NULL DEFAULT 300;
