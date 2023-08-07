####################
Configure a workflow
####################
There are two recommended procedures to configure a workflow:

- Workflow specification (JSON)

- Python API

Configure a workflow specification
==================================
1. Dump the workflow template to a JSON file. Alternatively, dump the example specification to a
   file. You might prefer it because it includes object definitions, like jobs and files. Finally,
   you can copy/paste/modify this `example workflow
   <https://github.nrel.gov/viz/wms/blob/main/examples/diamond_workflow.json5>`_

.. code-block:: console

    $ torc workflows template > workflow.json

.. code-block:: console

    $ torc workflows example > example.json

.. note:: The output of these is JSON. You can name the file with .json5 and use JSON5 syntax if
   you prefer.

2. Customize the parameters in the file in an editor.

3. Create a workflow in the database.

.. code-block:: console

    $ torc workflows create-from-json-file workflow.json
    2023-07-31 16:48:32,982 - INFO [torc.cli.workflows workflows.py:234] : Created a workflow from workflow.json5 with key=14022560


Configure with the Python API
=============================
The :ref:`workflow-builder` class provides a mechanism to build a workflow with a simple Python
script. Refer to that API documentation and this `example script
<https://github.nrel.gov/viz/wms/blob/main/examples/diamond_workflow.py>`_.

Note that if you don't have a CLI executable for your jobs and instead want torc to map a list of
input parameters across workers, you can call ``WorkflowBuilder.map_function_to_jobs()``. Refer to
the tutorial :ref:`map-function-tutorial` for more information.
