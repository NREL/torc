# Tutorial 4: Simple Job Parameterization

This tutorial teaches you how to create parameter sweeps—generating multiple related jobs from a single job definition using Torc's parameterization feature.

## Learning Objectives

By the end of this tutorial, you will:

- Understand how parameterization expands one job definition into many jobs
- Learn the different parameter formats (lists, ranges)
- Know how to use format specifiers for consistent naming
- See how parameterization combines with file dependencies

## Prerequisites

- Completed [Tutorial 1: Many Independent Jobs](./many-jobs.md)
- Completed [Tutorial 2: Diamond Workflow](./diamond.md)
- Torc server running

## Why Parameterization?

Without parameterization, a 5-value hyperparameter sweep would require writing 5 separate job definitions. With parameterization, you write one definition and Torc expands it:

```yaml
# Without parameterization: 5 separate definitions
jobs:
  - name: train_lr0.0001
    command: python train.py --lr=0.0001
  - name: train_lr0.0005
    command: python train.py --lr=0.0005
  # ... 3 more ...

# With parameterization: 1 definition
jobs:
  - name: train_lr{lr:.4f}
    command: python train.py --lr={lr}
    parameters:
      lr: "[0.0001,0.0005,0.001,0.005,0.01]"
```

## Step 1: Create the Workflow Specification

Save as `learning_rate_sweep.yaml`:

```yaml
name: lr_sweep
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

### Understanding the Specification

**Parameter Syntax:**
- `{lr}` - Simple substitution with the parameter value
- `{lr:.4f}` - Format specifier: 4 decimal places (e.g., `0.0010` not `0.001`)

**Parameter Values:**
- `"[0.0001,0.0005,0.001,0.005,0.01]"` - A list of 5 specific values

**File Parameterization:**
Notice that both jobs AND files have `parameters:`. When Torc expands:
- Each `train_lr{lr:.4f}` job gets a corresponding `model_lr{lr:.4f}` file
- The file dependencies are matched by parameter value

**Dependency Flow:**
1. `train_lr0.0001` → outputs `model_lr0.0001` → unblocks `evaluate_lr0.0001`
2. `train_lr0.0005` → outputs `model_lr0.0005` → unblocks `evaluate_lr0.0005`
3. (and so on for each learning rate)
4. All `evaluate_*` jobs → unblock `compare_results`

## Step 2: Create and Initialize the Workflow

```bash
WORKFLOW_ID=$(torc workflows create learning_rate_sweep.yaml -f json | jq -r '.id')
echo "Created workflow: $WORKFLOW_ID"

torc workflows initialize-jobs $WORKFLOW_ID
```

## Step 3: Verify the Expansion

```bash
# Count jobs (should be 11: 5 train + 5 evaluate + 1 compare)
torc jobs list $WORKFLOW_ID -f json | jq '.jobs | length'
```

List the job names:

```bash
torc jobs list $WORKFLOW_ID -f json | jq -r '.jobs[].name' | sort
```

Output:
```
compare_results
evaluate_lr0.0001
evaluate_lr0.0005
evaluate_lr0.0010
evaluate_lr0.0050
evaluate_lr0.0100
train_lr0.0001
train_lr0.0005
train_lr0.0010
train_lr0.0050
train_lr0.0100
```

Notice:
- One job per parameter value for `train_*` and `evaluate_*`
- Only one `compare_results` job (it has the parameter for dependencies, but doesn't expand because its name has no `{lr}`)

## Step 4: Check Dependencies

```bash
torc jobs list $WORKFLOW_ID
```

Expected statuses:
- All `train_*` jobs: **ready** (no input dependencies)
- All `evaluate_*` jobs: **blocked** (waiting for corresponding model file)
- `compare_results`: **blocked** (waiting for all metrics files)

## Step 5: Run the Workflow

```bash
torc run $WORKFLOW_ID
```

Execution flow:

1. **All 5 training jobs run in parallel** - They have no dependencies on each other
2. **Each evaluation unblocks independently** - When `train_lr0.0001` finishes, `evaluate_lr0.0001` can start (doesn't wait for other training jobs)
3. **Compare runs last** - Only after all 5 evaluations complete

This is more efficient than a simple two-stage workflow because evaluations can start as soon as their specific training job completes.

## Parameter Format Reference

### List Format

Explicit list of values:

```yaml
parameters:
  lr: "[0.0001,0.0005,0.001,0.005,0.01]"  # Numbers
  opt: "['adam','sgd','rmsprop']"          # Strings (note the quotes)
```

### Range Format

For integer or float sequences:

```yaml
parameters:
  i: "1:100"        # Integers 1 to 100 (inclusive)
  i: "0:100:10"     # Integers 0, 10, 20, ..., 100 (with step)
  lr: "0.0:1.0:0.1" # Floats 0.0, 0.1, 0.2, ..., 1.0
```

### Format Specifiers

Control how values appear in names:

| Specifier | Example Value | Result |
|-----------|---------------|--------|
| `{i}` | 5 | `5` |
| `{i:03d}` | 5 | `005` |
| `{lr:.4f}` | 0.001 | `0.0010` |
| `{lr:.2e}` | 0.001 | `1.00e-03` |

## How Parameterization and File Dependencies Interact

When both jobs and files are parameterized with the same parameter:

```yaml
jobs:
  - name: train_{i}
    output_files: [model_{i}]
    parameters:
      i: "1:3"

  - name: eval_{i}
    input_files: [model_{i}]
    parameters:
      i: "1:3"

files:
  - name: model_{i}
    path: /models/model_{i}.pt
    parameters:
      i: "1:3"
```

Torc creates these relationships:
- `train_1` → `model_1` → `eval_1`
- `train_2` → `model_2` → `eval_2`
- `train_3` → `model_3` → `eval_3`

Each chain is independent—`eval_2` doesn't wait for `train_1`.

## What You Learned

In this tutorial, you learned:

- ✅ How to use `parameters:` to expand one job definition into many
- ✅ List format (`"[a,b,c]"`) and range format (`"1:100"`)
- ✅ Format specifiers (`{i:03d}`, `{lr:.4f}`) for consistent naming
- ✅ How parameterized files create one-to-one dependencies
- ✅ The efficiency of parameter-matched dependencies (each chain runs independently)

## Next Steps

- [Tutorial 5: Advanced Parameterization](./advanced-params.md) - Multi-dimensional grid searches
- [Multi-Stage Workflows with Barriers](./multi-stage-barrier.md) - Scale to thousands of parameterized jobs
