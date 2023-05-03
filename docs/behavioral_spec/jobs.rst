####
Jobs
####


.. _job_status:

Job Statuses
============
The torc worker application and database service manage job status according to the rules shown
here.

- **uninitialized**: Initial state. Not yet known if it is blocked or ready.
- **ready**: The job can be submitted.
- **blocked**: The job cannot start because of dependencies.
- **submitted_pending**: The job was given to a compute node but is not yet running.
- **submitted**: The job is running on a compute node.
- **terminated**: Compute node timeout occurred and the job was notified to checkpoint and shut
  down.
- **done**: The job finished. It may or may not have completed successfully.
- **canceled**: A blocking job failed and so the job never ran.
- **disabled**: The job cannot run or change state.

.. graphviz::

   digraph job_statuses {
      "uninitialized" -> "ready";
      "uninitialized" -> "blocked";
      "uninitialized" -> "disabled";
      "disabled" -> "uninitialized";
      "ready" -> "submitted_pending";
      "ready" -> "scheduled";
      "submitted_pending" -> "submitted";
      "submitted_pending" -> "canceled";
      "scheduled" -> "submitted";
      "submitted" -> "done";
      "submitted" -> "terminated";
      "blocked" -> "canceled";
      "blocked" -> "ready";
   }

Scheduled jobs
--------------
If you set the ``scheduler`` and ``needs_compute_node_schedule`` fields of a job specification
then torc will schedule a compute node allocation for that job when it reaches the ``ready`` state.
At that time torc will set the job status to ``scheduled``. Any compute node with the required
resources can still acquire that job.

Job run ID
==========
Each job has a ``run_id`` attribute. The torc worker application increments its value every time it
runs a job. This allows you to compare results and utilization stats across workflow restarts.
