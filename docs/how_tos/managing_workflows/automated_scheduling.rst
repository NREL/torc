.. _automated-scheduling:

Automated scheduling
====================
By default, torc leaves scheduling of compute nodes to the user. If you know that an
initially-blocked job will need a specific compute node (or nodes), you can tell torc to schedule
it for you when all other conditions are met.

Define the ``schedule_compute_nodes`` object in the ``JobModel``. For example,

.. code-block:: python

    from torc.openapi_client.models.compute_node_schedule_params import ComputeNodeScheduleParams
    from torc.openapi_client.models.job_model import JobModel
    from torc.openapi_client.models.slurm_scheduler_model import SlurmSchedulerModel

    short_scheduler = api.add_slurm_scheduler(
        workflow.key,
        SlurmSchedulerModel(
            name="short",
            account="my_account",
            nodes=1,
            walltime="04:00:00",
        ),
    )
    job = JobModel(
        name="job1",
        command=f"python job.py",
        resource_requirements=medium.id,
        schedule_compute_nodes=ComputeNodeScheduleParams(
            num_jobs=1,
            scheduler=short_scheduler.id,
        )
    ),

When that job reaches the ``ready`` status, torc will send the schedule command with those
parameters.

.. note:: If one new compute node allocation can satisfy multiple jobs that will be ready at about
   the same time, you can set these fields for only one job. Setting it for multiple jobs may
   result in extra, unnecessary allocations.
