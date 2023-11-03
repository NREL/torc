"""Example workflow that defines job dependencies manually"""

import getpass

from torc.api import make_api
from torc.loggers import setup_logging
from torc.openapi_client.api import DefaultApi
from torc.openapi_client.models.workflows_model import WorkflowsModel
from torc.openapi_client.models.job_with_edges_model import JobWithEdgesModel
from torc.openapi_client.models.jobs_model import JobsModel
from torc.openapi_client.models.resource_requirements_model import (
    ResourceRequirementsModel,
)
from torc.openapi_client.models.slurm_schedulers_model import SlurmSchedulersModel


TORC_SERVICE_URL = "http://localhost:8529/_db/test-workflows/torc-service"

logger = setup_logging(__name__)


def create_workflow(api: DefaultApi) -> WorkflowsModel:
    """Creates a workflow."""
    workflow = WorkflowsModel(
        user=getpass.getuser(),
        name="manual_job_dependencies",
        description="Demo creation of a workflow with job dependencies specified manually.",
    )
    return api.post_workflows(workflow)


def build_workflow(api: DefaultApi, workflow: WorkflowsModel):
    """Builds the workflow."""
    small = api.post_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="small", num_cpus=1, memory="1g", runtime="P0DT45M"),
    )
    medium = api.post_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="medium", num_cpus=4, memory="10g", runtime="P0DT3H"),
    )
    api.post_slurm_schedulers(
        workflow.key,
        SlurmSchedulersModel(
            name="short",
            account="my_account",
            nodes=1,
            walltime="04:00:00",
        ),
    )

    blocking_jobs = []
    for i in range(1, 4):
        job = api.post_job_with_edges(
            workflow.key,
            JobWithEdgesModel(
                job=JobsModel(name=f"job{i}", command="echo test"),
                resource_requirements=medium.id,
            ),
        )
        blocking_jobs.append(job.id)

    api.post_job_with_edges(
        workflow.key,
        JobWithEdgesModel(
            job=JobsModel(name="postprocess", command="echo test"),
            resource_requirements=small.id,
            blocked_by=blocking_jobs,
        ),
    )
    logger.info("Created workflow %s", workflow.key)


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
