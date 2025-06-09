"""Test workflow execution"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pytest
from click.testing import CliRunner
from torc.openapi_client.api.default_api import DefaultApi
from torc.openapi_client.models.user_data_model import UserDataModel
from torc.openapi_client.models.compute_node_model import ComputeNodeModel
from torc.openapi_client.models.compute_nodes_resources import ComputeNodesResources
from torc.openapi_client.models.result_model import ResultModel
from torc.openapi_client.models.job_model import JobModel
from torc.api import iter_documents, add_jobs, wait_for_healthy_database
from torc.cli.torc import cli
from torc.common import GiB
from torc.exceptions import InvalidWorkflow
from torc.job_runner import JobRunner
from torc.common import timer_stats_collector
from torc.workflow_manager import WorkflowManager


def test_run_workflow(diamond_workflow):
    """Test full execution of diamond workflow with file dependencies."""
    db, scheduler_config_id, output_dir = diamond_workflow
    api: DefaultApi = db.api
    timer_stats_collector.enable()
    wait_for_healthy_database(api)
    user_data_work1 = api.list_job_user_data_consumes(
        db.workflow.key, db.get_document_key("jobs", "work1")
    )
    assert user_data_work1.items is not None
    assert len(user_data_work1.items) == 1
    assert user_data_work1.items[0].data is not None
    assert user_data_work1.items[0].data["key1"] == "val1"
    mgr = WorkflowManager(api, db.workflow.key)
    config = api.get_workflow_config(db.workflow.key)
    assert config.compute_node_resource_stats is not None
    config.compute_node_resource_stats.cpu = True
    config.compute_node_resource_stats.memory = True
    config.compute_node_resource_stats.process = True
    config.compute_node_resource_stats.interval = 1
    config.workflow_startup_script = "echo hello"
    config.workflow_completion_script = "echo hello"
    config.worker_startup_script = "echo hello"
    api.modify_workflow_config(db.workflow.key, config)
    mgr.start()
    runner = JobRunner(
        api,
        db.workflow,
        output_dir,
        time_limit="P0DT24H",
        job_completion_poll_interval=0.1,
        scheduler_config_id=scheduler_config_id,
    )
    runner.run_worker()

    assert api.is_workflow_complete(db.workflow.key).is_complete
    for name in ["preprocess", "work1", "work2", "postprocess"]:
        result = api.get_latest_job_result(db.workflow.key, db.get_document_key("jobs", name))
        assert result.return_code == 0

    for name in ["inputs", "file1", "file2", "file3", "file4"]:
        file = db.get_document("files", name)
        assert file.path
        # assert file.file_hash
        assert file.st_mtime

    result_data_work1 = UserDataModel(name="result1", data={"result": 1})
    result_data_overall = UserDataModel(name="overall_result", data={"overall_result": 2})
    result_data_work1 = api.add_job_user_data(
        db.workflow.key, db.get_document_key("jobs", "work1"), result_data_work1
    )
    ud_work1_consumes = api.list_job_user_data_consumes(
        db.workflow.key, db.get_document_key("jobs", "work1")
    )
    assert ud_work1_consumes.items is not None
    assert len(ud_work1_consumes.items) == 1
    ud_work1_produces = api.list_job_user_data_stores(
        db.workflow.key, db.get_document_key("jobs", "work1")
    )
    assert ud_work1_produces.items is not None
    assert len(ud_work1_produces.items) == 1
    result_data_overall = api.add_user_data(db.workflow.key, result_data_overall)
    assert db.workflow.key is not None
    assert result_data_overall.key is not None
    assert api.get_user_data(db.workflow.key, result_data_overall.key).name == "overall_result"

    events = db.list_documents("events")
    # start for workflow, start and stop for worker, start and stop for each job
    assert len(events) == 1 + 2 + 2 * 4

    timer_stats_collector.log_stats()
    stats_file = output_dir / "stats.json"
    assert not stats_file.exists()
    timer_stats_collector.log_json_stats(stats_file, clear=True)
    assert stats_file.exists()
    timer_stats_collector.log_stats(clear=True)

    cli_runner = CliRunner()
    cli_result = cli_runner.invoke(
        cli,
        [
            "-k",
            db.workflow.key,
            "-u",
            api.api_client.configuration.host,
            "graphs",
            "plot",
            "-k",
            "-o",
            str(output_dir),
            "job_job_dependencies",
            "job_file_dependencies",
            "job_user_data_dependencies",
        ],
    )
    assert cli_result.exit_code == 0
    for name in ("job_file_dependencies", "job_file_dependencies", "job_user_data_dependencies"):
        assert (output_dir / (name + ".dot")).exists()
        assert (output_dir / (name + ".dot.png")).exists()


def test_run_workflow_user_data_dependencies(diamond_workflow_user_data):
    """Test execution of diamond workflow with user data dependencies."""
    db, scheduler_config_id, output_dir = diamond_workflow_user_data
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    initial_value = db.get_document("user_data", "inputs").data["val"]

    def run_jobs(initial_val):
        runner = JobRunner(
            api,
            db.workflow,
            output_dir,
            time_limit="P0DT24H",
            job_completion_poll_interval=0.1,
            scheduler_config_id=scheduler_config_id,
        )
        runner.run_worker()

        assert api.is_workflow_complete(db.workflow.key).is_complete
        for name in ["preprocess", "work1", "work2", "postprocess"]:
            result = api.get_latest_job_result(db.workflow.key, db.get_document_key("jobs", name))
            assert result.return_code == 0

        expected_total = initial_val + 1 + 1 + initial_val + 2 + 1
        for name in ("inputs", "data1", "data2", "data3", "data4", "data5"):
            ud = db.get_document("user_data", name)
            assert ud.data
            if name == "data5":
                assert "result" in ud.data, ud.data
                assert ud.data["result"] == expected_total

    run_jobs(initial_value)

    mgr.restart()
    assert api.is_workflow_complete(db.workflow.key).is_complete

    ud = db.get_document("user_data", "inputs")
    new_value = 42
    ud.data["val"] = new_value
    api.modify_user_data(db.workflow.key, ud.key, ud)
    mgr.restart()
    assert not api.is_workflow_complete(db.workflow.key).is_complete
    for name in ["preprocess", "work1", "work2", "postprocess"]:
        job = api.get_job(db.workflow.key, db.get_document_key("jobs", name))
        if job.name == "preprocess":
            assert job.status == "ready"
        else:
            assert job.status == "blocked"

    run_jobs(new_value)


def test_run_workflow_user_data_ephemeral(workflow_with_ephemeral_resource, tmp_path):
    """Test execution of diamond workflow with user data dependencies."""
    db = workflow_with_ephemeral_resource
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    assert not db.get_document("user_data", "resource").data
    runner = JobRunner(
        api,
        db.workflow,
        tmp_path,
        time_limit="P0DT24H",
        job_completion_poll_interval=0.1,
    )
    runner.run_worker()
    assert api.is_workflow_complete(db.workflow.key).is_complete
    for result in iter_documents(api.list_results, db.workflow.key):
        assert result.return_code == 0
    assert db.get_document("user_data", "resource").data
    # Change the command so that the job gets rerun.
    job = db.get_document("jobs", "use_resource")
    job.command += " dummy_arg"
    api.modify_job(db.workflow.key, job.key, job)
    mgr.restart()
    assert not db.get_document("user_data", "resource").data
    runner = JobRunner(
        api,
        db.workflow,
        tmp_path,
        time_limit="P0DT24H",
        job_completion_poll_interval=0.1,
    )
    runner.run_worker()
    assert api.is_workflow_complete(db.workflow.key).is_complete
    count = 0
    for result in iter_documents(api.list_results, db.workflow.key):
        assert result.return_code == 0
        count += 1
    assert count == 4


def test_run_workflow_missing_files(diamond_workflow):
    """Verify that the check for missing files works."""
    db = diamond_workflow[0]
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    file = db.get_document("files", "inputs")
    Path(file.path).unlink()
    with pytest.raises(InvalidWorkflow):
        mgr.start()


def test_run_workflow_missing_user_data(diamond_workflow_user_data):
    """Verify that the check for missing user data works."""
    db = diamond_workflow_user_data[0]
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    ud = db.get_document("user_data", "inputs")
    ud.data.clear()
    api.modify_user_data(db.workflow.key, ud.key, ud)
    with pytest.raises(InvalidWorkflow):
        mgr.start()


def test_prepare_next_jobs_for_submission(diamond_workflow):
    """Test the API command prepare_next_jobs_for_submission."""
    db = diamond_workflow[0]
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    compute_node = _create_compute_node(api, db.workflow.key)
    mgr.start()
    result = api.prepare_next_jobs_for_submission(db.workflow.key, limit=5)
    assert len(result.jobs) == 1
    _fake_complete_job(api, db.workflow.key, result.jobs[0], compute_node)
    result = api.prepare_next_jobs_for_submission(db.workflow.key, limit=5)
    assert len(result.jobs) == 2
    for job in result.jobs:
        _fake_complete_job(api, db.workflow.key, job, compute_node)
    result = api.prepare_next_jobs_for_submission(db.workflow.key, limit=5)
    assert len(result.jobs) == 1
    _fake_complete_job(api, db.workflow.key, result.jobs[0], compute_node)
    assert api.is_workflow_complete(db.workflow.key).is_complete


@pytest.mark.parametrize("cancel_on_blocking_job_failure", [True, False])
def test_cancel_with_failed_job(workflow_with_cancel):
    """Test the cancel_on_blocking_job_failure feature for jobs."""
    db, output_dir, cancel_on_blocking_job_failure = workflow_with_cancel
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    runner = JobRunner(
        api,
        db.workflow,
        output_dir,
        time_limit="P0DT24H",
        job_completion_poll_interval=0.1,
    )
    runner.run_worker()
    assert api.is_workflow_complete(db.workflow.key).is_complete
    assert db.get_document("jobs", "bad_job").status == "done"
    assert db.get_document("jobs", "job1").status == "done"
    result = api.get_latest_job_result(db.workflow.key, db.get_document_key("jobs", "bad_job"))
    assert result.return_code == 1
    expected_status = "canceled" if cancel_on_blocking_job_failure else "done"
    assert db.get_document("jobs", "postprocess").status == expected_status


def test_reset_job_status_all(completed_workflow):
    """Verify that only job statuses can be reset."""
    db, _, _ = completed_workflow
    for name in ("preprocess", "work1", "work2", "postprocess"):
        assert db.get_document("jobs", name).status == "done"
    status = db.api.get_workflow_status(db.workflow.key)
    assert status.has_detected_need_to_run_completion_script
    db.api.reset_job_status(db.workflow.key, failed_only=False)
    for name in ("preprocess", "work1", "work2", "postprocess"):
        assert db.get_document("jobs", name).status == "uninitialized"

    mgr = WorkflowManager(db.api, db.workflow.key)
    mgr.restart()

    assert db.get_document("jobs", "preprocess").status == "ready"
    for name in ("work1", "work2", "postprocess"):
        assert db.get_document("jobs", name).status == "blocked"

    status = db.api.get_workflow_status(db.workflow.key)
    assert not status.has_detected_need_to_run_completion_script


def test_reset_job_status_failed_only(completed_workflow):
    """Verify that only jobs with failed status can be reset."""
    db, _, _ = completed_workflow
    for name in ("preprocess", "work1", "work2", "postprocess"):
        assert db.get_document("jobs", name).status == "done"
    job = db.get_document("jobs", "work2")
    result = db.api.get_latest_job_result(db.workflow.key, job.key)
    result.return_code = 1
    db.api.modify_result(db.workflow.key, result.key, result)
    db.api.reset_job_status(db.workflow.key, failed_only=True)
    assert db.get_document("jobs", "work2").status == "uninitialized"
    assert db.get_document("jobs", "postprocess").status == "uninitialized"
    for name in ("preprocess", "work1"):
        assert db.get_document("jobs", name).status == "done"

    mgr = WorkflowManager(db.api, db.workflow.key)
    mgr.restart()
    for name in ("preprocess", "work1"):
        assert db.get_document("jobs", name).status == "done"
    assert db.get_document("jobs", "work2").status == "ready"
    assert db.get_document("jobs", "postprocess").status == "blocked"


def test_reset_job_status_failed_blocked(completed_workflow):
    """Verify that resetting a failed job resets all downstream jobs."""
    db, _, _ = completed_workflow
    for name in ("preprocess", "work1", "work2", "postprocess"):
        assert db.get_document("jobs", name).status == "done"
    job = db.get_document("jobs", "preprocess")
    result = db.api.get_latest_job_result(db.workflow.key, job.key)
    result.return_code = 1
    db.api.modify_result(db.workflow.key, result.key, result)
    db.api.reset_job_status(db.workflow.key, failed_only=True)
    for name in ("preprocess", "work1", "work2", "postprocess"):
        assert db.get_document("jobs", name).status == "uninitialized"

    mgr = WorkflowManager(db.api, db.workflow.key)
    mgr.restart()

    assert db.get_document("jobs", "preprocess").status == "ready"
    for name in ("work1", "work2", "postprocess"):
        assert db.get_document("jobs", name).status == "blocked"


def test_reset_job_status_cli(completed_workflow):
    """Test the CLI command to reset job status."""
    db, _, _ = completed_workflow
    api = db.api
    for name in ("preprocess", "work1", "work2", "postprocess"):
        assert db.get_document("jobs", name).status == "done"
    job = db.get_document("jobs", "work1")
    result = db.api.get_latest_job_result(db.workflow.key, job.key)
    result.return_code = 1
    api.modify_result(db.workflow.key, result.key, result)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-k",
            db.workflow.key,
            "-u",
            api.api_client.configuration.host,
            "-n",
            "jobs",
            "reset-status",
            job.key,
        ],
    )
    assert result.exit_code == 0

    for name in ("preprocess", "work2"):
        assert db.get_document("jobs", name).status == "done"
    for name in ("work1", "postprocess"):
        assert db.get_document("jobs", name).status == "uninitialized"

    mgr = WorkflowManager(db.api, db.workflow.key)
    mgr.restart()

    for name in ("preprocess", "work2"):
        assert db.get_document("jobs", name).status == "done"
    assert db.get_document("jobs", "work1").status == "ready"
    assert db.get_document("jobs", "postprocess").status == "blocked"


def test_reinitialize_workflow_noop(completed_workflow):
    """Verify that a workflow can be reinitialized."""
    db, _, _ = completed_workflow
    mgr = WorkflowManager(db.api, db.workflow.key)
    mgr.restart()
    for name in ("preprocess", "work1", "work2", "postprocess"):
        job = db.get_document("jobs", name)
        assert job.status == "done"


@pytest.mark.parametrize(
    "field",
    ["name", "supports_termination", "cancel_on_blocking_job_failure"],
)
def test_reinitialize_workflow_changed_non_critical_fields(completed_workflow, field):
    """Verify restart behavior with a changed fields that do not affect results."""
    db, _, _ = completed_workflow
    mgr = WorkflowManager(db.api, db.workflow.key)
    preprocess = None
    for job in iter_documents(db.api.list_jobs, db.workflow.key):
        if job.name == "preprocess":
            preprocess = job
        assert job.status == "done"
    assert preprocess is not None
    new_values = {
        "name": preprocess.name + " new name",
        "supports_termination": not preprocess.supports_termination,
        "cancel_on_blocking_job_failure": not preprocess.cancel_on_blocking_job_failure,
    }
    setattr(preprocess, field, new_values[field])
    db.api.modify_job(db.workflow.key, preprocess.key, preprocess)

    mgr.restart()
    for job in iter_documents(db.api.list_jobs, db.workflow.key):
        assert job.status == "done"


@pytest.mark.parametrize("field", ["command", "invocation_script"])
def test_reinitialize_workflow_changed_critical_fields(completed_workflow, field):
    """Verify restart behavior with a changed fields that do affect results."""
    db, _, _ = completed_workflow
    mgr = WorkflowManager(db.api, db.workflow.key)
    job = db.get_document("jobs", "preprocess")
    assert job.status == "done"
    setattr(job, field, "new value")
    db.api.modify_job(db.workflow.key, job.key, job)

    mgr.restart(dry_run=True)
    for name in ("preprocess", "work1", "work2", "postprocess"):
        assert db.get_document("jobs", name).status == "done"

    mgr.restart()
    assert db.get_document("jobs", "preprocess").status == "ready"
    for name in ("work1", "work2", "postprocess"):
        job = db.get_document("jobs", name)
        assert job.status == "blocked"


def test_reinitialize_workflow_input_file_updated(completed_workflow):
    """Test workflow reinitialization after input files are changed."""
    db, _, _ = completed_workflow
    api = db.api
    file = db.get_document("files", "inputs")
    path = Path(file.path)
    path.touch()

    mgr = WorkflowManager(api, db.workflow.key)

    mgr.restart(dry_run=True)
    for name in ("preprocess", "work1", "work2", "postprocess"):
        assert db.get_document("jobs", name).status == "done"

    mgr.restart()
    assert db.get_document("jobs", "preprocess").status == "ready"
    for name in ("work1", "work2", "postprocess"):
        job = db.get_document("jobs", name)
        assert job.status == "blocked"


def test_reinitialize_workflow_incomplete(incomplete_workflow):
    """Test workflow reinitialization on an incomplete workflow."""
    db, _, _ = incomplete_workflow
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.restart()
    for name in ("preprocess", "work1"):
        job = db.get_document("jobs", name)
        assert job.status == "done"
    assert db.get_document("jobs", "work2").status == "ready"
    assert db.get_document("jobs", "postprocess").status == "blocked"


def test_reinitialize_workflow_disabled_job(incomplete_workflow):
    """Test workflow reinitialization on an incomplete workflow."""
    db, _, _ = incomplete_workflow
    api = db.api
    runner = CliRunner()
    job_key = db.get_document("jobs", "postprocess").key
    url = api.api_client.configuration.host
    result = runner.invoke(
        cli, ["-n", "-u", url, "-k", db.workflow.key, "jobs", "disable", job_key]
    )
    assert result.exit_code == 0
    assert db.get_document("jobs", "postprocess").status == "disabled"
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.restart()
    for name in ("preprocess", "work1"):
        job = db.get_document("jobs", name)
        assert job.status == "done"
    assert db.get_document("jobs", "work2").status == "ready"
    assert db.get_document("jobs", "postprocess").status == "disabled"


def test_reinitialize_workflow_incomplete_missing_files(
    incomplete_workflow_missing_files,
):
    """Test workflow reinitialization on an incomplete workflow with missing files."""
    db, _, _ = incomplete_workflow_missing_files
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.restart(ignore_missing_data=True)
    assert db.get_document("jobs", "preprocess").status == "done"
    assert db.get_document("jobs", "work1").status == "ready"
    assert db.get_document("jobs", "work2").status == "ready"
    assert db.get_document("jobs", "postprocess").status == "blocked"


@pytest.mark.parametrize(
    "missing_file", ["inputs.json", "f1.json", "f2.json", "f3.json", "f4.json", "f5.json"]
)
def test_restart_workflow_missing_files(complete_workflow_missing_files, missing_file):
    """Test workflow restart on a complete workflow with missing files."""
    db, scheduler_id, output_dir = complete_workflow_missing_files
    api = db.api
    (output_dir / missing_file).unlink()
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.restart(ignore_missing_data=True)
    status = api.get_workflow_status(db.workflow.key)
    assert status.run_id == 2

    stage1_events = db.list_documents("events")
    assert len(stage1_events) == 6  # 4 events for fake-completed jobs
    stage1_events.sort(key=lambda x: x["type"])
    assert stage1_events[4].get("type", "") == "restart"

    new_file = output_dir / missing_file
    new_file.write_text(json.dumps({"val": missing_file}))
    runner = JobRunner(
        api,
        db.workflow,
        output_dir,
        time_limit="P0DT24H",
        job_completion_poll_interval=0.1,
        scheduler_config_id=scheduler_id,
    )
    runner.run_worker()

    assert api.is_workflow_complete(db.workflow.key).is_complete
    stage2_events = db.list_documents("events")
    preprocess = db.get_document_key("jobs", "preprocess")
    work1 = db.get_document_key("jobs", "work1")
    work2 = db.get_document_key("jobs", "work2")
    postprocess = db.get_document_key("jobs", "postprocess")
    expected_complete = [preprocess, work1, work2, postprocess]
    match missing_file:
        case "inputs.json":
            expected_start = [preprocess, work1, work2, postprocess]
        case "f1.json" | "f2.json":
            expected_start = [preprocess, work1, work2, postprocess]
        case "f3.json":
            expected_start = [work1, postprocess]
        case "f4.json":
            expected_start = [work2, postprocess]
        case "f5.json":
            expected_start = [postprocess]
        case _:
            assert False
    expected_complete += expected_start
    assert sorted(expected_start) == _get_job_keys_by_event(stage2_events, "start")
    assert sorted(expected_complete) == _get_job_keys_by_event(stage2_events, "complete")

    api.reset_workflow_status(db.workflow.key)
    api.reset_job_status(db.workflow.key)
    for name in ("preprocess", "work1", "work2", "postprocess"):
        job = db.get_document("jobs", name)
        assert job.status == "uninitialized"


def test_restart_uninitialized(diamond_workflow):
    """Tests the restart workflow command with only_uninitialized."""
    db = diamond_workflow[0]
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    compute_node = _create_compute_node(api, db.workflow.key)
    mgr.start()
    for name in ("preprocess", "work1", "work2"):
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
                file.st_mtime = path.stat().st_mtime
                api.modify_file(db.workflow.key, file.key, file)

    runner = CliRunner()
    job_key = db.get_document("jobs", "work2").key
    url = api.api_client.configuration.host
    cli_result = runner.invoke(
        cli, ["-n", "-u", url, "-k", db.workflow.key, "jobs", "reset-status", job_key]
    )
    assert cli_result.exit_code == 0
    assert db.get_document("jobs", "preprocess").status == "done"
    assert db.get_document("jobs", "work1").status == "done"
    assert db.get_document("jobs", "work2").status == "uninitialized"
    assert db.get_document("jobs", "postprocess").status == "uninitialized"
    cli_result = runner.invoke(
        cli,
        ["-n", "-u", url, "-k", db.workflow.key, "workflows", "restart", "--only-uninitialized"],
    )
    assert cli_result.exit_code == 0
    assert db.get_document("jobs", "preprocess").status == "done"
    assert db.get_document("jobs", "work1").status == "done"
    assert db.get_document("jobs", "work2").status == "ready"
    assert db.get_document("jobs", "postprocess").status == "blocked"


@pytest.mark.parametrize("num_jobs", [5])
def test_ready_job_requirements(independent_job_workflow):
    """Test the API command for getting resource requirements for ready jobs."""
    db, num_jobs = independent_job_workflow
    reqs = db.api.get_ready_job_requirements(db.workflow.key)
    assert reqs.num_jobs == num_jobs


@pytest.mark.parametrize("num_jobs", [5])
def test_run_independent_job_workflow(independent_job_workflow, tmp_path):
    """Test execution of a workflow with jobs that can be run in parallel."""
    db, num_jobs = independent_job_workflow
    mgr = WorkflowManager(db.api, db.workflow.key)
    mgr.start()
    resources = ComputeNodesResources(
        num_cpus=2,
        num_gpus=0,
        memory_gb=16 * GiB,
        num_nodes=1,
        time_limit="P0DT24H",
    )
    runner = JobRunner(
        db.api,
        db.workflow,
        tmp_path,
        resources=resources,
        job_completion_poll_interval=0.1,
    )
    runner.run_worker()

    assert db.api.is_workflow_complete(db.workflow.key).is_complete
    for name in (str(i) for i in range(num_jobs)):
        result = db.api.get_latest_job_result(db.workflow.key, db.get_document_key("jobs", name))
        assert result.return_code == 0


@pytest.mark.parametrize("num_jobs", [100])
def test_concurrent_submitters(independent_job_workflow, tmp_path):
    """Test execution of a workflow with concurrent submitters.
    Tests database locking procedures.
    """
    db, num_jobs = independent_job_workflow
    mgr = WorkflowManager(db.api, db.workflow.key)
    mgr.start()
    cmd = [
        "python",
        "tests/scripts/run_jobs.py",
        db.url,
        db.workflow.key,
        "P0DT1H",
        str(tmp_path),
    ]
    num_submitters = 16
    pipes = [subprocess.Popen(cmd) for _ in range(num_submitters)]
    ret = 0
    timeout = time.time() + 120
    is_successful = False
    while time.time() < timeout:
        done = True
        for pipe in pipes:
            if pipe.poll() is None:
                done = False
                break
            if pipe.returncode != 0:
                ret = pipe.returncode
        if done:
            is_successful = True
            break
        time.sleep(1)

    assert is_successful, str([x.returncode for x in pipes])
    assert ret == 0
    assert db.api.is_workflow_complete(db.workflow.key).is_complete
    for name in (str(i) for i in range(num_jobs)):
        result = db.api.get_latest_job_result(db.workflow.key, db.get_document_key("jobs", name))
        assert result.return_code == 0


def test_map_functions(mapped_function_workflow):
    """Test a workflow that maps a function across workers."""
    db, output_dir = mapped_function_workflow
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    runner = JobRunner(
        api,
        db.workflow,
        output_dir,
        time_limit="P0DT24H",
        job_completion_poll_interval=0.1,
    )
    runner.run_worker()

    assert api.is_workflow_complete(db.workflow.key).is_complete
    for i in range(1, 6):
        job_key = db.get_document_key("jobs", str(i))
        result = api.get_latest_job_result(db.workflow.key, job_key)
        assert result.return_code == 0
        output_ud = api.list_job_user_data_stores(db.workflow.key, job_key)
        assert len(output_ud.items) == 1
        assert "result" in output_ud.items[0].data
        assert "output_data_path" in output_ud.items[0].data
    pp_key = db.get_document_key("jobs", "postprocess")
    output_ud = api.list_job_user_data_stores(db.workflow.key, pp_key)
    assert len(output_ud.items) == 1
    assert "total" in output_ud.items[0].data
    assert output_ud.items[0].data["total"] == 25
    assert "output_data_paths" in output_ud.items[0].data


def test_add_bulk_jobs(diamond_workflow):
    """Test the add_jobs helper function."""
    db = diamond_workflow[0]
    api = db.api
    initial_job_keys = api.list_job_keys(db.workflow.key)["items"]
    assert len(initial_job_keys) == 4
    resource_requirements = api.list_resource_requirements(db.workflow.key).items[0]

    jobs = (
        JobModel(
            name=f"added_job{i}",
            command="python my_script.py",
            resource_requirements=resource_requirements.id,
        )
        for i in range(1, 51)
    )

    added_jobs = add_jobs(api, db.workflow.key, jobs, max_transfer_size=11)
    assert len(added_jobs) == 50
    names = [x.name for x in api.list_jobs(db.workflow.key).items[len(initial_job_keys) :]]
    assert names == [f"added_job{i}" for i in range(1, 51)]

    final_job_keys = api.list_job_keys(db.workflow.key)["items"]
    assert len(final_job_keys) == len(initial_job_keys) + 50


def _fake_complete_job(api, workflow_key, job, compute_node):
    job = api.modify_job(workflow_key, job.key, job)
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
        workflow_key,
        job.key,
        status,
        job.rev,
        1,
        compute_node.key,
        result,
    )


def _get_job_keys_by_event(events, type_):
    return sorted([x["job_key"] for x in events if x["category"] == "job" and x["type"] == type_])


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


# def _disable_resource_stats(api):
#    config = api.get_workflow_config()
#    config.compute_node_resource_stats = WorkflowsconfigkeyComputeNodeResourceStats(
#        cpu=False, memory=False, disk=False, network=False, process=False
#    )
#    api.modify_workflow_config(config)
