.. _slurm-diamond-workflow:

######################
Slurm Diamond Workflow
######################
In this tutorial you will learn how to run a workflow on an HPC that uses the ``Slurm`` scheduler
with these torc features:

- Job dependencies based on input and output files
- Jobs with different compute node requirements
- Delayed compute node scheduling

The workflow is a derivation of the :ref:`diamond-workflow`. Follow the same steps except for these
deviations:

1. Use the workflow specification file ``examples/slurm_diamond_workflow.json5``.
2. Change the Slurm account name.
3. Configure and start the workflow from an HPC login node.
4. Instead of ``torc jobs run``, schedule a compute node to run the jobs with

.. code-block:: console

    $ torc hpc slurm schedule-nodes -n 1

Torc will schedule the second node with GPUs when the postprocess script is ready to run.
