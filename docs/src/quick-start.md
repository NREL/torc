# Quick Start

Choose the guide that matches your environment:

## [Quick Start (HPC)](./quick-start-hpc.md)

**For HPC clusters with Slurm** — Run workflows on compute nodes via Slurm.

- Start server on login node
- Define jobs with resource requirements (CPU, memory, runtime)
- Submit with `torc submit-slurm --account <account> workflow.yaml`
- Jobs run on compute nodes

## [Quick Start (Local)](./quick-start-local.md)

**For local execution** — Run workflows on the current machine.

- Ideal for testing, development, or non-HPC environments
- Start server locally
- Run with `torc run workflow.yaml`
- Jobs run on the current machine
