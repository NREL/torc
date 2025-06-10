"""pytest fixtures"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pytest
from click.testing import CliRunner

from torc import WorkflowManager, add_jobs, iter_documents, map_function_to_jobs
from torc.common import GiB
from torc.config import torc_settings
from torc.openapi_client import (
    ApiClient,
    ComputeNodeModel,
    ComputeNodeResourceStatsModel,
    ComputeNodesResources,
    Configuration,
    DefaultApi,
    FileModel,
    JobModel,
    JobSpecificationModel,
    LocalSchedulerModel,
    ResourceRequirementsModel,
    ResultModel,
    SlurmSchedulerModel,
    UserDataModel,
    WorkflowConfigModel,
    WorkflowModel,
    WorkflowSpecificationModel,
    WorkflowSpecificationsSchedulers,
)
from torc.cli.torc import cli
from torc.loggers import setup_logging
from torc.utils.files import load_json_file, dump_json_file
from torc.tests.database_interface import DatabaseInterface

from slurm_cluster import SlurmCluster


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

SACCT = Path(__file__).parent / "fake_sacct.py"
SBATCH = Path(__file__).parent / "fake_sbatch.py"
SCANCEL = Path(__file__).parent / "fake_scancel.py"
SQUEUE = Path(__file__).parent / "fake_squeue.py"


def pytest_sessionstart(session):
    """Records existing workflows."""
    api = _initialize_api()
    session.torc_workflow_keys = {x.key for x in iter_documents(api.list_workflows)}
    os.environ["TORC_FAKE_SACCT"] = f"{sys.executable} {SACCT}"
    os.environ["TORC_FAKE_SBATCH"] = f"{sys.executable} {SBATCH}"
    os.environ["TORC_FAKE_SCANCEL"] = f"{sys.executable} {SCANCEL}"
    os.environ["TORC_FAKE_SQUEUE"] = f"{sys.executable} {SQUEUE}"
    SlurmCluster.initialize()
    with open("tests/slurm.json", "w") as f:
        json.dump({"active_nodes": []}, f)


def pytest_sessionfinish(session, exitstatus):
    """Deletes any workflows created by the tests."""
    api = _initialize_api()
    for key in {x.key for x in iter_documents(api.list_workflows)} - session.torc_workflow_keys:
        api.remove_workflow(key)
    SlurmCluster.delete()


@pytest.fixture
def diamond_workflow(tmp_path):
    """Creates a diamond workflow out of 4 jobs using file-based dependencies."""
    api = _initialize_api()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    inputs_file = output_dir / "inputs.json"
    inputs_file.write_text(json.dumps({"val": 5}))

    workflow = api.add_workflow(
        WorkflowModel(
            user="tester",
            name="test_diamond_workflow",
            description="Test diamond workflow",
        )
    )

    inputs = api.add_file(workflow.key, FileModel(name="inputs", path=str(inputs_file)))
    f1 = api.add_file(workflow.key, FileModel(name="file1", path=str(output_dir / "f1.json")))
    f2 = api.add_file(workflow.key, FileModel(name="file2", path=str(output_dir / "f2.json")))
    f3 = api.add_file(workflow.key, FileModel(name="file3", path=str(output_dir / "f3.json")))
    f4 = api.add_file(workflow.key, FileModel(name="file4", path=str(output_dir / "f4.json")))
    f5 = api.add_file(workflow.key, FileModel(name="file5", path=str(output_dir / "f5.json")))

    small = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="small", num_cpus=1, memory="1g", runtime="P0DT1H"),
    )
    medium = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="medium", num_cpus=2, memory="2g", runtime="P0DT8H"),
    )
    large = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="large", num_cpus=2, memory="3g", runtime="P0DT12H"),
    )

    scheduler = api.add_local_scheduler(workflow.key, LocalSchedulerModel(name="test"))
    ud1 = api.add_user_data(
        workflow.key,
        UserDataModel(
            name="my_val1",
            is_ephemeral=False,
            data={"key1": "val1"},
        ),
    )
    ud2 = api.add_user_data(
        workflow.key,
        UserDataModel(
            name="my_val2",
            is_ephemeral=False,
            data={"key2": "val2"},
        ),
    )
    add_jobs(
        api,
        workflow.key,
        [
            JobModel(
                name="preprocess",
                command=f"python {PREPROCESS} -i {inputs.path} -o {f1.path} -o {f2.path}",
                input_files=[inputs.id],
                output_files=[f1.id, f2.id],
                resource_requirements=small.id,
                scheduler=scheduler.id,
            ),
            JobModel(
                name="work1",
                command=f"python {WORK} -i {f1.path} -o {f3.path}",
                input_user_data=[ud1.id],
                input_files=[f1.id],
                output_files=[f3.id],
                resource_requirements=medium.id,
                scheduler=scheduler.id,
            ),
            JobModel(
                name="work2",
                command=f"python {WORK} -i {f2.path} -o {f4.path}",
                input_user_data=[ud2.id],
                input_files=[f2.id],
                output_files=[f4.id],
                resource_requirements=large.id,
                scheduler=scheduler.id,
            ),
            JobModel(
                name="postprocess",
                command=f"python {POSTPROCESS} -i {f3.path} -i {f4.path} -o {f5.path}",
                input_files=[f3.id, f4.id],
                output_files=[f5.id],
                resource_requirements=small.id,
                scheduler=scheduler.id,
            ),
        ],
    )

    db = DatabaseInterface(api, workflow)
    config = api.get_workflow_config(db.workflow.key)
    config.workflow_completion_script = "echo hello"
    api.modify_workflow_config(db.workflow.key, config)
    api.initialize_jobs(workflow.key)
    scheduler = db.get_document("local_schedulers", "test")
    yield db, scheduler.id, output_dir
    api.remove_workflow(workflow.key)


@pytest.fixture
def diamond_workflow_user_data(tmp_path):
    """Creates a diamond workflow out of 4 jobs using user-data-based dependencies."""
    api = _initialize_api()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    workflow = api.add_workflow(
        WorkflowModel(
            user="tester",
            name="test_diamond_workflow",
            description="Test diamond workflow",
        )
    )
    inputs = api.add_user_data(workflow.key, UserDataModel(name="inputs", data={"val": 5}))
    d1 = api.add_user_data(workflow.key, UserDataModel(name="data1"))
    d2 = api.add_user_data(workflow.key, UserDataModel(name="data2"))
    d3 = api.add_user_data(workflow.key, UserDataModel(name="data3"))
    d4 = api.add_user_data(workflow.key, UserDataModel(name="data4"))
    d5 = api.add_user_data(workflow.key, UserDataModel(name="data5"))

    small = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="small", num_cpus=1, memory="1g", runtime="P0DT1H"),
    )
    medium = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="medium", num_cpus=2, memory="2g", runtime="P0DT8H"),
    )
    large = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="large", num_cpus=2, memory="3g", runtime="P0DT12H"),
    )

    scheduler = api.add_local_scheduler(workflow.key, LocalSchedulerModel(name="test"))
    add_jobs(
        api,
        workflow.key,
        [
            JobModel(
                name="preprocess",
                command=f"python {PREPROCESS_UD}",
                input_user_data=[inputs.id],
                output_user_data=[d1.id, d2.id],
                resource_requirements=small.id,
                scheduler=scheduler.id,
            ),
            JobModel(
                name="work1",
                command=f"python {WORK_UD}",
                input_user_data=[d1.id],
                output_user_data=[d3.id],
                resource_requirements=medium.id,
                scheduler=scheduler.id,
            ),
            JobModel(
                name="work2",
                command=f"python {WORK_UD}",
                input_user_data=[d2.id],
                output_user_data=[d4.id],
                resource_requirements=large.id,
                scheduler=scheduler.id,
            ),
            JobModel(
                name="postprocess",
                command=f"python {POSTPROCESS_UD}",
                input_user_data=[d3.id, d4.id],
                output_user_data=[d5.id],
                resource_requirements=small.id,
                scheduler=scheduler.id,
            ),
        ],
    )

    db = DatabaseInterface(api, workflow)
    api.initialize_jobs(workflow.key)
    scheduler = db.get_document("local_schedulers", "test")
    yield db, scheduler.id, output_dir
    api.remove_workflow(workflow.key)


@pytest.fixture
def workflow_with_ephemeral_resource():
    """Creates a workflow with one job that creates an ephemeral resource."""
    api = _initialize_api()

    workflow = api.add_workflow(
        WorkflowModel(
            user="tester",
            name="test_ephemeral_resource_workflow",
            description="Test workflow with ephemeral resource",
        )
    )
    resource = api.add_user_data(workflow.key, UserDataModel(name="resource", is_ephemeral=True))
    api.add_job(
        workflow.key,
        JobModel(
            name="create_resource",
            command=f"python {CREATE_RESOURCE_JOB}",
            output_user_data=[resource.id],
        ),
    )
    api.add_job(
        workflow.key,
        JobModel(
            name="use_resource",
            command=f"python {USE_RESOURCE_JOB}",
            input_user_data=[resource.id],
        ),
    )

    db = DatabaseInterface(api, workflow)
    api.initialize_jobs(workflow.key)
    yield db
    api.remove_workflow(workflow.key)


@pytest.fixture
def independent_job_workflow(num_jobs):
    """Creates a workflow out of independent jobs."""
    api = _initialize_api()

    workflow = api.add_workflow(WorkflowModel(user="test", name="test"))
    small = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(
            name="small",
            num_cpus=1,
            memory="1m",
            runtime="P0DT0H1M",
        ),
    )

    for i in range(num_jobs):
        job = JobModel(
            name=str(i),
            command="echo hello",
            resource_requirements=small.id,
        )
        api.add_job(workflow.key, job)

    db = DatabaseInterface(api, workflow)
    api.initialize_jobs(workflow.key)
    yield db, num_jobs
    api.remove_workflow(workflow.key)


def _initialize_api():
    if torc_settings.database_url is None:
        print(
            "database_url must be set in torc config files to run this test",
            file=sys.stderr,
        )
        sys.exit(1)

    setup_logging()
    configuration = Configuration()
    configuration.host = torc_settings.database_url
    return DefaultApi(ApiClient(configuration))


@pytest.fixture
def workflow_with_cancel(tmp_path, cancel_on_blocking_job_failure):
    """Creates a workflow with a job that can be canceled by a blocked job."""
    api = _initialize_api()
    bad_job = JobSpecificationModel(
        name="bad_job",
        command=f"python {INVALID}",
    )
    job1 = JobSpecificationModel(
        name="job1",
        command=f"python {SLEEP_JOB} 1",
    )
    job2 = JobSpecificationModel(
        name="job2",
        command=f"python {SLEEP_JOB} 1",
    )
    postprocess = JobSpecificationModel(
        name="postprocess",
        command=f"python {NOOP}",
        blocked_by=["bad_job", "job1", "job2"],
        cancel_on_blocking_job_failure=cancel_on_blocking_job_failure,
    )

    spec = WorkflowSpecificationModel(jobs=[bad_job, job1, job2, postprocess])
    workflow = api.add_workflow_specification(spec)
    db = DatabaseInterface(api, workflow)
    api.initialize_jobs(workflow.key)
    yield db, tmp_path, cancel_on_blocking_job_failure
    api.remove_workflow(workflow.key)


@pytest.fixture
def completed_workflow(diamond_workflow):
    """Fakes a completed diamond workflow."""
    db, scheduler_config_id, output_dir = diamond_workflow
    api = db.api
    for file in api.list_files(db.workflow.key).items:
        path = Path(file.path)
        if not path.exists():
            path.touch()
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    workflow_status = api.get_workflow_status(db.workflow.key)

    compute_node = _create_compute_node(api, db.workflow.key)
    for name in ("preprocess", "work1", "work2", "postprocess"):
        # Completing a job this way will cause blocked jobs to change status and revision,
        # so we need to update each time.
        job = db.get_document("jobs", name)
        status = "done"
        result = ResultModel(
            job_key=job.key,
            run_id=workflow_status.run_id,
            return_code=0,
            exec_time_minutes=5,
            completion_time=str(datetime.now()),
            status=status,
        )
        job = api.complete_job(
            db.workflow.key,
            job.key,
            status,
            job.rev,
            workflow_status.run_id,
            compute_node.key,
            result,
        )
    workflow_status.has_detected_need_to_run_completion_script = True
    api.modify_workflow_status(db.workflow.key, workflow_status)

    yield db, scheduler_config_id, output_dir


@pytest.fixture
def incomplete_workflow(diamond_workflow):
    """Fakes an incomplete diamond workflow.
    One work job and the postprocess job are not complete.
    """
    db, scheduler_config_id, output_dir = diamond_workflow
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    compute_node = _create_compute_node(api, db.workflow.key)
    mgr.start()
    for name in ("preprocess", "work1"):
        job = db.get_document("jobs", name)
        status = "done"
        result = ResultModel(
            job_key=job.key,
            run_id=1,
            return_code=0,
            exec_time_minutes=5,
            completion_time=str(datetime.now()),
            status=status,
        )
        job = api.complete_job(
            db.workflow.key, job.id, status, job.rev, 1, compute_node.key, result
        )

        for file in api.list_files_produced_by_job(db.workflow.key, job.key).items:
            path = Path(file.path)
            if not path.exists():
                path.touch()
                # file.file_hash = compute_file_hash(path)
                file.st_mtime = path.stat().st_mtime
                api.modify_file(db.workflow.key, file.key, file)

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
    (output_dir / "f3.json").unlink()
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

    small = ResourceRequirementsModel(name="small", num_cpus=1, memory="1g", runtime="P0DT1H")
    medium = ResourceRequirementsModel(name="medium", num_cpus=2, memory="2g", runtime="P0DT8H")
    large = ResourceRequirementsModel(name="large", num_cpus=2, memory="3g", runtime="P0DT12H")

    num_jobs_per_category = 3
    small_jobs = [
        JobSpecificationModel(
            name=f"job_small{i}",
            command=f"python {RC_JOB} -i {i} -c small",
            resource_requirements=small.name,
        )
        for i in range(1, num_jobs_per_category + 1)
    ]
    medium_jobs = [
        JobSpecificationModel(
            name=f"job_medium{i}",
            command=f"python {RC_JOB} -i {i} -c medium",
            resource_requirements=medium.name,
        )
        for i in range(1, num_jobs_per_category + 1)
    ]
    large_jobs = [
        JobSpecificationModel(
            name=f"job_large{i}",
            command=f"python {RC_JOB} -i {i} -c large",
            resource_requirements=large.name,
        )
        for i in range(1, num_jobs_per_category + 1)
    ]

    spec = WorkflowSpecificationModel(
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

    workflow = api.add_workflow_specification(spec)
    db = DatabaseInterface(api, workflow)
    api.initialize_jobs(workflow.key)
    yield db, output_dir, monitor_type
    api.remove_workflow(workflow.key)


@pytest.fixture
def cancelable_workflow(tmp_path):
    """Creates a workflow with jobs that can be canceled."""
    api = _initialize_api()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    small = ResourceRequirementsModel(name="small", num_cpus=1, memory="1g", runtime="P0DT1S")
    scheduler = LocalSchedulerModel(name="test")
    jobs = [
        JobSpecificationModel(
            name="job1",
            command=f"python {SLEEP_JOB} 1000",
            resource_requirements="small",
            supports_termination=True,
        ),
        JobSpecificationModel(
            name="job2",
            command=f"python {SLEEP_JOB} 1000",
            resource_requirements="small",
            supports_termination=True,
        ),
    ]

    spec = WorkflowSpecificationModel(
        jobs=jobs,
        resource_requirements=[small],
        schedulers=WorkflowSpecificationsSchedulers(local_schedulers=[scheduler]),
    )

    workflow = api.add_workflow_specification(spec)
    db = DatabaseInterface(api, workflow)
    scheduler = db.get_document("local_schedulers", "test")
    api.initialize_jobs(workflow.key)
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    yield db, scheduler.id, output_dir
    api.remove_workflow(workflow.key)


@pytest.fixture()
def create_workflow_cli(tmp_path_factory):
    """Creates a temporary workflow with the CLI."""
    api = _initialize_api()
    url = api.api_client.configuration.host
    tmp_path = tmp_path_factory.mktemp("torc")
    file = Path(__file__).parents[2] / "examples" / "independent_workflow.json5"
    data = load_json_file(file)
    data["config"]["compute_node_resource_stats"]["interval"] = 1
    if "CI" in os.environ:
        for req in data["resource_requirements"]:
            req["memory"] = "1m"
            req["num_cpus"] = 1
    w_file = tmp_path / file.name
    dump_json_file(data, w_file)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["-u", url, "-F", "json", "workflows", "create-from-json-file", str(w_file)],
    )
    assert result.exit_code == 0
    key = json.loads(result.stdout)["key"]
    yield key, url, tmp_path
    result = runner.invoke(cli, ["-n", "-k", key, "-u", url, "workflows", "delete", key])
    assert result.exit_code == 0


@pytest.fixture
def mapped_function_workflow(tmp_path):
    """Creates a workflow out of a function mapped to jobs."""
    api = _initialize_api()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    workflow = api.add_workflow(WorkflowModel(user="test", name="test_workflow"))
    params = [{"val": i} for i in range(5)]
    map_function_to_jobs(
        api,
        workflow.key,
        "mapped_function",
        "run",
        params,
        module_directory="tests/scripts",
        postprocess_func="postprocess",
    )
    db = DatabaseInterface(api, workflow)
    yield db, output_dir
    api.remove_workflow(workflow.key)


@pytest.fixture
def job_requirement_uniform():
    """Creates a workflow with uniform resource requirements."""
    api = _initialize_api()
    workflow = api.add_workflow(WorkflowModel(user="tester", name="test"))
    short = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="short", num_cpus=4, memory="4g", runtime="P0DT30M"),
    )

    jobs = [
        JobModel(name=f"job{i}", command="noop", resource_requirements=short.id)
        for i in range(1, 31)
    ]
    add_jobs(api, workflow.key, jobs)
    db = DatabaseInterface(api, workflow)
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    yield db
    api.remove_workflow(workflow.key)


@pytest.fixture
def job_requirement_runtime():
    """Creates a workflow with two different runtime resource requirements."""
    api = _initialize_api()
    workflow = api.add_workflow(WorkflowModel(user="tester", name="test"))
    short = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="short", num_cpus=4, memory="4g", runtime="P0DT40M"),
    )
    medium = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="medium", num_cpus=4, memory="4g", runtime="P0DT50M"),
    )

    api.add_job(
        workflow.key, JobModel(name="short_job", command="noop", resource_requirements=short.id)
    )
    api.add_job(
        workflow.key, JobModel(name="medium_job", command="noop", resource_requirements=medium.id)
    )

    db = DatabaseInterface(api, workflow)
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    yield db
    api.remove_workflow(workflow.key)


@pytest.fixture
def job_requirement_variations():
    """Creates a workflow with varying resource requirements."""
    api = _initialize_api()
    workflow = api.add_workflow(WorkflowModel(user="tester", name="test"))
    medium = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="medium", num_cpus=12, memory="8g", runtime="P0DT1H"),
    )
    large = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="large", num_cpus=18, memory="16g", runtime="P0DT1H"),
    )
    gpu = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(
            name="gpu", num_cpus=1, num_gpus=1, memory="32g", runtime="P0DT1H"
        ),
    )
    short = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="short", num_cpus=4, memory="4g", runtime="P0DT30M"),
    )
    long = api.add_resource_requirements(
        workflow.key,
        ResourceRequirementsModel(name="long", num_cpus=4, memory="8g", runtime="P0DT24H"),
    )
    api.add_slurm_scheduler(
        workflow.key,
        SlurmSchedulerModel(
            name="standard",
            account="my_account",
            nodes=1,
            walltime="04:00:00",
        ),
    )
    bigmem_scheduler = api.add_slurm_scheduler(
        workflow.key,
        SlurmSchedulerModel(
            name="bigmem",
            account="my_account",
            nodes=1,
            partition="bigmem",
            walltime="04:00:00",
        ),
    )

    # Order is important so that the tests can check that GPUs and memory are prioritized -
    # GPU and bigmem nodes should not pick up small jobs.
    jobs = [JobModel(name="short_job", command="noop", resource_requirements=short.id)]
    for i in range(1, 11):
        jobs.append(
            JobModel(name=f"medium_job{i}", command="noop", resource_requirements=medium.id)
        )
    for i in range(1, 11):
        jobs.append(
            JobModel(
                name=f"large_job{i}",
                command="noop",
                resource_requirements=large.id,
                scheduler=bigmem_scheduler.id,
            )
        )
    jobs += [
        JobModel(
            name="large_job_no_scheduler",
            command="noop",
            resource_requirements=large.id,
        ),
        JobModel(name="gpu_job", command="noop", resource_requirements=gpu.id),
        JobModel(name="long_job", command="noop", resource_requirements=long.id),
    ]
    add_jobs(api, workflow.key, jobs)
    db = DatabaseInterface(api, workflow)
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    yield db
    api.remove_workflow(workflow.key)


@pytest.fixture
def db_api():
    """Returns an api instance."""
    api = _initialize_api()
    yield api, api.api_client.configuration.host


def pytest_addoption(parser):
    """Create a CLI parameter for slurm_account"""
    parser.addoption("--slurm-account", action="store", default="")


@pytest.fixture(scope="session")
def slurm_account(pytestconfig):
    """Access the CLI parameter for slurm_account"""
    return pytestconfig.getoption("slurm_account")


def _create_compute_node(api, workflow_key):
    return api.add_compute_node(
        workflow_key,
        ComputeNodeModel(
            hostname="localhost",
            pid=os.getpid(),
            start_time=str(datetime.now()),
            resources=ComputeNodesResources(
                num_cpus=4,
                memory_gb=10 / GiB,
                num_nodes=1,
                time_limit=None,
                num_gpus=0,
            ),
            is_active=True,
            scheduler={},
        ),
    )
