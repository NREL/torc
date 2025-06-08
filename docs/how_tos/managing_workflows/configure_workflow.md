# Configure a workflow

Here are the recommended procedures to configure a workflow:

- Workflow specification (JSON)
- Python API
- Julia API

## Configure a workflow specification

1. Dump the workflow template to a JSON file. Alternatively, dump the example specification to a
   file. You might prefer it because it includes object definitions, like jobs and files. Finally,
   you can copy/paste/modify this [example workflow file](https://github.com/NREL/torc/blob/main/examples/diamond_workflow.json5)

```console
$ torc workflows template > workflow.json
```

```console
$ torc workflows example > example.json
```

```{eval-rst}
.. note:: The output of these is JSON. You can name the file with .json5 and use JSON5 syntax if
   you prefer.
```

2. Customize the parameters in the file in an editor.

   Refer to {ref}`workflow-specification` for more configuration options.

3. Create a workflow in the database.

```console
$ torc workflows create-from-json-file workflow.json
2023-07-31 16:48:32,982 - INFO [torc.cli.workflows workflows.py:234] : Created a workflow from workflow.json5 with key=14022560
```

## OpenAPI Clients

```{eval-rst}
.. note:: This method is recommended if your workflow has more than 10,000 jobs and required if the
   total size of the workflow exceeds 500 MiB.

```

### Configure with the Python API

You can build a workflow through the torc Python API. Refer to this [example Python script](https://github.com/NREL/torc/blob/main/examples/diamond_workflow.py) and the
{ref}`python-client-api-reference` .

Note that if you don't have a CLI executable for your jobs and instead want torc to map a list of
input parameters across workers, you can call `torc.api.map_function_to_jobs()`. Refer to
the tutorial {ref}`map-python-function-tutorial` for more information.

### Configure with the Julia API

You can build a workflow through the torc Julia API. Refer to this [example Julia script](https://github.com/NREL/torc/blob/main/examples/diamond_workflow.jl).

Note that if you don't have a CLI executable for your jobs and instead want torc to map a list of
input parameters across workers, you can call `Torc.map_function_to_jobs()`. Refer to
the tutorial {ref}`map-julia-function-tutorial` for more information.

## Compute node configuration options

Refer to {ref}`advanced_config_options` for how to customize behavior of the torc worker
application on compute nodes. Here are some example settings:

```{eval-rst}
.. tabs::

   .. code-tab:: js JSON5

    user: "user",
    name: "my_workflow",
    config: {
      compute_node_resource_stats: {
        cpu: true,
        disk: false,
        memory: true,
        network: false,
        process: true,
        monitor_type: "periodic",
        make_plots: true,
        interval: 10
      },
      compute_node_ignore_workflow_completion: false,
    }

   .. code-tab:: py

    from torc import make_api
    from torc.openapi_client import ComputeNodeResourceStatsModel, WorkflowModel

    api = make_api("http://localhost:8529/_db/test-workflows/torc-service")
    workflow = WorkflowModel(user="user", name="my_workflow")
    config = api.get_workflow_config(workflow.key)
    config.compute_node_resource_stats = ComputeNodeResourceStatsModel(
        cpu=True,
        memory=True,
        process=True,
        interval=10,
        monitor_type="aggregation",
    )
    config.compute_node_ignore_workflow_completion = False
    api.modify_workflow_config(workflow.key, config)


   .. code-tab:: jl

    using Torc
    import Torc: APIClient

    api = make_api("http://localhost:8529/_db/test-workflows/torc-service")
    workflow = send_api_command(
        api,
        APIClient.add_workflow,
        APIClient.WorkflowModel(user = "user", name = "my_workflow")
    )
    config = send_api_command(api, APIClient.get_workflows_key_config, workflow._key)
    config.compute_node_resource_stats = APIClient.ComputeNodeResourceStatsModel(
        cpu=true,
        memory=true,
        process=true,
        interval=10,
        monitor_type="aggregation",
    )
    config.compute_node_ignore_workflow_completion = false
    send_api_command(api, APIClient.put_workflows_key_config, workflow._key, config)
```
