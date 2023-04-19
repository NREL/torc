.. _configuration:

#############
Configuration
#############

Torc provides these mechanisms to configure a workflow of jobs. Refer to :ref:`jobs` for
complete information about how to define jobs.

.. _workflow_specification:

Workflow Specification
======================
Workflow specification in a JSON file. The JSON document fully defines a workflow and
relationships between objects. Users can upload the workflow to the database with a CLI command.
This is the recommended process because the JSON file defines everything about the workflow.

Refer to this `example <https://github.nrel.gov/viz/wms/blob/main/examples/diamond_workflow.json5>`_.

.. note:: In that example torc determines the order of execution of jobs based on the job/file
   input/output relationships.

You can create an empty version of this file with the command below. Save the output to a file
and customize as you wish.

.. code-block:: console

   $ torc workflows template

Here's how to upload the workflow to the database:

.. code-block:: console

   $ torc workflows create-from-json-file examples/diamond_workflow.json
   2023-03-28 16:36:35,149 - INFO [torc.cli.workflows workflows.py:156] : Created a workflow from examples/diamond_workflow.json5 with key=92238688

Commands File
=============
Job definitions in a text file. Each job is a CLI command with options and arguments. The text
file has one command on each line. The torc CLI tool creates an empty workflow, converts each
command into a job, and adds the job. Users can add dependencies and other resources with torc
CLI tools. This process is convenient if your workflow is simple.

This example will create a workflow from 5 commands with a name and description.

.. code-block:: console

   $ cat commands.txt
   bash my_script.sh -i input1.json -o output1.json
   bash my_script.sh -i input2.json -o output2.json
   bash my_script.sh -i input3.json -o output3.json

.. code-block:: console

   $ torc workflows create-from-commands-file -n my-workflow -d "My workflow" commands.txt

CLI commands
============
Build a workflow incrementally with torc CLI commands like the example below. This process may
be required if your workflow exceeds the size that can be transferred in one HTTP POST command.

.. code-block:: console

   $ torc workflows create -n my-workflow -d "My workflow"
   2023-03-28 16:17:36,736 - INFO [torc.cli.workflows workflows.py:78] : Created workflow with key=92237770

.. code-block:: console

   $ torc -k 92237770 jobs add -n job1 -c "bash my_script.sh -i input1.json -o output1.json"
   2023-03-28 18:19:17,330 - INFO [torc.cli.jobs jobs.py:80] : Added job with key=92237922

API calls
=========
Make your own API calls directly to the database. Here is one
`script example <https://github.nrel.gov/viz/wms/blob/main/examples/diamond_workflow.py>`_.
