# Quick Start

This guide will walk you through creating and running your first Torc workflows. These examples
rely on local execution. Refer to the Tutorials for HPC examples.

## Start the server
This will create a torc database in the current directory if it doesn't exist.
Setting `--completion-check-interval-secs` (or `-c`) will ensure that the server processes job completions quickly.
This should not be set on a shared server.

```console
torc-server run --database torc.db --completion-check-interval-secs 5
```

## Test the client connection
```console
torc workflows list
```

## Create a Workflow Specification

Torc supports YAML, JSON5, and KDL formats. Save as `workflow.yaml`:

```yaml
name: hello_world
description: Simple hello world workflow

jobs:
  - name: job 1
    command: echo "Hello from torc!"
  - name: job 2
    command: echo "Hello again from torc!"
```

> **Note:** Torc also accepts `.json5` and `.kdl` workflow specifications. See the [Workflow Specification Formats](./reference/workflow-formats.md) reference for details on all supported formats.

## Run Jobs
Run the jobs on the current computer. Use a short poll interval for demo purposes.
This will automatically initialize the jobs if you skipped that step.

```console
torc run --poll-interval 1
```

## View Results

```console
# View job results
torc results list
```

# Or use the TUI to view the results in table.
```console
torc-tui
```

## Example: Diamond Workflow

A workflow with fan-out and fan-in dependencies. You can find this example in the repository:
- [diamond_workflow.yaml](https://github.com/NREL/torc/blob/main/examples/yaml/diamond_workflow.yaml)
- [diamond_workflow.json5](https://github.com/NREL/torc/blob/main/examples/json/diamond_workflow.json5)
- [diamond_workflow.kdl](https://github.com/NREL/torc/blob/main/examples/kdl/diamond_workflow.kdl)

```yaml
name: diamond_workflow
description: Example workflow with implicit dependencies

jobs:
  - name: preprocess
    command: "bash tests/scripts/preprocess.sh -i ${files.input.f1} -o ${files.output.f2} -o ${files.output.f3}"

  - name: work1
    command: "bash tests/scripts/work.sh -i ${files.input.f2} -o ${files.output.f4}"

  - name: work2
    command: "bash tests/scripts/work.sh -i ${files.input.f3} -o ${files.output.f5}"

  - name: postprocess
    command: "bash tests/scripts/postprocess.sh -i ${files.input.f4} -i ${files.input.f5} -o ${files.output.f6}"

# File definitions - representing the data files in the workflow
files:
  - name: f1
    path: f1.json
  - name: f2
    path: f2.json
  - name: f3
    path: f3.json
  - name: f4
    path: f4.json
  - name: f5
    path: f5.json
  - name: f6
    path: f6.json
```

Dependencies are automatically inferred:
- `work1` and `work2` wait for `preprocess` (depend on its output files)
- `postprocess` waits for both `work1` and `work2` to complete

## More Examples

The [examples directory](https://github.com/NREL/torc/tree/main/examples) contains many more workflow examples in all supported formats:
- Simple workflows and resource monitoring
- Workflow actions for automation
- Slurm integration examples
- Parameterized workflows

Browse [examples/yaml](https://github.com/NREL/torc/tree/main/examples/yaml), [examples/json](https://github.com/NREL/torc/tree/main/examples/json), or [examples/kdl](https://github.com/NREL/torc/tree/main/examples/kdl) to explore the full collection.
