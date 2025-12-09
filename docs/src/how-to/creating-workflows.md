# How to Create Workflows

This guide shows different methods for creating Torc workflows, from the most common (specification files) to more advanced approaches (CLI, API).

## Using Workflow Specification Files (Recommended)

The easiest way to create workflows is with specification files. Torc supports YAML, JSON5, and KDL formats.

### Create from a YAML File

```bash
torc workflows create workflow.yaml
```

### Create from JSON5 or KDL

```bash
torc workflows create workflow.json5
torc workflows create workflow.kdl
```

Torc detects the format from the file extension.

### Create and Run in One Step

For quick iteration, combine creation and execution:

```bash
# Create and run locally
torc run workflow.yaml

# Create and submit to Slurm
torc submit workflow.yaml
```

For format syntax and examples, see the [Workflow Specification Formats](../reference/workflow-formats.md) reference.

## Using the CLI (Step by Step)

For programmatic workflow construction or when you need fine-grained control, create workflows piece by piece using the CLI.

### Step 1: Create an Empty Workflow

```bash
torc workflows new \
  --name "my_workflow" \
  --description "My test workflow"
```

Output:
```
Successfully created workflow:
  ID: 1
  Name: my_workflow
  User: dthom
  Description: My test workflow
```

Note the workflow ID (1) for subsequent commands.

### Step 2: Add Resource Requirements

```bash
torc resource-requirements create \
  --name "small" \
  --num-cpus 1 \
  --memory "1g" \
  --runtime "PT10M" \
  1  # workflow ID
```

Output:
```
Successfully created resource requirements:
  ID: 2
  Workflow ID: 1
  Name: small
```

### Step 3: Add Files (Optional)

```bash
torc files create \
  --name "input_file" \
  --path "/data/input.txt" \
  1  # workflow ID
```

### Step 4: Add Jobs

```bash
torc jobs create \
  --name "process_data" \
  --command "python process.py" \
  --resource-requirements-id 2 \
  --input-file-ids 1 \
  1  # workflow ID
```

### Step 5: Initialize and Run

```bash
# Initialize the workflow (resolves dependencies)
torc workflows initialize-jobs 1

# Run the workflow
torc run 1
```

## Using the Python API

For complex programmatic workflow construction, use the Python client:

```python
from torc import make_api
from torc.openapi_client import (
    WorkflowModel,
    JobModel,
    ResourceRequirementsModel,
)

# Connect to the server
api = make_api("http://localhost:8080/torc-service/v1")

# Create workflow
workflow = api.create_workflow(WorkflowModel(
    name="my_workflow",
    user="myuser",
    description="Programmatically created workflow",
))

# Add resource requirements
rr = api.create_resource_requirements(ResourceRequirementsModel(
    workflow_id=workflow.id,
    name="small",
    num_cpus=1,
    memory="1g",
    runtime="PT10M",
))

# Add jobs
api.create_job(JobModel(
    workflow_id=workflow.id,
    name="job1",
    command="echo 'Hello World'",
    resource_requirements_id=rr.id,
))

print(f"Created workflow {workflow.id}")
```

For more details, see the [Map Python Functions](../tutorials/map_python_function_across_workers.md) tutorial.

## Choosing a Method

| Method | Best For |
|--------|----------|
| **Specification files** | Most workflows; declarative, version-controllable |
| **CLI step-by-step** | Scripted workflows, testing individual components |
| **Python API** | Complex dynamic workflows, integration with Python pipelines |

## Common Tasks

### Validate a Workflow File Without Creating

```bash
# Dry run - validates but doesn't create
torc workflows create --dry-run workflow.yaml
```

### List Available Workflows

```bash
torc workflows list
```

### Delete a Workflow

```bash
torc workflows delete <workflow_id>
```

### View Workflow Details

```bash
torc workflows get <workflow_id>
```

## Defining File Dependencies

Jobs often need to read input files and produce output files. Torc can automatically infer job dependencies from these file relationships using **variable substitution**:

```yaml
files:
  - name: raw_data
    path: /data/raw.csv
  - name: processed_data
    path: /data/processed.csv

jobs:
  - name: preprocess
    command: "python preprocess.py -o ${files.output.raw_data}"

  - name: analyze
    command: "python analyze.py -i ${files.input.raw_data} -o ${files.output.processed_data}"
```

Key concepts:
- **`${files.input.NAME}`** - References a file this job reads (creates a dependency on the job that outputs it)
- **`${files.output.NAME}`** - References a file this job writes (satisfies dependencies for downstream jobs)

In the example above, `analyze` automatically depends on `preprocess` because it needs `raw_data` as input, which `preprocess` produces as output.

For a complete walkthrough, see [Tutorial: Diamond Workflow](../tutorials/diamond.md).

## Next Steps

- [Tutorial: Diamond Workflow](../tutorials/diamond.md) - Learn file-based dependencies with the fan-out/fan-in pattern
- [Workflow Specification Formats](../reference/workflow-formats.md) - Detailed format reference
- [Job Parameterization](../reference/parameterization.md) - Generate multiple jobs from templates
- [Tutorial: Many Independent Jobs](../tutorials/many-jobs.md) - Your first workflow
