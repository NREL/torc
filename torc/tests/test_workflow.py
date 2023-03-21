"""Test workflow execution"""

import json
import logging
import subprocess
import time
from pathlib import Path

import pytest
from swagger_client.models.workflow_prepare_jobs_for_submission_model import (
    WorkflowPrepareJobsForSubmissionModel,
)

from torc.common import GiB
from torc.job_runner import JobRunner
from torc.utils.timing import timer_stats_collector
from torc.workflow_manager import WorkflowManager


logger = logging.getLogger(__name__)


def test_run_workflow(diamond_workflow):
    """Test full execution of diamond workflow with file dependencies."""
    api, scheduler_config_id, output_dir = diamond_workflow
    timer_stats_collector.enable()
    user_data_work1 = api.get_jobs_get_user_data_key("work1")
    assert len(user_data_work1) == 1
    assert user_data_work1[0]["key1"] == "val1"
    mgr = WorkflowManager(api)
    config = api.get_workflow_config()
    config.compute_node_resource_stats.cpu = True
    config.compute_node_resource_stats.memory = True
    config.compute_node_resource_stats.process = True
    config.compute_node_resource_stats.interval = 1
    api.put_workflow_config_key(config, config.key)
    mgr.start()
    runner = JobRunner(
        api,
        output_dir,
        time_limit="P0DT24H",
        job_completion_poll_interval=0.1,
        scheduler_config_id=scheduler_config_id,
    )
    runner.run_worker()

    assert api.get_workflow_is_complete()
    for name in ["preprocess", "work1", "work2", "postprocess"]:
        result = api.get_results_find_by_job_key(name)
        assert result.return_code == 0

    for name in ["inputs", "file1", "file2", "file3", "file4"]:
        file = api.get_files_key(name)
        assert file.path
        # assert file.file_hash
        assert file.st_mtime

    events = api.get_events().items
    # start for workflow, start and stop for worker, start and stop for each job
    assert len(events) == 1 + 2 * 4 + 2

    timer_stats_collector.log_stats()
    stats_file = output_dir / "stats.json"
    assert not stats_file.exists()
    timer_stats_collector.log_json_stats(stats_file, clear=True)
    assert stats_file.exists()
    timer_stats_collector.log_stats(clear=True)


@pytest.mark.parametrize("cancel_on_blocking_job_failure", [True, False])
def test_cancel_with_failed_job(workflow_with_cancel):
    """Test the cancel_on_blocking_job_failure feature for jobs."""
    api, output_dir, cancel_on_blocking_job_failure = workflow_with_cancel
    mgr = WorkflowManager(api)
    mgr.start()
    runner = JobRunner(api, output_dir, time_limit="P0DT24H", job_completion_poll_interval=0.1)
    runner.run_worker()
    assert api.get_workflow_is_complete()
    assert api.get_jobs_key("job1").status == "done"
    result = api.get_results_find_by_job_key("job1")
    assert result.return_code == 1
    expected_status = "canceled" if cancel_on_blocking_job_failure else "done"
    assert api.get_jobs_key("job2").status == expected_status


def test_reinitialize_workflow_noop(completed_workflow):
    """Verify that a workflow can be reinitialized."""
    api, _, _ = completed_workflow

    mgr = WorkflowManager(api)
    mgr.reinitialize_jobs()
    for name in ("preprocess", "work1", "work2", "postprocess"):
        job = api.get_jobs_key(name)
        assert job.status == "done"


def test_reinitialize_workflow_input_file_updated(completed_workflow):
    """Test workflow reinitialization after input files are changed."""
    api, _, _ = completed_workflow
    file = api.get_files_key("inputs")
    path = Path(file.path)
    path.touch()

    mgr = WorkflowManager(api)
    mgr.reinitialize_jobs()
    assert api.get_jobs_key("preprocess").status == "ready"
    for name in ("work1", "work2", "postprocess"):
        job = api.get_jobs_key(name)
        assert job.status == "blocked"


def test_reinitialize_workflow_incomplete(incomplete_workflow):
    """Test workflow reinitialization on an incomplete workflow."""
    api, _, _ = incomplete_workflow
    mgr = WorkflowManager(api)
    mgr.reinitialize_jobs()
    for name in ("preprocess", "work1"):
        job = api.get_jobs_key(name)
        assert job.status == "done"
    assert api.get_jobs_key("work2").status == "ready"
    assert api.get_jobs_key("postprocess").status == "blocked"


def test_reinitialize_workflow_incomplete_missing_files(
    incomplete_workflow_missing_files,
):
    """Test workflow reinitialization on an incomplete workflow with missing files."""
    api, _, _ = incomplete_workflow_missing_files
    mgr = WorkflowManager(api)
    mgr.reinitialize_jobs()
    assert api.get_jobs_key("preprocess").status == "done"
    assert api.get_jobs_key("work1").status == "ready"
    assert api.get_jobs_key("work2").status == "ready"
    assert api.get_jobs_key("postprocess").status == "blocked"


@pytest.mark.parametrize(
    "missing_file", ["inputs.json", "f1.json", "f2.json", "f3.json", "f4.json"]
)
def test_restart_workflow_missing_files(complete_workflow_missing_files, missing_file):
    """Test workflow restart on a complete workflow with missing files."""
    api, _, output_dir = complete_workflow_missing_files
    (output_dir / missing_file).unlink()
    mgr = WorkflowManager(api)
    mgr.restart()
    status = api.get_workflow_status()
    assert status.run_id == 2

    stage1_events = api.get_events().items
    assert len(stage1_events) == 1
    assert stage1_events[0].get("type", "") == "restart"

    new_file = output_dir / missing_file
    new_file.write_text(json.dumps({"val": missing_file}))
    runner = JobRunner(
        api,
        output_dir,
        time_limit="P0DT24H",
        job_completion_poll_interval=0.1,
        scheduler_config_id=None,  # This tests the case where the node doesn't want this restriction.
    )
    runner.run_worker()

    assert api.get_workflow_is_complete()
    stage2_events = api.get_events().items
    match missing_file:
        case "inputs.json":
            expected = ["preprocess", "work1", "work2", "postprocess"]
        case "f1.json":
            expected = ["preprocess", "work1", "work2", "postprocess"]
        case "f2.json":
            expected = ["work1", "postprocess"]
        case "f3.json":
            expected = ["work2", "postprocess"]
        case "f4.json":
            expected = ["postprocess"]
        case _:
            assert False
    assert sorted(expected) == _get_job_names_by_event(stage2_events, "start")
    assert sorted(expected) == _get_job_names_by_event(stage2_events, "complete")

    for name in {"preprocess", "work1", "work2", "postprocess"}.difference(expected):
        assert api.get_jobs_key(name).run_id == 1
    for name in expected:
        assert api.get_jobs_key(name).run_id == 2

    api.put_workflow_status_reset()
    assert api.get_workflow_status().run_id == 0
    for name in ("preprocess", "work1", "work2", "postprocess"):
        job = api.get_jobs_key(name)
        assert job.run_id == 0
        assert job.status == "uninitialized"


def test_estimate_workflow(diamond_workflow):
    """Test the estimate workflow feature."""
    api = diamond_workflow[0]
    estimate = api.post_workflow_estimate()
    assert estimate.estimates_by_round


@pytest.mark.parametrize("num_jobs", [5])
def test_ready_job_requirements(independent_job_workflow):
    """Test the API command for getting resource requirements for ready jobs."""
    api, num_jobs = independent_job_workflow
    reqs = api.get_workflow_ready_job_requirements()
    assert reqs.num_jobs == num_jobs


@pytest.mark.parametrize("num_jobs", [5])
def test_run_independent_job_workflow(independent_job_workflow, tmp_path):
    """Test execution of a workflow with jobs that can be run in parallel."""
    api, num_jobs = independent_job_workflow
    mgr = WorkflowManager(api)
    mgr.start()
    resources = WorkflowPrepareJobsForSubmissionModel(
        num_cpus=2,
        num_gpus=0,
        memory_gb=16 * GiB,
        num_nodes=1,
        time_limit="P0DT24H",
    )
    runner = JobRunner(api, tmp_path, resources=resources, job_completion_poll_interval=0.1)
    runner.run_worker()

    assert api.get_workflow_is_complete()
    for name in (str(i) for i in range(num_jobs)):
        result = api.get_results_find_by_job_key(name)
        assert result.return_code == 0


@pytest.mark.parametrize("num_jobs", [100])
def test_concurrent_submitters(independent_job_workflow, tmp_path):
    """Test execution of a workflow with concurrent submitters.
    Tests database locking procedures.
    """
    api, num_jobs = independent_job_workflow
    mgr = WorkflowManager(api)
    mgr.start()
    cmd = [
        "python",
        "tests/scripts/run_jobs.py",
        "http://localhost:8529/_db/workflows/torc-service",
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
    assert api.get_workflow_is_complete()
    for name in (str(i) for i in range(num_jobs)):
        result = api.get_results_find_by_job_key(name)
        assert result.return_code == 0


def _get_job_names_by_event(events, type_):
    return sorted([x["name"] for x in events if x["category"] == "job" and x["type"] == type_])


# def _disable_resource_stats(api):
#    config = api.get_workflow_config()
#    config.compute_node_resource_stats = WorkflowConfigComputeNodeResourceStats(
#        cpu=False, memory=False, disk=False, network=False, process=False
#    )
#    api.put_workflow_config(config)
