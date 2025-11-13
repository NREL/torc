# Workflow and Job Creation Examples

This directory contains examples for creating workflows using the `create-from-spec` command and creating multiple jobs using the `create-from-file` command.

## Workflow Creation Overview

The `create-from-spec` command allows you to create complete workflows on the Torc server from a single specification file that follows the `WorkflowSpec` format. Supported formats include JSON, JSON5, and YAML. This is much more efficient than creating workflows piece by piece and ensures all components are created together with proper relationships.

## Job Batch Creation Overview

The `create-from-file` command allows you to create multiple jobs for an existing workflow from a simple text file containing one command per line. This is useful for processing large batches of similar tasks.

## Usage

```bash
# Create workflow from spec file (JSON format)
torc-client workflows create-from-spec sample_workflow.json

# Create workflow from JSON5 spec file
torc-client workflows create-from-spec sample_workflow.json5

# Create workflow from YAML spec file
torc-client workflows create-from-spec sample_workflow.yaml

# Create workflow and output response as JSON
torc-client --format json workflows create-from-spec sample_workflow.json

# Create multiple jobs from a file (requires existing workflow)
torc-client jobs create-from-file 123 job_commands.txt

# Create jobs with custom resource requirements
torc-client jobs create-from-file 123 job_commands.txt --cpus-per-job 4 --memory-per-job 8g --runtime-per-job P0DT30M
```

## Job Batch Creation from File

### Command Format
```bash
torc-client jobs create-from-file <WORKFLOW_ID> <FILE> [OPTIONS]
```

### Required Arguments
- `WORKFLOW_ID`: ID of the existing workflow to add jobs to
- `FILE`: Path to text file containing job commands (one per line)

### Options
- `--cpus-per-job <N>`: Number of CPUs per job (default: 1)
- `--memory-per-job <SIZE>`: Memory per job, e.g., "1m", "2g" (default: "1m")
- `--runtime-per-job <DURATION>`: Runtime per job in ISO 8601 duration format (default: "P0DT1M")

### File Format
The job commands file should contain:
- One command per line
- Lines starting with `#` are treated as comments and ignored
- Empty lines are ignored
- Each command will become a separate job

### Example File (`job_commands.txt`)
```
# Data processing batch jobs
python process_data.py --batch 1
python process_data.py --batch 2
python process_data.py --batch 3

# Analysis jobs
analyze_results.py --input batch1_results.json
analyze_results.py --input batch2_results.json
analyze_results.py --input batch3_results.json
```

### Job Naming
- Jobs are automatically named `job1`, `job2`, `job3`, etc.
- Index starts from current job count + 1 to avoid conflicts
- If name conflicts occur, jobs get suffixed with `_1`, `_2`, etc.

### Features
- **Bulk Creation**: Uses efficient batch API for creating up to 1000 jobs at once
- **Resource Requirements**: Automatically creates shared resource requirements for all jobs
- **Duplicate Prevention**: Checks existing job names to avoid conflicts
- **Error Handling**: Provides detailed error messages for troubleshooting

### Example Usage
```bash
# Create a workflow first
torc-client workflows create-from-spec my_workflow.json

# Add batch jobs to the workflow (assuming workflow ID is 42)
torc-client jobs create-from-file 42 job_commands.txt --cpus-per-job 2 --memory-per-job 4g

# Check the created jobs
torc-client jobs list 42
```

## Workflow Specification File Format

The JSON file must follow the `WorkflowSpec` format with the following structure:

```json
{
  "name": "workflow_name",
  "user": "username", 
  "description": "Workflow description",
  "jobs": [...],
  "files": [...],
  "user_data": [...],
  "resource_requirements": [...],
  "slurm_schedulers": [...]
}
```

### Required Fields

- **`name`**: Name of the workflow
- **`user`**: User who owns the workflow  
- **`description`**: Description of the workflow
- **`jobs`**: Array of job specifications (at least one job required)

### Optional Fields

- **`files`**: File models that jobs can reference
- **`user_data`**: User data objects for passing information between jobs
- **`resource_requirements`**: Resource requirement specifications that jobs can use
- **`slurm_schedulers`**: Slurm scheduler configurations for job execution

## Job Specifications

Each job in the `jobs` array supports these fields:

### Required Fields
- **`name`**: Unique name for the job
- **`command`**: Command to execute

### Optional Fields
- **`invocation_script`**: Wrapper script for the command
- **`cancel_on_blocking_job_failure`**: Whether to cancel if blocking jobs fail (default: false)
- **`supports_termination`**: Whether job supports graceful termination (default: false)
- **`resource_requirements_name`**: Name of resource requirements to use
- **`blocked_by_job_names`**: Array of job names this job depends on
- **`input_file_names`**: Array of file names this job needs as input
- **`output_file_names`**: Array of file names this job produces
- **`input_user_data_names`**: Array of user data names this job consumes
- **`output_data_names`**: Array of user data names this job produces
- **`scheduler_name`**: Name of scheduler to use for this job
- **`parameters`**: Object with parameter names and values for expanding jobs/files into multiple instances

## Features

### Efficient Bulk Creation
- Jobs are created in batches of 1000 for optimal performance
- Files, user data, resource requirements, and schedulers are created efficiently
- Name-to-ID mapping handles all references automatically

### Dependency Management
- Job dependencies specified by name are automatically converted to database IDs
- Dependencies are set after all jobs are created to avoid circular reference issues

### Error Handling & Rollback
- If any step fails, the entire workflow is automatically deleted (cascades to all components)
- Duplicate name detection within each resource type
- Detailed error messages for troubleshooting

### Validation
- Ensures all referenced resources exist (files, user data, schedulers, etc.)
- Validates job dependency references
- Checks for required fields and proper data types

## Example Output

### Success (Table Format)
```
Successfully created workflow from JSON file:
  File: sample_workflow.json
  Workflow ID: 42
  All jobs, files, user data, resource requirements, and schedulers created successfully
```

### Success (JSON Format)
```json
{
  "workflow_id": 42,
  "status": "success", 
  "message": "Workflow created successfully with ID: 42"
}
```

### Error Example
```
Error creating workflow from JSON file 'sample_workflow.json': Input file 'missing_file' not found for job 'data_validation'
```

## Job and File Parameterization

Torc supports **parameterization** to automatically generate multiple jobs or files from a single specification. This is especially useful for parameter sweeps, hyperparameter tuning, or processing multiple datasets without manually creating hundreds of nearly-identical job definitions.

### How It Works

Add a `parameters` field to a job or file specification with parameter names and their values. Torc will automatically:
1. Parse the parameter values (ranges, lists, or single values)
2. Generate the Cartesian product of all parameter combinations
3. Expand the specification into multiple jobs/files
4. Substitute parameter values into names, commands, file paths, and dependencies

### Parameter Value Formats

**Integer Ranges:**
```yaml
parameters:
  i: "1:100"           # 1, 2, 3, ..., 100 (inclusive)
  batch: "0:50:10"     # 0, 10, 20, 30, 40, 50 (with step)
```

**Float Ranges:**
```yaml
parameters:
  lr: "0.0:1.0:0.1"    # 0.0, 0.1, 0.2, ..., 1.0
  temp: "250:400:50"   # 250, 300, 350, 400
```

**Lists:**
```yaml
parameters:
  dataset: "['train','test','validation']"
  optimizer: "['adam','sgd']"
  batch_size: "[16,32,64]"
```

**Multi-dimensional Sweeps:**
```yaml
# Creates Cartesian product: 3 * 2 * 2 = 12 jobs
parameters:
  lr: "[0.001,0.01,0.1]"
  optimizer: "['adam','sgd']"
  batch_size: "[32,64]"
```

### Template Syntax

Use `{param_name}` in job/file names, commands, and paths to substitute parameter values:

```yaml
jobs:
  - name: job_{i:03d}          # job_001, job_002, ..., job_100
    command: echo {i}           # echo 1, echo 2, ..., echo 100
    parameters:
      i: "1:100"
```

**Format Specifiers:**
- `{i:03d}` - Zero-padded integers (e.g., 001, 042, 100)
- `{lr:.4f}` - Float with specific precision (e.g., 0.0010, 0.1000)

### Example: Simple Parallel Jobs

Instead of manually creating 100 jobs, use parameterization:

```yaml
# Before (418 lines): hundred_jobs_workflow.yaml
# After (27 lines): hundred_jobs_parameterized.yaml

jobs:
  - name: job_{i:03d}
    command: echo hello
    resource_requirements_name: minimal
    parameters:
      i: "1:100"
```

This single job specification expands to 100 jobs: `job_001` through `job_100`.

### Example: Hyperparameter Sweep

```yaml
jobs:
  - name: train_lr{lr:.4f}_bs{batch_size}_opt{optimizer}
    command: |
      python train.py \
        --learning-rate={lr} \
        --batch-size={batch_size} \
        --optimizer={optimizer}
    parameters:
      lr: "[0.0001,0.001,0.01]"
      batch_size: "[16,32,64]"
      optimizer: "['adam','sgd']"
```

This creates 18 jobs (3 × 3 × 2) with names like:
- `train_lr0.0001_bs16_optadam`
- `train_lr0.0001_bs32_optsgd`
- `train_lr0.0100_bs64_optadam`
- etc.

### Example: Parameterized Files and Dependencies

Files can also be parameterized, and dependencies automatically expand:

```yaml
files:
  - name: output_{run_id}
    path: /data/output_{run_id}.txt
    parameters:
      run_id: "1:10"

jobs:
  - name: process_{i}
    command: process.sh input_{i}.txt output_{i}.txt
    input_file_names:
      - input_{i}      # Expands to input_1, input_2, etc.
    output_file_names:
      - output_{i}     # Expands to output_1, output_2, etc.
    parameters:
      i: "1:10"

  - name: aggregate
    command: python aggregate.py
    input_file_names:
      - output_{i}     # Waits for ALL output files
    parameters:
      i: "1:10"
```

### Example Workflows

This directory includes several parameterized examples:

- **`hundred_jobs_parameterized.yaml`**: Simple parallel jobs (compare with `hundred_jobs_workflow.yaml`)
- **`hyperparameter_sweep.yaml`**: ML hyperparameter grid search with 18 training jobs
- **`data_pipeline_parameterized.yaml`**: Multi-stage data processing across 4 datasets
- **`simulation_sweep.yaml`**: Scientific simulations across temperature and pressure ranges

## Sample Workflow

The `sample_workflow.json` file demonstrates a complete data processing pipeline with:

- **3 Jobs**: data_download → data_validation → data_analysis
- **5 Files**: Input data, scripts, and output files
- **3 User Data Objects**: Metadata and analysis parameters
- **2 Resource Requirements**: Small and large job configurations
- **2 Slurm Schedulers**: Default and GPU schedulers

This example showcases:
- Job dependencies (`blocked_by_job_names`)
- File input/output relationships
- User data flow between jobs
- Resource requirement assignments
- Scheduler selection per job type