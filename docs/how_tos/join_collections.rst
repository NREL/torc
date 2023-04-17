################
Join Collections
################

There are several scenarios where you will want to see the contents of two collections joined by a
common key. One example is viewing job and result tables together. Torc often stores these types
of relationships with edges in the graph database.

The torc HTTP API provides commands to join these collections.

Torc CLI
========
The torc CLI toolkit provides the easiest way to join these collections. Look at the help of this
command.

.. code-block:: console

    torc collections join --help
    Usage: torc collections join [OPTIONS] {compute-node-executed-jobs|compute-
                                 node-utilization|job-blocks|job-needs-file|job-
                                 produces-file|job-requirements|job-results|job-
                                 schedulers|job-process-utilization|job-stores-
                                 data}

      Perform a join of collections from a pre-set configuration.

      Examples:
      1. Show jobs and results in a table.
         $ torc collections join job-results
      2. Show jobs and results in JSON format.
         $ torc -F JSON collections join job-results

    Options:
      -l, --limit INTEGER  Limit the output to this number of jobs.
      -s, --skip INTEGER   Skip this number of jobs.
      --help               Show this message and exit

Take one example:

.. code-block:: console

    $ torc collections join job-results

    +----------------------------------------------------------------------------------------------------------------------------+
    |                            jobs with edge='returned' direction='outbound' in workflow 95639437                             |
    +-------+-----------+-----------+-----------+----------------+----------------------+----------------------------+-----------+
    | index | from__key | from_name | to_run_id | to_return_code | to_exec_time_minutes |     to_completion_time     | to_status |
    +-------+-----------+-----------+-----------+----------------+----------------------+----------------------------+-----------+
    |   0   |  95639561 |   small   |     1     |       0        |  1.0095648964246113  | 2023-04-16T18:29:02.972248 |    done   |
    |   1   |  95639573 |   medium  |     1     |       0        |  1.0064559698104858  | 2023-04-16T18:29:03.004850 |    done   |
    |   2   |  95639585 |   large   |     1     |       0        |  1.0041922012964883  | 2023-04-16T18:29:03.032915 |    done   |
    +-------+-----------+-----------+-----------+----------------+----------------------+----------------------------+-----------+

Refer to the help for all possibilities.

.. note:: Setting the output format to JSON with ``torc -F JSON`` may be helpful for this command.

Flexible Torc CLI
=================
The above CLI command actually invokes a much more flexible CLI command:

.. code-block:: console

    torc collections join-by-edge --help
    Usage: torc collections join-by-edge [OPTIONS] COLLECTION EDGE

      Join a collection with one or more other collections connected by an edge.

    Options:
      --outbound / --inbound   Inbound or outbound edge.  [default: outbound]
      -l, --limit INTEGER      Limit the output to this number of jobs.
      -s, --skip INTEGER       Skip this number of jobs.
      -x, --exclude-from TEXT  Exclude this base column name on the from side.
                               Accepts multiple
      -y, --exclude-to TEXT    Exclude this base column name on the to side.
                               Accepts multiple
      --help                   Show this message and exit.

You can use this command to view any collection + edge in either direction as well as limit the
display to custom columns.

HTTP API
========
The format of the HTTP commands is:

- GET /workflows/:key/join_by_inbound_edge/:collection/:edge
- GET /workflows/:key/join_by_outbound_edge/:collection/:edge

Example:

.. code-block:: console

    $ curl --silent -X GET http://localhost:8529/_db/workflows/torc-service/workflows/95612117/join_by_outbound_edge/jobs/returned | jq .

    {
      "items": [
        {
          "from": {
            "_key": "95612239",
            "_id": "jobs__95612117/95612239",
            "_rev": "_f2v-wWS---",
            "name": "small",
            "command": "python tests/scripts/resource_consumption.py -i 1 -c small",
            "cancel_on_blocking_job_failure": true,
            "supports_termination": false,
            "run_id": 2,
            "status": "done"
          },
          "to": {
            "_key": "95612607",
            "_id": "results__95612117/95612607",
            "_rev": "_f2Vuclq---",
            "job_key": "95612239",
            "job_name": "small",
            "run_id": 1,
            "return_code": 0,
            "exec_time_minutes": 1.0095913807551067,
            "completion_time": "2023-04-15T11:22:24.711032",
            "status": "done"
          }
        },
      ]
    }
