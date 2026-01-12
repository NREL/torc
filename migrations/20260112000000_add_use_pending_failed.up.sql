-- Add use_pending_failed column to workflow table
-- When enabled, failed jobs use PendingFailed status to enable AI-assisted recovery
ALTER TABLE workflow ADD COLUMN use_pending_failed INTEGER NOT NULL DEFAULT 0;
