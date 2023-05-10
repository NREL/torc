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

When all jobs complete this command will show the job status as ``done``.

.. code-block:: console

   $ torc jobs list

This commmand will show the job results. A ``return_code`` of 0 is successful. Non-zero is a
failure.

.. code-block:: console

   $ torc results list

Cancel a workflow
=================
This CLI command will cancel a workflow as well as all active jobs. It may take 1-2 minutes for
compute nodes to kill their jobs and exit.

.. code-block:: console

   $ torc workflow cancel <workflow_key>

Parallelization within a compute node
=====================================
Torc attempts to maximize parallelization of jobs on a single node based on the job resource
requirement definitions. Be aware of the fact that the default number CPUs for a job is one, and so
it is critical that you define these values conservatively. Refer to
:ref:`job_resource_requirements` for more information.

If all jobs have similar resource requirements then you can set the option ``--max-parallel-jobs``
in the ``torc hpc slurm schedule-nodes`` command and avoid having to define the job requirements.
Torc will use that parameter to limit concurrent jobs on each compute node.
