(results)=

# Results

This section describes how to view and filter results from torc workflows.

```console
$ torc results list

 +-------------------------------------------------------------------------------------------------------------------+
 |                                   Results in workflow 10729055                                                    |
 +-------+-----------+----------+--------+-------------+-------------------+---------------------+--------+----------+
 | index | job_name  | job_key  | run_id | return_code | exec_time_minutes |   completion_time   | status |   key    |
 +-------+-----------+----------+--------+-------------+-------------------+---------------------+--------+----------+
 |   0   |   job1    | 10729174 |   1    |      0      | 36.4065907200177  | 2023-06-21T17:01:36 |  done  | 10794865 |
 |   1   |   job2    | 10729182 |   1    |      0      | 42.4065045873324  | 2023-06-21T17:01:36 |  done  | 10794909 |
 |   2   |   job3    | 10729190 |   1    |      0      | 29.4064182003339  | 2023-06-21T17:01:36 |  done  | 10794953 |
 |   3   |   job4    | 10729198 |   1    |      0      | 31.4063104391098  | 2023-06-21T17:01:36 |  done  | 10794997 |
 +-------------------------------------------------------------------------------------------------------------------+
```

```{eval-rst}
.. warning:: torc will increment the ``run_id`` field every time you run the workflow. If you
   restart the workflow then you likely need to filter on a specific ID.
```

Here are some example commands with filters.

1. Filter results of the second run.

```console
$ torc results list -f run_id=2
```

2. Filter results that passed.

```console
$ torc results list -f return_code=0
```

3. Filter results that failed with a return code of 1.

```console
$ torc results list -f return_code=1
```

Refer to {ref}`join-collections` if you would like to see more fields from the jobs collection in
the output.

Refer to {ref}`query-with-sql` if you would like to run more sophisticated queries or if you would
like to run queries across multiple workflows.

```{toctree}
:hidden: true
:maxdepth: 3

join_collections
query_with_sql
```
