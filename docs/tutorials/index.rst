.. _tutorials:

#########
Tutorials
#########
This section provides working examples that you can follow to learn how to use torc. The examples
are stored in the torc repository at ``/examples``, and so you'll need to clone it as described
below.

1. Clone the torc repository.

.. code-block:: console

    $ git clone https://github.nrel.gov/viz/torc.git

2. Change to the ``torc`` directory so that you have access to the torc test scripts.

.. code-block:: console

    $ cd torc/torc_package

3. Create a torc runtime configuration file. We will use it shorten the commands that we type
   below. Change ``<hostname>`` and ``<database-name>`` to correct values for your database
   (without the ``<>``).

.. code-block:: console

    $ torc config create -u http://<hostname>:8529/_db/<database-name>/torc-service
    Wrote torc config to /Users/dthom/.torc_settings.toml


.. toctree::
   :maxdepth: 4

   diamond_workflow
   slurm_diamond_workflow
   manual_job_dependencies
   cpu_affinity_workflow
   map_python_function
   map_julia_function
   large_workflow
