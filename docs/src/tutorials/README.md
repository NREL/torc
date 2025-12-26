# Tutorials

This section contains learning-oriented lessons to help you get started with Torc. Each tutorial
walks through a complete example from start to finish.

**Tutorials:**

1. [Configuration Files](./configuration.md) - Set up configuration files for Torc components
2. [Dashboard Deployment](./dashboard-deployment.md) - Deploy torc-dash for local, shared, or HPC
   environments
3. [Workflow Wizard](./workflow-wizard.md) - Create workflows using the dashboard's interactive
   wizard
4. [Many Independent Jobs](./many-jobs.md) - Create a workflow with 100 parallel jobs
5. [Diamond Workflow](./diamond.md) - Fan-out and fan-in with file dependencies
6. [User Data Dependencies](./user-data.md) - Pass JSON data between jobs
7. [Simple Parameterization](./simple-params.md) - Single parameter dimension sweep
8. [Advanced Parameterization](./advanced-params.md) - Multi-dimensional hyperparameter grid search
9. [Multi-Stage Workflows with Barriers](./multi-stage-barrier.md) - Scale to thousands of jobs
   efficiently
10. [Map Python Functions](./map_python_function_across_workers.md) - Distribute Python functions
    across workers
11. [Filtering CLI Output with Nushell](./filtering-with-nushell.md) - Filter jobs, results, and
    user data with readable queries
12. [Custom HPC Profile](./custom-hpc-profile.md) - Create an HPC profile for unsupported clusters
13. [MCP Server with Claude Code](./mcp-server.md) - Enable Claude to interact with your workflows
14. [Automatic Failure Recovery](./automatic-recovery.md) - Autonomous workflow monitoring with
    `torc watch`

Start with the Configuration Files tutorial to set up your environment, then try the Dashboard
Deployment tutorial if you want to use the web interface.

## Example Files

The repository includes ready-to-run example workflow specifications in YAML, JSON5, and KDL
formats. These complement the tutorials and demonstrate additional patterns:

| Example                                                                                                                       | Description                            | Tutorial                                |
| ----------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- | --------------------------------------- |
| [diamond_workflow.yaml](https://github.com/NREL/torc/blob/main/examples/yaml/diamond_workflow.yaml)                           | Fan-out/fan-in pattern                 | [Diamond Workflow](./diamond.md)        |
| [hundred_jobs_parameterized.yaml](https://github.com/NREL/torc/blob/main/examples/yaml/hundred_jobs_parameterized.yaml)       | 100 parallel jobs via parameterization | [Many Jobs](./many-jobs.md)             |
| [hyperparameter_sweep.yaml](https://github.com/NREL/torc/blob/main/examples/yaml/hyperparameter_sweep.yaml)                   | ML grid search (3×3×2 = 18 jobs)       | [Advanced Params](./advanced-params.md) |
| [multi_stage_barrier_pattern.yaml](https://github.com/NREL/torc/blob/main/examples/yaml/multi_stage_barrier_pattern.yaml)     | Efficient multi-stage workflow         | [Barriers](./multi-stage-barrier.md)    |
| [resource_monitoring_demo.yaml](https://github.com/NREL/torc/blob/main/examples/yaml/resource_monitoring_demo.yaml)           | CPU/memory tracking                    | —                                       |
| [workflow_actions_simple_slurm.yaml](https://github.com/NREL/torc/blob/main/examples/yaml/workflow_actions_simple_slurm.yaml) | Automated Slurm scheduling             | —                                       |

**Browse all examples:**

- [YAML examples](https://github.com/NREL/torc/tree/main/examples/yaml)
- [JSON5 examples](https://github.com/NREL/torc/tree/main/examples/json)
- [KDL examples](https://github.com/NREL/torc/tree/main/examples/kdl)
- [Python examples](https://github.com/NREL/torc/tree/main/examples/python)

See the [examples README](https://github.com/NREL/torc/tree/main/examples) for the complete list and
usage instructions.
