import getpass
import os

from torc import make_api, map_function_to_jobs
from torc.openapi_client import (
    ResourceRequirementsModel,
    SlurmSchedulerModel,
    WorkflowModel,
)


TORC_BASE_URL = os.getenv("TORC_BASE_URL", "http://localhost:8080/torc-service/v1")

api = make_api("http://localhost:8529/_db/workflows/torc-service")
params = [
    {"input1": 1, "input2": 2, "input3": 3},
    {"input1": 4, "input2": 5, "input3": 6},
    {"input1": 7, "input2": 8, "input3": 9},
]
workflow = api.create_workflow(
    WorkflowModel(
        user=getpass.getuser(),
        name="my_workflow",
        description="My workflow",
    )
)
assert workflow.id is not None
rr = api.create_resource_requirements(
    ResourceRequirementsModel(
        workflow_id=workflow.id,
        name="medium",
        num_cpus=4,
        memory="20g",
        runtime="P0DT1H",
    ),
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
