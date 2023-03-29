.. _job_input_output_data::

#####################
Job Input/Output Data
#####################

Torc provides a mechanism for users to store input and output data in the database. This data can
be stored on a per-job basis or for the overall workflow.

One way to run jobs with different parameters is to pass those parameters as command-line arguments
and options. A second way is to store the input parameters in the ``user_data`` collection of the
database. A common runner script can pull the parameters for each specific job at runtime.

.. note:: Torc sets the environment variable TORC_JOB_KEY with each job's unique key. Scripts can
   use this value to retrieve data from the database.

Jobs can also store result data and metatdata in the database.

.. warning:: The database is not currently designed to store large result data. You can store
   small result data or pointers to where the actual data resides.

Here is how to store and retrieve user data from torc CLI commands and API commands.

These examples add two JSON objects to the job.

Torc CLI
========

.. code-block:: console

   $ torc jobs add-user-data 92181820 "{key1: 'val1', key2: 'val2'}" "{key3: 'val3'}"
   2023-03-29 08:21:33,553 - INFO [torc.cli.jobs jobs.py:103] : Added user_data key=92340362 to job key=92181820
   2023-03-29 08:21:33,613 - INFO [torc.cli.jobs jobs.py:103] : Added user_data key=92340378 to job key=92181820


.. code-block:: console

   $ torc jobs get-user-data 92181820
   {'_key': '92340378', '_rev': '_fw08x8a---', 'key3': 'val3'}
   {'_key': '92340362', '_rev': '_fw08x4m---', 'key1': 'val1', 'key2': 'val2'}


Python API client
=================

.. code-block:: python

    from swagger_client import ApiClient, DefaultApi
    from swagger_client.configuration import Configuration

    configuration = Configuration()
    configuration.host = "http://localhost:8529/_db/workflows/torc-service"
    api = DefaultApi(ApiClient(configuration))
    workflow_key = "92181686"
    job_key = "92181820"
    data = [
        {
            "key1": "val1",
            "key2": "val2",
        },
        {
            "key3": "val3",
        },
    ]
    for item in data:
        result = api.post_jobs_user_data_workflow_key(item, workflow_key, job_key)
        print(f"Added user data key={result['_key']}")

    result = api.get_jobs_user_data_workflow_key(workflow_key, job_key)
    print(f"Job key={job_key} stores {result.items}")
