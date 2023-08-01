#####################
Check workflow status
#####################
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

This commmand will show the job results. A ``return_code`` of 0 is successful. Non-zero is a
failure.

.. code-block:: console

   $ torc results list

You can filter the output to see only passes or only failures.

.. code-block:: console

   $ torc results list -f return_code=0

.. code-block:: console

   $ torc results list -f return_code=1
