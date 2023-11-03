#################################
Declare Job Dependencies Manually
#################################
In some workflows it may be more convenient to declare dependencies between jobs manually rather
than through files or user data. This tutorial will teach you how to do that.

Suppose the workflow has 3 work jobs and one postprocessing job. The postprocessing job should
only be run once all work jobs complete successfully.

The ``examples`` directory in this repository has an example that creates the job
dependencies between the postprocessing job and work jobs through the ``blocked_by`` parameter.
Note that it sets ``cancel_on_blocking_job_failure = true``, which means that the postprocess job
won't run if any work job fails. If you expect failures then you should set that to false and then
send torc API calls to determine what failed.

Examples:

- `JSON5 <https://github.nrel.gov/viz/wms/blob/main/examples/manual_job_dependencies.json5>`_
- `Python <https://github.nrel.gov/viz/wms/blob/main/examples/manual_job_dependencies.py>`_
- `Julia <https://github.nrel.gov/viz/wms/blob/main/examples/manual_job_dependencies.jl>`_

These examples will work on a local computer or HPC environment. You can create the JSON5 workflow
with the CLI command ``torc workflows create-from-json-file
examples/manual_job_dependencies.json5``. You can run the Python and Julia workflows by running the
commands through Python or Julia, e.g., ``python examples/manual_job_dependencies.py``.

The rest of the steps would be identical to the other tutorials.
