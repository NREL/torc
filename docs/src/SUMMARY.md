# Summary

[Introduction](./introduction.md)

# User Guide

- [Getting Started](./getting-started.md)
  - [Installation](./installation.md)
  - [Quick Start](./quick-start.md)

# Understanding Torc

- [Explanation](./explanation/README.md)
  - [Architecture Overview](./explanation/architecture.md)
  - [Client](./explanation/client.md)
  - [Job Runners](./explanation/job-runners.md)
  - [Job State Transitions](./explanation/job-states.md)
  - [Environment Variables](./explanation/environment-variables.md)
  - [Workflow Reinitialization](./explanation/reinitialization.md)
  - [Workflow Archiving](./explanation/archiving.md)
  - [Dependency Resolution](./explanation/dependencies.md)
  - [Parallelization Strategies](./explanation/parallelization.md)
  - [Workflow Actions](./explanation/workflow-actions.md)
  - [Design](./explanation/design/README.md)
    - [Server API Handler](./explanation/design/server.md)
    - [Central Database](./explanation/design/database.md)
    - [Ready Queue](./explanation/design/ready-queue.md)

# How-To Guides

- [How-To](./how-to/README.md)
  - [Creating Workflows](./how-to/creating-workflows.md)
  - [Working with Slurm](./how-to/slurm.md)
  - [Managing Resources](./how-to/resources.md)
  - [Resource Monitoring](./how-to/resource-monitoring.md)
  - [Web Dashboard](./how-to/dashboard.md)
  - [Debugging Workflows](./how-to/debugging.md)
  - [Authentication](./how-to/authentication.md)
  - [Shell Completions](./how-to/shell-completions.md)
  - [Server Deployment](./how-to/server-deployment.md)
  - [Torc Server Arguments in Workflow Actions](./how-to/torc-server-args.md)

# Reference

- [Reference](./reference/README.md)
  - [Workflow Specification Formats](./reference/workflow-formats.md)
  - [Job Parameterization](./reference/parameterization.md)
  - [OpenAPI Specification](./reference/openapi.md)
  - [Configuration](./reference/configuration.md)
  - [Security](./reference/security.md)

# Tutorials

- [Tutorials](./tutorials/README.md)
  - [Many Independent Jobs](./tutorials/many-jobs.md)
  - [Diamond Workflow](./tutorials/diamond.md)
  - [User Data Dependencies](./tutorials/user-data.md)
  - [Simple Parameterization](./tutorials/simple-params.md)
  - [Advanced Parameterization](./tutorials/advanced-params.md)
  - [Multi-Stage Workflows with Barriers](./tutorials/multi-stage-barrier.md)
  - [Map Python functions across workers](./tutorials/map_python_function_across_workers.md)

---

[Contributing](./contributing.md)
