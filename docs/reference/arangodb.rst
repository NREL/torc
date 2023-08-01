########
ArangoDB
########
Torc relies heavily on the multi-model database `ArangoDB <https://www.arangodb.com/>`_.
It uses graphs to store relationships/dependencies between workflow objects and documents
for user-defined data.

Torc provides a moderately-comprehensive set of CLI commands and a custom HTTP API endpoint with
auto-generated client API libraries. The goal is for users to not be forced to deal with ArangoDB
directly, but there are still cases where that may be required. The web UI is particularly
beneficial for useful for running queries, visualizing workflow graphs, and making minor edits to
documents..
``arangodump/arangorestore`` are great for backups.

.. _arango-tools:

Arango tools
============
Here are documentation links for some of their tools:

- Web UI: https://www.arangodb.com/docs/stable/programs-web-interface.html
- Queries: https://www.arangodb.com/docs/stable/programs-web-interface-aql-editor.html
- Shell: https://www.arangodb.com/docs/stable/programs-arangosh.html
- Export: https://www.arangodb.com/docs/stable/programs-arangoexport.html
- Backups: https://www.arangodb.com/docs/stable/programs-arangodump.html
- HTTP API: https://www.arangodb.com/docs/stable/http/

.. _arango-tool-installation:

Installation
------------
The recommended way of running these tools is through Arango's Docker container. You can also
install it locally; refer to https://www.arangodb.com/download-major/.

Here are example commands with ``arangodump`` to test your installation.

Docker
~~~~~~

.. code-block:: console

    $ docker run -it arangodb/arangodb:latest arangodump --help

Singularity
~~~~~~~~~~~

.. code-block:: console

    $ module load singularity
    $ singularity run /datasets/images/arangodb/arangodb.sif arangodump --help

.. warning:: Some commands require access to the local filesystem. If you are currently on the
   HPC's shared filesystem, you might need to bind-mount the directory so that the software inside
   the container can access it.

Example with bind mount:

.. code-block:: console

    $ singularity run -B /scratch:/scratch /datasets/images/arangodb/arangodb.sif arangodump --help

Local
~~~~~

.. code-block:: console

    $ arangoexport --help
