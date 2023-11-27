.. _build-torc-packages:

###################
Build Torc Packages
###################
This page describes what developers should do to release new versions after making changes.

1. Update the torc version in all files by running ``python scripts/update_version.py NEW_VERSION``
   from the root of the repository. Choose the new version by following guidance from
   http://semver.org.

2. Rebuild the Python client installed inside torc by following the
   instructions at :ref:`generate-client-apis`.

3. If you changed any JavaScript code for the database service, rebuild ``torc-service.zip``. From
   the ``db_service`` subdirectory of the repository:

.. code-block:: console

    $ npm install
    $ zip -r torc-service.zip manifest.json index.js src scripts node_modules

The ``torc-service.zip`` file can be installed in ArangoDB in its web application by following
instructions at https://www.arangodb.com/docs/stable/foxx-getting-started.html#try-it-out or by
using the ``foxx`` CLI application. CLI instructions are at https://github.com/arangodb/foxx-cli.

Here is an example ``fox`` command to replace a torc service in database with these
pre-conditions. Replace as appropriate for your environment.

- ArangoDB is running in a Docker container with the name ``arangodb``.
- The local directory ``~/docker-share`` is bind-mounted in the container.
- ``~/docker-share`` contains ``torc-service.zip`` and ``password`` which contains the password
  for the user.
- The database name is ``test-workflows``.
- The user is ``root``.

.. code-block:: console

    $ docker run arangodb foxx replace \
        --server http://localhost:8529 \
        --username root \
        -p /share/password \
        -D test-workflows \
        /torc-service \
        /share/torc-service.zip

4. Run all tests on the HPC. The tests in ``tests/test_slurm_workflows.py`` do not run in
   environments where the Slurm CLI tools are not installed.
