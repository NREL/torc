Parallelization within a compute node
=====================================
Torc attempts to maximize parallelization of jobs on a single node based on the job resource
requirement definitions. Be aware of the fact that the default number CPUs for a job is one, and so
it is critical that you define these values conservatively. Refer to
:ref:`job_resource_requirements` for more information.

If all jobs have similar resource requirements then you can set the option ``--max-parallel-jobs``
in the ``torc hpc slurm schedule-nodes`` command and avoid having to define the job requirements.
Torc will use that parameter to limit concurrent jobs on each compute node.
