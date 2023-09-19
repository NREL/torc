"""Example large workflow using direct API"""

import getpass

from torc.api import make_api, send_api_command
from torc.loggers import setup_logging
from torc.openapi_client.models.compute_node_resource_stats_model import (
    ComputeNodeResourceStatsModel,
)
from torc.openapi_client.models.job_with_edges_model import JobWithEdgesModel
from torc.openapi_client.models.workflows_model import WorkflowsModel
from torc.openapi_client.models.jobs_model import JobsModel
from torc.openapi_client.models.bulk_jobs_model import BulkJobsModel
from torc.openapi_client.models.resource_requirements_model import ResourceRequirementsModel
from torc.openapi_client.models.slurm_schedulers_model import SlurmSchedulersModel


def create_workflow(api):
    """Creates a workflow directly through the API."""
    logger = setup_logging(__name__)
    workflow = WorkflowsModel(
        user=getpass.getuser(),
        name="large_workflow",
        description="Demo creation of a large workflow directly throught the API.",
    )
    workflow = api.post_workflows(workflow)
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

    job_count = 20_000
    jobs_remaining = job_count
    max_transfer_size = 10_000
    job_index = 1
    while jobs_remaining > 0:
        jobs = []
        for i in range(job_index, job_index + max_transfer_size):
            job = JobWithEdgesModel(
                job=JobsModel(
                    name=f"job{i}",
                    command="python my_script.py",
                ),
                resource_requirements=resource_requirements.id,
                scheduler=scheduler.id,
            )
            jobs.append(job)
            jobs_remaining -= 1
            if jobs_remaining == 0:
                break
        send_api_command(api.post_bulk_jobs, workflow.key, BulkJobsModel(jobs=jobs))
        job_index += max_transfer_size

    logger.info("Created workflow %s with %s jobs", workflow.key, job_count)
    return workflow.key


def main():
    """Entry point"""
    api = make_api("http://localhost:8529/_db/test-workflows/torc-service")
    create_workflow(api)


if __name__ == "__main__":
    main()
