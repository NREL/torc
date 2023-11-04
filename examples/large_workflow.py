"""Example large workflow using the API"""

import getpass

from torc.api import make_api, add_jobs
from torc.loggers import setup_logging
from torc.openapi_client.api import DefaultApi
from torc.openapi_client.models.compute_node_resource_stats_model import (
    ComputeNodeResourceStatsModel,
)
from torc.openapi_client.models.job_with_edges_model import JobWithEdgesModel
from torc.openapi_client.models.workflows_model import WorkflowsModel
from torc.openapi_client.models.jobs_model import JobsModel
from torc.openapi_client.models.resource_requirements_model import (
    ResourceRequirementsModel,
)
from torc.openapi_client.models.slurm_schedulers_model import SlurmSchedulersModel

TORC_SERVICE_URL = "http://localhost:8529/_db/test-workflows/torc-service"

logger = setup_logging(__name__)


def create_workflow(api: DefaultApi) -> WorkflowsModel:
    """Creates a workflow directly through the API."""
    workflow = WorkflowsModel(
        user=getpass.getuser(),
        name="large_workflow",
        description="Demo creation of a large workflow directly through the API.",
    )
    return api.post_workflows(workflow)


def build_workflow(api: DefaultApi, workflow: WorkflowsModel):
    """Builds the workflow."""
    config = api.get_workflows_key_config(workflow.key)
    config.compute_node_resource_stats = ComputeNodeResourceStatsModel(
        cpu=True,
        memory=True,
        process=True,
        interval=10,
        monitor_type="periodic",
        make_plots=True,
    )
    api.put_workflows_key_config(workflow.key, config)

    resource_requirements = api.post_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="medium", num_cpus=8, memory="16g", runtime="P0DT2H"),
    )
    scheduler = api.post_slurm_schedulers(
        workflow.key,
        SlurmSchedulersModel(
            name="short",
            account="my_account",
            nodes=1,
            walltime="04:00:00",
        ),
    )

    jobs = (
        JobWithEdgesModel(
            job=JobsModel(
                name=f"job{i}",
                command=f"python my_script.py {i}",
            ),
            resource_requirements=resource_requirements.id,
            scheduler=scheduler.id,
        )
        for i in range(1, 20_001)
    )

    add_jobs(api, workflow.key, jobs)

    logger.info("Created workflow %s", workflow.key)
    return workflow.key


def main():
    """Entry point"""
    api = make_api(TORC_SERVICE_URL)
    workflow = create_workflow(api)
    try:
        build_workflow(api, workflow)
    except Exception:
        logger.exception("Failed to build workflow")
        api.delete_workflows_key(workflow.key)
        raise


if __name__ == "__main__":
    main()
