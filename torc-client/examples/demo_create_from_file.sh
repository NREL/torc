#!/bin/bash

# Demo script for the create-from-file command
# This script demonstrates how to use the new jobs create-from-file command

set -e

echo "=== Torc Client: Create Jobs from File Demo ==="
echo ""

# Check if torc-client is available
if ! command -v torc-client &> /dev/null; then
    echo "Error: torc-client not found in PATH"
    echo "Please build the client first: cargo build --release"
    echo "Then add target/release to your PATH or run ./target/release/torc-client"
    exit 1
fi

# Create a demo directory
DEMO_DIR="demo_batch_jobs"
mkdir -p "$DEMO_DIR"
cd "$DEMO_DIR"

echo "1. Creating a sample workflow specification..."

# Create a sample workflow file
cat > sample_workflow.json << 'EOF'
{
  "name": "batch_processing_demo",
  "user": "demo_user",
  "description": "Demo workflow for batch job creation",
  "jobs": [
    {
      "name": "setup_job",
      "command": "echo 'Setting up environment'",
      "invocation_script": null,
      "cancel_on_blocking_job_failure": false,
      "supports_termination": true,
      "resource_requirements_name": null,
      "blocked_by_job_names": null,
      "input_file_names": null,
      "output_file_names": null,
      "input_user_data_names": null,
      "output_data_names": null,
      "scheduler_name": null
    }
  ],
  "files": null,
  "user_data": null,
  "resource_requirements": null,
  "slurm_schedulers": null
}
EOF

echo "2. Creating batch job commands file..."

# Create a batch jobs file
cat > batch_jobs.txt << 'EOF'
# Data processing batch jobs
# Lines starting with # are comments and will be ignored

# Simple data processing tasks
python process_data.py --batch 001 --input data_001.csv
python process_data.py --batch 002 --input data_002.csv
python process_data.py --batch 003 --input data_003.csv

# Analysis jobs with different parameters
analyze_results.py --input results_001.json --output summary_001.txt
analyze_results.py --input results_002.json --output summary_002.txt
analyze_results.py --input results_003.json --output summary_003.txt

# System maintenance tasks
cleanup_temp_files.sh /tmp/batch_001
cleanup_temp_files.sh /tmp/batch_002
cleanup_temp_files.sh /tmp/batch_003

# Reporting jobs
generate_report.py --batch 001 --format pdf
generate_report.py --batch 002 --format pdf
generate_report.py --batch 003 --format pdf
EOF

echo "3. Creating the workflow on the server..."

# Create the workflow and capture the workflow ID
WORKFLOW_OUTPUT=$(torc-client --format json workflows create-from-spec sample_workflow.json)
WORKFLOW_ID=$(echo "$WORKFLOW_OUTPUT" | jq -r '.workflow_id')

if [ "$WORKFLOW_ID" = "null" ] || [ -z "$WORKFLOW_ID" ]; then
    echo "Error: Failed to create workflow"
    echo "Output: $WORKFLOW_OUTPUT"
    exit 1
fi

echo "✓ Created workflow with ID: $WORKFLOW_ID"

echo "4. Creating batch jobs from file..."

# Create jobs from the batch file
torc-client jobs create-from-file "$WORKFLOW_ID" batch_jobs.txt \
    --cpus-per-job 2 \
    --memory-per-job 4g \
    --runtime-per-job P0DT15M

echo "5. Listing all jobs in the workflow..."

# List all jobs to verify they were created
torc-client jobs list "$WORKFLOW_ID"

echo ""
echo "6. Demo with different resource requirements..."

# Create another batch file with different job types
cat > high_performance_jobs.txt << 'EOF'
# High-performance computing jobs
# These jobs require more resources

# Machine learning training jobs
python train_model.py --dataset large_dataset.csv --epochs 100
python train_model.py --dataset medium_dataset.csv --epochs 200
python train_model.py --dataset small_dataset.csv --epochs 300

# Video processing jobs
ffmpeg -i video001.mp4 -vf scale=1920:1080 -c:v libx264 output001.mp4
ffmpeg -i video002.mp4 -vf scale=1920:1080 -c:v libx264 output002.mp4
EOF

echo "Creating high-performance batch jobs..."

# Create jobs with higher resource requirements
torc-client jobs create-from-file "$WORKFLOW_ID" high_performance_jobs.txt \
    --cpus-per-job 8 \
    --memory-per-job 32g \
    --runtime-per-job P0DT2H

echo "7. Final job count:"

# Show final job count
FINAL_OUTPUT=$(torc-client --format json jobs list "$WORKFLOW_ID")
JOB_COUNT=$(echo "$FINAL_OUTPUT" | jq '.items | length')

echo "✓ Total jobs in workflow: $JOB_COUNT"

echo ""
echo "=== Demo Summary ==="
echo "✓ Created workflow: $WORKFLOW_ID"
echo "✓ Added 12 batch processing jobs (2 CPUs, 4g memory, 15min runtime)"
echo "✓ Added 5 high-performance jobs (8 CPUs, 32g memory, 2h runtime)"
echo "✓ Total jobs created from files: 17"
echo ""
echo "Key features demonstrated:"
echo "- Comment support in job files (# comments are ignored)"
echo "- Automatic job naming (job1, job2, job3, etc.)"
echo "- Custom resource requirements per batch"
echo "- Bulk job creation for efficient processing"
echo ""
echo "Files created in $PWD:"
echo "- sample_workflow.json: Sample workflow specification"
echo "- batch_jobs.txt: Basic batch job commands"
echo "- high_performance_jobs.txt: Resource-intensive job commands"
echo ""
echo "Clean up by running: torc-client workflows delete $WORKFLOW_ID"
echo "This will also delete all associated jobs."

cd ..
echo ""
echo "Demo completed successfully!"