.. _generate_client_apis:

####################
Generate Client APIs
####################
The software package uses the ``Swagger`` tools to auto-generate client APIs from a Docker
container. You must have Docker installed.

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

5. Set the ``packageVersion`` in ``config.json to the same value as in
   ``torc_package/torc/version.py``.

6. Generate the python client.

.. code-block:: console

   $ bash make_api.sh

Here is what the script performed:

- Download the API specification `swagger.json` from the API endpoint. This is created by ArangoDB.
- Convert the spec from v2.0 (Swagger) to v3.0 (OpenAPI).
- Rename input schemas to names that make more sense for the application.
- Create a Python client package.
- Copy the package directory, ``swagger_client``, into the torc package at
  ``/torc_package/torc/swagger_client``, overwriting the existing code.

This procedure could be implemented to generate server stubs or additional client programming
languages. Refer to the ``Swagger`` documentation for more information.

7. Commit changes to the repository.
