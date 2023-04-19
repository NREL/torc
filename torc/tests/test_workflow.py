"""Test workflow execution"""

import json
import logging
import subprocess
import time
from pathlib import Path

import pytest
from swagger_client.models.prepare_jobs_for_submission_key_model import (
    PrepareJobsForSubmissionKeyModel,
)
from swagger_client.models.workflow_user_data_model import (
    WorkflowUserDataModel,
)

from torc.common import GiB
from torc.job_runner import JobRunner
from torc.utils.timing import timer_stats_collector
from torc.workflow_manager import WorkflowManager


logger = logging.getLogger(__name__)


def test_run_workflow(diamond_workflow):
    """Test full execution of diamond workflow with file dependencies."""
    db, scheduler_config_id, output_dir = diamond_workflow
    api = db.api
    timer_stats_collector.enable()
    user_data_work1 = api.get_workflows_workflow_jobs_key_user_data_consumes(
        db.workflow.key, db.get_document_key("jobs", "work1")
    )
    assert len(user_data_work1.items) == 1
    assert user_data_work1.items[0].data["key1"] == "val1"
    mgr = WorkflowManager(api, db.workflow.key)
    config = api.get_workflows_config_key(db.workflow.key)
    config.compute_node_resource_stats.cpu = True
    config.compute_node_resource_stats.memory = True
    config.compute_node_resource_stats.process = True
    config.compute_node_resource_stats.interval = 1
    api.put_workflows_config_key(config, db.workflow.key)
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

    assert api.get_workflows_is_complete_key(db.workflow.key)
    for name in ["preprocess", "work1", "work2", "postprocess"]:
        result = api.get_workflows_workflow_results_find_by_job_key(
            db.workflow.key, db.get_document_key("jobs", name)
        )
        assert result.return_code == 0

    for name in ["inputs", "file1", "file2", "file3", "file4"]:
        file = db.get_document("files", name)
        assert file.path
        # assert file.file_hash
        assert file.st_mtime

    result_data_work1 = WorkflowUserDataModel(name="result1", data={"result": 1})
    result_data_overall = WorkflowUserDataModel(name="overall_result", data={"overall_result": 2})
    result_data_work1 = api.post_workflows_workflow_jobs_key_user_data(
        result_data_work1, db.workflow.key, db.get_document_key("jobs", "work1")
    )
    ud_work1_consumes = api.get_workflows_workflow_jobs_key_user_data_consumes(
        db.workflow.key, db.get_document_key("jobs", "work1")
    )
    assert len(ud_work1_consumes.items) == 1
    ud_work1_produces = api.get_workflows_workflow_jobs_key_user_data_stores(
        db.workflow.key, db.get_document_key("jobs", "work1")
    )
    assert len(ud_work1_produces.items) == 1
    result_data_overall = api.post_workflows_workflow_user_data(
        result_data_overall, db.workflow.key
    )
    assert (
        api.get_workflows_workflow_user_data_key(db.workflow.key, result_data_overall.key).name
        == "overall_result"
    )

    events = db.list_documents("events")
    # start for workflow, start and stop for worker, start and stop for each job
    assert len(events) == 1 + 2 * 4

    timer_stats_collector.log_stats()
    stats_file = output_dir / "stats.json"
    assert not stats_file.exists()
    timer_stats_collector.log_json_stats(stats_file, clear=True)
    assert stats_file.exists()
    timer_stats_collector.log_stats(clear=True)


@pytest.mark.parametrize("cancel_on_blocking_job_failure", [True, False])
def test_cancel_with_failed_job(workflow_with_cancel):
    """Test the cancel_on_blocking_job_failure feature for jobs."""
    db, output_dir, cancel_on_blocking_job_failure = workflow_with_cancel
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    runner = JobRunner(
        api, db.workflow, output_dir, time_limit="P0DT24H", job_completion_poll_interval=0.1
    )
    runner.run_worker()
    assert api.get_workflows_is_complete_key(db.workflow.key)
    assert db.get_document("jobs", "job1").status == "done"
    result = api.get_workflows_workflow_results_find_by_job_key(
        db.workflow.key, db.get_document_key("jobs", "job1")
    )
    assert result.return_code == 1
    expected_status = "canceled" if cancel_on_blocking_job_failure else "done"
    assert db.get_document("jobs", "job2").status == expected_status


def test_reinitialize_workflow_noop(completed_workflow):
    """Verify that a workflow can be reinitialized."""
    db, _, _ = completed_workflow
    mgr = WorkflowManager(db.api, db.workflow.key)
    mgr.reinitialize_jobs()
    for name in ("preprocess", "work1", "work2", "postprocess"):
        job = db.get_document("jobs", name)
        assert job.status == "done"


def test_reinitialize_workflow_input_file_updated(completed_workflow):
    """Test workflow reinitialization after input files are changed."""
    db, _, _ = completed_workflow
    api = db.api
    file = db.get_document("files", "inputs")
    path = Path(file.path)
    path.touch()

    mgr = WorkflowManager(api, db.workflow.key)
    mgr.reinitialize_jobs()
    assert db.get_document("jobs", "preprocess").status == "ready"
    for name in ("work1", "work2", "postprocess"):
        job = db.get_document("jobs", name)
        assert job.status == "blocked"


def test_reinitialize_workflow_incomplete(incomplete_workflow):
    """Test workflow reinitialization on an incomplete workflow."""
    db, _, _ = incomplete_workflow
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.reinitialize_jobs()
    for name in ("preprocess", "work1"):
        job = db.get_document("jobs", name)
        assert job.status == "done"
    assert db.get_document("jobs", "work2").status == "ready"
    assert db.get_document("jobs", "postprocess").status == "blocked"


def test_reinitialize_workflow_incomplete_missing_files(
    incomplete_workflow_missing_files,
):
    """Test workflow reinitialization on an incomplete workflow with missing files."""
    db, _, _ = incomplete_workflow_missing_files
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.reinitialize_jobs()
    assert db.get_document("jobs", "preprocess").status == "done"
    assert db.get_document("jobs", "work1").status == "ready"
    assert db.get_document("jobs", "work2").status == "ready"
    assert db.get_document("jobs", "postprocess").status == "blocked"


@pytest.mark.parametrize(
    "missing_file", ["inputs.json", "f1.json", "f2.json", "f3.json", "f4.json"]
)
def test_restart_workflow_missing_files(complete_workflow_missing_files, missing_file):
    """Test workflow restart on a complete workflow with missing files."""
    db, _, output_dir = complete_workflow_missing_files
    api = db.api
    (output_dir / missing_file).unlink()
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.restart()
    status = api.get_workflows_status_key(db.workflow.key)
    assert status.run_id == 2

    stage1_events = db.list_documents("events")
    assert len(stage1_events) == 1
    assert stage1_events[0].get("type", "") == "restart"

    new_file = output_dir / missing_file
    new_file.write_text(json.dumps({"val": missing_file}))
    runner = JobRunner(
        api,
        db.workflow,
        output_dir,
        time_limit="P0DT24H",
        job_completion_poll_interval=0.1,
        scheduler_config_id=None,  # This tests the case where the node doesn't want this restriction.
    )
    runner.run_worker()

    assert api.get_workflows_is_complete_key(db.workflow.key)
    stage2_events = db.list_documents("events")
    preprocess = db.get_document_key("jobs", "preprocess")
    work1 = db.get_document_key("jobs", "work1")
    work2 = db.get_document_key("jobs", "work2")
    postprocess = db.get_document_key("jobs", "postprocess")
    match missing_file:
        case "inputs.json":
            expected = [preprocess, work1, work2, postprocess]
        case "f1.json":
            expected = [preprocess, work1, work2, postprocess]
        case "f2.json":
            expected = [work1, postprocess]
        case "f3.json":
            expected = [work2, postprocess]
        case "f4.json":
            expected = [postprocess]
        case _:
            assert False
    assert sorted(expected) == _get_job_keys_by_event(stage2_events, "start")
    assert sorted(expected) == _get_job_keys_by_event(stage2_events, "complete")

    for job_key in {preprocess, work1, work2, postprocess}.difference(expected):
        assert api.get_workflows_workflow_jobs_key(db.workflow.key, job_key).run_id == 1
    for job_key in expected:
        assert api.get_workflows_workflow_jobs_key(db.workflow.key, job_key).run_id == 2

    api.post_workflows_reset_status_key(db.workflow.key)
    for name in ("preprocess", "work1", "work2", "postprocess"):
        job = db.get_document("jobs", name)
        assert job.status == "uninitialized"


@pytest.mark.parametrize("num_jobs", [5])
def test_ready_job_requirements(independent_job_workflow):
    """Test the API command for getting resource requirements for ready jobs."""
    db, num_jobs = independent_job_workflow
    reqs = db.api.get_workflows_ready_job_requirements_key(db.workflow.key)
    assert reqs.num_jobs == num_jobs


@pytest.mark.parametrize("num_jobs", [5])
def test_run_independent_job_workflow(independent_job_workflow, tmp_path):
    """Test execution of a workflow with jobs that can be run in parallel."""
    db, num_jobs = independent_job_workflow
    mgr = WorkflowManager(db.api, db.workflow.key)
    mgr.start()
    resources = PrepareJobsForSubmissionKeyModel(
        num_cpus=2,
        num_gpus=0,
        memory_gb=16 * GiB,
        num_nodes=1,
        time_limit="P0DT24H",
    )
    runner = JobRunner(
        db.api, db.workflow, tmp_path, resources=resources, job_completion_poll_interval=0.1
    )
    runner.run_worker()

    assert db.api.get_workflows_is_complete_key(db.workflow.key)
    for name in (str(i) for i in range(num_jobs)):
        result = db.api.get_workflows_workflow_results_find_by_job_key(
            db.workflow.key, db.get_document_key("jobs", name)
        )
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
    pipes = [
        subprocess.Popen(cmd) for _ in range(num_submitters)  # pylint: disable=consider-using-with
    ]
    ret = 0
    while True:
        done = True
        for pipe in pipes:
            if pipe.poll() is None:
                done = False
                break
            if pipe.returncode != 0:
                ret = pipe.returncode
        if done:
            break
        time.sleep(1)

    assert ret == 0
    assert db.api.get_workflows_is_complete_key(db.workflow.key)
    for name in (str(i) for i in range(num_jobs)):
        result = db.api.get_workflows_workflow_results_find_by_job_key(
            db.workflow.key, db.get_document_key("jobs", name)
        )
        assert result.return_code == 0


def _get_job_keys_by_event(events, type_):
    return sorted([x["key"] for x in events if x["category"] == "job" and x["type"] == type_])


# def _disable_resource_stats(api):
#    config = api.get_workflow_config()
#    config.compute_node_resource_stats = WorkflowsconfigkeyComputeNodeResourceStats(
#        cpu=False, memory=False, disk=False, network=False, process=False
#    )
#    api.put_workflow_config(config)
