######################
Slurm Hardware Control
######################
Slurm provides advanced hardware control features that are not available in the default Torc
workflow. This page describes how you can use those features and still benefit from Torc's
management features.

The summary is that you need to schedule torc worker processes with your own ``sbatch`` scripts
that define your desired Slurm directives. Jobs started by those worker processes will inherit the
Slurm-defined settings.

Slurm CPU management
====================
You may want to use `Slurm's CPU management features <https://slurm.schedmd.com/mc_support.html>`_.

Let's suppose that a compute node has two sockets, 18 cores each, and that each job will consume
18 cores.

This example starts two torc worker processes through Slurm. ``srun`` binds each worker
process to cores on different sockets. Each job process run by a worker inherits that worker's
binding.

.. note:: You must swap ``<url>`` and ``<workflow-key>`` with your actual values below. If you
   added them to your ``~/.torc.json5`` file, you can delete the ``-u`` and ``-k`` options.

.. code-block:: shell

    #!/bin/bash
    #SBATCH --account=my_account
    #SBATCH --job-name=my_job
    #SBATCH --time=04:00:00
    #SBATCH --output=output/job_output_%j.o
    #SBATCH --error=output/job_output_%j.e
    #SBATCH --nodes=1

    srun -c18 -n2 --cpu-bind=mask_cpu:0x3ffff,0xffffc0000 \
        torc -u <url> -k <workflow-key> hpc slurm run-jobs -o output --is-subtask --max-parallel-jobs=1

Key points:

- Tell Slurm how many CPUs (``-c``) to give to each torc worker (and user job) and how many
  torc workers to start (``-n``).
- Tell torc that the worker is a subtask.
- Tell torc that each worker should only run one job at a time.

For more ``srun --cpu-bind`` options, refer to its man page (``man srun`` or ``pinfo srun``).

Resource monitoring
-------------------
Torc will not monitor overall node resource utilization if ``--is-subtask`` is ``true``. You can
still enable per-job process monitoring. However, be aware that torc will start one monitoring
subprocess for each worker process.
