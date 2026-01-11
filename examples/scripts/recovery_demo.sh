#!/bin/bash
# Recovery script for failure handler demo
#
# This script is called when a job fails with a recoverable error code.
# It logs the recovery attempt and can perform actions before retry.
#
# Environment variables set by Torc:
#   TORC_WORKFLOW_ID  - Workflow ID
#   TORC_JOB_ID       - Job ID
#   TORC_JOB_NAME     - Job name
#   TORC_ATTEMPT_ID   - Current attempt number (1, 2, 3...)
#   TORC_RETURN_CODE  - Exit code that triggered recovery
#   TORC_OUTPUT_DIR   - Output directory for logs/artifacts
#   TORC_API_URL      - Torc server API endpoint

echo "=== Recovery Script ==="
echo "Job: ${TORC_JOB_NAME:-unknown} (ID: ${TORC_JOB_ID:-unknown})"
echo "Workflow: ${TORC_WORKFLOW_ID:-unknown}"
echo "Attempt: ${TORC_ATTEMPT_ID:-unknown}"
echo "Exit code: ${TORC_RETURN_CODE:-unknown}"
echo "Output dir: ${TORC_OUTPUT_DIR:-unknown}"
echo ""

# Log recovery attempt
LOG_FILE="${TORC_OUTPUT_DIR:-/tmp}/recovery.log"
echo "$(date -Iseconds) - Recovery for job ${TORC_JOB_NAME} (exit code ${TORC_RETURN_CODE}, attempt ${TORC_ATTEMPT_ID})" >> "$LOG_FILE"

# Take action based on exit code
case ${TORC_RETURN_CODE:-0} in
    10)
        echo "Handling convergence failure (exit code 10)"
        echo "  - Would adjust solver parameters for retry"
        ;;
    11)
        echo "Handling resource/timeout issue (exit code 11)"
        echo "  - Would adjust resource allocation for retry"
        ;;
    12)
        echo "Handling transient error (exit code 12)"
        echo "  - No changes needed, simple retry"
        ;;
    *)
        echo "Unknown error code: ${TORC_RETURN_CODE}"
        echo "  - Proceeding with simple retry"
        ;;
esac

echo ""
echo "Recovery complete. Job will retry."
exit 0
