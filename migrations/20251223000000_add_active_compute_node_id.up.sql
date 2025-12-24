-- Add active_compute_node_id to job_internal table
-- This tracks which compute node is currently executing a job
-- Set when start_job is called, cleared when complete_job is called or job is reset

ALTER TABLE job_internal ADD COLUMN active_compute_node_id INTEGER REFERENCES compute_node(id) ON DELETE SET NULL;

-- Create index for efficient querying of jobs by active compute node
CREATE INDEX idx_job_internal_active_compute_node_id ON job_internal(active_compute_node_id) WHERE active_compute_node_id IS NOT NULL;
