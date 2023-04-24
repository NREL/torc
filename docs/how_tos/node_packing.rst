############
Node Packing
############
Node packing is a paradigm where you allocate an entire compute node for period of time and then
run as many jobs as possible in parallel given CPU and memory constraints. For example, if your
compute node has 36 CPUs and 92 GB of memory and each job consumes 1 CPU and 2 GB of memory, you
can run 36 jobs at once. Furthermore, if it takes a long time to acquire a compute node and your
jobs are relatively short, you can keep that node for as long as possible.

Here's how to employ node packing with Torc. This example assumes an HPC environment with Slurm and
that you are defining your workflow in a workflow specification file as described in
:ref:`workflow_specification`.

1. Maximize the ``walltime`` in your ``slurm_scheduler`` configuration. This could be 48 hours for
   the standard queue or 4 hours for the short queue.

.. code-block:: JavaScript

    schedulers: {
      slurm_schedulers: [
        {
          name: "standard",
          account: "my_account",
          walltime: "48:00:00",
        }
      ],
    },


2. Define a ``resource_requirements`` configuration for each class of job. Be sure to specify
   ``num_cpus``, ``memory``, and ``runtime``.

.. code-block:: JavaScript

    resource_requirements: [
      {
        name: "small",
        num_cpus: 1,
        num_gpus: 0,
        num_nodes: 1,
        memory: "2g",
        runtime: "P0DT30M"
      },
    ],

3. Specify a ``resource_requirements`` name for each job.

4. If you will schedule different types of compute nodes then specify a ``scheduler`` for each job.
   This field uses the format ``<scheduler_config_type>/<scheduler_config_name>`` (e.g.,
   `slurm_schedulers/standard`). If you only have one scheduler type, torc will use it for all
   jobs.

.. code-block:: JavaScript

    jobs: [
      {
        name: "work1",
        command: "python work.py",
        scheduler: "slurm_schedulers/standard",
        resource_requirements: "small",
      }
    ]
