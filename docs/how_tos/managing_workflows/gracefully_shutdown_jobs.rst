.. _job-graceful-shutdown:

Gracefully shutdown jobs
========================
A common error condition in HPC environments is underestimating the walltime for a job. The HPC
scheduler will kill the job. If you don't take precautions, you will lose the work and have to
start from the beginning.

Similar to Slurm, Torc offers one procedure to help with this problem: the
``supports_termination`` flag in the job defintion. If this is set to true then torc will send the
signal ``SIGTERM`` to each job process. If your job registers a signal handler for that signal, you
can gracefully shutdown such that a subsequent process can resume where it left off.

Don't set this flag if your job doesn't catch ``SIGTERM``. Torc will attempt to wait for the
process exit and capture its return code.

Torc performs these actions two minutes before the walltime timeout. That value can be customized
by setting the ``compute_node_worker_buffer_seconds`` field in the ``config`` section of a workflow
specification file.

Refer to this script for a Python example of detecting this signal:
https://github.nrel.gov/viz/wms/blob/main/torc_package/tests/scripts/sleep.py

.. note:: The torc worker application on compute nodes handles ``SIGTERM``. If you configure Slurm
   to terminate jobs at earlier time than the torc two-minute buffer, torc will respect it.
