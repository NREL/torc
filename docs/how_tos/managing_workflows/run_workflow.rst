##############
Run a workflow
##############

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
