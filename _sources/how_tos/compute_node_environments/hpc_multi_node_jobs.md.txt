# HPC Multi-Node Jobs

There are two ways to use HPC multi-node jobs with torc:

1. Torc starts a worker application on the first node and starts user jobs. Each user job controls
   the rest of the compute nodes. This is default behavior.
2. Torc starts a worker application on each compute node and each application pulls jobs from the
   database and runs them.

Here's how to run multi-node jobs for both paradigms:

Set the `nodes` parameter in your Slurm configuration in your workflow specification file.

```JavaScript
schedulers: {
  slurm_schedulers: [
    {
      name: "multi-node",
      account: "my_account",
      walltime: "48:00:00",
      nodes: 5,
    }
  ],
},
```

## One torc worker application

Develop your job script to be the manager of the overall effort. Torc will start it on the first
compute node in the allocation. Your script should then detect the other compute nodes and
distribute the work.

You can run Slurm commands to find the hostnames or make a torc API call. The Slurm commmands
are:

```console
$ scontrol show hostnames "$(squeue -j ${SLURM_JOB_ID} --format='%500N' -h)"
```

The torc API command is like this:

```python
from torc.hpc.slurm_interface import SlurmInterface

intf = SlurmInterface()
job_id = intf.get_current_job_id(job_id)
nodes = intf.list_active_nodes(job_id)
```

Schedule compute nodes with default options.

```console
$ torc hpc slurm schedule-nodes --num-hpc-jobs 1
```

## One torc worker application for each compute node

This paradigm is very similar to the default torc configuration where the user schedules some
number of single-node jobs to complete the workflow. The difference is that in this paradigm all
compute nodes will be allocated at the exact same time. This might be advantageous two reasons:

1. The user jobs need to communicate with each other or with some common resource.

2. There is a scheduling advantage to requesting multiple nodes at once. Some HPCs, including those
   at NREL, give a priority to larger jobs. If you need five compute nodes to complete your work,
   you *might* acquire and complete jobs on five nodes more quickly if you request a five-node job.
   This almost certainly breaks down at some point. It might take a very long time to acquire one
   thousand compute nodes. You're likely better off requesting one thousand invididual nodes and
   make incremental progress as nodes become available.

   Note that there is a potential cost to the multi-node approach. All compute nodes will stay
   active until all nodes finish their last job. If your jobs take a long time and are variable,
   you could get charged for many hours of compute time even though some nodes were idle.

```{eval-rst}
.. note:: The automatic-compute-node-rescheduling feature does not yet support this paradigm.
   Please contact the developers if you need that.
```

Schedule compute nodes with this extra option.

```console
$ torc hpc slurm schedule-nodes --num-hpc-jobs 1 --start-one-worker-per-node
```
