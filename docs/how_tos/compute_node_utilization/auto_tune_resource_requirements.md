# Auto-Tune Resource Requirements

In cases where you have many jobs and are uncertain of their resource requirements, you can use
torc's auto-tune feature.

The general concept is this:

- Create one resource requirements definition for each class of job; let's call them small,
  medium, and large. Make a guess about their requirements.
- Run one job of each type.
- Inspect the actual resource utilization.
- Update the resource requirements definitions in the database.
- Run all jobs.

Here is the step-by-step process.

1. Create the resource requirement definitions in the workflow specification file. Be conservative
   with initial values. You don't want the jobs to fail with walltime timeouts or out-of-memory
   errors.

```JavaScript
resource_requirements: [
    {
      name: "small",
      num_cpus: 1,
      num_gpus: 0,
      num_nodes: 1,
      memory: "10g",
      runtime: "P0DT30M"
    },
    {
      name: "medium",
      num_cpus: 4,
      num_gpus: 0,
      num_nodes: 1,
      memory: "20g",
      runtime: "P0DT1H"
    },
    {
      name: "medium",
      num_cpus: 8,
      num_gpus: 0,
      num_nodes: 1,
      memory: "40g",
      runtime: "P0DT6H"
    },
],
```

2. Specify a `resource_requirements` name for each job. You may or may not need to create a
   different scheduler for each job type. This example assumes a different scheduler is required in
   order to account for different walltimes.

```JavaScript
jobs: [
  {
    name: "work1",
    command: "python work.py 1",
    resource_requirements: "small",
    scheduler: "slurm_schedulers/small",
  },
  {
    name: "work2",
    command: "python work.py 2",
    resource_requirements: "small",
    scheduler: "slurm_schedulers/small",
  },
  {
    name: "work3",
    command: "python work.py 3",
    resource_requirements: "medium",
    scheduler: "slurm_schedulers/medium",
  },
  {
    name: "work4",
    command: "python work.py 4",
    resource_requirements: "medium",
    scheduler: "slurm_schedulers/medium",
  },
  {
    name: "work5",
    command: "python work.py 5",
    resource_requirements: "large",
    scheduler: "slurm_schedulers/large",
  },
  {
    name: "work6",
    command: "python work.py 6",
    resource_requirements: "large",
    scheduler: "slurm_schedulers/large",
  },
]
```

3. Start the workflow with the `--auto-tune-resource-requirements` option.

```console
$ torc workflows start -a
```

4. Schedule one node for each resource requirements type. First, identify the scheduler keys.

```console
$ torc hpc slurm list-configs

+-------------------------------------------------------------------------------------------------------------------------------------------+
|                                                 Slurm configurations in workflow 95612117                                                 |
+-------+--------+------------+------+------+-------+-----------+--------+------+----------+----------+-------------------------------------+
| index |  name  |  account   | gres | mem  | nodes | partition |  qos   | tmp  | walltime |   key    |                  id                 |
+-------+--------+------------+------+------+-------+-----------+--------+------+----------+----------+-------------------------------------+
|   0   | small  | my_account | None | None |   1   |    None   | normal | None | 00:30:00 | 95614387 | slurm_schedulers__95612117/95614387 |
|   1   | medium | my_account | None | None |   1   |    None   | normal | None | 01:00:00 | 95614398 | slurm_schedulers__95612117/95614398 |
|   2   | large  | my_account | None | None |   1   |    None   | normal | None | 06:00:00 | 95614405 | slurm_schedulers__95612117/95614405 |
+-------+--------+------------+------+------+-------+-----------+--------+------+----------+----------+-------------------------------------+
```

```console
$ torc hpc slurm schedule-nodes -n 1 -s 95614387
$ torc hpc slurm schedule-nodes -n 1 -s 95614398
$ torc hpc slurm schedule-nodes -n 1 -s 95614405
```

5. Wait for all jobs to finish.
6. Run this command to process the results and update the database.

```console
$ torc workflows process-auto-tune-resource-requirements-results

2023-04-14 12:23:09,222 - INFO [torc.cli.workflows workflows.py:355] : Updated resource requirements. Look at current requirements with
  'torc -k 95612117 -u http://localhost:8529/_db/test-workflows/torc-service resource-requirements list'
 and at changes by reading the events with
  'torc -k 95612117 -u http://localhost:8529/_db/test-workflows/torc-service events list -f category=resource_requirements'
```

7. Note the output above. You can use the suggested commands to view what torc changed. You make
   more changes if you'd like. Refer to the command `torc hpc slurm modify-config`.
8. Schedule more nodes for each set of requirements. You will likely need many more nodes this time.
   Use the `recommend` command to help estimate the number of nodes.

```console
$ torc hpc slurm recommend-nodes -s 95614387
$ torc hpc slurm recommend-nodes -s 95614398
$ torc hpc slurm recommend-nodes -s 95614405
```

Use the output above to assign numbers for X, Y, and Z below.

```console
$ torc hpc slurm schedule-nodes -n X -s 95614387
$ torc hpc slurm schedule-nodes -n Y -s 95614398
$ torc hpc slurm schedule-nodes -n Z -s 95614405
```
