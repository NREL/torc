# Tutorial 5: Advanced Multi-Dimensional Parameterization

**Goal**: Create a grid search over multiple hyperparameters.

**Use Case**: Full hyperparameter optimization, A/B/C testing, factorial experiments.

## Step 1: Create Workflow Specification

Save as `grid_search.yaml`:

```yaml
name: hyperparameter_grid_search
user: myuser
description: 3D grid search over learning rate, batch size, and optimizer

jobs:
  # Data preparation (runs once)
  - name: prepare_data
    command: python prepare_data.py --output=/data/processed.pkl
    resource_requirements_name: data_prep
    output_file_names:
      - training_data

  # Training jobs (one per parameter combination)
  - name: train_lr{lr:.4f}_bs{bs}_opt{opt}
    command: |
      python train.py \
        --data=/data/processed.pkl \
        --learning-rate={lr} \
        --batch-size={bs} \
        --optimizer={opt} \
        --output=/models/model_lr{lr:.4f}_bs{bs}_opt{opt}.pt \
        --metrics=/results/metrics_lr{lr:.4f}_bs{bs}_opt{opt}.json
    resource_requirements_name: gpu_training
    input_file_names:
      - training_data
    output_file_names:
      - model_lr{lr:.4f}_bs{bs}_opt{opt}
      - metrics_lr{lr:.4f}_bs{bs}_opt{opt}
    parameters:
      lr: "[0.0001,0.001,0.01]"
      bs: "[16,32,64]"
      opt: "['adam','sgd']"

  # Aggregate results
  - name: aggregate_results
    command: |
      python aggregate.py \
        --input-dir=/results \
        --output=/results/summary.csv
    resource_requirements_name: minimal
    input_file_names:
      - metrics_lr{lr:.4f}_bs{bs}_opt{opt}
    parameters:
      lr: "[0.0001,0.001,0.01]"
      bs: "[16,32,64]"
      opt: "['adam','sgd']"

  # Find best model
  - name: select_best_model
    command: |
      python select_best.py \
        --summary=/results/summary.csv \
        --output=/results/best_config.json
    resource_requirements_name: minimal
    blocked_by_job_names:
      - aggregate_results

files:
  - name: training_data
    path: /data/processed.pkl

  - name: model_lr{lr:.4f}_bs{bs}_opt{opt}
    path: /models/model_lr{lr:.4f}_bs{bs}_opt{opt}.pt
    parameters:
      lr: "[0.0001,0.001,0.01]"
      bs: "[16,32,64]"
      opt: "['adam','sgd']"

  - name: metrics_lr{lr:.4f}_bs{bs}_opt{opt}
    path: /results/metrics_lr{lr:.4f}_bs{bs}_opt{opt}.json
    parameters:
      lr: "[0.0001,0.001,0.01]"
      bs: "[16,32,64]"
      opt: "['adam','sgd']"

resource_requirements:
  - name: data_prep
    num_cpus: 8
    memory: 32g
    runtime: PT1H

  - name: gpu_training
    num_cpus: 8
    num_gpus: 1
    memory: 16g
    runtime: PT4H

  - name: minimal
    num_cpus: 1
    memory: 2g
    runtime: PT10M
```

## Step 2: Create Workflow

```bash
WORKFLOW_ID=$(torc-client workflows create-from-spec grid_search.yaml | jq -r '.id')
torc-client workflows initialize-jobs $WORKFLOW_ID
```

## Step 3: Verify Expansion

```bash
# Count jobs: 1 prepare + (3 * 3 * 2) training + 1 aggregate + 1 select = 21
torc-client jobs list $WORKFLOW_ID | jq '.jobs | length'

# View training job names
torc-client jobs list $WORKFLOW_ID | jq '.jobs[] | select(.name | startswith("train_")) | .name' | sort
```

Output (18 training jobs):
```
"train_lr0.0001_bs16_optadam"
"train_lr0.0001_bs16_optsgd"
"train_lr0.0001_bs32_optadam"
"train_lr0.0001_bs32_optsgd"
"train_lr0.0001_bs64_optadam"
"train_lr0.0001_bs64_optsgd"
"train_lr0.0010_bs16_optadam"
... (18 total)
```

## Step 4: Visualize Dependency Graph

```bash
# Check blocked jobs
torc-client jobs list $WORKFLOW_ID | jq -r '.jobs[] | "\(.name): \(.status)"' | grep blocked
```

Expected:
- All `train_*` jobs: `blocked` (waiting for `prepare_data`)
- `aggregate_results`: `blocked` (waiting for all `train_*`)
- `select_best_model`: `blocked` (waiting for `aggregate_results`)

## Step 5: Run Workflow on Slurm

For this large job, submit multiple Slurm workers:

```bash
# Submit 4 workers with 2 GPUs each (can run 8 training jobs in parallel)
for i in {1..4}; do
  sbatch --nodes=1 --gres=gpu:2 --time=8:00:00 \
    <<EOF
#!/bin/bash
torc-job-runner $WORKFLOW_ID
EOF
done
```

## Step 6: Monitor Progress

```bash
# Watch job completion
watch -n 10 'torc-client jobs list-by-status $WORKFLOW_ID | jq'
```

## Step 7: Retrieve Results

After completion:

```bash
# View best configuration
cat /results/best_config.json | jq

# View summary of all runs
cat /results/summary.csv
```
