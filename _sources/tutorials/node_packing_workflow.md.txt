(node-packing-workflow)=

# Node-Packing Workflow

In this tutorial you will learn how to create a workflow that is optimized for maintaining a maximum
queue depth of jobs on many compute nodes. This removes the need for users to think deeply about how
many nodes to allocate and how to spread jobs across them.

```{eval-rst}
.. note:: This workflow does not define any dependencies between jobs. It is a simple
   workflow that runs jobs in parallel on compute nodes. Refer to the other tutorials for
   examples with job dependencies.
```

The workflow has 1000 jobs, each with the following requirements:
- 8 CPUs
- 10 GB of memory
- 1 hour of runtime

The actual CLI commands for the jobs are not important for this tutorial. Let's create a file with
dummy commands.

1. Create the commands file.

Ensure that the file is empty.
```console
$ rm -f /tmp/commands.txt
```
```console
$ for i in {1..1000}; do echo "hello world" >> /tmp/commands.txt; done
```

2. Create the workflow from the commands file.
```console
$ torc workflows create-from-commands-file \
    --name my-workflow \
    --description "My workflow" \
    --cpus-per-job=8 \
    --memory-per-job=10g \
    --runtime-per-job=P0DT1H \
    commands.txt
INFO: Created a workflow from /tmp/commands.txt with key=6016359
```

3. Add an HPC scheduler. Change `account` to your HPC account. This configuration is built on the
assumption that the wait time for the short partition (NREL Kestrel HPC has a "short" partition with
a 4 hour walltime limit) is short.
```console
$ torc hpc slurm add-config -a account -w 04:00:00 -N short
```

4. Start the workflow.
```console
$ torc -k 6016359 workflows start
```

5. Ask torc to recommend the number of compute nodes to schedule. (NREL Kestrel HPC compute nodes hav 104 CPUs.)
```console
$ torc -k 6016359 hpc slurm recommend-nodes --num-cpus=104 --memory-gb=240
```
```console
Requirements for jobs in the ready state:
num_jobs=1000 num_cpus=8000 num_gpus=0 memory_gb=10000 max_num_nodes=1 max_runtime='P0DT1H'
  Based on CPUs, number of required nodes = 20
  Based on memory, number of required nodes = 11
  Max job runtime: P0DT1H
  Slurm walltime: 04:00:00
  Jobs per node by duration: 4

After accounting for a max runtime and a limiter based on CPU, torc recommends scheduling 20 nodes.
Please perform a sanity check on this number before scheduling jobs.
The algorithm is most accurate when the jobs have uniform requirements.
```

6. Schedule compute nodes to run the jobs.
```console
$ torc hpc slurm schedule-nodes -n 20
```

7. Monitor progress with torc or squeue.

8. View the results.

```console
$ torc results list
```
