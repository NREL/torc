# Tutorial 4: Simple Job Parameterization

**Goal**: Create a parameter sweep with one parameter dimension.

**Use Case**: Testing different configurations, hyperparameter search over one parameter.

## Step 1: Create Workflow Specification

Save as `learning_rate_sweep.yaml`:

```yaml
name: lr_sweep
user: myuser
description: Test different learning rates

jobs:
  - name: train_lr{lr:.4f}
    command: |
      python train.py \
        --learning-rate={lr} \
        --output=/models/model_lr{lr:.4f}.pt
    resource_requirements: gpu
    output_files:
      - model_lr{lr:.4f}
    parameters:
      lr: "[0.0001,0.0005,0.001,0.005,0.01]"

  - name: evaluate_lr{lr:.4f}
    command: |
      python evaluate.py \
        --model=/models/model_lr{lr:.4f}.pt \
        --output=/results/metrics_lr{lr:.4f}.json
    resource_requirements: gpu
    input_files:
      - model_lr{lr:.4f}
    output_files:
      - metrics_lr{lr:.4f}
    parameters:
      lr: "[0.0001,0.0005,0.001,0.005,0.01]"

  - name: compare_results
    command: |
      python compare.py --input-dir=/results --output=/results/comparison.csv
    resource_requirements: minimal
    input_files:
      - metrics_lr{lr:.4f}
    parameters:
      lr: "[0.0001,0.0005,0.001,0.005,0.01]"

files:
  - name: model_lr{lr:.4f}
    path: /models/model_lr{lr:.4f}.pt
    parameters:
      lr: "[0.0001,0.0005,0.001,0.005,0.01]"

  - name: metrics_lr{lr:.4f}
    path: /results/metrics_lr{lr:.4f}.json
    parameters:
      lr: "[0.0001,0.0005,0.001,0.005,0.01]"

resource_requirements:
  - name: gpu
    num_cpus: 8
    num_gpus: 1
    memory: 16g
    runtime: PT2H

  - name: minimal
    num_cpus: 1
    memory: 2g
    runtime: PT10M
```

## Step 2: Create Workflow

```bash
WORKFLOW_ID=$(torc workflows create-from-spec learning_rate_sweep.yaml | jq -r '.id')
torc workflows initialize-jobs $WORKFLOW_ID
```

## Step 3: Verify Expansion

```bash
# Count jobs (should be 11: 5 train + 5 evaluate + 1 compare)
torc jobs list $WORKFLOW_ID | jq '.jobs | length'

# View job names
torc jobs list $WORKFLOW_ID | jq '.jobs[] | .name' | sort
```

Output:
```
"compare_results"
"evaluate_lr0.0001"
"evaluate_lr0.0005"
"evaluate_lr0.0010"
"evaluate_lr0.0050"
"evaluate_lr0.0100"
"train_lr0.0001"
"train_lr0.0005"
"train_lr0.0010"
"train_lr0.0050"
"train_lr0.0100"
```

## Step 4: Check Dependencies

```bash
# Check status - training jobs should be ready, evaluation blocked
torc jobs list $WORKFLOW_ID | jq '.jobs[] | {name, status}'
```

Expected:
- All `train_*` jobs: `ready`
- All `evaluate_*` jobs: `blocked` (waiting for corresponding `train_*`)
- `compare_results`: `blocked` (waiting for all `evaluate_*`)

## Step 5: Run Workflow

```bash
torc run-jobs $WORKFLOW_ID
```

Execution flow:
1. All 5 training jobs run in parallel
2. As each training completes, its evaluation job becomes ready
3. After all evaluations complete, `compare_results` runs
