.. torc documentation master file, created by
   sphinx-quickstart on Sat Feb 11 11:41:31 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Torc Workflow Management System
===============================
The torc software package orchestrates execution of workflows on distributed computing resources.
It also provides mechanisms for users to manage result data.

Features
--------
- Manage job dependencies.
- Manage job resource requirements.
- Auto-tune resource requirements.
- Acquire compute resources.
- Track resource utilization.
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
Torc relies heavily on the multi-model database `ArangoDB <https://www.arangodb.com/>`_.
It uses graphs to store relationships/dependencies between workflow objects and documents
for user-defined data.

Torc provides a moderately-comprehensive set of CLI commands and a custom HTTP API endpoint with
auto-generated client API libraries. The goal is for users to not be forced to deal with ArangoDB
directly, but there are still cases where that may be required. The web UI is particularly
beneficial for useful for running queries and visualizing workflow graphs.
``arangodump/arangorestore`` are great for backups.

Here are documentation links for some of their tools:

- Web UI: https://www.arangodb.com/docs/stable/programs-web-interface.html
- Queries: https://www.arangodb.com/docs/stable/programs-web-interface-aql-editor.html
- Shell: https://www.arangodb.com/docs/stable/programs-arangosh.html
- Export: https://www.arangodb.com/docs/stable/programs-arangoexport.html
- Backups: https://www.arangodb.com/docs/stable/programs-arangodump.html
- HTTP API: https://www.arangodb.com/docs/stable/http/

.. raw:: html

   <hr>


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   overview
   installation
   quick_start
   usage
   architecture
   job_input_output_data


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
