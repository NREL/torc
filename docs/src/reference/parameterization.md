# Job Parameterization

Parameterization allows creating multiple jobs/files from a single specification by expanding parameter ranges.

## Parameter Formats

### Integer Ranges

```yaml
parameters:
  i: "1:10"        # Expands to [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  i: "0:100:10"    # Expands to [0, 10, 20, 30, ..., 90, 100] (with step)
```

### Float Ranges

```yaml
parameters:
  lr: "0.0001:0.01:10"  # 10 values from 0.0001 to 0.01 (log scale)
  alpha: "0.0:1.0:0.1"  # [0.0, 0.1, 0.2, ..., 0.9, 1.0]
```

### Lists (Integer)

```yaml
parameters:
  batch_size: "[16,32,64,128]"
```

### Lists (Float)

```yaml
parameters:
  threshold: "[0.1,0.5,0.9]"
```

### Lists (String)

```yaml
parameters:
  optimizer: "['adam','sgd','rmsprop']"
  dataset: "['train','test','validation']"
```

## Template Substitution

Use parameter values in job/file specifications with `{param_name}` syntax:

### Basic Substitution

```yaml
jobs:
  - name: job_{i}
    command: python train.py --run={i}
    parameters:
      i: "1:5"
```

Expands to:
```yaml
jobs:
  - name: job_1
    command: python train.py --run=1
  - name: job_2
    command: python train.py --run=2
  # ... etc
```

### Format Specifiers

**Zero-padded integers:**

```yaml
jobs:
  - name: job_{i:03d}
    command: echo {i}
    parameters:
      i: "1:100"
```

Expands to: `job_001`, `job_002`, ..., `job_100`

**Float precision:**

```yaml
jobs:
  - name: train_lr{lr:.4f}
    command: python train.py --lr={lr}
    parameters:
      lr: "[0.0001,0.001,0.01]"
```

Expands to: `train_lr0.0001`, `train_lr0.0010`, `train_lr0.0100`

**Multiple decimals:**

```yaml
files:
  - name: result_{threshold:.2f}
    path: /results/threshold_{threshold:.2f}.csv
    parameters:
      threshold: "0.1:1.0:0.1"
```

Expands to: `result_0.10`, `result_0.20`, ..., `result_1.00`

## Multi-Dimensional Parameterization

Use multiple parameters to create Cartesian products:

### Example: Hyperparameter Sweep

```yaml
jobs:
  - name: train_lr{lr:.4f}_bs{batch_size}
    command: |
      python train.py \
        --learning-rate={lr} \
        --batch-size={batch_size}
    parameters:
      lr: "[0.0001,0.001,0.01]"
      batch_size: "[16,32,64]"
```

This expands to 3 × 3 = **9 jobs**:
- `train_lr0.0001_bs16`
- `train_lr0.0001_bs32`
- `train_lr0.0001_bs64`
- `train_lr0.0010_bs16`
- ... (9 total)

### Example: Multi-Dataset Processing

```yaml
jobs:
  - name: process_{dataset}_rep{rep:02d}
    command: python process.py --data={dataset} --replicate={rep}
    parameters:
      dataset: "['train','validation','test']"
      rep: "1:5"
```

This expands to 3 × 5 = **15 jobs**

## Parameterized Dependencies

Parameters work in dependency specifications:

```yaml
jobs:
  # Generate data for each configuration
  - name: generate_{config}
    command: python generate.py --config={config}
    output_files:
      - data_{config}
    parameters:
      config: "['A','B','C']"

  # Process each generated dataset
  - name: process_{config}
    command: python process.py --input=data_{config}.pkl
    input_files:
      - data_{config}
    blocked_by:
      - generate_{config}
    parameters:
      config: "['A','B','C']"
```

This creates 6 jobs with proper dependencies:
- `generate_A` → `process_A`
- `generate_B` → `process_B`
- `generate_C` → `process_C`

## Parameterized Files and User Data

**Files:**

```yaml
files:
  - name: model_{run_id:03d}
    path: /models/run_{run_id:03d}.pt
    parameters:
      run_id: "1:100"
```

**User Data:**

```yaml
user_data:
  - name: config_{experiment}
    data:
      experiment: "{experiment}"
      learning_rate: 0.001
    parameters:
      experiment: "['baseline','ablation','full']"
```

## Best Practices

1. **Use descriptive parameter names** - `lr` not `x`, `batch_size` not `b`
2. **Format numbers consistently** - Use `:03d` for run IDs, `:.4f` for learning rates
3. **Keep parameter counts reasonable** - 3×3×3 = 27 jobs is manageable, 10×10×10 = 1000 may overwhelm the system
4. **Match parameter ranges across related jobs** - Use same parameter values for generator and consumer jobs
5. **Consider parameter dependencies** - Some parameter combinations may be invalid
