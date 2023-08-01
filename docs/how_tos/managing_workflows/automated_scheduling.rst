.. _automated-scheduling:

Automated scheduling
====================
By default, torc leaves scheduling of compute nodes to the user. If you know that an
initially-blocked job will need a specific compute node (or nodes), you can tell torc to schedule
it for you when all other conditions are met.

Set the ``scheduler`` and ``needs_compute_node_schedule`` fields of the job in the workflow
specification file. When that job reaches the ``ready`` status, torc will send the schedule command
with the same parameters that were originally used.

.. note:: If one new compute node allocation can satisfy multiple jobs that will be ready at about
   the same time, you can set these fields for only one job. Setting it for multiple jobs may
   result in multiple allocations.
