# Prototype workflow management software

This software package orchestrates execution of a workflow of jobs (CLI commands) on distributed
computing resources.

Features:
- Manage job dependencies
  - direct job-job dependencies
  - indirect job-job dependencies based on required input files and produced output files
- Manage job resource requirements
  - CPU
  - Memory
  - GPUs
  - Local storage
  - Number of nodes
- Restart workflow
  - Account for job failures
  - Account for node timeouts and hardware failures
  - Account for changes (or not) of program and data files

## Architecture

- Store information about jobs and dependencies in a graph database.
- A server implements an HTTP API endpoint that manages the database.
  - With ArangoDB as the database, this API endpoint is a service inside the database.
- The API conforms to the OpenAPI specification.
  - The software package auto-generates client APIs in common programming languages with `Swagger`
  tools.
  - Users can use a client API or send commands through `curl` with JSON documents.
- User defines a workflow through the API.
  - API exists in common programming languages, HTTP, and JSON.

### Database layout/schema

Nodes:
- jobs
- files
- job resource requirements
- results
- scheduler configurations (SLURM, AWS, etc.)
- user data (any number of arbitrary objects)
- compute nodes

Edges:
- blocks: job blocks another job
- executed: compute_node executed jobs
- needs: job needs a file
- produces: job produces a file
- requires: job has a set of resource requirements
- returned: job returned a result
- scheduled_by: job is scheduled by a specific scheduler, like SLURM or AWS Batch
- stores: job stores one or more user data objects

Documents:
- events: Orchestration software posts events when starting and completing worker nodes and jobs.
etc.

Users can post their own events. Common structure is TBD.


### Worker nodes
The software package provides a tool that can pull jobs from the database that meets its hardware
resource availability.

### Worker node scheduling
TBD. Currently, it is BYON (bring your own nodes). It would not be difficult to write an
application to acquire nodes based on initial job readiness and then subsequently acquire more
nodes as needed.

The HPC case is straightforward. The user can provide the account and desired QoS. The worker nodes
will be scheduled with their credentials because they will submit the start command in a terminal.

The cloud case is similarly straightforward if the user is willing to pay full price (aka AWS On
Demand). It is more challenging if the user wants to use something like AWS Spot Pricing. The tool
would need to detect interruptions and be intelligent about selecting compute nodes that are
available.

### User Interface
There are two basic mechanisms for users to define workflow:
1. Direct: Define nodes and edges through database calls. Requires that the user understand the
database schema. Relationships between jobs and files are defined in edges and not through
primary key / foreign key relationships in tables.
2. Job definition abstraction: Define dependency nodes like files and resource requirements but
then use the JobDefinition abstraction that includes the names of each dependent node. This is
analagous to primary key / foreign key relationships in tables. This is likely simpler for users.

## Database choice
The current choice is ArangoDB because of these reasons:
- It is a multi-model database that can simultaneously be a key-value store, document database, and
graph database.
- Graph nodes and edges can store full JSON documents and filters can use those documents. Neo4j
can store key-value pairs but not nested structures. That may be limiting, especially for
user-defined events. Using Neo4j for storing job dependencies may require a second database.

## Database Installation
1. Install ArangoDB.

Choose one of the following:
- Install ArangoDB Community Edition locally by following instructions at
https://www.arangodb.com/download-major/
- Run the ArangoDB container by following instructions at
https://www.arangodb.com/download-major/docker/

Verify the installation by logging into the ArangoDB web server at `http://localhost:8529`. You can
also use Arango's JavaScript REPL via `arangodb/bin/arangosh`.

2. Create a database called `workflows` in the web UI or `arangosh`.

3. Create the service that will implement the API endpoint. Change to the `db_service` directory
after cloning this repository.

```
$ npm install
$ zip -r wms-service.zip manifest.json node_modules index.js src scripts
```

4. Install that service via the web app by following instructions at
`https://www.arangodb.com/docs/stable/foxx-getting-started.html#try-it-out` or by using the `foxx`
CLI application. CLI instructions are at `https://github.com/arangodb/foxx-cli`.

When developing the API, use `foxx`.

Default `foxx` instructions didn't fully work. Here are some that did:

```
$ foxx server set dev http://127.0.0.1:8529 -D workflows -u root
```
Open `~/.foxxrc` and set the password if you have authentication enabled.

Confirm the installation with
```
$ foxx list --server dev
  /wms-service           [DEV]
```

If you install the `foxx` CLI and configure authentication, this command will install the service:

```
$ foxx install -H dev /wms-service wms-service.zip
```

You can replace an existing service with
```
$ foxx replace -H dev /wms-service wms-service.zip
```

5. Enable development mode with this command (this can also be done in the settings tab of the web
UI)
```
$ foxx set-dev --server dev /wms-service
```

Be sure to read `https://www.arangodb.com/docs/stable/foxx-guides-development-mode.html` when
developing the API endpoint.

6. Test the endpoint by running this command to get an example workflow. (`jq` is not required but
generally useful for displaying and filtering JSON output).
```
$ curl --silent -X GET http://localhost:8529/_db/workflows/wms-service/workflow/example | jq .
```

## Client APIs
The software package uses the `Swagger` tools to auto-generate client APIs. Refer to
https://swagger.io/docs/open-source-tools/swagger-codegen/ for installation instructions. They
also have a Docker container available.

A Python client is checked into this repository at `python_client`. If the API definitions are
changed then this needs to be regen
You can create client APIs if the database is running on the current system and the API endpoint
service is installed by running the script `db_service/make_api.sh`.

`db_service/make_api.sh` does the following:
- Download the API specification `swagger.json` from the API endpoint. This is created by ArangoDB.
- Convert the spec from v2.0 (Swagger) to v3.0 (OpenAPI).
- Rename input schemas to names that make more sense for the application.
- Create a Python client.

Before running it:
- Change to the `db_service` directory.
- Set the environment variable `SWAGGER_CODEGEN_CLI` to the path to `swagger-codegen-cli.jar`.

This procedure could be implemented to generate server stubs or additional client programming
languages. Refer to the `Swagger` documentation for more information.

## Usage

### curl / JSON
Pipe the example workflow to a JSON file. Install `jq` from https://stedolan.github.io/jq/download/
```
$ curl --silent -X GET http://localhost:8529/_db/workflows/wms-service/workflow/example | jq . > workflow.json
```

Edit file as desired and the post it back to the server.
```
$ curl --silent -X POST http://localhost:8529/_db/workflows/wms-service/workflow -d "$(cat workflow.json)"
```

To view the current workflow:
```
$ curl --silent -X GET http://localhost:8528/_db/workflows/wms-service/workflow | jq .
```

To delete the current workflow:
```
$ curl --silent -X DELETE http://localhost:8529/_db/workflows/wms-service/workflow
```

### Local worker via Python
One-time installation:
1. Create a virtual environment with your preferred tool.
2. Install the swagger client.
```
$ cd python_client
$ pip install -e .
```
3. Install the `wms` package.
```
$ cd ../worker
$ pip install -e .
```

Run the example workflow. This will delete any existing workflow, create a new workflow, and then
run it.
```
python local_worker.py
```

### SLURM worker on HPC via Python
1. Install the database and API service with the Singularity container (details TBD).
1. Follow the local worker installation.
2. Add your workflow to the database.
3. Acquire one or more compute nodes with SLURM.
4. Run jobs.
```
$ cd worker
$ python wms/slurm_job_runner.py
```
