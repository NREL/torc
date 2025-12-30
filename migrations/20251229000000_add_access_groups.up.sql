-- ============================================================================
-- ACCESS GROUPS SCHEMA
-- ============================================================================
-- This migration adds support for team-based access control:
-- - Groups represent teams that can share access to workflows
-- - Users can belong to multiple groups
-- - Workflows can be associated with groups for shared access

-- ----------------------------------------------------------------------------
-- access_group: Teams/groups for access control
-- ----------------------------------------------------------------------------
CREATE TABLE access_group (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  description TEXT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ----------------------------------------------------------------------------
-- user_group_membership: Links users to groups
-- ----------------------------------------------------------------------------
CREATE TABLE user_group_membership (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  user_name TEXT NOT NULL,
  group_id INTEGER NOT NULL,
  role TEXT NOT NULL DEFAULT 'member',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (group_id) REFERENCES access_group(id) ON DELETE CASCADE,
  UNIQUE(user_name, group_id)
);

-- ----------------------------------------------------------------------------
-- workflow_access_group: Links workflows to groups for shared access
-- ----------------------------------------------------------------------------
CREATE TABLE workflow_access_group (
  workflow_id INTEGER NOT NULL,
  group_id INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (workflow_id, group_id),
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE,
  FOREIGN KEY (group_id) REFERENCES access_group(id) ON DELETE CASCADE
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Index for looking up groups by user
CREATE INDEX idx_user_group_membership_user ON user_group_membership(user_name);

-- Index for looking up users by group
CREATE INDEX idx_user_group_membership_group ON user_group_membership(group_id);

-- Index for looking up groups by workflow
CREATE INDEX idx_workflow_access_group_workflow ON workflow_access_group(workflow_id);

-- Index for looking up workflows by group
CREATE INDEX idx_workflow_access_group_group ON workflow_access_group(group_id);
