.. wms documentation master file, created by
   sphinx-quickstart on Sat Feb 11 11:41:31 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Prototype Workflow Management System
====================================
This software package orchestrates execution of a workflow of jobs on distributed
computing resources.

Features
--------
- Manage job dependencies.
- Manage job resource requirements.
- Support cloud and HPC environments simultaneously.
- Support workflow restarts.

   - Account for job failures
   - Account for node timeouts and hardware failures
   - Account for changes (or not) of program and data files

Refer to :ref:`overview` for an illustration of its capabilities.

.. raw:: html

   <hr>

ArangoDB
--------
The software relies heavily on the multi-model database `ArangoDB <https://www.arangodb.com/>`_.
It uses graphs to store relationships/dependencies between workflow objects and documents
for user-defined data.

While the software implements some abstractions, like a custom HTTP API endpoint and several
CLI commands, we recommend that users learn and use ArangoDB web UI and CLI tools to query results.

- Web UI: https://www.arangodb.com/docs/stable/programs-web-interface.html
- Queries: https://www.arangodb.com/docs/stable/programs-web-interface-aql-editor.html
- Shell: https://www.arangodb.com/docs/stable/programs-arangosh.html
- Export: https://www.arangodb.com/docs/stable/programs-arangoexport.html
- HTTP API: https://www.arangodb.com/docs/stable/http/

The web UI is particularly useful for running queries and visualizing workflow graphs.

.. raw:: html

   <hr>


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   overview
   installation
   usage
   architecture
   job_input_parameters


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
