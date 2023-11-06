.. _generate-client-apis:

********************
Generate Client APIs
********************
The software package uses the ``OpenAPI`` tools to auto-generate client APIs from Docker
containers.

.. note:: You must have Docker (or Podman) installed.

This repository stores an OpenAPI specification at ``db_service/openapi.yaml``. If you add, delete,
or modify APIs in the torc-service then you must modify this file. You can do this manually by
editing the file with your changes or semi-manually by converting the ArangoDB-generated Swagger
v2 specification to OpenAPI v3 and then making custom edits. There is no fully-automated method
because the ArangoDB-generated methods have several problems:

- Method names can be nonsensical, like ``workflowsworkflowcompute_node_stats_stats``.
- It doesn't recognize models that are returned in the get-all methods and instead makes inline
  models. Those inline models cannot be used in put methods.
- It doesn't handle the case where one schema composes another. It creates an inline model for
  the composed schema and those cannot be used in put methods.
- It generates duplicate models like workflow_jobs_model and jobs_key_model. This
  is OK with Swagger v2 but fails with OpenAPI v3.

One way to approach this problem is the following:

- Generate an ``openapi.yaml`` without your changes (instructions below).
- Generate an ``openapi.yaml`` with your changes.
- Make a textual diff, edit it, and then add it to the official ``openapi.yaml``.

Be sure to follow existing conventions:

- Use ``model`` instead of ``body``.
- Replace odd-looking strings, like ``workflows_workflow_jobs`` with ``jobs``.
- Ensure that that are no names with ``inline``.
- Use these terms:

  - ``list_<collection>``: Return all documents from a collection. Example: ``list_jobs``
  - ``get_<collection_singular>``: Return one document from a collection. Example: ``get_job``.
      There can be singular/plural ambiguity with some collections. ``get_resource_requirements``
      returns one resource-requirements document.
  - ``modify_<collection_singular>``: Modify one document. Example: ``modify_job``
  - ``remove_<collection_singular>``: Remove one document and return it. Example: ``remove_job``
  - ``delete_<collection>``: Delete all documents in the collection. Example: ``delete_jobs``

How to generate openapi.yaml
============================

1. Download the Swagger v2 specification from ArangoDB. You can do this in the ArangoDB web UI on
   the ``torc-services`` API page or by running this command, after adjusting your URL and
   username/password.

.. code-block:: console

    $ curl --silent -X GET http://localhost:8529/_db/test-workflows/_admin/aardvark/foxxes/docs/swagger.json\?mount\=%2Ftorc-service > swagger.json

2. Download this `Java .jar
   file <https://mvnrepository.com/artifact/io.swagger.codegen.v3/swagger-codegen-cli/3.0.36>`_

3. Assuming that you saved the specification to ``swagger.json``, run this command to
   convert the spec to OpenAPI v3 (``./openapi.yaml``):

.. code-block:: console

    $ java -jar swagger-codegen-cli-3.0.36.jar generate --lang=openapi-yaml --input-spec=swagger.json

=============

How to generate OpenAPI clients
===============================

1. Change to the ``db_service`` directory in the repository.

.. code-block:: console

   $ cd db_service

2. Set the ``packageVersion`` in config.json to the same value as in
   ``torc_package/torc/version.py``.

3. Generate the Python and Julia client by running the script below. It performs the following
   actions:

- Create a Python client package.
- Create a Julia client package.
- Copy the Python package directory, ``python_client/openapi_client``, into the ``torc`` package at
  ``/torc_package/torc/openapi_client``, overwriting the existing code.
- Copy the Julia package directory, ``julia_client/openapi_client``, into the ``Torc`` package at
  ``/julia/Torc/src/api``, overwriting the existing code.

.. code-block:: console

   $ bash make_api_clients.sh

This procedure could be implemented to generate additional client programming languages. Refer to
the ``OpenAPI`` documentation for more information.

4. Commit changes to the repository.
