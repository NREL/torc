# HPC Quick Start

This page assumes that you have a database and have completed the torc installation instructions.

You will have to use your own workflow scripts to follow along here. Refer to {ref}`tutorials` to
run pre-defined workflows stored inside the torc repository.

1. ssh to a login node on your HPC.
2. Persist the database URL in your environment. Replace the hostname and database name.

```console
$ torc config create -u http://<database_hostname>:8529/_db/<database_name>/torc-service
Wrote torc config to /Users/dthom/.torc_settings.toml
```

3. Create a text file with one command per line. Here are contents of one such file:

```console
$ cat commands.txt
bash my_script1.sh 1
bash my_script1.sh 2
```

4. Create the workflow.

```console
$ torc workflows create-from-commands-file -n my-workflow -d "My workflow" --cpus-per-job=4 --memory="5g" --runtime=P0DT1H commands.txt
2023-04-10 10:52:52,240 - INFO [torc.cli.workflows workflows.py:144] : Created a workflow from commands.txt with key=94956990
```

5. Add an HPC scheduler. Change `account` to your HPC account.

```console
$ torc hpc slurm add-config -a account -w 04:00:00 -N short
```

6. Start the workflow.

```console
$ torc -k 94956990 workflows start
2023-03-28 16:37:58,708 - INFO [torc.workflow_manager workflow_manager.py:99] : Started workflow
```

7. Schedule compute nodes where X below is the number of HPC jobs to start with the scheduler
   defined in step 6. Note that there could be multiple compute nodes in each HPC job.

```console
$ torc -k 94956990 hpc slurm schedule-nodes -n X
```

You can optionally ask for a recommendation for the number of nodes with this command:

```console
$ torc workflows recommend-nodes --num-cpus 36
```

8. Monitor progress with torc or squeue

```console
$ torc -k 94956990 jobs list
```

```console
$ watch -n 10 squeue -u $USER
```

Refer to {ref}`workflow-key-shortcuts` for instructions on how to avoid typing the key repeatedly.
