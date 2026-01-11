#!/bin/bash
# Recovery script for simulation failure handler example
#
# This script is called when a simulation job fails with a recoverable error code.
# It reads the config file, adjusts parameters based on the error type, and writes
# the updated config for the retry attempt.
#
# Environment variables set by Torc:
#   TORC_WORKFLOW_ID  - Workflow ID
#   TORC_JOB_ID       - Job ID
#   TORC_JOB_NAME     - Job name
#   TORC_ATTEMPT_ID   - Current attempt number (1, 2, 3...)
#   TORC_RETURN_CODE  - Exit code that triggered recovery
#   TORC_OUTPUT_DIR   - Output directory for logs/artifacts
#   TORC_API_URL      - Torc server API endpoint
#
# Arguments:
#   --error-type TYPE  - Type of error (solver, timestep, mesh, memory)
#   --config PATH      - Path to the config file to modify

set -e

# Parse arguments
ERROR_TYPE=""
CONFIG_PATH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --error-type)
            ERROR_TYPE="$2"
            shift 2
            ;;
        --config)
            CONFIG_PATH="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

if [[ -z "$ERROR_TYPE" || -z "$CONFIG_PATH" ]]; then
    echo "Usage: $0 --error-type TYPE --config PATH" >&2
    exit 1
fi

echo "=== Recovery Script ==="
echo "Job: ${TORC_JOB_NAME} (ID: ${TORC_JOB_ID})"
echo "Attempt: ${TORC_ATTEMPT_ID}"
echo "Error code: ${TORC_RETURN_CODE}"
echo "Error type: ${ERROR_TYPE}"
echo "Config: ${CONFIG_PATH}"

# Check if config file exists
if [[ ! -f "$CONFIG_PATH" ]]; then
    echo "Warning: Config file not found: $CONFIG_PATH"
    echo "This is a demo script - in production, this would modify the config."
    exit 0
fi

# Adjust config based on error type
# Note: This is a simplified example. In production, you would use a proper
# YAML/JSON parser to modify the config file.
case $ERROR_TYPE in
    solver)
        echo "Adjusting solver parameters..."
        echo "  - Reducing relaxation_factor by 20%"
        echo "  - Increasing max_iterations by 50%"
        # In production: modify relaxation_factor and max_iterations in config
        # Example with yq: yq -i '.solver.relaxation_factor *= 0.8' "$CONFIG_PATH"
        ;;
    timestep)
        echo "Adjusting timestep parameters..."
        echo "  - Reducing timestep by 50%"
        echo "  - Enabling adaptive timestep"
        # In production: modify dt and enable adaptive_dt in config
        ;;
    mesh)
        echo "Adjusting mesh parameters..."
        echo "  - Increasing mesh tolerance by 20%"
        echo "  - Enabling mesh refinement"
        # In production: modify mesh_tolerance in config
        ;;
    memory)
        echo "Adjusting memory parameters..."
        echo "  - Reducing batch_size by 50%"
        echo "  - Enabling memory-efficient mode"
        # In production: modify batch_size and enable memory_efficient in config
        ;;
    *)
        echo "Unknown error type: $ERROR_TYPE" >&2
        exit 1
        ;;
esac

echo "Config adjusted for attempt $((TORC_ATTEMPT_ID + 1))"
echo "Recovery script completed successfully"
exit 0
