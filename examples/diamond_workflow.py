"""Example diamond workflow"""
import json
import logging
import shutil
from pathlib import Path

from swagger_client.models.file_model import FileModel
from swagger_client.models.job_definition import JobDefinition
from swagger_client.models.resource_requirements_model import ResourceRequirementsModel
from swagger_client.models.workflow_model import WorkflowModel

from wms.api import make_api


TEST_WORKFLOW = "test_workflow"
PREPROCESS = Path("tests") / "worker" / "scripts" / "preprocess.py"
POSTPROCESS = Path("tests") / "worker" / "scripts" / "postprocess.py"
WORK = Path("tests") / "worker" / "scripts" / "work.py"

logger = logging.getLogger(__name__)


def create_workflow(api, output_dir: Path):
    """Creates a workflow with implicit job dependencies declared through files."""
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
    )
    api.post_workflow(workflow)
    api.post_workflow_initialize_jobs()
    print("Created workflow with 4 jobs")


def main():
    """Entry point"""
    output_dir = Path("demo_diamond_workflow_output")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    api = make_api("http://localhost:8529/_db/workflows/wms-service")
    create_workflow(api, output_dir)


if __name__ == "__main__":
    main()
