(job-graceful-shutdown)=

# Gracefully shutdown jobs

A common error condition in HPC environments is underestimating the walltime for a job. The HPC
scheduler will kill the job. If you don't take precautions, you will lose the work and have to
start from the beginning.

Similar to Slurm, Torc offers one procedure to help with this problem: the
`supports_termination` flag in the job defintion.

In all cases Torc will send the `SIGTERM` to all running job processes 30 seconds before the
allocation expiration time (configurable via the `compute_node_expiration_buffer_seconds` field
in the `config` section of the workflow specification).

By default Torc will set the job status and return code to `terminated`. If
`supports_termination` is `true` then torc will wait for the processes to complete and then set
the return code to whatever the process returns.

You can leverage this feature to resume interrupted work by doing the following:

- Register a signal handler for `SIGTERM` in your application.
- In that hander, cause your code to save the current state and gracefully shut down. Return an
  appropriate exit code and record files such that a new instance of your application can resume
  from where it left off.
- Set `supports_termination=true` on each job.
- Set `compute_node_expiration_buffer_seconds` to the amount of time your application will need
  to gracefully shut down.

If this is set to true then torc will send the
signal `SIGTERM` to each job process. If your job registers a signal handler for that signal, you
can gracefully shutdown such that a subsequent process can resume where it left off.

Refer to this script for a Python example of handling `SIGTERM`:
<https://github.com/NREL/torc/blob/main/torc_package/tests/scripts/sleep.py>

```{eval-rst}
.. note:: The torc worker application on compute nodes handles ``SIGTERM``. If you configure Slurm
   to terminate jobs at an earlier time than the torc setting, torc will respect it.
```
