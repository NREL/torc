############
Architecture
############

- Store information about jobs and dependencies in a graph database.
- A server implements an HTTP API endpoint that manages the database.

  - With ArangoDB as the database, this API endpoint is a service inside the database.

- The API conforms to the OpenAPI specification.

  - The software package auto-generates client APIs in common programming languages with ``Swagger``
    tools.
  - Users can use a client API or send commands through ``curl`` with JSON documents.

- User defines a workflow through the API.

  - API exists in common programming languages, HTTP, and JSON.

Database layout/schema
======================

Nodes
-----

- jobs
- files
- job resource requirements
- results
- scheduler configurations (SLURM, AWS, etc.)
- user data (any number of arbitrary objects)
- compute nodes

Edges
-----

- blocks: job blocks another job
- executed: compute_node executed jobs
- needs: job needs a file
- produces: job produces a file
- requires: job has a set of resource requirements
- returned: job returned a result
- scheduled_by: job is scheduled by a specific scheduler, like SLURM or AWS Batch
- stores: job stores one or more user data objects

Documents
---------

- events: Orchestration software posts events when starting and completing worker nodes and jobs.
  etc.

Users can post their own events. Common structure is TBD.


Worker nodes
============
The software package provides a tool that can pull jobs from the database that meets its hardware
resource availability.

Worker node scheduling
----------------------
TBD. Currently, the user must start their own nodes. It would not be difficult to write an
application to acquire nodes based on initial job readiness and then subsequently acquire more
nodes as needed.

The HPC case is straightforward. The user can provide the account and desired QoS. The worker nodes
will be scheduled with their credentials because they will submit the start command in a terminal.

The cloud case is similarly straightforward if the user is willing to pay full price (aka AWS On
Demand). It is more challenging if the user wants to use something like AWS Spot Pricing. The tool
would need to detect interruptions and be intelligent about selecting compute nodes that are
available.

User Interface
--------------
There are two basic mechanisms for users to define workflow:

1. Direct: Define nodes and edges through database calls. Requires that the user understand the
database schema. Relationships between jobs and files are defined in edges and not through
primary key / foreign key relationships in tables.

2. Job definition abstraction: Define dependency nodes like files and resource requirements but
then use the JobDefinition abstraction that includes the names of each dependent node. This is
analagous to primary key / foreign key relationships in tables. This is likely simpler for users.

Database choice
===============
The current choice is ArangoDB because of these reasons:

- It is a multi-model database that can simultaneously be a key-value store, document database, and
  graph database.
- Graph nodes and edges can store full JSON documents and filters can use those documents. Neo4j
  can store key-value pairs but not nested structures. That may be limiting, especially for
  user-defined events. Using Neo4j for storing job dependencies may require a second database.
