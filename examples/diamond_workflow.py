"""Example diamond workflow"""
import json
import logging
from pathlib import Path

from swagger_client.models.files_workflow_model import FilesWorkflowModel
from swagger_client.models.job_specifications_workflow_model import JobSpecificationsWorkflowModel
from swagger_client.models.resource_requirements_workflow_model import (
    ResourceRequirementsWorkflowModel,
)
from swagger_client.models.workflow_specifications_model import WorkflowSpecificationsModel

from torc.api import make_api


TEST_WORKFLOW = "test_workflow"
PREPROCESS = Path("tests") / "worker" / "scripts" / "preprocess.py"
POSTPROCESS = Path("tests") / "worker" / "scripts" / "postprocess.py"
WORK = Path("tests") / "worker" / "scripts" / "work.py"

logger = logging.getLogger(__name__)


def create_workflow(api):
    """Creates a workflow with implicit job dependencies declared through files."""
    inputs_file = Path("inputs.json")
    inputs_file.write_text(json.dumps({"val": 5}), encoding="utf-8")

    inputs = FilesWorkflowModel(name="inputs", path=str(inputs_file))
    f1 = FilesWorkflowModel(name="file1", path="f1.json")
    f2 = FilesWorkflowModel(name="file2", path="f2.json")
    f3 = FilesWorkflowModel(name="file3", path="f3.json")
    f4 = FilesWorkflowModel(name="file4", path="f4.json")

    small = ResourceRequirementsWorkflowModel(
        name="small", num_cpus=1, memory="1g", runtime="P0DT1H"
    )
    medium = ResourceRequirementsWorkflowModel(
        name="medium", num_cpus=4, memory="8g", runtime="P0DT8H"
    )
    large = ResourceRequirementsWorkflowModel(
        name="large", num_cpus=8, memory="16g", runtime="P0DT12H"
    )

    preprocess = JobSpecificationsWorkflowModel(
        name="preprocess",
        command=f"python {PREPROCESS} -i {inputs.path} -o {f1.path}",
        input_files=[inputs.name],
        output_files=[f1.name],
        resource_requirements=small.name,
    )
    work1 = JobSpecificationsWorkflowModel(
        name="work1",
        command=f"python {WORK} -i {f1.path} -o {f2.path}",
        user_data=[{"key1": "val1"}],
        input_files=[f1.name],
        output_files=[f2.name],
        resource_requirements=medium.name,
    )
    work2 = JobSpecificationsWorkflowModel(
        name="work2",
        command=f"python {WORK} -i {f1.path} -o {f3.path}",
        input_files=[f1.name],
        output_files=[f3.name],
        resource_requirements=large.name,
    )
    postprocess = JobSpecificationsWorkflowModel(
        name="postprocess",
        command=f"python {POSTPROCESS} -i {f2.path} -i {f3.path} -o {f4.path}",
        input_files=[f2.name, f3.name],
        output_files=[f4.name],
        resource_requirements=small.name,
    )

    spec = WorkflowSpecificationsModel(
        files=[inputs, f1, f2, f3, f4],
        jobs=[preprocess, work1, work2, postprocess],
        resource_requirements=[small, medium, large],
    )
    workflow = api.post_workflow_specifications(spec)
    api.post_workflows_initialize_jobs_key(workflow.key)
    print(f"Created workflow {workflow.key} with 4 jobs")


def main():
    """Entry point"""
    api = make_api("http://localhost:8529/_db/workflows/torc-service")
    create_workflow(api)


if __name__ == "__main__":
    main()
