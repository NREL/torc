(map-python-function-tutorial)=

# Map a Python function to compute nodes

This tutorial will teach you how to build a workflow from Python functions instead of CLI
executables and run on it on an HPC with `Slurm`.

## Workflow Description

Let's suppose that your code is in a module called `simulation.py` and looks something like this:

```python
def run(input_params: dict) -> dict:
    """Runs one simulation on a set of input parameters.

    Returns
    -------
    dict
        Result of the simulation.
    """
    job_name = input_params["job_name"]
    return {
        "inputs": input_params,
        "result": 5,
        "output_data_path": f"/projects/my-project/{job_name}",
    }


def postprocess(results: list[dict]) -> dict:
    """Collects the results of the workers and performs postprocessing.

    Parameters
    ----------
    results : list[dict]
        Results from each simulation

    Returns
    -------
    dict
        Final result
    """
    total = 0
    paths = []
    for result in results:
        assert "result" in result
        assert "output_data_path" in result
        total += result["result"]
        paths.append(result["output_data_path"])
    return {"total": total, "output_data_paths": paths}
```

You need to run this function on hundreds of sets of input parameters and want torc to help you
scale this work on an HPC.

The recommended procedure for this task is torc's Python API as shown below. The
goal is to mimic the behavior of Python's [concurrent.futures.ProcessPoolExecutor.map](https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor)
as much as possible.

Similar functionality is also available with [Dask](https://docs.dask.org/en/stable/deploying.html?highlight=slurm#deploy-dask-clusters).

### Resource Constraints

- Each function call needs 4 CPUs and 20 GiB of memory.
- The function call takes 1 hour to run.

On Eagle the 92 GiB nodes are easiest to acquire but would only be able to run 4 jobs at a time.
The 180 GiB nodes are fewer in number but would use fewer AUs because they would be able to run 8
jobs at a time.

## Torc Overview

Here is what torc does to solve this problem:

- User creates a workflow in Python.
- User passes a runnable function as well as a list of all input parameters that need to be mapped
  to the function.
- For each set of input parameters torc creates an object in the `user_data` table in the
  database, creates a job with a relationship to that object as an input, and creates a
  placeholder for data to be created by that job.
- When torc runs each job it reads the correct input parameters from the database, imports the
  user's function, and then calls it with the input parameters.
- When the function completes, torc stores any returned data in the database.
- When all workers complete torc collects all result data from the database into a list and passes
  that to the postprocess function. It also stores any returned data from that function into the
  database.

## Build the workflow

1. Write a script to create the workflow. Note that you need to correct the `api` URL and the
   Slurm `account`.

```python
import getpass
import os

from torc import make_api, map_function_to_jobs
from torc.openapi_client import ResourceRequirementsModel, SlurmSchedulerModel, WorkflowModel


TORC_BASE_URL = os.getenv("TORC_BASE_URL", "http://localhost:8080/torc-service/v1")

api = make_api("http://localhost:8529/_db/workflows/torc-service")
params = [
    {"input1": 1, "input2": 2, "input3": 3},
    {"input1": 4, "input2": 5, "input3": 6},
    {"input1": 7, "input2": 8, "input3": 9},
]
workflow = api.create_workflow(WorkflowModel(
    user=getpass.getuser(),
    name="my_workflow",
    description="My workflow",
))
assert workflow.id is not None
rr = api.create_resource_requirements(
    ResourceRequirementsModel(workflow_id=workflow.id, name="medium", num_cpus=4, memory="20g", runtime="P0DT1H"),
)
jobs = map_function_to_jobs(
    api,
    workflow.id,
    "simulation",
    "run",
    params,
    resource_requirements_id=rr.id,
    # Note that this is optional.
    postprocess_func="postprocess",
)
scheduler = api.create_slurm_scheduler(
    SlurmSchedulerModel(
        workflow_id=workflow.id,
        name="short",
        account="my_account",
        mem="180224",
        walltime="04:00:00",
        nodes=1,
    ),
)
print(f"Created workflow with ID {workflow.id} {len(jobs)} jobs.")
```

```{eval-rst}
.. note:: Refer to :ref:`python-client-api-reference` for complete API documentation.
```

**Requirements**:

- Your run function should raise an exception if there is a failure. If that happens, torc will
  record a non-zero return code for the job.

- If you want torc to store result data in the database, return it from your run function.
  **Note**: this result data must not be large - the database is not designed for that. If you have
  large result data, return a pointer (i.e., file path) to its location here.

- If you choose to define a postprocess function and want torc to store the final data in the
  database, return it from that function.

- The `params` must be serializable in JSON format because they will be stored in the database.
  Basic types like numbers and strings and lists and dictionaries of those will work fine. If you
  need to store complex, custom types, consider these options:

  - Define data models with [Pydantic](https://docs.pydantic.dev/latest/usage/models/). You can
    use their existing serialization/de-serialization methods or define custom methods.
  - Pickle your data and store the result as a string. Your run function would need to understand
    how to de-serialize it. Note that this has portability limitations. (Please contact the
    developers if you would like to see this happen automatically.)

- Torc must be able to import simulation.py from Python. Here are some options:

  - Put the script in the current directory.
  - Install it in the environment.
  - Specify its parent directory like this:

```python
builder.map_function_to_jobs("simulation", "run", params, module_directory="parent_dir")
```

2. Create the workflow.

```console
$ python <your-script>
Created workflow 3141686 with 3 jobs.
```

5. Start the workflow.

```console
$ torc workflows start
2023-08-07 11:51:03,891 - INFO [torc.workflow_manager workflow_manager.py:156] : Changed all uninitialized jobs to ready or blocked.
2023-08-05 11:51:03,894 - INFO [torc.workflow_manager workflow_manager.py:82] : Started workflow
```

```console
$ torc jobs list
+---------------------------------------------------------------------------------------------+
|                                     Jobs in workflow 3141686                                |
+-------+-------------+---------------------------+---------+------------------------+--------+
| index |     name    |          command          |  status | schedule_compute_nodes |  _key  |
+-------+-------------+---------------------------+---------+------------------------+--------+
|   1   |      0      |   torc jobs run-function  |  ready  |            None        | 788309 |
|   2   |      1      |   torc jobs run-function  |  ready  |            None        | 788323 |
|   3   |      2      |   torc jobs run-function  |  ready  |            None        | 788337 |
|   4   | postprocess | torc jobs run-postprocess | blocked |            None        | 788389 |
+-------+-------------+---------------------------+---------+------------------------+--------+
```

6. Schedule compute nodes with `Slurm`. This example only needs one compute node. You will need
   to make some estimation for your jobs.

   The computes nodes in this example can run eight jobs at a time and can complete four rounds of
   work (32 jobs per allocation). So, the number of required compute nodes is `num_jobs / 32`.

```console
$ torc hpc slurm schedule-nodes -n1
```

7. The jobs will run whenever Slurm allocates compute nodes. Monitor status as discussed in
   {ref}`check-status`.
8. View the result data overall or by job (if your run and postprocess functions return something).
   Note that listing all user-data will return input parameters.

```console
$ torc list user-data
```

```console
$ torc jobs list-user-data --stores 788309
$ torc jobs list-user-data --stores 788323
$ torc jobs list-user-data --stores 788337
$ torc jobs list-user-data --stores 788389
```

## Workflow Restarts

If you find that one or more input parameters were incorrect *after* running the workflow, you can
correct them without re-running the entire workflow. Torc stores relationships between the
parameters and jobs, and will restart only the affected jobs. Here's how to do that:

1. Identify the key(s) for the affected parameters.

```console
$ torc user-data list
[
  {
    "is_ephemeral": false,
    "name": "0",
    "data": {
      "module": "simulation",
      "func": "run",
      "params": {
        "var1": "0",
        "var2": 0
      }
    },
    "key": "3141795",
    "rev": "_gagG-Hy---"
  },
  {
    "is_ephemeral": false,
    "name": "1",
    "data": {
      "module": "simulation",
      "func": "run",
      "params": {
        "var1": "1",
        "var2": 1
      }
    },
    "key": "3141797",
    "rev": "_gagG-H2---"
  },
  {
    "is_ephemeral": false,
    "name": "2",
    "data": {
      "module": "simulation",
      "func": "run",
      "params": {
        "var1": "2",
        "var2": 2
      }
    },
    "key": "3141799",
    "rev": "_gagG-H2--_"
  },
]
```

2. Modify the data.

```console
$ torc user-data modify 3141813 -d '{"module":"simulation.py","func":"run","params":{"var1":"100","var2":100}}'
```

```{eval-rst}
.. note:: You can get and set user-data through the Python API. Search for
   get_user_data_key and put_user_data_key at
   :ref:`default-api`.
```

3. Re-initialize the workflow.

```console
$ torc workflows reinitialize
```

4. Confirm that only one job has a `ready` status.

```console
$ torc jobs list
```

5. Schedule a node to run the job.

```console
$ torc hpc slurm schedule-nodes -n1
```

## Other jobs

You could add "normal" jobs to the workflow as well. For example, you might have preprocessing and
postprocessing work to do. You can add those jobs through the API. You could also add multiple
rounds of mapped functions. `map_function_to_jobs` provides a `blocked_by_job_ids` parameter to specify
ordering. You could also define job-job relationships through files or user-data as discussed
elsewhere in this documentation.
