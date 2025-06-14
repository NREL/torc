# Resource Utilization Statistics

Torc will optionally monitor resource utilization on compute nodes.

## Configuration

You can define these settings in the `config` field of the workflow specification JSON5 file.

```JavaScript
config: {
  compute_node_resource_stats: {
    cpu: true,
    disk: false,
    memory: true,
    network: false,
    process: true,
    include_child_processes: true,
    recurse_child_processes: false,
    monitor_type: "aggregation",
    make_plots: true,
    interval: 10,
  }
}
```

Setting `cpu`, `disk`, `memory`, or `network` to true will track those resources on the
compute node overall. Setting `process` to true will track CPU and memory usage on a per-job
basis.

You can set `monitor_type` to these options:

- `aggregation`: Track min/max/average stats in memory and record the results in the database.
- `periodic`: Record time-series data on an interval in per-node SQLite database files
  (`<output-dir>/stats/*.sqlite`).

If `monitor_type = periodic` and `make_plots = true` then torc will generate HTML plots of the
results (`<output-dir>/stats/*.html`).

## Aggregated Stats

The commands below will print summaries of the stats in the terminal. These stats are stored in the
database.

```console
$ torc jobs list-process-stats
```

```console
$ torc compute-nodes list-resource-stats
```

## Time Series Stats

If you set `monitor_type = periodic` in the config then you will one SQLite file per compute node
in `<output-dir>/stats/*.sqlite`. Here are some example commands.

```console
$ sqlite3 -table output/stats/compute_node_98209950.sqlite
SQLite version 3.41.2 2023-03-22 11:56:21
sqlite> .tables
cpu      disk     memory   network  process
```

```console
$ sqlite> select * from cpu;
+------+------+--------+------+-------------+----------------------------+
| user | nice | system | idle | cpu_percent |         timestamp          |
+------+------+--------+------+-------------+----------------------------+
| 2.0  | 0.0  | 2.0    | 10.0 | 28.6        | 2023-04-28 13:51:42.655853 |
| 0.0  | 0.0  | 0.0    | 0.0  | 0.0         | 2023-04-28 13:51:46.350560 |
| 16.1 | 0.0  | 7.4    | 76.5 | 23.5        | 2023-04-28 13:51:49.541241 |
| 11.0 | 0.0  | 10.8   | 78.2 | 21.8        | 2023-04-28 13:51:51.702789 |
| 10.3 | 0.0  | 8.1    | 81.6 | 18.4        | 2023-04-28 13:51:52.832309 |
| 11.5 | 0.0  | 1.8    | 86.7 | 13.3        | 2023-04-28 13:51:53.966989 |
| 9.4  | 0.0  | 3.5    | 87.1 | 12.9        | 2023-04-28 13:51:54.175749 |
+------+------+--------+------+-------------+----------------------------
```

```console
$ sqlite> select timestamp, available / (1024*1024*1024) as available_gb, percent from memory;
+----------------------------+--------------+---------+
|         timestamp          | available_gb | percent |
+----------------------------+--------------+---------+
| 2023-04-28 13:51:42.655853 | 17           | 45.6    |
| 2023-04-28 13:51:46.350560 | 17           | 45.6    |
| 2023-04-28 13:51:49.541241 | 16           | 47.0    |
| 2023-04-28 13:51:51.702789 | 17           | 46.6    |
| 2023-04-28 13:51:52.832309 | 17           | 45.6    |
| 2023-04-28 13:51:53.966989 | 17           | 45.8    |
| 2023-04-28 13:51:54.071424 | 17           | 45.2    |
+----------------------------+--------------+---------+
```

```console
$ sqlite> select timestamp, job_key, cpu_percent, rss / (1024*1024*1024) AS rss_gb from process;
+----------------------------+----------+-------------+--------------------+
|         timestamp          | job_key  | cpu_percent |       rss_gb       |
+----------------------------+----------+-------------+--------------------+
| 2023-04-28 13:51:46.350560 | 98207990 | 82.8        | 0.331188201904297  |
| 2023-04-28 13:51:46.350560 | 98208002 | 0.0         | 0.396995544433594  |
| 2023-04-28 13:51:49.541241 | 98207918 | 0.0         | 0.0418891906738281 |
| 2023-04-28 13:51:49.541241 | 98207930 | 0.0         | 0.0420913696289062 |
| 2023-04-28 13:51:49.541241 | 98207954 | 0.0         | 0.216609954833984  |
| 2023-04-28 13:51:49.541241 | 98207966 | 0.0         | 0.0409011840820312 |
| 2023-04-28 13:51:49.541241 | 98207990 | 0.0         | 0.0354042053222656 |
| 2023-04-28 13:51:49.541241 | 98208002 | 0.0         | 0.0270614624023437 |
| 2023-04-28 13:51:51.702789 | 98207954 | 0.0         | 0.041168212890625  |
| 2023-04-28 13:51:51.702789 | 98207966 | 0.0         | 0.0479011535644531 |
| 2023-04-28 13:51:51.702789 | 98207990 | 0.0         | 0.0424423217773437 |
| 2023-04-28 13:51:51.702789 | 98208002 | 0.0         | 0.0340538024902344 |
| 2023-04-28 13:51:52.832309 | 98207990 | 83.2        | 0.293796539306641  |
| 2023-04-28 13:51:52.832309 | 98208002 | 0.0         | 0.410999298095703  |
| 2023-04-28 13:51:53.966989 | 98207990 | 0.0         | 0.0494346618652344 |
| 2023-04-28 13:51:53.966989 | 98208002 | 0.0         | 0.0381813049316406 |
+----------------------------+----------+-------------+--------------------+
```

### Time Series Job-Process Stats

As stated above, torc records time-series stats in one SQLite file per compute node. This is
inconvenient for job-process stats. You typically want to look at all process stats together rather
than have them separated by compute node. Torc provides a CLI command to concatenate them in one
file.

```console
$ torc stats concatenate-process output/stats
2023-04-27 17:01:10,907 - INFO [torc.utils.sql sql.py:103] : Added table process from output/stats/compute_node_98209951.sqlite to output/stats/job_process_stats.sqlite
2023-04-27 17:01:10,909 - INFO [torc.utils.sql sql.py:103] : Added table process from output/stats/compute_node_98209950.sqlite to output/stats/job_process_stats.sqlite
```
