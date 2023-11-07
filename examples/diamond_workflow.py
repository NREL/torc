"""Example diamond workflow"""

import getpass
import json
import sys
from pathlib import Path

from torc.api import make_api, add_jobs
from torc.loggers import setup_logging
from torc.openapi_client.models.compute_node_resource_stats_model import (
    ComputeNodeResourceStatsModel,
)
from torc.openapi_client.api import DefaultApi
from torc.openapi_client.models.files_model import FilesModel
from torc.openapi_client.models.job_with_edges_model import JobWithEdgesModel
from torc.openapi_client.models.workflows_model import WorkflowsModel
from torc.openapi_client.models.jobs_model import JobsModel
from torc.openapi_client.models.resource_requirements_model import (
    ResourceRequirementsModel,
)
from torc.openapi_client.models.slurm_schedulers_model import SlurmSchedulersModel
from torc.torc_rc import TorcRuntimeConfig


TORC_SERVICE_URL = "http://localhost:8529/_db/test-workflows/torc-service"
TEST_WORKFLOW = "test_workflow"
PREPROCESS = Path("tests") / "worker" / "scripts" / "preprocess.py"
POSTPROCESS = Path("tests") / "worker" / "scripts" / "postprocess.py"
WORK = Path("tests") / "worker" / "scripts" / "work.py"

logger = setup_logging(__name__)


def create_workflow(api: DefaultApi) -> WorkflowsModel:
    """Create the workflow"""
    workflow = WorkflowsModel(
        user=getpass.getuser(),
        name="diamond_workflow",
        description="Example diamond workflow",
    )
    return api.add_workflow(workflow)


def build_workflow(api: DefaultApi, workflow: WorkflowsModel):
    """Creates a workflow with implicit job dependencies declared through files."""
    config = api.get_workflow_config(workflow.key)
    config.compute_node_resource_stats = ComputeNodeResourceStatsModel(
        cpu=True,
        memory=True,
        process=True,
        interval=5,
        monitor_type="aggregation",
    )
    api.modify_workflow_config(workflow.key, config)

    inputs_file = Path("inputs.json")
    inputs_file.write_text(json.dumps({"val": 5}), encoding="utf-8")

    inputs = api.add_file(workflow.key, FilesModel(name="inputs", path=str(inputs_file)))
    f1 = api.add_file(workflow.key, FilesModel(name="file1", path="f1.json"))
    f2 = api.add_file(workflow.key, FilesModel(name="file2", path="f2.json"))
    f3 = api.add_file(workflow.key, FilesModel(name="file3", path="f3.json"))
    f4 = api.add_file(workflow.key, FilesModel(name="file4", path="f4.json"))

    small = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="small", num_cpus=1, memory="1g", runtime="P0DT1H"),
    )
    medium = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="medium", num_cpus=4, memory="8g", runtime="P0DT8H"),
    )
    large = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="large", num_cpus=8, memory="16g", runtime="P0DT12H"),
    )
    api.add_slurm_scheduler(
        workflow.key,
        SlurmSchedulersModel(
            name="short",
            account="my_account",
            nodes=1,
            walltime="04:00:00",
        ),
    )

    jobs = [
        JobWithEdgesModel(
            job=JobsModel(
                name="preprocess",
                command=f"python {PREPROCESS} -i {inputs.path} -o {f1.path}",
            ),
            input_files=[inputs.id],
            output_files=[f1.id],
            resource_requirements=small.id,
        ),
        JobWithEdgesModel(
            job=JobsModel(
                name="work1",
                command=f"python {WORK} -i {f1.path} -o {f2.path}",
            ),
            input_files=[f1.id],
            output_files=[f2.id],
            resource_requirements=medium.id,
        ),
        JobWithEdgesModel(
            job=JobsModel(
                name="work2",
                command=f"python {WORK} -i {f1.path} -o {f3.path}",
            ),
            input_files=[f1.id],
            output_files=[f3.id],
            resource_requirements=large.id,
        ),
        JobWithEdgesModel(
            job=JobsModel(
                name="postprocess",
                command=f"python {POSTPROCESS} -i {f2.path} -i {f3.path} -o {f4.path}",
            ),
            input_files=[f2.id, f3.id],
            output_files=[f4.id],
            resource_requirements=small.id,
        ),
    ]
    add_jobs(api, workflow.key, jobs)

    logger.info("Created workflow %s with %s jobs", workflow.key, len(jobs))


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
        api.remove_workflow(workflow.key)
        raise


if __name__ == "__main__":
    main()
