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

.. code-block:: console

   2023-03-28 16:36:35,149 - INFO [torc.cli.workflows workflows.py:156] : Created a workflow from examples/independent_workflow.json5 with key=92238688

.. code-block:: console

   $ torc workflows start

.. code-block:: console

   2023-03-28 16:37:58,708 - INFO [torc.workflow_manager workflow_manager.py:99] : Started workflow

.. code-block:: console

   $ torc workflows recommend-nodes -n 36

.. code-block:: console

   Requirements for jobs in the ready state:
   {'max_memory_gb': 16.0,
    'max_num_nodes': 1,
    'max_runtime': 'P0DT12H',
    'memory_gb': 25.0,
    'num_cpus': 13,
    'num_gpus': 0,
    'num_jobs': 3}
   Based on CPUs, number of required nodes = 1

.. code-block:: console

   $ torc hpc slurm schedule-nodes -n1

Check workflow status
=====================
Monitor progress with torc or squeue.

.. code-block:: console

   $ watch -n 10 squeue -u $USER

.. code-block:: console

   $ torc jobs list

.. note:: torc will not yet automatically schedule new nodes to run jobs that become unblocked.
   You will have to run the schedule-nodes command again.

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
