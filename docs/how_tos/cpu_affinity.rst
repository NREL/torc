.. _set_cpu_affinity:

################
Set CPU Affinity
################
Torc supports the Linux kernel feature of setting CPU affinity for processes. You might want to do
this for reasons described by https://www.gnu.org/software/libc/manual/html_node/CPU-Affinity.html.

It works on Linux as well some other UNIX platforms. It will not work on Windows.

This page describes how to do this for your jobs. There are several caveats to understand:

- It is very possible that using this feature will produce slower results. The Linux scheduler may
  do a better job on its own.
- You should only do this if you are confident that your applications will benefit from it. Be
  sure to consider how libraries used by your code will be affected. Test the performance to
  confirm.
- This feature is only intended to be used on a compute node that will run jobs with identical
  CPU requirements.

When you schedule or run jobs with the commands below, set ``--cpu-affinity-cpus-per-job``.

Suppose a set of jobs needs 4 CPUs each and the compute node has 36 CPUs.

.. code-block:: console

    $ torc hpc slurm schedule-nodes --cpu-affinity-cpus-per-job 4
    $ torc jobs run --cpu-affinity-cpus-per-job 4

The torc worker application on the compute node will create 9 CPU masks. Each time it starts a job
it will pick an available mask as set the job's process affinity to an available mask with the
system call ``sched_setaffinity``. Torc will keep 9 jobs running in parallel until all complete.
