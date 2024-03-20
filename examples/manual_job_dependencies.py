"""Example workflow that defines job dependencies manually"""

import getpass
import sys

from torc.api import make_api
from torc.loggers import setup_logging
from torc.openapi_client.api import DefaultApi
from torc.openapi_client.models.workflow_model import WorkflowModel
from torc.openapi_client.models.job_model import JobModel
from torc.openapi_client.models.resource_requirements_model import (
    ResourceRequirementsModel,
)
from torc.openapi_client.models.slurm_scheduler_model import SlurmSchedulerModel
from torc.torc_rc import TorcRuntimeConfig


logger = setup_logging(__name__)


def create_workflow(api: DefaultApi) -> WorkflowModel:
    """Creates a workflow."""
    workflow = WorkflowModel(
        user=getpass.getuser(),
        name="manual_job_dependencies",
        description="Demo creation of a workflow with job dependencies specified manually.",
    )
    return api.add_workflow(workflow)


def build_workflow(api: DefaultApi, workflow: WorkflowModel):
    """Builds the workflow."""
    small = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(
            name="small", num_cpus=1, memory="1g", runtime="P0DT45M"
        ),
    )
    medium = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(
            name="medium", num_cpus=4, memory="10g", runtime="P0DT3H"
        ),
    )
    api.add_slurm_scheduler(
        workflow.key,
        SlurmSchedulerModel(
            name="short",
            account="my_account",
            nodes=1,
            walltime="04:00:00",
        ),
    )

    blocking_jobs = []
    for i in range(1, 4):
        job = api.add_job(
            workflow.key,
            JobModel(
                name=f"job{i}",
                command="echo test",
                resource_requirements=medium.id,
            ),
        )
        blocking_jobs.append(job.id)

    job = api.add_job(
        workflow.key,
        JobModel(
            name="job5",
            command="bash error.sh",
            resource_requirements=small.id,
        ),
    )
    blocking_jobs.append(job.id)
    api.add_job(
        workflow.key,
        JobModel(
            name="postprocess",
            command="echo test",
            resource_requirements=small.id,
            blocked_by=blocking_jobs,
        ),
    )
    logger.info("Created workflow %s", workflow.key)


def main():
    """Entry point"""
    config = TorcRuntimeConfig.load()
    if config.database_url is None:
        logger.error(
            "There is no torc config file or the database URL is not defined. "
            "Please fix the config file or define the URL in this script."
        )
        sys.exit(1)
    api = make_api(config.database_url)
    workflow = create_workflow(api)
    try:
        build_workflow(api, workflow)
    except Exception:
        logger.exception("Failed to build workflow")
        api.remove_workflow(workflow.key)
        raise


if __name__ == "__main__":
    main()
