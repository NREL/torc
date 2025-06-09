(generate-client-apis)=

# Generate Client APIs

The software package uses the `OpenAPI` tools to auto-generate client APIs from Docker
containers.

```{eval-rst}
.. note:: You must have Docker (or Podman) installed.
```

This repository stores an OpenAPI specification at `db_service/openapi.yaml`. If you add, delete,
or modify APIs in the torc-service then you must modify this file. You can do this manually by
editing the file with your changes or semi-manually by converting the ArangoDB-generated Swagger
v2 specification to OpenAPI v3 and then making custom edits. There is no fully-automated method
because the ArangoDB-generated methods have several problems:

- Method names can be nonsensical, like `workflowsworkflowcompute_node_stats_stats`.
- It doesn't recognize models that are returned in the get-all methods and instead makes inline
  models. Those inline models cannot be used in put methods.
- It doesn't handle the case where one schema composes another. It creates an inline model for
  the composed schema and those cannot be used in put methods.
- It generates duplicate models like workflow_jobs_model and jobs_key_model. This
  is OK with Swagger v2 but fails with OpenAPI v3.

We gave up trying to automate conversion of ArangoDB's Swagger v2 specification to OpenAPI v3
and instead manually manage the `openapi.yaml` file.
______________________________________________________________________

## How to generate OpenAPI clients

1. Change to the `db_service` directory in the repository.

```console
$ cd db_service
```

2. Generate the Python and Julia client by running the script below. It performs the following
   actions:

- Create a Python client package.
- Create a Julia client package.
- Copy the Python package directory, `python_client/openapi_client`, into the `torc` package at
  `/torc_package/torc/openapi_client`, overwriting the existing code.
- Copy the Julia package directory, `julia_client/openapi_client`, into the `Torc` package at
  `/julia/Torc/src/api`, overwriting the existing code.

```console
$ bash make_api_clients.sh
```

This procedure could be implemented to generate additional client programming languages. Refer to
the `OpenAPI` documentation for more information.

3. Commit changes to the repository.
