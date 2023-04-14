############################
HPC Compute Node Environment
############################

When configuring your HPC environment for running torc, it's best to start from a clean directory.
Torc will create log files and output directories on every compute node it uses.

Torc will run your jobs in the same environment without changing directories. You can setup your
jobs to write files whereever you'd like, but it is recommended to write those files in the current
directory or a sub-directory.

.. code-block:: console

   $ mkdir work-dir
   $ torc workflows start
   $ torc worklows recommend-nodes -n 36
   $ torc hpc slurm schedule-nodes -n 10
