.. _generate-client-apis:

********************
Generate Client APIs
********************
The software package uses the ``OpenAPI`` and ``Swagger`` tools to auto-generate client APIs from
Docker containers.

.. note:: You must have Docker installed.

The Swagger container does not support Macs with M1 or M2 processors. If you have one of those then
you'll need to download the Swagger jar file from this `Maven repository
<https://mvnrepository.com/artifact/io.swagger.codegen.v3/swagger-codegen-cli/3.0.36>`_ and then
set the environment variable ``LOCAL_SWAGGER_CODEGEN_CLI`` with the path to the file. For example,

.. code-block:: console

    $ export LOCAL_SWAGGER_CODEGEN_CLI=~/Downloads/swagger-codegen-cli-3.0.36.jar

This repository stores an OpenAPI specification at ``db_service/openapi.yaml``.
If the API definitions are changed then this needs to be regenerated. Here's how to to that:

1. Start the workflow database. By default the script assumes it is running at
http://localhost:8529. You can change it by setting this environment variable with your hostname
and port:

.. code-block:: console

   $ export TORC_URL=http://hostname:port

2. Set the database name in this environment variable. Replace ``db_name`` with your database name.

.. code-block:: console

   $ export TORC_DATABASE_NAME=db_name

3. Optionally set these environment variables for username/password. The default username is
   ``root``.

.. code-block:: console

   $ export TORC_USER=$USER
   $ export TORC_PASSWORD=my-password

4. Change to the ``db_service`` directory in the repository.

.. code-block:: console

   $ cd db_service

5. Set the ``packageVersion`` in config.json to the same value as in
   ``torc_package/torc/version.py``.

6. Generate the Python and Julia client by running the script below. It performs the following
   actions:

- Download the API specification `swagger.json` from the API endpoint. This is created by ArangoDB.
- Convert the spec from v2.0 (Swagger) to v3.0 (OpenAPI).
- Rename input schemas to names that make more sense for the application.
- Create a Python client package.
- Create a Julia client package.
- Copy the Python package directory, ``python_client/openapi_client``, into the ``torc`` package at
  ``/torc_package/torc/openapi_client``, overwriting the existing code.
- Copy the Julia package directory, ``julia_client/openapi_client``, into the ``Torc`` package at
  ``/julia/Torc/src/api``, overwriting the existing code.

.. code-block:: console

   $ bash make_api.sh

This procedure could be implemented to generate additional client programming languages. Refer to
the ``OpenAPI`` documentation for more information.

7. Commit changes to the repository.
