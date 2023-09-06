.. _check-status:

#####################
Check workflow status
#####################

TUI
===
The torc terminal-based management console provides views of job status and results.

.. code-block:: console

   $ torc tui

Monitor events
==============
The torc worker app posts events to the database whenever compute nodes start and stop and jobs
start and complete. Monitor these events dynamically with this command:

.. code-block:: console

   $ torc events monitor

Job status
==========
Monitor progress with torc or squeue.

.. code-block:: console

   $ watch -n 10 squeue -u $USER

.. code-block:: console

   $ torc jobs list

After a job completes its status will be be ``done``. You can filter the jobs to see how many
are ready, in progress, and done

.. code-block:: console

   $ torc jobs list -f status=ready

.. code-block:: console

   $ torc jobs list -f status=submitted

.. code-block:: console

   $ torc jobs list -f status=done

Return codes
============
This commmand will show the job results. A ``return_code`` of 0 is successful. Non-zero is a
failure.

.. code-block:: console

   $ torc results list

You can filter the output to see only passes or only failures.

.. code-block:: console

   $ torc results list -f return_code=0

.. code-block:: console

   $ torc results list -f return_code=1
