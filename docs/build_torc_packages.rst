.. _building_torc:

###################
Build Torc Packages
###################
This page describes what developers should do to release new versions after making changes.

1. Update the torc version in the files ``torc_package/torc/version.py`` and
   ``db_service/config.json``, following guidance from http://semver.org. Also update this version
   in ``docs/installation.rst`` (TODO: automate).

2. Rebuild the Python client installed inside torc by following the
   instructions at :ref:`generate_client_apis`.

3. If you changed any JavaScript code for the database service, rebuild ``torc-service.zip``. From
   the ``db_service`` subdirectory of the repository:

.. code-block:: console

    $ npm install
    $ zip -r torc-service.zip manifest.json index.js src scripts node_modules

The ``torc-service.zip`` file can be installed in ArangoDB in its web application by following
instructions at https://www.arangodb.com/docs/stable/foxx-getting-started.html#try-it-out or by
using the ``foxx`` CLI application. CLI instructions are at https://github.com/arangodb/foxx-cli.

4. Run all tests on the HPC. The tests in ``tests/test_slurm_workflows.py`` do not run in
   environments where the Slurm CLI tools are not installed.

.. toctree::
   :maxdepth: 2
   :hidden:

   generate_client_apis
