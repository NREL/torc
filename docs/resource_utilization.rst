###############################
Resource Utilization Statistics
###############################

Torc will optionally monitor resource utilization on compute nodes. You can define these settings
in the ``config`` field of the workflow specification JSON5 file.

.. code-block:: JavaScript

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
       interval: 1
     }
   }

Setting ``cpu``, ``disk``, ``memory``, or ``network`` to true will track those resources on the
compute node overall. Setting ``process`` to true will track CPU and memory usage on a per-job
basis.

You can set ``monitor_type`` to these options:

- ``aggregation``: Track min/max/average stats in memory and record the results in the database.
- ``periodic``: Record time-series data on an interval in per-node SQLite database files
  (``<output-dir>/stats/*.sqlite``).

If ``monitor_type = periodic`` and ``make_plots = true`` then torc will generate HTML plots of the
results.

These command will print summaries of the stats in the terminal:

.. code-block:: console

   $ torc jobs list-process-stats

.. code-block:: console

   $ torc compute-nodes list-resource-stats
