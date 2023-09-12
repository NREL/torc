#########
Debugging
#########

Log files
=========
Torc configures logging for its own code as well as the compute node scheduler (such as Slurm).
The base directory of output files is controlled by the directory specified in these commands:

.. code-block:: console

   $ torc hpc slurm schedule-nodes
   $ torc jobs run

The default directory is ``./output`` but you can provide a custom directory with ``-o
<your-directory>``.

Compute node log files
----------------------
There are three sets of log files for each compute node allocation:

- Compute node scheduler stderr/stdout (such as Slurm srun messages)
- Torc job runner messages. Includes messages about running each job.
- Output for each job. Torc logs the stderr/stdout for each job in unique log files.

Here are example log files for a job runner in a Slurm compute environment::

    ./output/job_output_12230487_0.e
    ./output/job_output_12230487_0.o
    ./output/job_runner_slurm_12230487.log
    ./output/job-stdio/slurm_12230487_1208438_1.e
    ./output/job-stdio/slurm_12230487_1208438_1.o

- ``12230487`` is the Slurm job ID
- ``0`` is the Slurm node ID. This matters if there are multiple nodes in the Slurm allocation
  running jobs concurrently.
- ``1208438`` is the torc job key.
- ``1`` is the workflow run ID. This increases every time you restart the workflow.

.. note:: If you restart a workflow with the same output directory, these files will accumulate.
   Torc does not delete or overwrite them.

Results report
--------------
Run this command to see the log files above associated with each job. Refer to ``--help`` to see
how to limit the output to specific run IDs or job keys.

.. code-block:: console

    $ torc reports results

    {
      "workflow": {
        "name": "demo",
        "user": "dthom",
        "description": "Demo workflow.",
        "timestamp": "2023-09-11T17:46:09.404Z",
        "key": "27816293",
        "id": "workflows/27816293",
        "rev": "_gmTXxFu---"
      },
      "jobs": [
        {
          "name": "job1",
          "key": "27816420",
          "runs": [
            {
              "run_id": 1,
              "return_code": 0,
              "status": "done",
              "completion_time": "2023-09-11 11:49:54.542138",
              "exec_time_minutes": 3.056766168276469,
              "job_runner_log_file": "output/job_runner_slurm_13259924_0_97525.log",
              "slurm_stdio_files": [
                "output/job_output_13259924.e",
                "output/job_output_13259924.o"
              ],
              "job_stdio_files": [
                "output/job-stdio/slurm_13259924_0_97525_27816420_1.e",
                "output/job-stdio/slurm_13259924_0_97525_27816420_1.o"
              ]
            },
        }
      ]
    }

Slurm error messages
====================
Common Slurm error messages include these strings:

- ``srun``
- ``slurmstepd``
- ``DUE TO TIME LIMIT``

Useful grep commands
--------------------

.. code-block:: console

    $ grep -n "srun\|slurmstepd\|DUE TO TIME LIMIT" output/*.e


Common Problems
===============

Compute nodes exit without pulling jobs
---------------------------------------
You scheduled a compute node to run jobs but it exits without running any jobs.

Possible reason: the job requirements are misconfigured. The job resource requirements need to
match the compute node scheduled to run the job. This includes runtime, CPUs, and memory. The torc
job runner will log a message like the one below whenever it doesn't receive any jobs and will
exit.

::

    2023-04-21 20:18:15,884 - INFO [torc.job_runner job_runner.py:398] : Reason: No jobs matched status='ready', memory_bytes <= 98784247808, num_cpus <= 36, runtime_seconds <= 3587.317633, num_nodes == 1, scheduler_config_id == slurm_schedulers__1208235/1208418

In this example torc is reporting that the compute node has 36 available CPUs, 92 GiB of memory,
and a runtime limit of just under one hour. Compare those values against the resource requirements
in the database.

.. code-block:: console

    $ torc resource-requirements list

    +--------------------------------------------------------------------------------+
    |                   Resource requirements in workflow 96282097                   |
    +-------+--------+----------+----------+-----------+--------+---------+----------+
    | index |  name  | num_cpus | num_gpus | num_nodes | memory | runtime |   key    |
    +-------+--------+----------+----------+-----------+--------+---------+----------+
    |   0   | small  |    1     |    0     |     1     |   1g   |  P0DT1H | 96282228 |
    +-------+--------+----------+----------+-----------+--------+---------+----------+

To see those requirements alongside the jobs, run this command:

.. code-block:: console

    $ torc collections join job-requirements

This example includes a common mistake: the job runtime is one hour. The compute node was likely
scheduled with a one-hour walltime, but when the torc job runner requested jobs, 13 seconds had
passed and so the node will never receive jobs.
