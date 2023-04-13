###############
HPC Quick Start
###############
This page assumes that you have a database and have completed the torc installation instructions.

1. ssh to a login node on your HPC.
2. Persist the database URL in your environment. Replace the hostname and database name.

.. code-block:: console

   $ torc config create -u http://<database_hostname>:8529/_db/<database_name>/torc-service

.. code-block:: console

   Wrote torc config to /Users/dthom/.torc.json5

3. Create a text file with one command per line. Here are contents of one such file:

.. code-block:: console

   $ cat commands.txt
   bash my_script1.sh 1
   bash my_script1.sh 2

4. Create the workflow.

.. code-block:: console

   $ torc workflows create-from-commands-file -n my-workflow -d "My workflow" commands.txt

.. code-block:: console

   2023-04-10 10:52:52,240 - INFO [torc.cli.workflows workflows.py:144] : Created a workflow from commands.txt with key=94956990

5. Add an HPC scheduler. Change ``account`` to your HPC account.

.. code-block:: console

   $ torc hpc slurm add-config -a <account> -w 04:00:00 -N short

6. Start the workflow.

.. code-block:: console

   $ torc -k 94956990 workflows start

.. code-block:: console

   2023-03-28 16:37:58,708 - INFO [torc.workflow_manager workflow_manager.py:99] : Started workflow

7. Schedule HPC nodes where X below is the number of nodes to acquire with the scheduler defined
   in step 5.

.. note:: This step will not always be required. We plan to do this automatically.

.. code-block:: console

   $ torc -k 94956990 hpc slurm schedule-nodes -nX

8. Monitor progress with torc or squeue

.. code-block:: console

   $ torc -k 94956990 jobs list

.. code-block:: console

   $ watch -n 10 squeue -u $USER

Refer to :ref:`workflow_key_shortcuts` for instructions on how avoid typing the key constantly.
