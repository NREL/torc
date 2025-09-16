# API Access With cURL

The CLI toolkit offers support for most torc database API commands. If you find that some commands
are missing or that you would prefer to access them directly, here's how to do it.

The main point to understand is that torc creates a set of database collections for every workflow.
For example, suppose you create a workflow with key=95587030. Torc will create these collections in
the database:

Documents:

- aws_schedulers\_\_95587030
- blocks\_\_95587030
- compute_node_stats\_\_95587030
- compute_nodes\_\_95587030
- events\_\_95587030
- files\_\_95587030
- job_process_stats\_\_95587030
- jobs\_\_95587030
- resource_requirements\_\_95587030
- results\_\_95587030
- scheduled_compute_nodes\_\_95587030
- slurm_schedulers\_\_95587030
- user_data\_\_95587030

Edges:

- executed\_\_95587030
- local_schedulers\_\_95587030
- needs\_\_95587030
- node_used\_\_95587030
- process_used\_\_95587030
- produces\_\_95587030
- requires\_\_95587030
- returned\_\_95587030
- scheduled_bys\_\_95587030
- stores\_\_95587030

There are also these collections that contain information for all workflows:

- workflow_configs
- workflow_statuses
- workflows
- has_workflow_config
- has_workflow_status

## Access through torc-service API

Torc implements a custom HTTP API endpoint that is installed into each workflow database. The torc
CLI and Python API uses this interface.

Here is how to access it through curl.

The general format of the URL is
`<database_hostname>:8529/<database_name>/torc-service/<collection_name>`

The format for accessing all documents in a collection under a workflow is
`<database_hostname>:8529/<database_name>/torc-service/workflows/<collection_name>`

The format for accessing one document in one collection under a workflow is
`<database_hostname>:8529/<database_name>/torc-service/workflows/<collection_name>/<key>`

### List all workflows

```console
$ curl --silent -X GET http://localhost:8529/_db/test-workflows/torc-service/workflows | jq .
{
  "items": [
    {
      "_key": "95587030",
      "_id": "workflows/95587030",
      "_rev": "_f2D1nq----",
      "name": "my_workflow",
      "user": "dthom",
      "description": "My Workflow"
    }
  ],
  "skip": 0,
  "limit": 1000,
  "max_limit": 1000,
  "count": 1,
  "total_count": 1,
  "has_more": false
}
```

### Get one workflow

```console
$ curl --silent -X GET http://localhost:8529/_db/test-workflows/torc-service/workflows/95587030 | jq .
{
  "_key": "95587030",
  "_id": "workflows/95587030",
  "_rev": "_f2D1nq----",
  "name": "my_workflow",
  "user": "dthom",
  "description": "My Workflow"
}
```

### List all jobs in one workflow

```console
$ curl --silent -X GET http://localhost:8529/_db/test-workflows/torc-service/workflows/95587030/jobs | jq .
```

### Get one job in one workflow

```console
$ curl --silent -X GET http://localhost:8529/_db/test-workflows/torc-service/workflows/95587030/jobs/95587160 | jq .
{
  "_key": "95587160",
  "_id": "jobs__95587030/95587160",
  "_rev": "_f2D1nr2---",
  "name": "medium",
  "command": "python my_script.py",
  "cancel_on_blocking_job_failure": true,
  "supports_termination": false,
  "status": "ready"
}
```

## Access through ArangoDB HTTP API

You can also access all collections through Arango's HTTP API. This accesses the data exactly as it
is stored in the database with no translation by torc.

The ArangoDB documentation is <https://www.arangodb.com/docs/stable/http/api.html>

Here are two examples:

```console
$ curl -u root:openSesame --silent GET http://localhost:8529/_db/test-workflows/_api/document/workflows/95587030 | jq .
{
  "_key": "95587030",
  "_id": "workflows/95587030",
  "_rev": "_f2D1nq----",
  "name": "my_workflow",
  "user": "dthom",
  "description": "My test workflow"
}
```

```console
$ curl -u root:openSesame --silent GET http://localhost:8529/_db/test-workflows/_api/document/jobs__95587030/95587152 | jq .
{
  "_key": "95587152",
  "_id": "jobs__95587030/95587152",
  "_rev": "_f2D1nru---",
  "name": "small",
  "command": "python my_script.py",
  "cancel_on_blocking_job_failure": true,
  "supports_termination": false,
  "internal": {
    "memory_bytes": 0,
    "num_cpus": 0,
    "num_gpus": 0,
    "runtime_seconds": 0,
    "scheduler_config_id": ""
  },
  "status": "ready"
}
```
