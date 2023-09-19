"""pytest fixtures"""

# pylint: disable=redefined-outer-name,duplicate-code

import getpass
import json
import sys
from datetime import datetime
from pathlib import Path

import pytest
from click.testing import CliRunner
from torc.openapi_client import ApiClient, DefaultApi
from torc.openapi_client.configuration import Configuration
from torc.openapi_client.models.workflow_specifications_schedulers import (
    WorkflowSpecificationsSchedulers,
)
from torc.openapi_client.models.workflow_local_schedulers_model import (
    WorkflowLocalSchedulersModel,
)
from torc.openapi_client.models.workflow_job_specifications_model import (
    WorkflowJobSpecificationsModel,
)
from torc.openapi_client.models.workflow_resource_requirements_model import (
    WorkflowResourceRequirementsModel,
)
from torc.openapi_client.models.workflow_specifications_model import (
    WorkflowSpecificationsModel,
)
from torc.openapi_client.models.workflow_config_model import (
    WorkflowConfigModel,
)
from torc.openapi_client.models.workflow_results_model import WorkflowResultsModel
from torc.openapi_client.models.compute_node_resource_stats_model import (
    ComputeNodeResourceStatsModel,
)
from torc.api import iter_documents
from torc.cli.torc import cli
from torc.torc_rc import TorcRuntimeConfig
from torc.utils.files import load_data, dump_data
from torc.workflow_builder import WorkflowBuilder
from torc.workflow_manager import WorkflowManager
from torc.tests.database_interface import DatabaseInterface


TEST_WORKFLOW = "test_workflow"
PREPROCESS = Path("tests") / "scripts" / "preprocess.py"
POSTPROCESS = Path("tests") / "scripts" / "postprocess.py"
WORK = Path("tests") / "scripts" / "work.py"
PREPROCESS_UD = Path("tests") / "scripts" / "preprocess_ud.py"
POSTPROCESS_UD = Path("tests") / "scripts" / "postprocess_ud.py"
WORK_UD = Path("tests") / "scripts" / "work_ud.py"
INVALID = Path("tests") / "scripts" / "invalid.py"
NOOP = Path("tests") / "scripts" / "noop.py"
RC_JOB = Path("tests") / "scripts" / "resource_consumption.py"
CREATE_RESOURCE_JOB = Path("tests") / "scripts" / "create_resource.py"
USE_RESOURCE_JOB = Path("tests") / "scripts" / "use_resource.py"
SLEEP_JOB = Path("tests") / "scripts" / "sleep.py"


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
    """Creates a diamond workflow out of 4 jobs using file-based dependencies."""
    api = _initialize_api()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    inputs_file = output_dir / "inputs.json"
    inputs_file.write_text(json.dumps({"val": 5}))

    builder = WorkflowBuilder()
    inputs = builder.add_file(name="inputs", path=str(inputs_file))
    f1 = builder.add_file(name="file1", path=str(output_dir / "f1.json"))
    f2 = builder.add_file(name="file2", path=str(output_dir / "f2.json"))
    f3 = builder.add_file(name="file3", path=str(output_dir / "f3.json"))
    f4 = builder.add_file(name="file4", path=str(output_dir / "f4.json"))

    small = builder.add_resource_requirements(
        name="small", num_cpus=1, memory="1g", runtime="P0DT1H"
    )
    medium = builder.add_resource_requirements(
        name="medium", num_cpus=4, memory="8g", runtime="P0DT8H"
    )
    large = builder.add_resource_requirements(
        name="large", num_cpus=8, memory="16g", runtime="P0DT12H"
    )

    scheduler = builder.add_local_scheduler(name="test")
    builder.add_job(
        name="preprocess",
        command=f"python {PREPROCESS} -i {inputs.path} -o {f1.path}",
        input_files=[inputs.name],
        output_files=[f1.name],
        resource_requirements=small.name,
        scheduler="local_schedulers/test",
    )
    builder.add_job(
        name="work1",
        command=f"python {WORK} -i {f1.path} -o {f2.path}",
        input_user_data=["my_val1"],
        input_files=[f1.name],
        output_files=[f2.name],
        resource_requirements=medium.name,
        scheduler="local_schedulers/test",
    )
    builder.add_job(
        name="work2",
        command=f"python {WORK} -i {f1.path} -o {f3.path}",
        input_user_data=["my_val2"],
        input_files=[f1.name],
        output_files=[f3.name],
        resource_requirements=large.name,
        scheduler="local_schedulers/test",
    )
    builder.add_job(
        name="postprocess",
        command=f"python {POSTPROCESS} -i {f2.path} -i {f3.path} -o {f4.path}",
        input_files=[f2.name, f3.name],
        output_files=[f4.name],
        resource_requirements=small.name,
        scheduler="local_schedulers/test",
    )
    builder.add_user_data(
        name="my_val1",
        is_ephemeral=False,
        data={"key1": "val1"},
    )
    builder.add_user_data(
        name="my_val2",
        is_ephemeral=False,
        data={"key2": "val2"},
    )

    spec = builder.build()
    workflow = api.post_workflow_specifications(spec)
    db = DatabaseInterface(api, workflow)
    api.post_workflows_key_initialize_jobs(workflow.key)
    scheduler = db.get_document("local_schedulers", "test")
    yield db, scheduler.id, output_dir
    api.delete_workflows_key(workflow.key)
    api.api_client.close()


@pytest.fixture
def diamond_workflow_user_data(tmp_path):
    """Creates a diamond workflow out of 4 jobs using user-data-based dependencies."""
    api = _initialize_api()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    builder = WorkflowBuilder()
    inputs = builder.add_user_data(name="inputs", data={"val": 5})
    d1 = builder.add_user_data(name="data1")
    d2 = builder.add_user_data(name="data2")
    d3 = builder.add_user_data(name="data3")
    d4 = builder.add_user_data(name="data4")
    d5 = builder.add_user_data(name="data5")

    small = builder.add_resource_requirements(
        name="small", num_cpus=1, memory="1g", runtime="P0DT1H"
    )
    medium = builder.add_resource_requirements(
        name="medium", num_cpus=4, memory="8g", runtime="P0DT8H"
    )
    large = builder.add_resource_requirements(
        name="large", num_cpus=8, memory="16g", runtime="P0DT12H"
    )

    scheduler = builder.add_local_scheduler(name="test")
    builder.add_job(
        name="preprocess",
        command=f"python {PREPROCESS_UD}",
        input_user_data=[inputs.name],
        output_user_data=[d1.name, d2.name],
        resource_requirements=small.name,
        scheduler="local_schedulers/test",
    )
    builder.add_job(
        name="work1",
        command=f"python {WORK_UD}",
        input_user_data=[d1.name],
        output_user_data=[d3.name],
        resource_requirements=medium.name,
        scheduler="local_schedulers/test",
    )
    builder.add_job(
        name="work2",
        command=f"python {WORK_UD}",
        input_user_data=[d2.name],
        output_user_data=[d4.name],
        resource_requirements=large.name,
        scheduler="local_schedulers/test",
    )
    builder.add_job(
        name="postprocess",
        command=f"python {POSTPROCESS_UD}",
        input_user_data=[d3.name, d4.name],
        output_user_data=[d5.name],
        resource_requirements=small.name,
        scheduler="local_schedulers/test",
    )

    spec = builder.build()
    workflow = api.post_workflow_specifications(spec)
    db = DatabaseInterface(api, workflow)
    api.post_workflows_key_initialize_jobs(workflow.key)
    scheduler = db.get_document("local_schedulers", "test")
    yield db, scheduler.id, output_dir
    api.delete_workflows_key(workflow.key)
    api.api_client.close()


@pytest.fixture
def workflow_with_ephemeral_resource():
    """Creates a workflow with one job that creates an ephemeral resource."""
    api = _initialize_api()

    builder = WorkflowBuilder()
    resource = builder.add_user_data(name="resource", is_ephemeral=True)
    builder.add_job(
        name="create_resource",
        command=f"python {CREATE_RESOURCE_JOB}",
        output_user_data=[resource.name],
    )
    builder.add_job(
        name="use_resource",
        command=f"python {USE_RESOURCE_JOB}",
        input_user_data=[resource.name],
    )

    spec = builder.build()
    workflow = api.post_workflow_specifications(spec)
    db = DatabaseInterface(api, workflow)
    api.post_workflows_key_initialize_jobs(workflow.key)
    yield db
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
    api.post_workflows_key_initialize_jobs(workflow.key)
    yield db, num_jobs
    api.delete_workflows_key(workflow.key)
    api.api_client.close()


def _initialize_api():
    config = TorcRuntimeConfig.load()
    if config.database_url is None:
        print(
            f"database_url must be set in {TorcRuntimeConfig.path()} to run this test",
            file=sys.stderr,
        )
        sys.exit(1)

    configuration = Configuration()
    configuration.host = config.database_url
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
    api.post_workflows_key_initialize_jobs(workflow.key)
    yield db, tmp_path, cancel_on_blocking_job_failure
    api.delete_workflows_key(workflow.key)
    api.api_client.close()


@pytest.fixture
def completed_workflow(diamond_workflow):
    """Fakes a completed diamond workflow."""
    db, scheduler_config_id, output_dir = diamond_workflow
    api = db.api
    for file in api.get_workflows_workflow_files(db.workflow.key).items:
        path = Path(file.path)
        if not path.exists():
            path.touch()
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    workflow_status = api.get_workflows_key_status(db.workflow.key)

    for name in ("preprocess", "work1", "work2", "postprocess"):
        # Completing a job this way will cause blocked jobs to change status and revision,
        # so we need to update each time.
        job = db.get_document("jobs", name)
        status = "done"
        result = WorkflowResultsModel(
            job_key=job.key,
            run_id=workflow_status.run_id,
            return_code=0,
            exec_time_minutes=5,
            completion_time=str(datetime.now()),
            status=status,
        )
        job = api.post_workflows_workflow_jobs_key_complete_job_status_rev_run_id(
            db.workflow.key, job.key, status, job.rev, workflow_status.run_id, result
        )

    yield db, scheduler_config_id, output_dir


@pytest.fixture
def incomplete_workflow(diamond_workflow):
    """Fakes an incomplete diamond workflow.
    One work job and the postprocess job are not complete.
    """
    db, scheduler_config_id, output_dir = diamond_workflow
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    for name in ("preprocess", "work1"):
        job = db.get_document("jobs", name)
        status = "done"
        result = WorkflowResultsModel(
            job_key=job.key,
            run_id=1,
            return_code=0,
            exec_time_minutes=5,
            completion_time=str(datetime.now()),
            status=status,
        )
        job = api.post_workflows_workflow_jobs_key_complete_job_status_rev_run_id(
            db.workflow.key, job.id, status, job.rev, 1, result
        )

        for file in api.get_workflows_workflow_files_produced_by_job_key(
            db.workflow.key, job.key
        ).items:
            path = Path(file.path)
            if not path.exists():
                path.touch()
                # file.file_hash = compute_file_hash(path)
                file.st_mtime = path.stat().st_mtime
                api.put_workflows_workflow_files_key(db.workflow.key, file.key, file)

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

    num_jobs_per_category = 3
    small_jobs = [
        WorkflowJobSpecificationsModel(
            name=f"job_small{i}",
            command=f"python {RC_JOB} -i {i} -c small",
            resource_requirements=small.name,
        )
        for i in range(1, num_jobs_per_category + 1)
    ]
    medium_jobs = [
        WorkflowJobSpecificationsModel(
            name=f"job_medium{i}",
            command=f"python {RC_JOB} -i {i} -c medium",
            resource_requirements=medium.name,
        )
        for i in range(1, num_jobs_per_category + 1)
    ]
    large_jobs = [
        WorkflowJobSpecificationsModel(
            name=f"job_large{i}",
            command=f"python {RC_JOB} -i {i} -c large",
            resource_requirements=large.name,
        )
        for i in range(1, num_jobs_per_category + 1)
    ]

    spec = WorkflowSpecificationsModel(
        jobs=small_jobs + medium_jobs + large_jobs,
        resource_requirements=[small, medium, large],
        config=WorkflowConfigModel(
            compute_node_resource_stats=ComputeNodeResourceStatsModel(
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
    api.post_workflows_key_initialize_jobs(workflow.key)
    yield db, output_dir, monitor_type
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
    api.post_workflows_key_initialize_jobs(workflow.key)
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    yield db, scheduler.id, output_dir
    api.delete_workflows_key(workflow.key)
    api.api_client.close()


@pytest.fixture()
def create_workflow_cli(tmp_path_factory):
    """Creates a temporary workflow with the CLI."""
    api = _initialize_api()
    url = api.api_client.configuration.host
    tmp_path = tmp_path_factory.mktemp("torc")
    file = Path(__file__).parent.parent.parent / "examples" / "independent_workflow.json5"
    data = load_data(file)
    data["config"]["compute_node_resource_stats"]["interval"] = 1
    w_file = tmp_path / file.name
    dump_data(data, w_file)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli,
        ["-u", url, "-F", "json", "workflows", "create-from-json-file", str(w_file)],
    )
    assert result.exit_code == 0
    key = json.loads(result.stdout)["key"]
    yield key, url, tmp_path
    result = runner.invoke(cli, ["-n", "-k", key, "-u", url, "workflows", "delete", key])
    assert result.exit_code == 0
    api.api_client.close()


@pytest.fixture
def mapped_function_workflow(tmp_path):
    """Creates a workflow out of a function mapped to jobs."""
    api = _initialize_api()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    builder = WorkflowBuilder()
    params = [{"val": i} for i in range(5)]
    builder.map_function_to_jobs(
        "mapped_function",
        "run",
        params,
        module_directory="tests/scripts",
        postprocess_func="postprocess",
    )
    spec = builder.build()
    workflow = api.post_workflow_specifications(spec)
    db = DatabaseInterface(api, workflow)
    yield db, output_dir
    api.delete_workflows_key(workflow.key)
    api.api_client.close()


@pytest.fixture
def job_requirement_variations():
    """Creates a workflow with varying resource requirements."""
    api = _initialize_api()
    builder = WorkflowBuilder()
    medium = builder.add_resource_requirements(
        name="medium", num_cpus=12, memory="8g", runtime="P0DT1H"
    )
    large = builder.add_resource_requirements(
        name="large", num_cpus=18, memory="16g", runtime="P0DT1H"
    )
    gpu = builder.add_resource_requirements(
        name="gpu", num_cpus=1, num_gpus=1, memory="32g", runtime="P0DT1H"
    )
    short = builder.add_resource_requirements(
        name="short", num_cpus=4, memory="4g", runtime="P0DT30M"
    )
    long = builder.add_resource_requirements(
        name="long", num_cpus=4, memory="8g", runtime="P0DT24H"
    )
    builder.add_slurm_scheduler(
        name="standard",
        account="my_account",
        nodes=1,
        walltime="04:00:00",
    )
    builder.add_slurm_scheduler(
        name="bigmem",
        account="my_account",
        nodes=1,
        partition="bigmem",
        walltime="04:00:00",
    )

    # Order is important so that the tests can check that GPUs and memory are prioritized -
    # GPU and bigmem nodes should not pick up small jobs.
    builder.add_job(name="short_job", command="noop", resource_requirements=short.name)
    for i in range(1, 11):
        builder.add_job(name=f"medium_job{i}", command="noop", resource_requirements=medium.name)
    for i in range(1, 11):
        builder.add_job(
            name=f"large_job{i}",
            command="noop",
            resource_requirements=large.name,
            scheduler="slurm_schedulers/bigmem",
        )
    builder.add_job(name="gpu_job", command="noop", resource_requirements=gpu.name)
    builder.add_job(name="long_job", command="noop", resource_requirements=long.name)

    spec = builder.build(user=getpass.getuser(), name="test")
    workflow = api.post_workflow_specifications(spec)
    db = DatabaseInterface(api, workflow)
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    yield db
    api.delete_workflows_key(workflow.key)
    api.api_client.close()


@pytest.fixture
def db_api():
    """Returns an api instance."""
    api = _initialize_api()
    yield api, api.api_client.configuration.host
    api.api_client.close()


def pytest_addoption(parser):
    """Create a CLI parameter for slurm_account"""
    parser.addoption("--slurm-account", action="store", default="")


@pytest.fixture(scope="session")
def slurm_account(pytestconfig):
    """Access the CLI parameter for slurm_account"""
    return pytestconfig.getoption("slurm_account")
