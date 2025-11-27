# Dependency Resolution

Torc supports two types of dependencies:

## 1. Explicit Dependencies

Declared via `blocked_by`:

```yaml
jobs:
  - name: preprocess
    command: preprocess.sh
  - name: analyze
    command: analyze.sh
    blocked_by:
      - preprocess
```

## 2. Implicit Dependencies

Inferred from file and user_data relationships.

### File Dependencies

```yaml
jobs:
  - name: preprocess
    command: process.sh
    output_files:
      - intermediate_data

  - name: analyze
    command: analyze.sh
    input_files:
      - intermediate_data  # Implicitly depends on preprocess
```

### User Data Dependencies
User scripts ingest JSON data into Torc's database. This is analagous to JSON files except that
they are stored in the database AND user code must understand Torc's API.

```yaml
jobs:
  - name: generate_config
    command: make_config.py
    output_user_data:
      - config

  - name: run_simulation
    command: simulate.py
    input_user_data:
      - config  # Implicitly depends on generate_config
      
user_data:
  - name: config
```

## Resolution Process

During workflow creation, the server:
1. Resolves all names to IDs
2. Stores explicit dependencies in `job_blocked_by`
3. Stores file/user_data relationships in junction tables
4. During `initialize_jobs`, queries junction tables to add implicit dependencies

## Dependency Graph Evaluation

When `initialize` is called:
1. All jobs start in `uninitialized` state
2. Server builds complete dependency graph from explicit and implicit dependencies
3. Jobs with no unsatisfied dependencies are marked `ready`
4. Jobs waiting on dependencies are marked `blocked`
5. As jobs complete, blocked jobs are re-evaluated and may become `ready`
