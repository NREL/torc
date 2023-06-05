#########
Execution
#########

Run a workflow
==============
This is an HPC example that schedules one node to do the work. Note that it saves the workflow
key to the local torc rc file. You will need to change this if you change workflows.

.. note:: The paths to all relevant scripts need to correct based on your current directory.

.. code-block:: console

   $ torc workflows create-from-json-file -U examples/independent_workflow.json5
   2023-03-28 16:36:35,149 - INFO [torc.cli.workflows workflows.py:156] : Created a workflow from examples/independent_workflow.json5 with key=92238688

This command will identify relationships between workflow objects and initialize the job status.

.. code-block:: console

   $ torc workflows start
   2023-03-28 16:37:58,708 - INFO [torc.workflow_manager workflow_manager.py:99] : Started workflow

This command asks the database to give a recommendation on how many compute nodes should be
scheduled given that each node has 36 CPUs.

.. code-block:: console

   $ torc workflows recommend-nodes -n 36
   Requirements for jobs in the ready state:
   {'max_memory_gb': 16.0,
    'max_num_nodes': 1,
    'max_runtime': 'P0DT12H',
    'memory_gb': 25.0,
    'num_cpus': 13,
    'num_gpus': 0,
    'num_jobs': 3}
   Based on CPUs, number of required nodes = 1

This command schedules one compute node.

.. code-block:: console

   $ torc hpc slurm schedule-nodes -n1

.. _automated_scheduling:

Automated scheduling
====================
By default, torc leaves scheduling of compute nodes to the user. If you know that an
initially-blocked job will need a specific compute node (or nodes), you can tell torc to schedule
it for you when all other conditions are met.

Set the ``scheduler`` and ``needs_compute_node_schedule`` fields of the job in the workflow
specification file. When that job reaches the ``ready`` status, torc will send the schedule command
with the same parameters that were originally used.

.. note:: If one new compute node allocation can satisfy multiple jobs that will be ready at about
   the same time, you can set these fields for only one job. Setting it for multiple jobs may
   result in multiple allocations.

Check workflow status
=====================
Monitor progress with torc or squeue.

.. code-block:: console

   $ watch -n 10 squeue -u $USER

.. code-block:: console

   $ torc jobs list

After a job completes its status will be be ``done``. You can filter the jobs to see how many
are ready, in progress, and done

.. code-block:: console

   $ torc jobs list -f status=ready

.. code-block:: console

   $ torc jobs list -f status=submitted

.. code-block:: console

   $ torc jobs list -f status=done

This commmand will show the job results. A ``return_code`` of 0 is successful. Non-zero is a
failure.

.. code-block:: console

   $ torc results list

You can filter the output to see only passes or only failures.

.. code-block:: console

   $ torc results list -f return_code=0

.. code-block:: console

   $ torc results list -f return_code=1

Cancel a workflow
=================
This CLI command will cancel a workflow as well as all active jobs. It may take 1-2 minutes for
compute nodes to kill their jobs and exit.

.. code-block:: console

   $ torc workflow cancel <workflow_key>

Restart a workflow
==================
Common cases that require you to restart a workflow include:

- Jobs failed because of a code or data bug.
- Jobs failed because they consumed more memory than expected.
- Jobs failed because they took longer than expected and the node allocation timed out.

The steps to restart a workflow are slightly different depending on whether the job actually
completed from torc's perspective and whether you defined job dependencies.

If a job completes with a return code, torc stores a result in the database. However, if the job
consumed all of the compute node's memory, the out-of-memory handler (or perhaps Slurm) will
terminate the process and possibly the torc worker application. If an HPC node exhausts its time,
the scheduler will terminate all of your processes. In these cases torc will not record a result.
The job status will still be ``submitted``.

Restarting jobs that did not finish
-----------------------------------
Run this command to re-initialize the workflow and relevant job statuses.

.. code-block:: console

   $ torc workflows restart

Check the status if you'd like.

.. code-block:: console

   $ torc jobs list -f status=ready

Schedule compute nodes to run those jobs.

.. code-block:: console

   $ torc hpc slurm schedule-nodes -nX

Where ``X`` is the number of Slurm jobs to schedule.

With job dependencies
---------------------
If your jobs failed because of code and/or data bugs and

1. You fixed those bugs.
2. You defined dependencies on jobs for those files or data.

then you can the same steps above to re-initialize the job statuses and schedule new nodes.

Without job dependencies
------------------------
If you did not define job dependencies on files or data then you'll need to perform additional
steps to reset the status of jobs that you need to rerun.

If you want to rerun all jobs with a non-zero return code, run this command:

.. code-block:: console

   $ torc workflows reset-job-status --failed-only

If you only want to rerun a subset of failed jobs, you will need to pass those job keys to this
command:

.. code-block:: console

   $ torc jobs reset-status KEY1 KEY2 ...

If the list of jobs to rerun is long then you'll want to employ some shell scripting. This command
will filter results by ``return_code=1``, return the output in JSON format, use the ``jq`` tool to
extract only job keys, and then pass those keys to the ``jobs reset-status`` command.

.. code-block:: console

   $ torc jobs reset-status $(torc -F json results list -f return_code=1 | jq -r '.results | .[] | .job_key')

Next, just as described above, run ``torc workflows restart`` and ``torc hpc slurm schedule-nodes``
to rerun the jobs.

Parallelization within a compute node
=====================================
Torc attempts to maximize parallelization of jobs on a single node based on the job resource
requirement definitions. Be aware of the fact that the default number CPUs for a job is one, and so
it is critical that you define these values conservatively. Refer to
:ref:`job_resource_requirements` for more information.

If all jobs have similar resource requirements then you can set the option ``--max-parallel-jobs``
in the ``torc hpc slurm schedule-nodes`` command and avoid having to define the job requirements.
Torc will use that parameter to limit concurrent jobs on each compute node.
