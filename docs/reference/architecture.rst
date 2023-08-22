############
Architecture
############

.. toctree::
   :maxdepth: 2
   :hidden:

   hpc_workflow

Overview
========
- Store information about jobs and dependencies in an ArangoDB graph database.
- A server implements an HTTP API endpoint that manages the database.

  - With ArangoDB as the database, this API endpoint is a service inside the database.
  - ArangoDB balances client requests across multiple V8 JavaScript contexts running in the server.

- The API conforms to the OpenAPI specification.

  - The software package auto-generates client APIs in common programming languages with
    ``OpenAPI`` tools.
  - Users can use a client API or send commands through ``curl`` (or any client API tool) with
    JSON documents.

- User defines a workflow through the API.

  - API exists in common programming languages, HTTP, and JSON.
  - The software package provides a suite of CLI commands to manage workflows in the database.
    This toolkit abstracts the database implementation details from the user.


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
Currently, the user must schedule initial compute nodes with a torc CLI tool. They can enable
specific jobs in subsequent rounds to be scheduled automatically. In the near future torc could
always schedule compute nodes automatically.

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

2. API calls using OpenAPI-auto-generated client libraries. The torc CLI tools use a Python client.
   The build process also makes a Julia client. We can generate others that users want.

3. API calls using client API tools: ``curl``, `Postman <https://www.postman.com/>`_,
   `Insomnia <https://insomnia.rest/>`_, etc.

The first option abstracts the database schema from the user. The latter two require a fair
understanding of the implementation.
