# Quick Start

Choose the approach that matches your environment and preference:

## [Quick Start (AI-Assisted)](./tutorials/ai-assistant.md)

**For conversational workflow management** — Use Claude Code or GitHub Copilot.

- Natural language: _"Create a workflow with 10 parallel jobs"_
- Debug failures: _"Why did job 5 fail? Show me the logs"_
- Works with both local and HPC execution
- Ideal for interactive exploration and debugging

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

---

**Not sure which to choose?**

- New to Torc? Start with **AI-Assisted** for guided exploration
- On an HPC cluster? Use **HPC** for production workloads
- Testing locally? Use **Local** for quick iteration
