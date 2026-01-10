-- Add slurm_defaults column to workflow table
-- This stores JSON-serialized default Slurm parameters that apply to all schedulers
ALTER TABLE workflow ADD COLUMN slurm_defaults TEXT NULL;
