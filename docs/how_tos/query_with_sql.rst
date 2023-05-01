##############
Query with SQL
##############
Users may prefer to use SQL to query results rather than the torc CLI or API, and so torc provides
a way to export the ArangoDB collections to SQLite. This page describes how to use that feature.

Export to SQLite
================
By default this command will export all worklows stored in the database. You can pass your desired
workflow keys as positional arguments to limit the exported tables.

.. code-block:: console

    $ torc export sqlite
    2023-04-28 15:00:31,205 - INFO [torc.cli.export export.py:116] : Exported database to workflow.sqlite for all workflows

.. note:: There is a significant difference between the ArangoDB contents and the SQLite file. The
   ArangoDB stores one set of collections for each workflow. The SQLite file stores each type of
   collection in the same table. For example, all jobs for all workflows are stored in the ``jobs``
   table.

SQL queries
===========
The ``sqlite3`` CLI tool provides a convenient interface to query the result file. If it is not
already installed in your environment, you should be able to install it with your package
management tool.

.. warning:: NREL's Eagle HPC environment has an old version of the tool that does not support
   ``sqlite3 -table``. Use ``sqlite3 -header -column`` instead.

View the tables
---------------
.. code-block:: console

    $ sqlite3 -table workflow.sqlite
    sqlite> .tables
    blocks                 needs                  slurm_schedulers
    consumes               produces               user_data
    events                 requires               workflow_configs
    files                  resource_requirements  workflow_statuses
    jobs                   scheduled_bys          workflows

View the jobs for one workflow
------------------------------
.. code-block:: console

    sqlite> SELECT key, name, status FROM jobs WHERE workflow_key = 98078061;
    +----------+-------------+--------+
    |   key    |    name     | status |
    +----------+-------------+--------+
    | 98078218 | preprocess  | done   |
    | 98078274 | work2       | done   |
    | 98078244 | work1       | done   |
    | 98078304 | postprocess | done   |
    +----------+-------------+--------+

Join jobs with results
----------------------
.. code-block:: console

    sqlite> SELECT jobs.name, results.return_code, results.status, results.exec_time_minutes
        FROM jobs
        JOIN results
        ON jobs.key = results.job_key
        WHERE jobs.workflow_key = 98078061;
    +-------------+-------------+--------+---------------------+
    |    name     | return_code | status |  exec_time_minutes  |
    +-------------+-------------+--------+---------------------+
    | preprocess  | 0           | done   | 0.00443786382675171 |
    | work2       | 0           | done   | 0.0314231514930725  |
    | work1       | 0           | done   | 0.0294709006945292  |
    | postprocess | 0           | done   | 0.0451397975285848  |
    +-------------+-------------+--------+---------------------+

Join jobs with process stats
----------------------------
.. code-block:: console

    sqlite> SELECT jobs.name, jobs.run_id, s.max_cpu_percent, s.max_rss
        FROM jobs
        JOIN job_process_stats AS s
        ON jobs.key == s.job_key
        WHERE jobs.workflow_key = 98081576;
    +-------------+--------+-----------------+-------------+
    |    name     | run_id | max_cpu_percent |   max_rss   |
    +-------------+--------+-----------------+-------------+
    | preprocess  | 1      | 82.4            | 433516544.0 |
    | work1       | 1      | 73.5            | 72708096.0  |
    | work2       | 1      | 78.7            | 167821312.0 |
    | postprocess | 1      | 90.5            | 389586944.0 |
    +-------------+--------+-----------------+-------------+
