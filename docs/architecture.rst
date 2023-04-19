############
Architecture
############

.. toctree::
   :maxdepth: 3

   hpc_workflow

Overview
========
- Store information about jobs and dependencies in the ArangoDB graph database.
- A server implements an HTTP API endpoint that manages the database.

  - With ArangoDB as the database, this API endpoint is a service inside the database.
  - ArangoDB balances client requests across multiple V8 JavaScript contexts running in the server.

- The API conforms to the OpenAPI specification.

  - The software package auto-generates client APIs in common programming languages with ``Swagger``
    tools.
  - Users can use a client API or send commands through ``curl`` (or any client API tool) with
    JSON documents.

- User defines a workflow through the API.

  - API exists in common programming languages, HTTP, and JSON.
  - The software package provides a suite of CLI commands to manage workflows in the database.
    This toolkit abstracts the database implementation details from the user.

ArangoDB
========
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

Database layout/schema
======================

This section describes how torc defines and gives access to collections in ArangoDB.

An ArangoDB instance can host many databases. Each database can store many collections. Each
database can install multiple API services.

Torc is designed to store hundreds-to-thousands of workflows for a team of 10-20 users in one
database. Each workflow gets its own set of job/file/result collections. Each user has read/write
access to their own database but not others. This is differentiated from a solution where end users
do not have direct access to the database, and instead store data indirectly through an application
with its own access control system.

Torc installs one API service in each database to facilitate management through client software.

The nodes, edges, and documents discussed below are part of one workflow in one database.

Nodes
-----

- jobs
- files
- job resource requirements
- results
- scheduler configurations (Slurm, AWS, etc.)
- user data (any number of arbitrary objects)
- compute nodes
- compute node stats
- job process stats

.. note:: When looking at the collections in ArangoDB tools you will see that each collection name
   includes its workflow identifier.

Job Restarts
~~~~~~~~~~~~
The orchestrator stores one result and process stats object for each run of a job in case a
workflow is restarted.

Those objects contain a ``run_id`` field that gets incremented each time a job runs.

Edges
-----

- blocks: job blocks another job
- consumes: job consumes user data object in the database
- executed: compute_node executed jobs
- needs: job needs a file
- nodes_used: compute nodes used resources - connects compute nodes to usage stats
- process_used: job processes used resources - connects jobs to process usage stats
- produces: job produces a file
- requires: job has a set of resource requirements
- returned: job returned a result
- scheduled_bys: job is scheduled by a specific scheduler, like Slurm or AWS Batch
- stores: job stores one or more user data objects

Documents
---------

- events: Torc posts events when starting and completing worker nodes and jobs.

Users can post their own events. Common structure is TBD.

Worker nodes
============
The software package provides a tool that can pull jobs from the database that meets its hardware
resource availability.

Worker node scheduling
----------------------
Currently, the user must schedule compute nodes with a torc CLI tool. In the near future we plan
to add functionality to do this automatically - including scheduling new nodes as needed.

The HPC case is straightforward. The user can provide the account and desired QoS. The worker nodes
will be scheduled with their credentials because they will submit the start command in a session
on a login node.

The cloud case is similarly straightforward if the user is willing to pay full price (aka AWS On
Demand). It is more challenging if the user wants to use something like AWS Spot Pricing. The tool
would need to detect interruptions and be intelligent about selecting compute nodes that are
available. That is TBD.

User Interface
--------------
Torc provides these mechanisms for users to define workflows:

1. torc CLI tools. The toolkit provides most functionality required for users.

2. API calls using Swagger-auto-generated client libraries. The torc CLI tools use a Python client.
   We can generate others that users want.

3. API calls using client API tools: ``curl``, `Postman <https://www.postman.com/>`_,
   `Insomnia <https://insomnia.rest/>`_, etc.

The first option abstracts the database schema from the user. The latter two require a fair
understanding of the implementation.

Database choice
===============
The current choice is ArangoDB because of these reasons:

- It is a multi-model database that can simultaneously be a key-value store, document database, and
  graph database.
- Graph nodes and edges can store full JSON documents and filters can use those documents. Neo4j
  can store key-value pairs but not nested structures. That may be limiting, especially for
  user-defined events. Using Neo4j for storing job dependencies may require a second database.
- ArangoDB provides built-in API services.
