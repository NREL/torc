# Tutorial 3: User Data Dependencies

**Goal**: Pass JSON configuration data between jobs without using files.

**Use Case**: Configuration management, parameter passing, metadata propagation.

## Step 1: Create Workflow Specification

Save as `user_data_workflow.yaml`:

```yaml
name: config_pipeline
user: myuser
description: Jobs that pass configuration via user_data

jobs:
  - name: generate_config
    command: |
      echo '{"learning_rate": 0.001, "batch_size": 32, "epochs": 10}' > /tmp/config.json
      torc-client user-data update ${user_data.output.ml_config} \
        --data "$(cat /tmp/config.json)"
    resource_requirements_name: minimal

  - name: train_model
    command: |
      echo "Training with config:"
      torc-client user-data get ${user_data.input.ml_config} | jq '.data'
      python train.py --config="${user_data.input.ml_config}"
    resource_requirements_name: gpu_large

  - name: evaluate_model
    command: |
      echo "Evaluating with config:"
      torc-client user-data get ${user_data.input.ml_config} | jq '.data'
      python evaluate.py --config="${user_data.input.ml_config}"
    resource_requirements_name: gpu_small

user_data:
  - name: ml_config
    data: null  # Will be populated by generate_config job

resource_requirements:
  - name: minimal
    num_cpus: 1
    memory: 1g
    runtime: PT5M

  - name: gpu_small
    num_cpus: 4
    num_gpus: 1
    memory: 16g
    runtime: PT1H

  - name: gpu_large
    num_cpus: 8
    num_gpus: 2
    memory: 32g
    runtime: PT4H
```

## Step 2: Create Workflow

```bash
WORKFLOW_ID=$(torc-client workflows create-from-spec user_data_workflow.yaml | jq -r '.id')
torc-client workflows initialize-jobs $WORKFLOW_ID
```

## Step 3: Check Initial State

```bash
# Check user_data - should be null/empty
torc-client user-data list $WORKFLOW_ID | jq '.user_data[] | {name, data}'
```

Output:
```json
{"name": "ml_config", "data": null}
```

## Step 4: Run Workflow

```bash
torc run-jobs $WORKFLOW_ID
```

## Step 5: Observe Data Flow

After `generate_config` completes:

```bash
# Check updated user_data
torc-client user-data list $WORKFLOW_ID | jq '.user_data[] | {name, data}'
```

Output:
```json
{
  "name": "ml_config",
  "data": {
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 10
  }
}
```

Now `train_model` and `evaluate_model` become ready because their input user_data is available.

## When to Use user_data vs Files

- **Use files** for: Large datasets, binary data, file-based tools
- **Use user_data** for: Configurations, parameters, metadata, small JSON/YAML data
