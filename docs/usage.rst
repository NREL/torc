#####
Usage
#####

The ``torc`` CLI toolkit provides the simplest mechanism to build and manage workflows. It
provides most functionality and this page describes on it. If you need or want more control, you
are welcome to use the API through Swagger-generated libaries or API tools like ``curl``, `Postman
<https://www.postman.com/>`_, and `Insomnia <https://insomnia.rest/>`_. You can also use Arango
tools to manage data directly in the database.

Torc CLI Details
================
The CLI toolkit contains some nuances that users should understand in order to have a good
experience.

General Usage
-------------
The torc CLI commands are hierarchical with help at every level. For example:

.. code-block:: console

   $ torc
   $ torc --help

   $ torc workflows
   $ torc workflows --help

   $ torc hpc slurm --help

Database Connection
-------------------

All of the commands described here require connecting to the database. We recommend that you set
this environment variable to avoid having to type it in every command.

This works if you are running ArangoDB on your local computer. Change ``localhost`` to the hostname
or IP address of your database server.

.. code-block:: console

   $ export TORC_DATABASE_URL=http://localhost:8529/_db/workflows/torc-service

The other option is to pass the URL to every command.

.. code-block:: console

   $ torc -u http://localhost:8529/_db/workflows/torc-service workflows list

Workflow Key
------------
Most commands are tied to one workflow in the database, and so the workflow identifier is critical.
There are three ways to set it:

1. Set it in every command with the ``-k`` or ``--workflow-key`` options.

.. code-block:: console

   $ torc -k 247827 jobs list

2. Set an environment variable to apply it globally in one environment.

.. code-block:: console

   $ export TORC_WORKFLOW_ID=247827
   $ torc jobs list

3. Let the tool prompt you to pick.

.. code-block:: console

   $ torc jobs list

   This command requires a workflow key and one was not provided. Please choose one from below.

   +-----------------------------------------------------------+
   |                             workflow                      |
   +-------+--------------+-------+-----------------+----------+
   | index |  name        |  user | description     |   key    |
   +-------+--------------+-------+-----------------+----------+
   |   1   | workflow1    | user1 | My workflow 1   | 92181686 |
   |   2   | workflow2    | user2 | My workflow 2   | 92181834 |
   +-------+--------------+-------+-----------------+----------+
   workflow key is required. Select an index from above: >>> 2

Configuration
=============

The CLI toolkit provides these mechanisms to configure a workflow.

1. Workflow specification in a JSON file. The JSON document fully defines a workflow and
   relationships between objects. Users can upload the workflow to the database with a CLI command.

Refer to this `example <https://github.nrel.gov/viz/wms/blob/main/examples/diamond_workflow.json5>`_.

Note that in this example torc determines the order of execution of jobs based on the job/file
input/output relationships.

.. code-block:: console

   $ torc workflows create-from-json-file examples/diamond_workflow.json
   2023-03-28 16:36:35,149 - INFO [torc.cli.workflows workflows.py:156] : Created a workflow from examples/diamond_workflow.json5 with key=92238688

2. Job definitions in a text file. Each job is a CLI command with options and arguments. The text
   file has one command on each line. The torc CLI tool creates an empty workflow, converts each
   command into a job, and adds the job. Users can add dependencies and other resources with torc
   CLI tools.

   This example will create a workflow from 5 commands.

.. code-block:: console

   $ cat commands.txt
   bash my_script.sh -i input1.json -o output1.json
   bash my_script.sh -i input2.json -o output2.json
   bash my_script.sh -i input3.json -o output3.json

   $ torc workflows create-from-commands-file commands.txt

3. Build a workflow incrementally with torc CLI commands like the following:

.. code-block:: console

   $ torc workflows create -n my-workflow -d "My workflow"
   2023-03-28 16:17:36,736 - INFO [torc.cli.workflows workflows.py:78] : Created workflow with key=92237770
   $ export TORC_WORKFLOW_ID=92237770
   $ torc jobs add -n job1 -c "bash my_script.sh -i input1.json -o output1.json"
   2023-03-28 18:19:17,330 - INFO [torc.cli.jobs jobs.py:80] : Added job with key=92237922

4. Make your own API calls directly to the database. Here is one
   `script example <https://github.nrel.gov/viz/wms/blob/main/examples/diamond_workflow.py>`_.

Job Input/Output Data
=====================
Refer to :ref:`job_input_output_data` for a discussion of of how to store in input and output
data for jobs.

Run a workflow
==============
This is an HPC example that schedules one node to do the work. Note that the paths to all relevant
scripts need to correct.

.. code-block:: console

   $ torc workflows create-from-json-file examples/independent_workflow.json5
   2023-03-28 16:36:35,149 - INFO [torc.cli.workflows workflows.py:156] : Created a workflow from examples/independent_workflow.json5 with key=92238688
   $ export TORC_WORKFLOW_ID=92238688
   $ torc workflows start
   2023-03-28 16:37:58,708 - INFO [torc.workflow_manager workflow_manager.py:99] : Started workflow
   $ torc hpc slurm schedule-nodes -n1
   # Monitor progress with torc or squeue
   $ watch -n 10 squeue -u $USER
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

Resource Utilization Statistics
===============================
Torc will optionally monitor resource utilization on compute nodes. You can define these settings
in the ``config`` field of the workflow specification JSON5 file.

.. code-block:: JavaScript

   config: {
     compute_node_resource_stats: {
       cpu: true,
       disk: false,
       memory: true,
       network: false,
       process: true,
       include_child_processes: true,
       recurse_child_processes: false,
       monitor_type: "aggregation",
       make_plots: true,
       interval: 1
     }
   }

Setting ``cpu``, ``disk``, ``memory``, or ``network`` to true will track those resources on the
compute node overall. Setting ``process`` to true will track CPU and memory usage on a per-job
basis.

You can set ``monitor_type`` to these options:

- ``aggregation``: Track min/max/average stats in memory and record the results in the database.
- ``periodic``: Record time-series data on an interval in per-node SQLite database files.

If ``monitor_type = periodic`` and ``make_plots = true`` then torc will generate HTML plots of the
results.

These command will print summaries of the stats in the terminal:

.. code-block:: console

   $ torc jobs list-process-stats
   $ torc compute-nodes list-resource-stats

Cloud Compute Nodes
===================
We currently do not perform compute node scheduling, but plan to add it soon. The existing ``torc
local run-jobs`` command will work on an allocated node.
