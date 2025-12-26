# Dependency Resolution

Torc supports two types of dependencies. For a hands-on tutorial, see
[Diamond Workflow with File Dependencies](../tutorials/diamond.md).

## 1. Explicit Dependencies

Declared via `depends_on`:

```yaml
jobs:
  - name: preprocess
    command: preprocess.sh
  - name: analyze
    command: analyze.sh
    depends_on:
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

User scripts ingest JSON data into Torc's database. This is analagous to JSON files except that they
are stored in the database AND user code must understand Torc's API.

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
2. Stores explicit dependencies in `job_depends_on`
3. Stores file/user_data relationships in junction tables
4. During `initialize_jobs`, queries junction tables to add implicit dependencies

## Dependency Graph Evaluation

When `initialize` is called:

1. All jobs start in `uninitialized` state
2. Server builds complete dependency graph from explicit and implicit dependencies
3. Jobs with no unsatisfied dependencies are marked `ready`
4. Jobs waiting on dependencies are marked `blocked`
5. As jobs complete, blocked jobs are re-evaluated and may become `ready`

## Variable Substitution Syntax

In workflow specification files (YAML, JSON5, KDL), use these patterns to reference files and user
data in job commands:

| Pattern                    | Description                                            |
| -------------------------- | ------------------------------------------------------ |
| `${files.input.NAME}`      | File path this job reads (creates implicit dependency) |
| `${files.output.NAME}`     | File path this job writes (satisfies dependencies)     |
| `${user_data.input.NAME}`  | User data this job reads                               |
| `${user_data.output.NAME}` | User data this job writes                              |

Example:

```yaml
jobs:
  - name: process
    command: "python process.py -i ${files.input.raw} -o ${files.output.result}"
```

See [Workflow Specification Formats](../reference/workflow-formats.md) for complete syntax details.
