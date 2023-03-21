.. _generate_client_apis:

####################
Generate Client APIs
####################
The software package uses the ``Swagger`` tools to auto-generate client APIs. Refer to
https://swagger.io/docs/open-source-tools/swagger-codegen/ for installation instructions. They
also have a Docker container available.

This repository stores an OpenAPI specification at ``db_service/openapi.yaml``.
If the API definitions are changed then this needs to be regenerated. Here's how to to that:

1. Start the workflow database. By default the script assumes it is running at
http://localhost:8529. You can change it by setting this environment variable with your hostname
and port:

.. code-block:: console

   $ export TORC_URL=http://hostname:port

2. Change to the ``db_service`` directory in the repository.

.. code-block:: console

   $ cd db_service

3. Set an environment variable for the swagger CLI tool and optionallly the database root password.

.. code-block:: console

   $ export SWAGGER_CODEGEN_CLI=~/tools/swagger-codegen-cli.jar
   $ export TORC_PASSWORD=my_password

4. Generate the python client.

.. code-block:: console

   $ bash make_api.sh

The local directory now contains ``python_client``.

Here is what the script performed:

- Download the API specification `swagger.json` from the API endpoint. This is created by ArangoDB.
- Convert the spec from v2.0 (Swagger) to v3.0 (OpenAPI).
- Rename input schemas to names that make more sense for the application.
- Create a Python client.

This procedure could be implemented to generate server stubs or additional client programming
languages. Refer to the ``Swagger`` documentation for more information.
