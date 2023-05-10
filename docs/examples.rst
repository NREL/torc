.. _examples:

########
Examples
########
The torc repository contains example workflows at
https://github.nrel.gov/viz/wms/tree/main/examples. If you install the torc Python package and have
access to a database, you can run the examples listed on this page to learn how torc works.

1. Clone the torc repository.

.. code-block:: console

    $ git clone https://github.nrel.gov/viz/wms.git

2. Change to the ``torc`` directory so that you have access to the torc test scripts.

.. code-block:: console

    $ cd wms/torc

3. Create a torc runtime configuration file. We will use it shorten the commands that we type
   below. Change ``<hostname>`` and ``<database-name>`` to correct values for your database
   (without the ``<>``).

.. code-block:: console

    $ torc config create -u http://<hostname>:8529/_db/<database-name>/torc-service
    Wrote torc config to /Users/dthom/.torc.json5

Diamond Workflow
================
The workflow specification file ``examples/diamond_workflow.json5`` creates a workflow with four
jobs that have dependencies based on the files that the jobs produce and consume. This is the same
workflow described at :ref:`overview`.

You can run this workflow on a laptop.

Ensure that you are in the ``torc`` directory. It has a ``tests`` subdirectory which is required by
this workflow.

1. Create the directory and file needed by the first job.

.. code-block:: console

    $ mkdir output
    $ echo "{\"val\": 5}" > output/inputs.json

2. Create the workflow. The ``-U`` option will update the ``rc`` file with the newly-created
   workflow key.

.. code-block:: console

    $ torc workflows create-from-json-file ../examples/diamond_workflow.json5 -U
    2023-04-28 11:49:07,932 - INFO [torc.cli.workflows workflows.py:218] : Created a workflow from ../examples/diamond_workflow.json5 with key=98178840
    2023-04-28 11:49:07,934 - INFO [torc.cli.workflows workflows.py:560] : Updating /Users/dthom/.torc.json5 with workflow_key=98178840
    Wrote torc config to /Users/dthom/.torc.json5

3. Start the workflow. This will check required inputs and initialize the job statuses.

.. code-block:: console

    $ torc workflows start
    2023-04-28 11:50:09,206 - INFO [torc.workflow_manager workflow_manager.py:114] : Started workflow

4. Check the configuration and statuses.

.. code-block:: console

    $ torc jobs list
    +-----------------------------------------------------------------------------------------------------------------------------------------------+
    |                                                           Jobs in workflow 98178840                                                           |
    +-------+-------------+-------------------------------------------------------------------------------------------+---------+--------+----------+
    | index |     name    |                                          command                                          |  status | run_id |   key    |
    +-------+-------------+-------------------------------------------------------------------------------------------+---------+--------+----------+
    |   0   |  preprocess |         python tests/scripts/preprocess.py -i output/inputs.json -o output/f1.json        |  ready  |   0    | 98178995 |
    |   1   |    work1    |              python tests/scripts/work.py -i output/f1.json -o output/f2.json             | blocked |   0    | 98179023 |
    |   2   |    work2    |              python tests/scripts/work.py -i output/f1.json -o output/f3.json             | blocked |   0    | 98179057 |
    |   3   | postprocess | python tests/scripts/postprocess.py -i output/f2.json -i output/f3.json -o output/f4.json | blocked |   0    | 98179091 |
    +-------+-------------+-------------------------------------------------------------------------------------------+---------+--------+----------+

5. Make a visualization of the job dependencies.

.. code-block:: console

    $ torc graphs plot job_job_dependencies job_file_dependencies
    2023-04-28 11:55:25,692 - INFO [torc.cli.graphs graphs.py:73] : Created graph image file output/job_job_dependencies.dot.png
    2023-04-28 11:55:25,902 - INFO [torc.cli.graphs graphs.py:73] : Created graph image file output/job_file_dependencies.dot.png

Open the resulting files in an image viewer.

6. Run the workflow locally. The ``-p1`` option tells torc to poll for completions every second.
   These jobs are quick and so there is no reason to wait for the default polling interval.

.. code-block:: console

    $ torc jobs run -p 1

7. View the results.

.. code-block:: console

    $ torc results list
    +-----------------------------------------------------------------------------------------------------------------+
    |                                           Results in workflow 98178840                                          |
    +-------+----------+--------+-------------+----------------------+----------------------------+--------+----------+
    | index | job_key  | run_id | return_code |  exec_time_minutes   |      completion_time       | status |   key    |
    +-------+----------+--------+-------------+----------------------+----------------------------+--------+----------+
    |   0   | 98178995 |   1    |      0      | 0.01993496815363566  | 2023-04-29T11:53:21.728950 |  done  | 98179560 |
    |   1   | 98179023 |   1    |      0      | 0.050372012456258136 | 2023-04-29T11:53:24.908490 |  done  | 98179743 |
    |   2   | 98179057 |   1    |      0      | 0.04883763392766317  | 2023-04-29T11:53:24.966426 |  done  | 98179793 |
    |   3   | 98179091 |   1    |      0      | 0.04541379610697428  | 2023-04-29T11:53:27.917966 |  done  | 98179916 |
    +-------+----------+--------+-------------+----------------------+----------------------------+--------+----------+

8. View the jobs joined with the results.

.. code-block:: console

    $ torc collections join job-results
    +------------------------------------------------------------------------------------------------------------------+
    |                       jobs with edge='returned' direction='outbound' in workflow 98178840                        |
    +-------+-------------+-----------+----------------+----------------------+----------------------------+-----------+
    | index |  from_name  | to_run_id | to_return_code | to_exec_time_minutes |     to_completion_time     | to_status |
    +-------+-------------+-----------+----------------+----------------------+----------------------------+-----------+
    |   0   |  preprocess |     1     |       0        | 0.01993496815363566  | 2023-04-29T11:53:21.728950 |    done   |
    |   1   |    work1    |     1     |       0        | 0.050372012456258136 | 2023-04-29T11:53:24.908490 |    done   |
    |   2   |    work2    |     1     |       0        | 0.04883763392766317  | 2023-04-29T11:53:24.966426 |    done   |
    |   3   | postprocess |     1     |       0        | 0.04541379610697428  | 2023-04-29T11:53:27.917966 |    done   |
    +-------+-------------+-----------+----------------+----------------------+----------------------------+-----------+

Slurm Diamond Workflow
======================
This example is similar to the previous example. It has these differences:

- It must be run on an HPC with the Slurm scheduler.
- It uses a default compute node as well as one with GPUs.
- It uses torc's delayed-compute-node-scheduling feature.

Follow the same steps except for these deviations:

1. Use the workflow specification file ``examples/slurm_diamond_workflow.json5``.
2. Change the Slurm account name.
3. Configure and start the workflow from an HPC login node.
4. Instead of ``torc jobs run``, schedule a compute node to run the jobs with

.. code-block:: console

    $ torc hpc slurm schedule-nodes -n 1

Torc will schedule the second node with GPUs when the postprocess script is ready to run.

CPU Affinity Workflow
=====================
This workflow demonstrates how to set CPU affinity for all job processes. Refer to
:ref:`set_cpu_affinity` for more information about this feature.

The workflow must be run on an HPC with the Slurm scheduler. The steps are similar to the other
Slurm workflows except that you must set the additional parameter below when you schedule nodes.
The job script in this example assumes 9 CPUs per job.

Use the workflow specification file ``examples/slurm_cpu_affinity_workflow.json5``.

.. code-block:: console

    $ torc hpc slurm schedule-nodes -n 1 --cpu-affinity-cpus-per-job 9
