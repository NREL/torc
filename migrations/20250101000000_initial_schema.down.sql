-- ============================================================================
-- TORC SCHEMA ROLLBACK
-- ============================================================================
-- This migration drops all tables in reverse dependency order to cleanly
-- roll back the consolidated schema.
--
-- Schema Version: 2025-01-01
-- ============================================================================

-- ============================================================================
-- DROP INDEXES
-- ============================================================================
-- Drop all performance indexes first

DROP INDEX IF EXISTS idx_job_workflow_unblocking;
DROP INDEX IF EXISTS idx_job_unblocking_pending;
DROP INDEX IF EXISTS idx_job_workflow_status;
DROP INDEX IF EXISTS idx_job_status;
DROP INDEX IF EXISTS idx_job_depends_on_workflow_depends_on;
DROP INDEX IF EXISTS idx_job_depends_on_depends_on_job_id;

-- ============================================================================
-- DROP AUXILIARY TABLES
-- ============================================================================
-- Drop event log and workflow action tables

DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS workflow_action;

-- ============================================================================
-- DROP EXECUTION AND MONITORING TABLES
-- ============================================================================
-- Drop tables that track execution results and compute resources
-- Must drop workflow_result before result due to foreign key

DROP TABLE IF EXISTS workflow_result;
DROP TABLE IF EXISTS result;
DROP TABLE IF EXISTS scheduled_compute_node;
DROP TABLE IF EXISTS compute_node;

-- ============================================================================
-- DROP SCHEDULER CONFIGURATION TABLES
-- ============================================================================
-- Drop scheduler configuration tables

DROP TABLE IF EXISTS slurm_scheduler;
DROP TABLE IF EXISTS local_scheduler;

-- ============================================================================
-- DROP RELATIONSHIP TABLES
-- ============================================================================
-- Drop junction tables that establish job/file/user_data relationships

DROP TABLE IF EXISTS job_output_user_data;
DROP TABLE IF EXISTS job_input_user_data;
DROP TABLE IF EXISTS job_output_file;
DROP TABLE IF EXISTS job_input_file;
DROP TABLE IF EXISTS job_depends_on;

-- ============================================================================
-- DROP CORE TABLES
-- ============================================================================
-- Drop core entity tables in reverse dependency order

DROP TABLE IF EXISTS user_data;
DROP TABLE IF EXISTS file;
DROP TABLE IF EXISTS job_internal;
DROP TABLE IF EXISTS job;
DROP TABLE IF EXISTS resource_requirements;
DROP TABLE IF EXISTS workflow;
DROP TABLE IF EXISTS workflow_status;
