# Quick Start

This guide will walk you through creating and running your first Torc workflows. These examples
rely on local execution. Refer to the Tutorials for HPC examples.

## Start the server
This will create a torc database in the current directory if it doesn't exist.

```console
torc-server --database torc.db
```

## Test the client connection
```console
torc workflows list
```

## Create a Workflow Specification

Save as `workflow.yaml`:

```yaml
name: hello_world
description: Simple hello world workflow

jobs:
  - name: job 1
    command: echo "Hello from torc!"
  - name: job 2
    command: echo "Hello again from torc!"
```

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

A workflow with fan-out and fan-in dependencies:

```yaml
name: diamon_workflow
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
