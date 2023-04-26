###########
Plot Graphs
###########

This page describes how to create plots of dependency graphs in your workflow.

**Pre-requisite**: You must be able to run the ArangoDB tool ``arangoexport``. The recommended way
of running it is through Arango's Docker container. You can also install it locally; refer to
https://www.arangodb.com/download-major/.

1. Ensure you can run ``arangoexport``

**Docker**:

.. code-block:: console

    $ docker run -it arangodb/arangodb:latest arangoexport --help

**Singularity on Eagle**:

.. code-block:: console

    $ module load singularity
    $ singularity run /datasets/images/arangodb/arangodb.sif arangoexport --help

**Local**:

.. code-block:: console

    $ arangoexport --help

2. Export only the collections of interest. Examples of collections that you may want to include in
   the same graph are

- ``jobs`` vertexes + ``blocks`` edges
- ``jobs`` and ``files`` vertexes + ``produces`` and ``needs`` edges
- ``jobs`` and ``user_data`` vertexes + ``stores`` and ``consumes`` edges

Here is an example ``arangoexport`` command to export one graph.

.. code-block:: console

    $ arangoexport \
        --server.endpoint "http+tcp://localhost:8529" \
        --server.database workflows \
        --type xgmml \
        --graph-name job-blocks \
        --collection jobs__97903629 \
        --collection blocks__97903629 \
        --xgmml-label-only true \
        --xgmml-label-attribute name
    Connected to ArangoDB 'http+tcp://127.0.0.1:8529, version: 3.10.2, database: 'test-workflows', username: 'root'
    # Export graph with collections jobs__97903629, blocks__97903629 as 'job-blocks'
    # Exporting collection 'jobs__97903629'...
    # Exporting collection 'blocks__97903629'...
    Processed 1 graph, wrote 753 bytes, 2 HTTP request(s)

Key points:

- Set the endpoint and database for your configuration.
- ``graph-name`` can be any name. Arango will create a file with that name in ``./export``.
- Append your workflow key to each collection in the format ``<collection>__<key>``.
- You may want to append ``--overwrite true``.

The file ``export/job-blocks.xgmml`` now exists.

3. Create the plot with the torc CLI command.

.. code-block:: console

    $ torc graphs plot export/job-blocks.xgmml
    Created job-blocks.png
