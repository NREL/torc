"""pytest fixtures"""

# pylint: disable=redefined-outer-name,duplicate-code

import json
from datetime import datetime
from pathlib import Path

import pytest
from click.testing import CliRunner
from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration
from swagger_client.models.workflow_specifications_schedulers import (
    WorkflowSpecificationsSchedulers,
)
from swagger_client.models.workflow_files_model import WorkflowFilesModel
from swagger_client.models.workflow_local_schedulers_model import WorkflowLocalSchedulersModel
from swagger_client.models.workflow_job_specifications_model import WorkflowJobSpecificationsModel
from swagger_client.models.workflow_resource_requirements_model import (
    WorkflowResourceRequirementsModel,
)
from swagger_client.models.workflow_specifications_model import WorkflowSpecificationsModel
from swagger_client.models.workflow_results_model import WorkflowResultsModel
from swagger_client.models.workflow_config_compute_node_resource_stats import (
    WorkflowConfigComputeNodeResourceStats,
)
from swagger_client.models.workflow_config_model import WorkflowConfigModel

from torc.api import iter_documents
from torc.cli.torc import cli
from torc.workflow_manager import WorkflowManager
from torc.tests.database_interface import DatabaseInterface


TEST_WORKFLOW = "test_workflow"
PREPROCESS = Path("tests") / "scripts" / "preprocess.py"
POSTPROCESS = Path("tests") / "scripts" / "postprocess.py"
WORK = Path("tests") / "scripts" / "work.py"
INVALID = Path("tests") / "scripts" / "invalid.py"
NOOP = Path("tests") / "scripts" / "noop.py"
RC_JOB = Path("tests") / "scripts" / "resource_consumption.py"
SLEEP_JOB = Path("tests") / "scripts" / "sleep.py"
URL = "http://localhost:8529/_db/test-workflows/torc-service"


def pytest_sessionstart(session):
    """Records existing workflows."""
    api = _initialize_api()
    session.torc_workflow_keys = {x.key for x in iter_documents(api.get_workflows)}
    api.api_client.close()


def pytest_sessionfinish(session, exitstatus):  # pylint: disable=unused-argument
    """Deletes any workflows created by the tests."""
    api = _initialize_api()
    for key in {x.key for x in iter_documents(api.get_workflows)} - session.torc_workflow_keys:
        api.delete_workflows_key(key)
    api.api_client.close()


@pytest.fixture
def diamond_workflow(tmp_path):
    """Creates a diamond workflow out of 4 jobs."""
    api = _initialize_api()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    inputs_file = output_dir / "inputs.json"
    inputs_file.write_text(json.dumps({"val": 5}))

    inputs = WorkflowFilesModel(name="inputs", path=str(inputs_file))
    f1 = WorkflowFilesModel(name="file1", path=str(output_dir / "f1.json"))
    f2 = WorkflowFilesModel(name="file2", path=str(output_dir / "f2.json"))
    f3 = WorkflowFilesModel(name="file3", path=str(output_dir / "f3.json"))
    f4 = WorkflowFilesModel(name="file4", path=str(output_dir / "f4.json"))

    small = WorkflowResourceRequirementsModel(
        name="small", num_cpus=1, memory="1g", runtime="P0DT1H"
    )
    medium = WorkflowResourceRequirementsModel(
        name="medium", num_cpus=4, memory="8g", runtime="P0DT8H"
    )
    large = WorkflowResourceRequirementsModel(
        name="large", num_cpus=8, memory="16g", runtime="P0DT12H"
    )

    scheduler = WorkflowLocalSchedulersModel(name="test")
    preprocess = WorkflowJobSpecificationsModel(
        name="preprocess",
        command=f"python {PREPROCESS} -i {inputs.path} -o {f1.path}",
        input_files=[inputs.name],
        output_files=[f1.name],
        resource_requirements=small.name,
        scheduler="local_schedulers/test",
    )
    work1 = WorkflowJobSpecificationsModel(
        name="work1",
        command=f"python {WORK} -i {f1.path} -o {f2.path}",
        user_data=[{"key1": "val1"}],
        input_files=[f1.name],
        output_files=[f2.name],
        resource_requirements=medium.name,
        scheduler="local_schedulers/test",
    )
    work2 = WorkflowJobSpecificationsModel(
        name="work2",
        command=f"python {WORK} -i {f1.path} -o {f3.path}",
        user_data=[{"key2": "val2"}],
        input_files=[f1.name],
        output_files=[f3.name],
        resource_requirements=large.name,
        scheduler="local_schedulers/test",
    )
    postprocess = WorkflowJobSpecificationsModel(
        name="postprocess",
        command=f"python {POSTPROCESS} -i {f2.path} -i {f3.path} -o {f4.path}",
        input_files=[f2.name, f3.name],
        output_files=[f4.name],
        resource_requirements=small.name,
        scheduler="local_schedulers/test",
    )

    spec = WorkflowSpecificationsModel(
        files=[inputs, f1, f2, f3, f4],
        jobs=[preprocess, work1, work2, postprocess],
        resource_requirements=[small, medium, large],
        schedulers=WorkflowSpecificationsSchedulers(local_schedulers=[scheduler]),
    )

    workflow = api.post_workflow_specifications(spec)
    db = DatabaseInterface(api, workflow)
    api.post_workflows_initialize_jobs_key(workflow.key)
    scheduler = db.get_document("local_schedulers", "test")
    yield db, scheduler.id, output_dir
    api.delete_workflows_key(workflow.key)
    api.api_client.close()


@pytest.fixture
def independent_job_workflow(num_jobs):
    """Creates a workflow out of independent jobs."""
    api = _initialize_api()

    small = WorkflowResourceRequirementsModel(
        name="small", num_cpus=1, memory="1m", runtime="P0DT0H1M"
    )
    jobs = []
    for i in range(num_jobs):
        job = WorkflowJobSpecificationsModel(
            name=str(i),
            command="echo hello",
            resource_requirements=small.name,
        )
        jobs.append(job)

    spec = WorkflowSpecificationsModel(jobs=jobs, resource_requirements=[small])
    workflow = api.post_workflow_specifications(spec)
    db = DatabaseInterface(api, workflow)
    api.post_workflows_initialize_jobs_key(workflow.key)
    yield db, num_jobs
    api.delete_workflows_key(workflow.key)
    api.api_client.close()


def _initialize_api():
    configuration = Configuration()
    configuration.host = URL
    return DefaultApi(ApiClient(configuration))


@pytest.fixture
def workflow_with_cancel(tmp_path, cancel_on_blocking_job_failure):
    """Creates a diamond workflow out of 4 jobs."""
    api = _initialize_api()
    job1 = WorkflowJobSpecificationsModel(
        name="job1",
        command=f"python {INVALID}",
    )
    job2 = WorkflowJobSpecificationsModel(
        name="job2",
        command=f"python {NOOP}",
        blocked_by=["job1"],
        cancel_on_blocking_job_failure=cancel_on_blocking_job_failure,
    )

    spec = WorkflowSpecificationsModel(jobs=[job1, job2])
    workflow = api.post_workflow_specifications(spec)
    db = DatabaseInterface(api, workflow)
    api.post_workflows_initialize_jobs_key(workflow.key)
    yield db, tmp_path, cancel_on_blocking_job_failure
    api.delete_workflows_key(workflow.key)
    api.api_client.close()


@pytest.fixture
def completed_workflow(diamond_workflow):
    """Fakes a completed diamond workflow."""
    db, scheduler_config_id, output_dir = diamond_workflow
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.initialize_files()
    status = api.get_workflows_status_key(db.workflow.key)
    status.run_id = 1
    api.put_workflows_status_key(status, db.workflow.key)
    job_keys = [job.key for job in api.get_workflows_workflow_jobs(db.workflow.key).items]
    for job_key in job_keys:
        # Completing a job this way will cause blocked jobs to change status and revision,
        # so we need to update each time.
        job = api.get_workflows_workflow_jobs_key(db.workflow.key, job_key)
        # Fake out what normally happens at submission time.
        job.run_id += 1
        job = api.put_workflows_workflow_jobs_key(job, db.workflow.key, job_key)
        status = "done"
        result = WorkflowResultsModel(
            job_key=job.key,
            job_name=job.name,
            run_id=job.run_id,
            return_code=0,
            exec_time_minutes=5,
            completion_time=str(datetime.now()),
            status=status,
        )
        job = api.post_workflows_workflow_jobs_key_complete_job_status_rev(
            result, db.workflow.key, job_key, status, job._rev  # pylint: disable=protected-access
        )

    for file in api.get_workflows_workflow_files(db.workflow.key).items:
        path = Path(file.path)
        if not path.exists():
            path.touch()
            file.st_mtime = path.stat().st_mtime
            api.put_workflows_workflow_files_key(file, db.workflow.key, file.key)

    yield db, scheduler_config_id, output_dir


@pytest.fixture
def incomplete_workflow(diamond_workflow):
    """Fakes an incomplete diamond workflow.
    One work job and the postprocess job are not complete.
    """
    db, scheduler_config_id, output_dir = diamond_workflow
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.initialize_files()
    for name in ("preprocess", "work1"):
        job = db.get_document("jobs", name)
        status = "done"
        result = WorkflowResultsModel(
            job_key=job.key,
            job_name=job.name,
            run_id=job.run_id,
            return_code=0,
            exec_time_minutes=5,
            completion_time=str(datetime.now()),
            status=status,
        )
        job = api.post_workflows_workflow_jobs_key_complete_job_status_rev(
            result, db.workflow.key, job.id, status, job._rev  # pylint: disable=protected-access
        )

        for file in api.get_workflows_workflow_files_produced_by_job_key(
            db.workflow.key, job.key
        ).items:
            path = Path(file.path)
            if not path.exists():
                path.touch()
                # file.file_hash = compute_file_hash(path)
                file.st_mtime = path.stat().st_mtime
                api.put_workflows_workflow_files_key(file, db.workflow.key, file.key)

    assert db.get_document("jobs", "preprocess").status == "done"
    assert db.get_document("jobs", "work1").status == "done"
    assert db.get_document("jobs", "work2").status == "ready"
    assert db.get_document("jobs", "postprocess").status == "blocked"
    yield db, scheduler_config_id, output_dir


@pytest.fixture
def incomplete_workflow_missing_files(incomplete_workflow):
    """Fakes an incomplete diamond workflow.
    One work job and the postprocess job are not complete.
    The file produced by the work job that completed is deleted.
    """
    db, scheduler_config_id, output_dir = incomplete_workflow
    (output_dir / "f2.json").unlink()
    yield db, scheduler_config_id, output_dir


@pytest.fixture
def complete_workflow_missing_files(completed_workflow):
    """Fakes an completed diamond workflow and then deletes the specified file."""
    db, scheduler_config_id, output_dir = completed_workflow
    yield db, scheduler_config_id, output_dir


@pytest.fixture
def multi_resource_requirement_workflow(tmp_path, monitor_type):
    """Creates a workflow with jobs that need different categories of resource requirements."""
    api = _initialize_api()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    small = WorkflowResourceRequirementsModel(
        name="small", num_cpus=1, memory="1g", runtime="P0DT1H"
    )
    medium = WorkflowResourceRequirementsModel(
        name="medium", num_cpus=4, memory="8g", runtime="P0DT8H"
    )
    large = WorkflowResourceRequirementsModel(
        name="large", num_cpus=8, memory="16g", runtime="P0DT12H"
    )

    scheduler = WorkflowLocalSchedulersModel(name="test")
    num_jobs_per_category = 3
    small_jobs = [
        WorkflowJobSpecificationsModel(
            name=f"job_small{i}",
            command=f"python {RC_JOB} -i {i} -c small",
            resource_requirements=small.name,
            scheduler="local_schedulers/test",
        )
        for i in range(1, num_jobs_per_category + 1)
    ]
    medium_jobs = [
        WorkflowJobSpecificationsModel(
            name=f"job_medium{i}",
            command=f"python {RC_JOB} -i {i} -c medium",
            resource_requirements=medium.name,
            scheduler="local_schedulers/test",
        )
        for i in range(1, num_jobs_per_category + 1)
    ]
    large_jobs = [
        WorkflowJobSpecificationsModel(
            name=f"job_large{i}",
            command=f"python {RC_JOB} -i {i} -c large",
            resource_requirements=large.name,
            scheduler="local_schedulers/test",
        )
        for i in range(1, num_jobs_per_category + 1)
    ]

    spec = WorkflowSpecificationsModel(
        jobs=small_jobs + medium_jobs + large_jobs,
        resource_requirements=[small, medium, large],
        schedulers=WorkflowSpecificationsSchedulers(local_schedulers=[scheduler]),
        config=WorkflowConfigModel(
            compute_node_resource_stats=WorkflowConfigComputeNodeResourceStats(
                cpu=True,
                memory=True,
                process=True,
                interval=0.1,
                monitor_type=monitor_type,
                make_plots=True,
            )
        ),
    )

    workflow = api.post_workflow_specifications(spec)
    db = DatabaseInterface(api, workflow)
    scheduler = db.get_document("local_schedulers", "test")
    api.post_workflows_initialize_jobs_key(workflow.key)
    yield db, scheduler.id, output_dir, monitor_type
    api.delete_workflows_key(workflow.key)
    api.api_client.close()


@pytest.fixture
def cancelable_workflow(tmp_path):
    """Creates a workflow with jobs that can be canceled."""
    api = _initialize_api()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    small = WorkflowResourceRequirementsModel(
        name="small", num_cpus=1, memory="1g", runtime="P0DT1S"
    )
    scheduler = WorkflowLocalSchedulersModel(name="test")
    jobs = [
        WorkflowJobSpecificationsModel(
            name="job1",
            command=f"python {SLEEP_JOB} 1000",
            resource_requirements="small",
            supports_termination=True,
        ),
        WorkflowJobSpecificationsModel(
            name="job2",
            command=f"python {SLEEP_JOB} 1000",
            resource_requirements="small",
            supports_termination=True,
        ),
    ]

    spec = WorkflowSpecificationsModel(
        jobs=jobs,
        resource_requirements=[small],
        schedulers=WorkflowSpecificationsSchedulers(local_schedulers=[scheduler]),
    )

    workflow = api.post_workflow_specifications(spec)
    db = DatabaseInterface(api, workflow)
    scheduler = db.get_document("local_schedulers", "test")
    api.post_workflows_initialize_jobs_key(workflow.key)
    yield db, scheduler.id, output_dir
    api.delete_workflows_key(workflow.key)
    api.api_client.close()


@pytest.fixture()
def create_workflow_cli(tmp_path_factory):
    """Creates a temporary workflow with the CLI."""
    tmp_path = tmp_path_factory.mktemp("torc")
    file = Path(__file__).parent.parent.parent / "examples" / "independent_workflow.json5"
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli, ["-u", URL, "-F", "json", "workflows", "create-from-json-file", str(file)]
    )
    assert result.exit_code == 0
    key = json.loads(result.stdout)["key"]
    yield key, URL, tmp_path
    result = runner.invoke(cli, ["-k", key, "-u", URL, "workflows", "delete", key])
    assert result.exit_code == 0


@pytest.fixture
def db_api():
    """Returns an api instance."""
    api = _initialize_api()
    yield api, URL
    api.api_client.close()


def pytest_addoption(parser):
    """Create a CLI parameter for slurm_account"""
    parser.addoption("--slurm-account", action="store", default="")


@pytest.fixture(scope="session")
def slurm_account(pytestconfig):
    """Access the CLI parameter for slurm_account"""
    return pytestconfig.getoption("slurm_account")
