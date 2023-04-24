###################
HPC Multi-Node Jobs
###################

Here's how to run multi-node jobs with torc:

1. Set the ``nodes`` parameter in your Slurm configuration in your workflow specification file.

.. code-block:: JavaScript

    schedulers: {
      slurm_schedulers: [
        {
          name: "multi-node",
          account: "my_account",
          walltime: "48:00:00",
          nodes: 5,
        }
      ],
    },

2. Develop your job script to be the manager of the overall effort. Torc will start it on the first
   compute node in the allocation. Your script should then detect the other compute nodes and
   distribute the work.

   You can run Slurm commands to find the hostnames or make a torc API call. The Slurm commmands
   are:

.. code-block:: console

   $ scontrol show hostnames "$(squeue -j ${SLURM_JOB_ID} --format='%500N' -h)"

The torc API command is like this:

.. code-block:: python

    from torc.hpc.slurm_interface import SlurmInterface

    intf = SlurmInterface()
    job_id = intf.get_current_job_id(job_id)
    nodes = intf.list_active_nodes(job_id)
