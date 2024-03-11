"""Example large workflow using the API"""

import getpass
import sys

from torc.api import make_api, add_jobs
from torc.loggers import setup_logging
from torc.openapi_client.api import DefaultApi
from torc.openapi_client.models.compute_node_resource_stats_model import (
    ComputeNodeResourceStatsModel,
)
from torc.openapi_client.models.workflow_model import WorkflowModel
from torc.openapi_client.models.job_model import JobModel
from torc.openapi_client.models.resource_requirements_model import (
    ResourceRequirementsModel,
)
from torc.openapi_client.models.slurm_scheduler_model import SlurmSchedulerModel
from torc.torc_rc import TorcRuntimeConfig

logger = setup_logging(__name__)


def create_workflow(api: DefaultApi) -> WorkflowModel:
    """Creates a workflow directly through the API."""
    workflow = WorkflowModel(
        user=getpass.getuser(),
        name="large_workflow",
        description="Demo creation of a large workflow directly through the API.",
    )
    return api.add_workflow(workflow)


def build_workflow(api: DefaultApi, workflow: WorkflowModel):
    """Builds the workflow."""
    config = api.get_workflow_config(workflow.key)
    config.compute_node_resource_stats = ComputeNodeResourceStatsModel(
        cpu=True,
        memory=True,
        process=True,
        interval=10,
        monitor_type="periodic",
        make_plots=True,
    )
    api.modify_workflow_config(workflow.key, config)

    resource_requirements = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(
            name="medium", num_cpus=8, memory="16g", runtime="P0DT2H"
        ),
    )
    scheduler = api.add_slurm_scheduler(
        workflow.key,
        SlurmSchedulerModel(
            name="short",
            account="my_account",
            nodes=1,
            walltime="04:00:00",
        ),
    )

    jobs = (
        JobModel(
            name=f"job{i}",
            command=f"python my_script.py {i}",
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
