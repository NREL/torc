#!/bin/bash
# OOM Test Script
# This script allocates memory progressively until it triggers an OOM condition.
# Used for testing Slurm debugging features (parse-logs, sacct).
#
# Usage: ./oom_test.sh [delay_seconds] [chunk_size_gb]
#   delay_seconds: Time to wait before starting allocation (default: 60)
#   chunk_size_gb: Size of each allocation chunk in GB (default: 10)

set -e

DELAY_SECONDS=${1:-60}
CHUNK_SIZE_GB=${2:-10}

echo "OOM Test Script Starting"
echo "========================"
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo "PID: $$"
echo "Delay before allocation: ${DELAY_SECONDS}s"
echo "Chunk size: ${CHUNK_SIZE_GB}GB"
echo ""

# Show initial memory state
echo "Initial memory state:"
free -h 2>/dev/null || echo "(free command not available)"
echo ""

# Wait before starting memory allocation
echo "Waiting ${DELAY_SECONDS} seconds before starting memory allocation..."
sleep "${DELAY_SECONDS}"

echo ""
echo "Starting memory allocation..."
echo "This will continue until OOM killer terminates the process."
echo ""

# Allocate memory in chunks using Python
# This approach is more reliable than shell-based methods
python3 << EOF
import sys
import time

chunk_size_gb = ${CHUNK_SIZE_GB}
chunk_size_bytes = chunk_size_gb * 1024 * 1024 * 1024

allocations = []
total_allocated = 0

print(f"Allocating memory in {chunk_size_gb}GB chunks...")
sys.stdout.flush()

try:
    while True:
        # Allocate a chunk of memory and touch it to ensure it's actually allocated
        chunk = bytearray(chunk_size_bytes)
        # Touch every page to force physical allocation
        for i in range(0, len(chunk), 4096):
            chunk[i] = 1
        allocations.append(chunk)
        total_allocated += chunk_size_gb
        print(f"Allocated {total_allocated}GB total ({len(allocations)} chunks)")
        sys.stdout.flush()
        time.sleep(1)  # Small delay between allocations
except MemoryError:
    print(f"MemoryError after allocating {total_allocated}GB")
    sys.stdout.flush()
    # Keep the memory allocated and wait to be killed
    time.sleep(300)
except Exception as e:
    print(f"Error: {e}")
    sys.stdout.flush()
    sys.exit(1)
EOF

echo "Script completed (this should not be reached if OOM occurred)"
