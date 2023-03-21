"""Script to run jobs on a local computer"""

import json
import logging
import shutil
import sys
from pathlib import Path

from prettytable import PrettyTable
from swagger_client.models.file_model import FileModel
from swagger_client.models.job_definition import JobDefinition
from swagger_client.models.resource_requirements_model import ResourceRequirementsModel
from swagger_client.models.workflow_model import WorkflowModel
from swagger_client.models.workflow_config_compute_node_resource_stats import (
    WorkflowConfigComputeNodeResourceStats,
)
from swagger_client.models.workflow_config_model import WorkflowConfigModel

from torc.api import make_api
from torc.loggers import setup_logging
from torc.job_runner import JobRunner
from torc.workflow_manager import WorkflowManager


TEST_WORKFLOW = "test_workflow"
PREPROCESS = Path("tests") / "scripts" / "preprocess.py"
POSTPROCESS = Path("tests") / "scripts" / "postprocess.py"
WORK = Path("tests") / "scripts" / "work.py"

logger = logging.getLogger(__name__)


def create_workflow(api, output_dir: Path):
    """Create a diamond workflow with file dependencies."""
    output_dir.mkdir(exist_ok=True)
    inputs_file = output_dir / "inputs.json"
    inputs_file.write_text(json.dumps({"val": 5}))

    inputs = FileModel(name="inputs", path=str(inputs_file))
    f1 = FileModel(name="file1", path=str(output_dir / "f1.json"))
    f2 = FileModel(name="file2", path=str(output_dir / "f2.json"))
    f3 = FileModel(name="file3", path=str(output_dir / "f3.json"))
    f4 = FileModel(name="file4", path=str(output_dir / "f4.json"))

    small = ResourceRequirementsModel(name="small", num_cpus=1, memory="1g", runtime="P0DT1H")
    medium = ResourceRequirementsModel(name="medium", num_cpus=4, memory="8g", runtime="P0DT8H")
    large = ResourceRequirementsModel(name="large", num_cpus=8, memory="16g", runtime="P0DT12H")

    preprocess = JobDefinition(
        name="preprocess",
        command=f"python {PREPROCESS} -i {inputs.path} -o {f1.path}",
        input_files=[inputs.name],
        output_files=[f1.name],
        resource_requirements=small.name,
    )
    work1 = JobDefinition(
        name="work1",
        command=f"python {WORK} -i {f1.path} -o {f2.path}",
        user_data=[{"key1": "val1"}],
        input_files=[f1.name],
        output_files=[f2.name],
        resource_requirements=medium.name,
    )
    work2 = JobDefinition(
        name="work2",
        command=f"python {WORK} -i {f1.path} -o {f3.path}",
        input_files=[f1.name],
        output_files=[f3.name],
        resource_requirements=large.name,
    )
    postprocess = JobDefinition(
        name="postprocess",
        command=f"python {POSTPROCESS} -i {f2.path} -i {f3.path} -o {f4.path}",
        input_files=[f2.name, f3.name],
        output_files=[f4.name],
        resource_requirements=small.name,
    )

    workflow = WorkflowModel(
        files=[inputs, f1, f2, f3, f4],
        jobs=[preprocess, work1, work2, postprocess],
        resource_requirements=[small, medium, large],
        config=WorkflowConfigModel(
            compute_node_resource_stats=WorkflowConfigComputeNodeResourceStats(
                cpu=True,
                memory=True,
                process=True,
                interval=1,
            )
        ),
    )
    api.post_workflow(workflow)
    api.post_workflow_initialize_jobs()
    logger.info("Created workflow")


def run_workflow(api, output_dir: Path):
    """Run the workflow stored in the database."""
    mgr = WorkflowManager(api)
    mgr.start()
    runner = JobRunner(api, output_dir, time_limit="P0DT24H")
    logger.info("Start workflow")
    runner.run_worker()


def restart_workflow(api, output_dir: Path):
    """Restart the workflow stored in the database."""
    mgr = WorkflowManager(api)
    mgr.reinitialize_jobs()
    runner = JobRunner(api, output_dir, time_limit="P0DT24H")
    logger.info("Start workflow")
    runner.run_worker()


def main():
    """Entry point"""
    usage = f"Usage: python {sys.argv[0]} create|estimate|run|restart"
    if len(sys.argv) == 1:
        print(usage, file=sys.stderr)
        sys.exit(1)

    setup_logging(__name__)

    api = make_api("http://localhost:8529/_db/workflows/torc-service")
    output_dir = Path("output_dir")
    mode = sys.argv[1]
    if mode == "create":
        if output_dir.exists():
            shutil.rmtree(output_dir)
        api.delete_workflow()
        create_workflow(api, output_dir)
    elif mode == "estimate":
        data = api.post_workflow_estimate()
        table = PrettyTable(title="Resource Estimates")
        table.field_names = ("round", "num_jobs", "num_cpus", "memory_gb", "num_gpus")
        for i, row in enumerate(data.estimates_by_round, start=1):
            table.add_row((i, row["num_jobs"], row["num_cpus"], row["memory_gb"], row["num_gpus"]))
        print(table)
    elif mode == "run":
        api.delete_workflow()
        create_workflow(api, output_dir)
        run_workflow(api, output_dir)
    elif mode == "restart":
        restart_workflow(api, output_dir)
    else:
        print(usage, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
