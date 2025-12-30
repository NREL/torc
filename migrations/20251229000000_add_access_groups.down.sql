-- Reverse the access groups migration

DROP INDEX IF EXISTS idx_workflow_access_group_group;
DROP INDEX IF EXISTS idx_workflow_access_group_workflow;
DROP INDEX IF EXISTS idx_user_group_membership_group;
DROP INDEX IF EXISTS idx_user_group_membership_user;

DROP TABLE IF EXISTS workflow_access_group;
DROP TABLE IF EXISTS user_group_membership;
DROP TABLE IF EXISTS access_group;
