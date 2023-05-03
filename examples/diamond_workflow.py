"""Example diamond workflow"""

import getpass
import json
import logging
from pathlib import Path

from torc.api import make_api
from torc.workflow_builder import WorkflowBuilder


TEST_WORKFLOW = "test_workflow"
PREPROCESS = Path("tests") / "worker" / "scripts" / "preprocess.py"
POSTPROCESS = Path("tests") / "worker" / "scripts" / "postprocess.py"
WORK = Path("tests") / "worker" / "scripts" / "work.py"

logger = logging.getLogger(__name__)


def create_workflow(api):
    """Creates a workflow with implicit job dependencies declared through files."""
    builder = WorkflowBuilder()
    inputs_file = Path("inputs.json")
    inputs_file.write_text(json.dumps({"val": 5}), encoding="utf-8")

    inputs = builder.add_file(name="inputs", path=str(inputs_file))
    f1 = builder.add_file(name="file1", path="f1.json")
    f2 = builder.add_file(name="file2", path="f2.json")
    f3 = builder.add_file(name="file3", path="f3.json")
    f4 = builder.add_file(name="file4", path="f4.json")

    small = builder.add_resource_requirements(
        name="small", num_cpus=1, memory="1g", runtime="P0DT1H"
    )
    medium = builder.add_resource_requirements(
        name="medium", num_cpus=4, memory="8g", runtime="P0DT8H"
    )
    large = builder.add_resource_requirements(
        name="large", num_cpus=8, memory="16g", runtime="P0DT12H"
    )

    builder.add_job(
        name="preprocess",
        command=f"python {PREPROCESS} -i {inputs.path} -o {f1.path}",
        input_files=[inputs.name],
        output_files=[f1.name],
        resource_requirements=small.name,
        consumes_user_data=["my_val"],
    )
    builder.add_job(
        name="work1",
        command=f"python {WORK} -i {f1.path} -o {f2.path}",
        input_files=[f1.name],
        output_files=[f2.name],
        resource_requirements=medium.name,
    )
    builder.add_job(
        name="work2",
        command=f"python {WORK} -i {f1.path} -o {f3.path}",
        input_files=[f1.name],
        output_files=[f3.name],
        resource_requirements=large.name,
    )
    builder.add_job(
        name="postprocess",
        command=f"python {POSTPROCESS} -i {f2.path} -i {f3.path} -o {f4.path}",
        input_files=[f2.name, f3.name],
        output_files=[f4.name],
        resource_requirements=small.name,
    )
    builder.add_user_data(
        name="my_val",
        is_ephemeral=False,
        data={"key1": "val1"},
    )

    spec = builder.build(
        user=getpass.getuser(),
        name="diamond_workflow",
        description="Example diamond workflow",
    )
    workflow = api.post_workflow_specifications(spec)
    print(f"Created workflow {workflow.key} with 4 jobs")


def main():
    """Entry point"""
    api = make_api("http://localhost:8529/_db/test-workflows/torc-service")
    create_workflow(api)


if __name__ == "__main__":
    main()
