##############################
Custom Invocation Environments
##############################
By default torc will run a job's ``command`` as a subprocess (and not in a shell). You may want to
alter the environment before invoking the actual work command. For example, you may want to load an
environment module or activate a conda environment.

Here are the steps to run a job in a conda environment that requires an HPC environment module.

1. Define your job's ``command`` as a CLI command that can run in a pre-defined conda environment
   with a custom invocation script. This example assumes that ``custom_env.sh`` is located in the
   current directory.

.. code-block:: JavaScript

    command: "python work.py arg1 arg2"
    invocation_script: "bash custom_env.sh"

2. Develop the ``invocation_script``. Here is a script that activates a conda environment and the
   invokes the command and arguments (``$@`` is a bash variable that includes all arguments passed
   on the command line).

.. code-block:: bash

    #!/bin/bash
    module load conda
    conda activate my-env
    $@

The command that torc will run is this:

.. code-block:: console

   $ bash custom_env.sh python work.py arg1 arg2

CPU control with Slurm
======================
If you are running jobs in an HPC environment with Slurm then you should consider using a custom
invocation environment where you run your job through ``srun``. Slurm provides functionality to
bind processes to specific cores for optimized execution in a particular system configuration. If
you allocate an entire node but only need a subset of CPUs for one job, you may benefit from the
Slurm feature set.

Let's suppose that your job's command is ``my_executable arg1 arg2``. Your custom invocation script
could be

.. code-block:: bash

    #!/bin/bash
    srun $@

where you pass other options to ``srun`` as described in Slurm documentation below.

- https://slurm.schedmd.com/cpu_management.html
- https://slurm.schedmd.com/mc_support.html

You can also run the command below and search for ``cpu-bind``.

.. code-block:: console

    $ pinfo srun
