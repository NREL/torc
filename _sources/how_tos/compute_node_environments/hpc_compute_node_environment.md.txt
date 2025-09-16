# HPC Compute Node Environment

When configuring your HPC environment for running torc, it's best to start from a clean directory
on the shared filesystem. Torc will create log files and output directories on every compute node
it uses.

Torc will run your jobs in the same environment without changing directories. You can setup your
jobs to write files wherever you'd like, but it is recommended to write those files in the current
directory or a sub-directory.

```console
$ mkdir work-dir && cd work-dir
$ torc workflows start
$ torc hpc slurm recommend-nodes -n 36
$ torc hpc slurm schedule-nodes -n 10
```

## Slurm Configuration

Torc natively supports the Slurm parameters below. You can set these in the `slurm_schedulers`
section of your workflow specification file or in the `torc hpc slurm add-config` command.

- name
- account
- gres
- mem
- nodes
- partition
- qos
- tmp
- walltime

If you want to set addtional parameters not natively supported by torc, define the `extra` field
in the specification file or CLI command. Torc will forward those parameters to `sbatch`. For
example:

```JavaScript
schedulers: {
  slurm_schedulers: [
    {
      name: "my-config",
      account: "my-account",
      nodes: 1,
      partition: "debug",
      walltime: "01:00:00",
      extra: "--reservation=my-reservation",
    },
  ],
},
```

```console
$ torc hpc slurm add-config -a my-account -N my-config --extra="--reservation=my-reservation"
```
