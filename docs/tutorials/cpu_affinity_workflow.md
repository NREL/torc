# CPU Affinity Workflow

In this tutorial you will learn how to set CPU affinity for all job processes. Refer to
{ref}`set_cpu_affinity` for more information about this feature.

The workflow must be run on an HPC with the Slurm scheduler. The steps are similar to the
{ref}`slurm-diamond-workflow` except that you must set the additional parameter below when you
schedule nodes. The job script in this example assumes 9 CPUs per job.

Use the workflow specification file `examples/slurm_cpu_affinity_workflow.json5`.

```console
$ torc hpc slurm schedule-nodes -n 1 --cpu-affinity-cpus-per-job 9
```
