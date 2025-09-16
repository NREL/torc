% torc documentation master file, created by
% sphinx-quickstart on Sat Feb 11 11:41:31 2023.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Torc User Guide

The torc workflow management system orchestrates the execution of jobs on distributed computing
resources, including HPC and cloud environments.

Torc provides these features:

- Manage dependencies between jobs and resources.
- Support workflow restarts, accounting for job failures, compute node timeouts, and program and
  data file files.
- Persistent store for user input and output data.
- Track resource utilization.
- Auto-tune resource requirements.

# How to use this guide

- Refer to {ref}`overview` for an illustration of torc's capabilities.
- Refer to {ref}`how-tos` for step-by-step instructions for installation and running workflows.
- Refer to {ref}`tutorials` for examples of building workflows with torc.
- Refer to {ref}`reference` for CLI and API documentation.
- Refer to {ref}`explanation` for descriptions of how torc works and what a user will observe when
  using it.

```{toctree}
:hidden: true
:maxdepth: 4

overview
how_tos/index
tutorials/index
reference/index
explanation/index
```

# Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
