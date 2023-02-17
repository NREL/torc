#####
Usage
#####

Configuration
=============
The ``wms`` tool offers several ways to configure a workflow. In all cases there is one database
per workflow on a single instance of ArangoDB.

There methods to configure a workflow are the following:

1. HTTP API with JSON-formatted objects using ``curl``
2. Python API
3. Others? APIs for other languages can easily be generated. Please contact the developers if you
   would like another option.
4. ArangoDB UI. This is not great for configuring an entire workflow, but it is very convenient
   for editing an existing workflow.

.. raw:: html

   <hr>

HTTP API
--------
There is an API endpoint that provides an example workflow. You can redirect this to a file, get an
idea of the required format, make your own version, and then send it back.

Install ``jq`` from https://stedolan.github.io/jq/download/ in order to pretty-print the JSON text.

.. code-block:: console

    $ curl --silent -X GET http://localhost:8529/_db/workflows/wms-service/workflow/example | jq . > workflow.json

or if you have authentication enabled:

.. code-block:: console

    $ curl --user username:password --silent -X GET http://localhost:8529/_db/workflows/wms-service/workflow/example | jq . > workflow.json

Edit file as desired and the post it back to the server.

.. code-block:: console

    $ curl --silent -X POST http://localhost:8529/_db/workflows/wms-service/workflow -d "$(cat workflow.json)"

To view the current workflow:

.. code-block:: console

    $ curl --silent -X GET http://localhost:8528/_db/workflows/wms-service/workflow | jq .

To delete the current workflow:

.. code-block:: console

    $ curl --silent -X DELETE http://localhost:8529/_db/workflows/wms-service/workflow

.. raw:: html

   <hr>

This example workflow is stored in https://github.nrel.gov/viz/wms/blob/main/examples/workflow.json

Python API
----------
Refer to this Python script: https://github.nrel.gov/viz/wms/blob/main/examples/diamond_workflow.py

Running it in a terminal will delete the existing workflow and then create the workflow 
described in :ref:`overview`.

.. code-block:: console

   $ python examples/diamond_workflow.py

Run the example workflow. This will delete any existing workflow, create a new workflow, and then
run it.

.. code-block:: console

    python local_worker.py

.. raw:: html

   <hr>

Execution
=========

Local system
------------
One-time installation:

1. Create a virtual environment with your preferred tool (e.g., conda).
2. Install the swagger client.

.. code-block:: console

    $ pip install -e python_client

3. Install the ``wms`` package.

.. code-block:: console

    $ pip install -e worker

4. Run the workflow.

.. code-block:: console

   $ wms workflow run-local http://localhost:8528/_db/workflows/wms-service

.. raw:: html

   <hr>

SLURM worker on HPC via Python
------------------------------
1. Install the database and API service as described in :ref:`eagle_db_installation`.
2. Install the ``wms`` package.
3. Add your workflow to the database.
4. Run this command to get a recommendation for how many compute nodes you need.

.. code-block:: console

   $ wms hpc recommend-nodes --num-cpus=36 DATABASE_URL

5. Create an HPC configuration file that defines the parameters to pass along to SLURM. Note that
   you'll need to run this step multiple times if you require different types of nodes for
   different jobs (like big-memory nodes for some jobs).

   This command prints the available options. Customize as desired and create the file.

.. code-block:: console

   $ wms hpc slurm-config --help

6. Acquire the nodes by passing the HPC config file and the number of HPC job requests to make
   (note that each job could acquire multiple nodes) to this command. The script passed to SLURM
   will start a ``wms`` job-runner script on each node. When SLURM starts allocates a node and
   starts that script, it will begin pulling and executing jobs from the database.

.. code-block:: console

   $ wms hpc schedule-nodes [OPTIONS] DATABASE_URL CONFIG_FILE NUM_HPC_JOBS

As of now the orchestrator will not automatically schedule new nodes after blocked jobs become
ready. We plan to add this functionality.

Check job status in the database. If your node allocations have completed you can rerun steps 4-6.

Here is the simplest way to check job status. If you have lots of jobs then you will want to run
a query with filters directly against the database, such in the query page of the web UI.

.. code-block:: console

   $ curl --silent -X GET http://localhost:8529/_db/workflows/wms-service/jobs | jq .

This example will show only job names and status.

.. code-block:: console

   $ curl --silent -X GET http://localhost:8529/_db/workflows/wms-service/jobs | jq '.items | .[] | [.name, .status]'

.. raw:: html

   <hr>

Cloud Compute Nodes
-------------------
We currently do not perform compute node scheduling, but plan to add it soon. The existing ``wms
workflow run-local`` command will work on an allocated node.
