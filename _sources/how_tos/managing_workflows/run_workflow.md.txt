# Run a workflow

This is an HPC example that schedules one node to do the work.

```{eval-rst}
.. note:: The paths to all relevant scripts need to correct based on your current directory.
```

```console
$ torc workflows create-from-json-file examples/independent_workflow.json5
2023-03-28 16:36:35,149 - INFO [torc.cli.workflows workflows.py:156] : Created a workflow from examples/independent_workflow.json5 with key=92238688
```

This command will identify relationships between workflow objects and initialize the job status.

```console
$ torc workflows start
2023-03-28 16:37:58,708 - INFO [torc.workflow_manager workflow_manager.py:99] : Started workflow
```

This command asks the database to give a recommendation on how many compute nodes should be
scheduled given that each node has 104 CPUs.

```console
$ torc hpc slurm recommend-nodes -n 104
Requirements for jobs in the ready state:
{'max_num_nodes': 1,
 'max_runtime': 'P0DT12H',
 'memory_gb': 25.0,
 'num_cpus': 13,
 'num_gpus': 0,
 'num_jobs': 3}
Based on CPUs, number of required nodes = 1
```

This command schedules one compute node.

```console
$ torc hpc slurm schedule-nodes -n1
```
