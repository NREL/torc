# Creating Workflows

Torc supports creating workflows through several methods:
- Using Workflow Specification Files
  - YAML Format
  - JSON Format
  - JSON5 Format
  - KDL Format
- Using the Torc Client CLI
- Using auto-generated OpenAPI clients

## Using Workflow Specification Files

This is the recommended approach for most workflows. The file formats are straightforward to
understand, no coding is required, and the parameterization system allows you to
define similar jobs in a concise manner.

### YAML Format

```yaml
# workflow.yaml
name: my_workflow
description: Process data pipeline

jobs:
  - name: preprocess
    command: bash preprocess.sh -o ${files.output.preprocessed_data}
    resource_requirements: small

  - name: analyze
    command: python analyze.py -i ${files.input.preprocessed_data} -o ${files.output.results}
    resource_requirements: large

files:
  - name: preprocessed_data
    path: /tmp/preprocessed.json
  - name: results
    path: /tmp/results.csv

resource_requirements:
  - name: small
    num_cpus: 2
    num_gpus: 0
    num_nodes: 1
    memory: 4g
    runtime: PT30M
  - name: large
    num_cpus: 16
    num_gpus: 1
    num_nodes: 1
    memory: 64g
    runtime: PT4H
```

Create workflow:
```bash
torc workflows create workflow.yaml
```

### JSON5 Format

JSON5 allows comments and trailing commas:

```json5
{
  name: "my_workflow",
  user: "username",
  description: "Process data pipeline",

  jobs: [
    {
      name: "preprocess",
      command: "bash preprocess.sh -o ${files.output.preprocessed_data}",
      resource_requirements: "small",
    },
    {
      name: "analyze",
      command: "python analyze.py -i ${files.input.preprocessed_data} -o ${files.output.results}",
      resource_requirements: "small",
    },
  ],

  files: [
    {name: "preprocessed_data", path: "/tmp/preprocessed.json"},
  ],

  resource_requirements: [
    {
      name: "small",
      num_cpus: 2,
      memory: "4g",
      runtime: "PT30M",
    },
  ],
}
```

### KDL Format

Alternative configuration language with a more modern syntax:

```kdl
name "my_workflow"
user "username"
description "Process data pipeline"

// File definitions
file "preprocessed_data" path="/tmp/preprocessed.json"
file "results" path="/tmp/results.csv"

// Resource requirements
resource_requirements "small" {
    num_cpus 2
    num_gpus 0
    num_nodes 1
    memory "4g"
    runtime "PT30M"
}

resource_requirements "large" {
    num_cpus 16
    num_gpus 1
    num_nodes 1
    memory "64g"
    runtime "PT4H"
}

// Job definitions
job "preprocess" {
    command "bash preprocess.sh -o ${files.output.preprocessed_data}"
    resource_requirements "small"
}

job "analyze" {
    command "python analyze.py -i ${files.input.preprocessed_data} -o ${files.output.results}"
    resource_requirements "large"
}
```

**Note**: In KDL, boolean values use `#true` and `#false` syntax (e.g., `enabled #true`).

## Choosing a Format

**Use YAML when:**
- You need parameter expansion for job/file generation
- You want the most widely supported format
- You're creating complex workflows with many repeated patterns

**Use JSON5 when:**
- You need JSON compatibility
- You want to programmatically generate or manipulate workflows
- You prefer JSON-like structure with comment support

**Use KDL when:**
- You prefer minimal, clean syntax
- You want a more modern configuration language

All three formats support the same core features (jobs, files, user_data, resource requirements, Slurm schedulers, actions, and resource monitoring).

## Example Workflows

The Torc repository includes comprehensive examples in all three formats, organized by type:

```
examples/
├── yaml/     # YAML format examples
├── json/     # JSON and JSON5 format examples
└── kdl/      # KDL format examples
```

Browse the examples directory to find:
- **Simple workflows**: `sample_workflow`, `diamond_workflow`, `three_stage_workflow`
- **Resource monitoring**: `resource_monitoring_demo`
- **Workflow actions**: `workflow_actions_*`
- **Slurm integration**: `slurm_staged_pipeline`, `workflow_actions_simple_slurm`
- **Parameterized workflows**: `hundred_jobs_parameterized`, `hyperparameter_sweep`, `data_pipeline_parameterized`

Each workflow is available in multiple formats so you can compare syntax and choose your preference.


## One Job at a Time via CLI

To create a workflow with individual job creation:

```bash
# Create workflow
torc workflows create \
  --name "my_workflow" \
  --user "$(whoami)" \
  --description "My test workflow"
```
```
Successfully created workflow:
  ID: 1
  Name: my_workflow
  User: dthom
  Description: My test workflow
```
Note the ID returned from the previous command. You will use it in the following commands.


```bash
# Create resource requirements
torc resource-requirements create \
  --name "small" \
  --num-cpus 1 \
  --memory "1g" \
  --runtime "PT10M" \
  1
```
```
Successfully created resource requirements:
  ID: 2
  Workflow ID: 1
  Name: small
  Number of CPUs: 1
  Number of GPUs: 0
  Number of nodes: 1
  Memory: 1g
  Runtime: PT10M
```

# Create a file
```bash
torc files create \
  --name "input_file" \
  --path "/data/input.txt" \
  1
```
```
Successfully created file:
  ID: 1
  Name: input_file
  Path: /data/input.txt
  Workflow ID: 1
```

# Create a job
torc jobs create \
  --name "process_data" \
  --command "python process.py" \
  --resource-requirements-id $RR_ID \
  --input-file-ids 1 \
  1

## OpenAPI clients
The torc developers will soon publish Python and Julia OpenAPI clients along with helper functions
for common tasks.
