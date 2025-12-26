-- Add is_recovery column to workflow_action table
-- This flag marks actions created during recovery (e.g., by `torc slurm regenerate`)
-- Recovery actions are ephemeral and deleted when the workflow is reinitialized

ALTER TABLE workflow_action ADD COLUMN is_recovery INTEGER NOT NULL DEFAULT 0;
