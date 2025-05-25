(large-workflow)=

# Large Workflow

In this tutorial you will learn how to create a workflow directly through the API. This is required
for large workflows. The API service in the database is limited to 512 MiB of memory, and so if
the workflow specification exceeds that size, creation will fail. Large workflows also put extra
burden on the API service. The example used here builds the workflow incrementally. This should be
used for any workflow with more than 10,000 jobs.

The builder script is [large_workflow.py](https://github.nrel.gov/viz/torc/blob/main/examples/large_workflow.py). It creates a
workflow with 20,000 independent jobs. It creates jobs in two batchs of 10,000 each. It specifies
resource requirements and a scheduler for each job.

```{eval-rst}
.. note:: If you need to add file, user_data, or blocking-job dependencies, you can do that as
   well.
```

1. Create the workflow.

```console
$ python examples/large_workflow.py
2023-09-19 13:21:17,411 - INFO [__main__ large_workflow.py:72] : Created workflow 113899556 with 20000 jobs
```

2. Start the workflow

```console
$ torc -k 113899556 workflows start
2023-09-19 13:22:50,305 - INFO [torc.workflow_manager workflow_manager.py:85] : Started workflow
```

The rest of the steps would be identical to the other tutorials.
