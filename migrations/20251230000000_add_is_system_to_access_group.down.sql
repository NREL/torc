-- SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
-- This is a destructive migration - it will lose the is_system flag

-- Create a new table without is_system
CREATE TABLE access_group_new (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  description TEXT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Copy data
INSERT INTO access_group_new (id, name, description, created_at)
SELECT id, name, description, created_at FROM access_group;

-- Drop old table
DROP TABLE access_group;

-- Rename new table
ALTER TABLE access_group_new RENAME TO access_group;
