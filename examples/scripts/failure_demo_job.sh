#!/bin/bash
#
# Demo job script that simulates various failure modes for testing failure handlers.
#
# This script randomly succeeds or fails with different exit codes to demonstrate
# how failure handlers can automatically retry jobs based on specific error types.
#
# Exit codes:
#   0:  Success
#   1:  Unrecoverable error (should not be retried)
#   10: Convergence failure (recoverable with parameter adjustment)
#   11: Timeout/resource issue (recoverable with retry)
#   12: Transient error (recoverable with simple retry)
#
# Usage:
#   ./failure_demo_job.sh [--fail-rate RATE] [--work-time SECONDS]
#
# Environment variables (set by torc):
#   TORC_ATTEMPT_ID: Current attempt number (1, 2, 3, ...)
#   TORC_JOB_NAME: Name of the job

# Default values
FAIL_RATE=70  # Percentage (0-100)
WORK_TIME=0.5

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fail-rate)
            # Convert decimal to percentage (0.7 -> 70)
            FAIL_RATE=$(echo "$2 * 100" | bc | cut -d. -f1)
            shift 2
            ;;
        --work-time)
            WORK_TIME="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Get environment variables from torc
ATTEMPT_ID="${TORC_ATTEMPT_ID:-1}"
JOB_NAME="${TORC_JOB_NAME:-demo_job}"

echo "=== $JOB_NAME (attempt $ATTEMPT_ID) ==="
echo "PID: $$"
echo "Fail rate: ${FAIL_RATE}%"

# Simulate some work
echo "Working for $WORK_TIME seconds..."
sleep "$WORK_TIME"

# Decrease fail rate with each attempt (simulating that retries help)
# Each attempt reduces fail rate by 60% (multiply by 0.4)
# attempt 1: 70%, attempt 2: 28%, attempt 3: 11%, attempt 4: 4%
EFFECTIVE_FAIL_RATE=$FAIL_RATE
for ((i=1; i<ATTEMPT_ID; i++)); do
    EFFECTIVE_FAIL_RATE=$((EFFECTIVE_FAIL_RATE * 40 / 100))
done
echo "Effective fail rate for attempt $ATTEMPT_ID: ${EFFECTIVE_FAIL_RATE}%"

# Generate random number 0-99
RAND=$((RANDOM % 100))

if [[ $RAND -lt $EFFECTIVE_FAIL_RATE ]]; then
    # Choose a failure type (weighted selection)
    # convergence: 35%, timeout: 30%, transient: 30%, unrecoverable: 5%
    FAILURE_RAND=$((RANDOM % 100))

    if [[ $FAILURE_RAND -lt 35 ]]; then
        echo "ERROR: Convergence failure"
        echo "The solver did not converge within the specified tolerance."
        echo "Hint: A recovery script could adjust solver parameters."
        exit 10
    elif [[ $FAILURE_RAND -lt 65 ]]; then
        echo "ERROR: Resource limit exceeded"
        echo "The job exceeded expected resource usage."
        echo "Hint: A recovery script could adjust resource allocation."
        exit 11
    elif [[ $FAILURE_RAND -lt 95 ]]; then
        echo "ERROR: Transient error"
        echo "A temporary issue occurred (e.g., network blip, busy resource)."
        echo "Hint: Simple retry should resolve this."
        exit 12
    else
        echo "ERROR: Unrecoverable error"
        echo "This error cannot be recovered by retrying."
        exit 1
    fi
else
    echo "SUCCESS: Job completed successfully!"
    exit 0
fi
