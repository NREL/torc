-- Add is_system flag to access_group table
-- System groups (like "admin") are managed by the server and cannot be deleted via API

ALTER TABLE access_group ADD COLUMN is_system INTEGER NOT NULL DEFAULT 0;
