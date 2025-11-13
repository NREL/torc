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
    resource_requirements_name: small

  - name: analyze
    command: python analyze.py -i ${files.input.preprocessed_data} -o ${files.output.results}
    resource_requirements_name: large

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
torc-client workflows create-from-spec workflow.yaml
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
      resource_requirements_name: "small",
    },
    {
      name: "analyze",
      command: "python analyze.py -i ${files.input.preprocessed_data} -o ${files.output.results}",
      resource_requirements_name: "small",
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

Alternative configuration language:

```kdl
name "my_workflow"
user "username"
description "Process data pipeline"

jobs {
  job {
    name "preprocess"
    command "bash preprocess.sh -o ${files.output.results}"
    resource_requirements_name "small"
  }
  job {
    name "analyze"
    command "python anaylyze.py -i ${files.input.preprocessed_data} -o ${files.output.results}"
    resource_requirements_name "small"
  }
}

files {
  file name="preprocessed_data" path="/tmp/preprocessed.json"
}

resource_requirements {
  requirement {
    name "small"
    num_cpus 2
    memory "4g"
    runtime "PT30M"
  }
}

```
## One Job at a Time via CLI

To create a workflow with individual job creation:

```bash
# Create workflow
torc-client workflows create \
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
torc-client resource-requirements create \
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
torc-client files create \
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
torc-client jobs create \
  --name "process_data" \
  --command "python process.py" \
  --resource-requirements-id $RR_ID \
  --input-file-ids 1 \
  1

## OpenAPI clients
The torc developers will soon publish Python and Julia OpenAPI clients along with helper functions
for common tasks.
