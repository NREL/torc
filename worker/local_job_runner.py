import json
import logging
import shutil
from pathlib import Path

from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration
from swagger_client.rest import ApiException
from swagger_client.models.file_model import FileModel
from swagger_client.models.hpc_config_model import HpcConfigModel
from swagger_client.models.job_model import JobModel
from swagger_client.models.job_definition import JobDefinition
from swagger_client.models.resource_requirements_model import ResourceRequirementsModel
from swagger_client.models.workflow import Workflow

from wms.loggers import setup_logging
from wms.job_runner import JobRunner


TEST_WORKFLOW = "test_workflow"
PREPROCESS = Path("tests") / "preprocess.py"
POSTPROCESS = Path("tests") / "postprocess.py"
WORK = Path("tests") / "work.py"

logger = logging.getLogger(__name__)


def create_database(api: DefaultApi):
    api.delete_workflow()


def create_workflow(api: DefaultApi, output_dir: Path):
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

    hpc_config = HpcConfigModel(name="debug", hpc_type="slurm", account="dsgrid", partition="debug")

    preprocess = JobDefinition(
        name="preprocess",
        command=f"python {PREPROCESS} -i {inputs.path} -o {f1.path}",
        input_files=[inputs.name],
        output_files=[f1.name],
        resource_requirements=small.name,
        scheduler=hpc_config.name,
    )
    work1 = JobDefinition(
        name="work1",
        command=f"python {WORK} -i {f1.path} -o {f2.path}",
        input_files=[f1.name],
        output_files=[f2.name],
        resource_requirements=medium.name,
        scheduler=hpc_config.name,
    )
    work2 = JobDefinition(
        name="work2",
        command=f"python {WORK} -i {f1.path} -o {f3.path}",
        input_files=[f1.name],
        output_files=[f3.name],
        resource_requirements=large.name,
        scheduler=hpc_config.name,
    )
    postprocess = JobDefinition(
        name="postprocess",
        command=f"python {POSTPROCESS} -i {f2.path} -i {f3.path} -o {f4.path}",
        input_files=[f2.name, f3.name],
        output_files=[f4.name],
        resource_requirements=small.name,
        scheduler=hpc_config.name,
    )

    workflow = Workflow(
        files=[inputs, f1, f2, f3, f4],
        jobs=[preprocess, work1, work2, postprocess],
        resource_requirements=[small, medium, large],
        schedulers=[hpc_config],
    )
    api.post_workflow(workflow)
    api.post_workflow_initialize_jobs()
    logger.info("Created workflow")


def run_workflow(db, output_dir: Path):
    runner = JobRunner(db, output_dir, time_limit="P0DT24H")
    logger.info("Start workflow")
    runner.run_worker()


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from prettytable import PrettyTable

    usage = f"Usage: python {sys.argv[0]} create|recommend|run"
    if len(sys.argv) == 1:
        print(usage, file=sys.stderr)
        sys.exit(1)

    setup_logging("wms")

    configuration = Configuration()
    configuration.host = "http://localhost:8529/_db/workflows/wms-service"
    api = DefaultApi(ApiClient(configuration))

    output_dir = Path("output")
    mode = sys.argv[1]
    if mode == "create":
        if output_dir.exists():
            shutil.rmtree(output_dir)
        create_database(api)
        create_workflow(api, output_dir)
    elif mode == "estimate":
        data = api.post_workflow_estimate()
        table = PrettyTable(title="Resource Estimates")
        table.field_names = ("round", "num_jobs", "num_cpus", "memory_gb", "num_gpus")
        for i, row in enumerate(data.estimates_by_round, start=1):
            table.add_row((i, row["num_jobs"], row["num_cpus"], row["memory_gb"], row["num_gpus"]))
        print(table)
    elif mode == "run":
        create_database(api)
        create_workflow(api, output_dir)
        run_workflow(api, output_dir)
    else:
        print(usage, file=sys.stderr)
        sys.exit(1)
