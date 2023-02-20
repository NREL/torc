.. _eagle_db_installation:

##############################
Database Installation on Eagle
##############################

1. Start the ArangoDB Singularity container in a directory where you want
   to keep your database. Note that you can reload your data after stopping and restarting the
   container. 

.. warning:: Do not run ArangoDB on a login node.

This script will acquire a node and start the database in a container. Edit the SLURM and
ArangoDB parameters as needed. ArangoDB will store its data in ``arangodb3`` and
``arangodb3-apps``. Reuse these directories if you start a new session later.

.. code-block:: console

    #!/bin/bash
    #SBATCH --account=my-account
    #SBATCH --job-name=arangodb
    #SBATCH --time=01:00:00
    #SBATCH --output=output_%j.o
    #SBATCH --error=output_%j.e
    #SBATCH --nodes=1
    #SBATCH --partition=debug

    module load singularity-container
    singularity run \
        --network-args "portmap=8529:8529" \
        --env "ARANGO_ROOT_PASSWORD=openSesame" \
        -B arangodb3:/var/lib/arangodb3 \
        -B arangodb3-apps:/var/lib/arangodb3-apps \
        /scratch/dthom/containers/arangodb.sif

Copy that text into ``batch_arangod.sh`` and submit it to SLURM. ``tail`` will print text
from ``arangod`` when it starts.

.. code-block:: console

   $ sbatch batch_arangod.sh
   $ tail -f output*.o


2. Open an SSH tunnel on your computer if you want to be able to access the web UI which is running
   on the compute node.

.. code-block:: console

   # This example uses the node r102u34. Change it to your compute node.
   $ ssh -L 8529:r102u34:8529 $USER@eagle.hpc.nrel.gov

3. Create a database for a workflow. You can use the web UI or ``arangosh``.

.. code-block:: console

    $ module load singularity-container
    $ mkdir arangodb3 arangodb3-apps
    $ singularity run \
          --network-args "portmap=8529:8529" \
          --env "ARANGO_ROOT_PASSWORD=openSesame" \
          -B arangodb3:/var/lib/arangodb3 \
          -B arangodb3-apps:/var/lib/arangodb3-apps \
          /datasets/images/arangodb/arangodb.sif \
          arangosh

You will be at a prompt like this::

    127.0.0.1:8529@_system>

Here is the ``arangosh`` command to create a database. You can use any name; all examples in this
page use ``workflows``. Note that there can only be one workflow per database, but you can create
as many databases as you want.

.. code-block:: console

   127.0.0.1:8529@_system> db._createDatabase('workflows')

.. raw:: html

   <hr>

4. Build the API service package from your local clone of this repository. This is probably easier
   to do on your local computer. When there is a shared directory on Eagle, this step won't be
   necessary.

.. code-block:: console

    $ cd db_service
    $ npm install
    $ zip -r wms-service.zip manifest.json index.js src scripts

5. Use the foxx-cli Singularity container to install the API service. This can be done on a login
   node. Change the IP address to the database compute node if you are not already on that node.
   You will be prompted for your password. If you don't have authentication enabled, exclude the
   ``--password`` option.

.. code-block:: console

    $ module load singularity-container
    $ singularity run -B /scratch:/scratch \
        /scratch/dthom/containers/foxx.sif install \
        --server http://127.0.0.1:8529 \
        --database workflows \
        -username root \
        -password \
        /wms-service \
        /scratch/dthom/wms/wms-service.zip
    $ singularity run -B /scratch:/scratch \
        /scratch/dthom/containers/foxx.sif set-dev \
        --server http://127.0.0.1:8529 \
        --database workflows \
        -username root \
        -password \
        --server http://127.0.0.1:8529 \
        /wms-service

You can install foxx-cli in your environment if you prefer, but you need ``npm`` installed.

.. code-block:: console

    $ npm install --global foxx-cli

.. raw:: html

   <hr>

6. Test the installation.

   Test the endpoint by running this command to get an example workflow. (``jq`` is not required
   but generally useful for displaying and filtering JSON output).


.. code-block:: console

    $ curl --silent -X GET http://localhost:8529/_db/workflows/wms-service/workflow/example | jq .
