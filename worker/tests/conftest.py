"""pytest fixtures"""

# pylint: disable=redefined-outer-name,duplicate-code

import json
from datetime import datetime
from pathlib import Path

import pytest

from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration
from swagger_client.models.workflow_scheduler import WorkflowScheduler
from swagger_client.models.workflow_schedulers import WorkflowSchedulers
from swagger_client.models.file_model import FileModel
from swagger_client.models.local_schedulers_model import LocalSchedulersModel
from swagger_client.models.job_definition import JobDefinition
from swagger_client.models.resource_requirements_model import ResourceRequirementsModel
from swagger_client.models.workflow_model import WorkflowModel
from swagger_client.models.result_model import ResultModel
from swagger_client.models.workflow_config_compute_node_resource_stats import (
    WorkflowConfigComputeNodeResourceStats,
)
from swagger_client.models.workflow_config_model import WorkflowConfigModel


TEST_WORKFLOW = "test_workflow"
PREPROCESS = Path("tests") / "scripts" / "preprocess.py"
POSTPROCESS = Path("tests") / "scripts" / "postprocess.py"
WORK = Path("tests") / "scripts" / "work.py"
INVALID = Path("tests") / "scripts" / "invalid.py"
NOOP = Path("tests") / "scripts" / "noop.py"
RC_JOB = Path("tests") / "scripts" / "resource_consumption.py"


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

    scheduler = LocalSchedulersModel(name="local")
    preprocess = JobDefinition(
        name="preprocess",
        command=f"python {PREPROCESS} -i {inputs.path} -o {f1.path}",
        input_files=[inputs.name],
        output_files=[f1.name],
        resource_requirements=small.name,
        scheduler=WorkflowScheduler(name="local", type="local"),
    )
    work1 = JobDefinition(
        name="work1",
        command=f"python {WORK} -i {f1.path} -o {f2.path}",
        user_data=[{"key1": "val1"}],
        input_files=[f1.name],
        output_files=[f2.name],
        resource_requirements=medium.name,
        scheduler=WorkflowScheduler(name="local", type="local"),
    )
    work2 = JobDefinition(
        name="work2",
        command=f"python {WORK} -i {f1.path} -o {f3.path}",
        user_data=[{"key2": "val2"}],
        input_files=[f1.name],
        output_files=[f3.name],
        resource_requirements=large.name,
        scheduler=WorkflowScheduler(name="local", type="local"),
    )
    postprocess = JobDefinition(
        name="postprocess",
        command=f"python {POSTPROCESS} -i {f2.path} -i {f3.path} -o {f4.path}",
        input_files=[f2.name, f3.name],
        output_files=[f4.name],
        resource_requirements=small.name,
        scheduler=WorkflowScheduler(name="local", type="local"),
    )

    workflow = WorkflowModel(
        files=[inputs, f1, f2, f3, f4],
        jobs=[preprocess, work1, work2, postprocess],
        resource_requirements=[small, medium, large],
        schedulers=WorkflowSchedulers(local_schedulers=[scheduler]),
    )
    for file in workflow.files:
        path = Path(file.path)
        if path.exists():
            # file.file_hash = compute_file_hash(path)
            file.st_mtime = path.stat().st_mtime

    api.post_workflow(workflow)
    api.post_workflow_initialize_jobs()
    scheduler = api.get_local_schedulers_key("local")
    yield api, scheduler.id, output_dir
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

    workflow = WorkflowModel(jobs=jobs, resource_requirements=[small])
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

    workflow = WorkflowModel(jobs=[job1, job2])
    api.post_workflow(workflow)
    api.post_workflow_initialize_jobs()
    yield api, tmp_path, cancel_on_blocking_job_failure
    api.delete_workflow()


@pytest.fixture
def completed_workflow(diamond_workflow):
    """Fakes a completed diamond workflow."""
    api, scheduler_config_id, output_dir = diamond_workflow
    status = api.get_workflow_status()
    status.run_id = 1
    api.put_workflow_status(status)
    job_names = [job.name for job in api.get_jobs().items]
    for name in job_names:
        # Completing a job this way will cause blocked jobs to change status and revision,
        # so we need to update each time.
        job = api.get_jobs_key(name)
        # Fake out what normally happens at submission time.
        job.run_id += 1
        job = api.put_jobs_key(job, name)
        status = "done"
        result = ResultModel(
            name=name,
            run_id=job.run_id,
            return_code=0,
            exec_time_minutes=5,
            completion_time=str(datetime.now()),
            status=status,
        )
        job = api.post_jobs_complete_job_key_status_rev(
            result, name, status, job._rev  # pylint: disable=protected-access
        )

    for file in api.get_files().items:
        path = Path(file.path)
        if not path.exists():
            path.touch()
            file.st_mtime = path.stat().st_mtime
            api.put_files_key(file, file.name)

    yield api, scheduler_config_id, output_dir


@pytest.fixture
def incomplete_workflow(diamond_workflow):
    """Fakes an incomplete diamond workflow.
    One work job and the postprocess job are not complete.
    """
    api, scheduler_config_id, output_dir = diamond_workflow
    for name in ("preprocess", "work1"):
        job = api.get_jobs_key(name)
        status = "done"
        result = ResultModel(
            name=name,
            run_id=job.run_id,
            return_code=0,
            exec_time_minutes=5,
            completion_time=str(datetime.now()),
            status=status,
        )
        job = api.post_jobs_complete_job_key_status_rev(
            result, name, status, job._rev  # pylint: disable=protected-access
        )

        for file in api.get_files_produced_by_job_key(name).items:
            path = Path(file.path)
            if not path.exists():
                path.touch()
                # file.file_hash = compute_file_hash(path)
                file.st_mtime = path.stat().st_mtime
                api.put_files_key(file, file.name)

    assert api.get_jobs_key("preprocess").status == "done"
    assert api.get_jobs_key("work1").status == "done"
    assert api.get_jobs_key("work2").status == "ready"
    assert api.get_jobs_key("postprocess").status == "blocked"
    yield api, scheduler_config_id, output_dir


@pytest.fixture
def incomplete_workflow_missing_files(incomplete_workflow):
    """Fakes an incomplete diamond workflow.
    One work job and the postprocess job are not complete.
    The file produced by the work job that completed is deleted.
    """
    api, scheduler_config_id, output_dir = incomplete_workflow
    (output_dir / "f2.json").unlink()
    yield api, scheduler_config_id, output_dir


@pytest.fixture
def complete_workflow_missing_files(completed_workflow):
    """Fakes an completed diamond workflow and then deletes the specified file."""
    api, scheduler_config_id, output_dir = completed_workflow
    yield api, scheduler_config_id, output_dir


@pytest.fixture
def multi_resource_requirement_workflow(tmp_path):
    """Creates a workflow with jobs that need different categories of resource requirements."""
    api = _initialize_api()
    api.delete_workflow()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    small = ResourceRequirementsModel(name="small", num_cpus=1, memory="1g", runtime="P0DT1H")
    medium = ResourceRequirementsModel(name="medium", num_cpus=4, memory="8g", runtime="P0DT8H")
    large = ResourceRequirementsModel(name="large", num_cpus=8, memory="16g", runtime="P0DT12H")

    scheduler = LocalSchedulersModel(name="local")
    num_jobs_per_category = 3
    small_jobs = [
        JobDefinition(
            name=f"job_small{i}",
            command=f"python {RC_JOB} -i {i} -c small",
            resource_requirements=small.name,
            scheduler=WorkflowScheduler(name="local", type="local"),
        )
        for i in range(1, num_jobs_per_category + 1)
    ]
    medium_jobs = [
        JobDefinition(
            name=f"job_medium{i}",
            command=f"python {RC_JOB} -i {i} -c medium",
            resource_requirements=medium.name,
            scheduler=WorkflowScheduler(name="local", type="local"),
        )
        for i in range(1, num_jobs_per_category + 1)
    ]
    large_jobs = [
        JobDefinition(
            name=f"job_large{i}",
            command=f"python {RC_JOB} -i {i} -c large",
            resource_requirements=large.name,
            scheduler=WorkflowScheduler(name="local", type="local"),
        )
        for i in range(1, num_jobs_per_category + 1)
    ]

    workflow = WorkflowModel(
        jobs=small_jobs + medium_jobs + large_jobs,
        resource_requirements=[small, medium, large],
        schedulers=WorkflowSchedulers(local_schedulers=[scheduler]),
        config=WorkflowConfigModel(
            compute_node_resource_stats=WorkflowConfigComputeNodeResourceStats(
                cpu=True,
                memory=True,
                process=True,
                interval=0.1,
            )
        ),
    )

    api.post_workflow(workflow)
    scheduler = api.get_local_schedulers_key("local")
    api.post_workflow_initialize_jobs()
    yield api, scheduler.id, output_dir
    api.delete_workflow()
