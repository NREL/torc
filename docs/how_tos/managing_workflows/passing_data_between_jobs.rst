.. _passing-data-between-jobs:

#########################
Passing data between jobs
#########################
Other pages in this documentation describe how to declare dependencies between jobs through files.
It can often be more convenient to accomplish the same objective directly through the database.

Here are specifics steps to accomplish this using the Python API. You could achieve the same
result with the torc CLI, but the API is likely more convenient.

1. Declare the data in the ``user_data`` collection in your workflow specification JSON file.
   This is a placeholder for data that will be produced by a job.

.. code-block:: JavaScript

    user_data: [
      {
        name: "output_data1",
      }
    ]

2. Declare the jobs that will store and consume the data. Note that this process uses the ``name``
   field. When the workflow is uploaded to the database, torc will create relationships with keys,
   and you will use those keys.

   In this example torc will run work1.py before work2.py because it detects the dependency between
   the two jobs.

.. code-block:: JavaScript

    jobs: [
      {
        command: "python work1.py",
        stores_user_data: ["output_data1"],
      },
      {
        command: "python work2.py",
        consumes_user_data: ["output_data1"],
      }
    ]

3. Develop code in your scripts to store and retrive the data.

Here is code to connect to the database and identify your job. This example relies on database
settings in ``~/.torc.json5``. Refer to ``torc config --help`` for more information.

.. code-block:: python

    import os

    from torc.api import make_api
    from torc.torc_rc import TorcRuntimeConfig

    config = TorcRuntimeConfig.load()
    api = make_api(config.database_url)
    workflow_key = os.environ["TORC_WORKFLOW_KEY"]
    job_key = os.environ["TORC_JOB_KEY"]

Here is code in ``work1.py`` to identify the data object in the database, add data, and then upload
it to the database.

.. code-block:: python

    result = api.get_workflows_workflow_jobs_key_user_data_stores(workflow_key, job_key)
    output_data1 = result.items[0]
    output_data1.data = {"result": 1.2}
    api.put_workflows_workflow_user_data_key(spark_ud, workflow_key, output_data1.key)

Here is code in ``work2.py`` to read the data from the database.

.. code-block:: python

    result = api.get_workflows_workflow_jobs_key_user_data_consumes(workflow_key, job_key)
    output_data1 = result.items[0]

Here is a comparable example with a CLI command that joins the job and user_data collections and
filters on the job consuming the data. You would need to parse the JSON yourself.

.. code-block:: console

    $ torc -k $TORC_WORKFLOW_KEY -F json collections join job-consumes-data -f key=$TORC_JOB_KEY
    {
      "items": [
        {
          "from": {
            "_key": "96282248",
            "name": "name: "my_job""
          },
          "to": {
            "_key": "96282238",
            "is_ephemeral": false,
            "name": "output_data1",
            "data": {
              "result": 1.2
            }
          }
        }
      ]
    }
