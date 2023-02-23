import json
from datetime import datetime
from pathlib import Path

import pytest

from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration
from swagger_client.models.file_model import FileModel
from swagger_client.models.hpc_config_model import HpcConfigModel
from swagger_client.models.job_definition import JobDefinition
from swagger_client.models.resource_requirements_model import ResourceRequirementsModel
from swagger_client.models.workflow import Workflow
from swagger_client.models.result_model import ResultModel


TEST_WORKFLOW = "test_workflow"
PREPROCESS = Path("tests") / "scripts" / "preprocess.py"
POSTPROCESS = Path("tests") / "scripts" / "postprocess.py"
WORK = Path("tests") / "scripts" / "work.py"
INVALID = Path("tests") / "scripts" / "invalid.py"
NOOP = Path("tests") / "scripts" / "noop.py"


@pytest.fixture
def diamond_workflow(tmp_path):
    """Creates a diamond workflow out of 4 jobs."""
    api = _initialize_api()
    api.delete_workflow()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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

    hpc_config = HpcConfigModel(
        name="debug", hpc_type="slurm", account="dsgrid", partition="debug"
    )

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
        user_data=[{"key1": "val1"}],
        input_files=[f1.name],
        output_files=[f2.name],
        resource_requirements=medium.name,
        scheduler=hpc_config.name,
    )
    work2 = JobDefinition(
        name="work2",
        command=f"python {WORK} -i {f1.path} -o {f3.path}",
        user_data=[{"key2": "val2"}],
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
    for file in workflow.files:
        path = Path(file.path)
        if path.exists():
            # file.file_hash = compute_file_hash(path)
            file.st_mtime = path.stat().st_mtime

    api.post_workflow(workflow)
    api.post_workflow_initialize_jobs()
    yield api, output_dir
    api.delete_workflow()


@pytest.fixture
def independent_job_workflow(num_jobs):
    """Creates a workflow out of independent jobs."""
    api = _initialize_api()
    api.delete_workflow()

    small = ResourceRequirementsModel(name="small", num_cpus=1, memory="1m", runtime="P0DT0H1M")
    jobs = []
    for i in range(num_jobs):
        job = JobDefinition(
            name=str(i),
            command="echo hello",
            resource_requirements=small.name,
        )
        jobs.append(job)

    workflow = Workflow(jobs=jobs, resource_requirements=[small])
    api.post_workflow(workflow)
    api.post_workflow_initialize_jobs()
    yield api, num_jobs
    api.delete_workflow()


def _initialize_api():
    configuration = Configuration()
    configuration.host = "http://localhost:8529/_db/workflows/wms-service"
    return DefaultApi(ApiClient(configuration))


@pytest.fixture
def workflow_with_cancel(tmp_path, cancel_on_blocking_job_failure):
    """Creates a diamond workflow out of 4 jobs."""
    api = _initialize_api()
    api.delete_workflow()

    job1 = JobDefinition(
        name="job1",
        command=f"python {INVALID}",
    )
    job2 = JobDefinition(
        name="job2",
        command=f"python {NOOP}",
        blocked_by=["job1"],
        cancel_on_blocking_job_failure=cancel_on_blocking_job_failure,
    )

    workflow = Workflow(jobs=[job1, job2])
    api.post_workflow(workflow)
    api.post_workflow_initialize_jobs()
    yield api, tmp_path, cancel_on_blocking_job_failure
    api.delete_workflow()


@pytest.fixture
def completed_workflow(diamond_workflow):
    """Fakes a completed diamond workflow."""
    api, output_dir = diamond_workflow
    job_names = [job.name for job in api.get_jobs().items]
    for name in job_names:
        # Completing a job this way will cause blocked jobs to change status and revision,
        # so we need to update each time.
        job = api.get_jobs_name(name)
        status = "done"
        result = ResultModel(
            name=name,
            return_code=0,
            exec_time_minutes=5,
            completion_time=str(datetime.now()),
            status=status,
        )
        job = api.post_jobs_complete_job_name_status_rev(result, name, status, job._rev)

    for file in api.get_files().items:
        path = Path(file.path)
        if not path.exists():
            path.touch()
            file.st_mtime = path.stat().st_mtime
            api.put_files_name(file, file.name)

    yield api, output_dir


@pytest.fixture
def incomplete_workflow(diamond_workflow):
    """Fakes an incomplete diamond workflow.
    One work job and the postprocess job are not complete.
    """
    api, output_dir = diamond_workflow
    for name in ("preprocess", "work1"):
        job = api.get_jobs_name(name)
        status = "done"
        result = ResultModel(
            name=name,
            return_code=0,
            exec_time_minutes=5,
            completion_time=str(datetime.now()),
            status=status,
        )
        job = api.post_jobs_complete_job_name_status_rev(result, name, status, job._rev)

        for file in api.get_files_produced_by_job_name(name).items:
            path = Path(file.path)
            if not path.exists():
                path.touch()
                # file.file_hash = compute_file_hash(path)
                file.st_mtime = path.stat().st_mtime
                api.put_files_name(file, file.name)

    assert api.get_jobs_name("preprocess").status == "done"
    assert api.get_jobs_name("work1").status == "done"
    assert api.get_jobs_name("work2").status == "ready"
    assert api.get_jobs_name("postprocess").status == "blocked"
    yield api, output_dir


@pytest.fixture
def incomplete_workflow_missing_files(incomplete_workflow):
    """Fakes an incomplete diamond workflow.
    One work job and the postprocess job are not complete.
    The file produced by the work job that completed is deleted.
    """
    api, output_dir = incomplete_workflow
    (output_dir / "f2.json").unlink()
    yield api, output_dir


@pytest.fixture
def complete_workflow_missing_files(completed_workflow):
    """Fakes an completed diamond workflow and then deletes the specified file."""
    api, output_dir = completed_workflow
    yield api, output_dir
