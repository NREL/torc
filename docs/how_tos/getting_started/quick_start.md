# Quick Start

This page assumes that you have a database and have completed the torc installation instructions.
Refer to {ref}`database-installation` if you haven't set up a database yet.

If you have not globally configured a connection to your database, refer to {ref}`database-connection`.

This page runs a trivial workflow. Please refer to the [torc examples]
(https://github.com/NREL/torc/tree/main/examples) or {ref}`tutorials` for more complex workflows.

## Create a workflow

1. Create a text file with one command per line. Here is one example file with dummy commands:

   ```console
   $ cat commands.txt
   echo "Hello, World!"
   echo "Hello, World!"
   echo "Hello, World!"
   echo "Hello, World!"
   echo "Hello, World!"
   ```

2. Create the workflow.

   ```console
   $ torc workflows create-from-commands-file \
       --name my-workflow \
       --description "My workflow" \
       --cpus-per-job=1 \
       --memory-per-job=1g \
       --runtime-per-job=P0DT1H \
       commands.txt
   ```

    ```console
   2023-04-10 10:52:52,240 - INFO [torc.cli.workflows workflows.py:144] : Created a workflow from commands.txt with key=94956990
   ```

3. If you are in an HPC environment, add a Slurm scheduler configuration. If you are running locally,
   skip this step. Change `account` to your HPC account.

   ```console
   $ torc hpc slurm add-config -a account -w 01:00:00 -N debug-config -p debug
   ```

4. Start the workflow. This initializes the jobs, but does not run them yet.

   ```console
   $ torc -k 94956990 workflows start
   2023-03-28 16:37:58,708 - INFO [torc.workflow_manager workflow_manager.py:99] : Started workflow
   ```

5. Start a worker to run the jobs.

   If you are running locally, start a local worker.

   ```console
   $ torc -k 94956990 jobs run -p 1
   ```

   If you are running in an HPC environment, start a worker with the Slurm scheduler.
   This will schedule one compute node with the Slurm scheduler defined in step 3.

    ```console
    $ torc -k 94956990 hpc slurm schedule-nodes -n 1
    ```

6. Monitor progress with torc or, if using an HPC with Slurm, `squeue`.

   ```console
   $ torc -k 94956990 jobs list
   ```

   ```console
   $ watch -n 10 squeue -u $USER
   ```

7. View the results when the workflow is complete.

   ```console
   $ torc -k 94956990 results list
   ```
