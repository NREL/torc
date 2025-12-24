# Introduction

**Torc** is a distributed workflow orchestration system for managing computational pipelines ranging
from simple workflows needing to parallelize independent jobs to complex workflows with job
dependencies, mixed resource requirements, and multiple stages, compute node scheduling.

## Ways to Use Torc

Torc offers multiple interfaces to match your preferred workflow:

| Interface | Best For | Example |
|-----------|----------|---------|
| **Dashboard** | Visual monitoring, team collaboration | Point-and-click in browser |
| **AI Assistants** | Natural language interaction, debugging, quick tasks | *"Create a workflow with 10 parallel jobs"* |
| **CLI** | Scripting, automation, power users | `torc run workflow.yaml` |
| **Spec Files** | Version control, reproducibility, complex workflows | YAML, KDL, or JSON5 files |
| **Python/Julia** | Programmatic workflow generation | API libraries |

You can mix these freely—create a workflow with AI, monitor it in the dashboard, and script restarts with the CLI.

## Key Features

Torc provides:

- **AI-Assisted Management** — Use Claude Code or GitHub Copilot to create, debug, and manage workflows through conversation
- **Declarative Workflow Definitions** — Define workflows in YAML, JSON, JSON5, or KDL
- **Automatic Dependency Resolution** — Dependencies inferred from file and data relationships
- **Distributed Execution** — Run jobs across local machines and HPC clusters
- **Resource Management** — Track CPU, memory, and GPU usage across all jobs
- **Automatic Failure Recovery** — Detect OOM/timeout failures and retry with adjusted resources
- **Fault Tolerance** — Resume workflows after failures without losing progress

## Who Should Use Torc?

Torc is designed for:

- **HPC Users** who need to parallelize jobs across cluster resources
- **Computational Scientists** running parameter sweeps and simulations
- **Data Engineers** building complex data processing pipelines
- **ML/AI Researchers** managing training workflows and hyperparameter searches
- **Anyone** who needs reliable, resumable workflow orchestration

## Key Features

### Job Parameterization

Create parameter sweeps with simple syntax:

```yaml
jobs:
  - name: job_{index}
    command: bash work.sh {index}
    parameters:
      index: "1:100"
```

This expands to 100 jobs.

### Implicit Dependencies

Dependencies between jobs are automatically inferred based on file dependencies.

```yaml
name: my_workflow
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

### Slurm Integration

Native support for HPC clusters:

```yaml
slurm_schedulers:
  - name: big memory nodes
    partition: bigmem
    account: myproject
    walltime: 04:00:00
    num_nodes: 5
```

## Documentation Structure

This documentation is divided into these sections:

- **[Tutorials](./tutorials/README.md)** - Step-by-step lessons to learn Torc
- **[How-To Guides](./how-to/README.md)** - Practical guides for specific tasks
- **[Explanation](./explanation/README.md)** - In-depth discussion of concepts
- **[Reference](./reference/README.md)** - Technical specifications and API docs

## Next Steps

- **New to Torc?** Start with [Getting Started](./getting-started.md)
- **Prefer AI assistance?** See [AI-Assisted Workflow Management](./tutorials/ai-assistant.md)
- **Want to understand how it works?** Read the [Architecture Overview](./explanation/architecture.md)
- **Ready to create workflows?** Jump to [Creating Workflows](./how-to/creating-workflows.md)
- **Need specific examples?** Check out the [Tutorials](./tutorials/README.md)
