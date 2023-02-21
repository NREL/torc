import json
import logging
import subprocess
import time
from pathlib import Path

import pytest
from swagger_client.models.worker_resources import WorkerResources

from wms.common import GiB
from wms.job_runner import JobRunner
from wms.resource_monitor import ComputeNodeResourceStatConfig
from wms.utils.timing import timer_stats_collector
from wms.workflow_manager import WorkflowManager


logger = logging.getLogger(__name__)


def test_run_workflow(diamond_workflow):
    api, output_dir = diamond_workflow
    timer_stats_collector.enable()
    user_data_work1 = api.get_jobs_get_user_data_name("work1")
    assert len(user_data_work1) == 1
    assert user_data_work1[0]["key1"] == "val1"
    mgr = WorkflowManager(api)
    mgr.start()
    stats = ComputeNodeResourceStatConfig(interval=1, name="test")
    runner = JobRunner(
        api,
        output_dir,
        time_limit="P0DT24H",
        job_completion_poll_interval=0.1,
        stats=stats,
    )
    runner.run_worker()

    assert api.get_workflow_is_complete()
    for name in ["preprocess", "work1", "work2", "postprocess"]:
        result = api.get_results_find_by_job_name_name(name)
        assert result.return_code == 0

    for name in ["inputs", "file1", "file2", "file3", "file4"]:
        file = api.get_files_name(name)
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
    api, output_dir, cancel_on_blocking_job_failure = workflow_with_cancel
    mgr = WorkflowManager(api)
    mgr.start()
    runner = JobRunner(api, output_dir, time_limit="P0DT24H", job_completion_poll_interval=0.1)
    runner.run_worker()
    assert api.get_workflow_is_complete()
    assert api.get_jobs_name("job1").status == "done"
    result = api.get_results_find_by_job_name_name("job1")
    assert result.return_code == 1
    expected_status = "canceled" if cancel_on_blocking_job_failure else "done"
    assert api.get_jobs_name("job2").status == expected_status


def test_reinitialize_workflow_noop(completed_workflow):
    api, _ = completed_workflow

    mgr = WorkflowManager(api)
    mgr.reinitialize_jobs()
    for name in ("preprocess", "work1", "work2", "postprocess"):
        job = api.get_jobs_name(name)
        assert job.status == "done"


def test_reinitialize_workflow_input_file_updated(completed_workflow):
    api, _ = completed_workflow
    file = api.get_files_name("inputs")
    path = Path(file.path)
    path.touch()

    mgr = WorkflowManager(api)
    mgr.reinitialize_jobs()
    assert api.get_jobs_name("preprocess").status == "ready"
    for name in ("work1", "work2", "postprocess"):
        job = api.get_jobs_name(name)
        assert job.status == "blocked"


def test_reinitialize_workflow_incomplete(incomplete_workflow):
    api, _ = incomplete_workflow
    mgr = WorkflowManager(api)
    mgr.reinitialize_jobs()
    for name in ("preprocess", "work1"):
        job = api.get_jobs_name(name)
        assert job.status == "done"
    assert api.get_jobs_name("work2").status == "ready"
    assert api.get_jobs_name("postprocess").status == "blocked"


def test_reinitialize_workflow_incomplete_missing_files(
    incomplete_workflow_missing_files,
):
    api, _ = incomplete_workflow_missing_files
    mgr = WorkflowManager(api)
    mgr.reinitialize_jobs()
    assert api.get_jobs_name("preprocess").status == "done"
    assert api.get_jobs_name("work1").status == "ready"
    assert api.get_jobs_name("work2").status == "ready"
    assert api.get_jobs_name("postprocess").status == "blocked"


@pytest.mark.parametrize(
    "missing_file", ["inputs.json", "f1.json", "f2.json", "f3.json", "f4.json"]
)
def test_restart_workflow_missing_files(complete_workflow_missing_files, missing_file):
    api, output_dir = complete_workflow_missing_files
    (output_dir / missing_file).unlink()
    mgr = WorkflowManager(api)
    mgr.reinitialize_jobs()

    stage1_events = api.get_events().items
    assert not stage1_events
    new_file = output_dir / missing_file
    new_file.write_text(json.dumps({"val": missing_file}))
    runner = JobRunner(api, output_dir, time_limit="P0DT24H", job_completion_poll_interval=0.1)
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


def test_estimate_workflow(diamond_workflow):
    api, _ = diamond_workflow
    estimate = api.post_workflow_estimate()
    assert estimate.estimates_by_round


@pytest.mark.parametrize("num_jobs", [5])
def test_ready_job_requirements(independent_job_workflow):
    api, num_jobs = independent_job_workflow
    reqs = api.get_workflow_ready_job_requirements()
    assert reqs.num_jobs == num_jobs


@pytest.mark.parametrize("num_jobs", [5])
def test_run_independent_job_workflow(independent_job_workflow, tmp_path):
    api, num_jobs = independent_job_workflow
    mgr = WorkflowManager(api)
    mgr.start()
    resources = WorkerResources(
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
        result = api.get_results_find_by_job_name_name(name)
        assert result.return_code == 0


@pytest.mark.parametrize("num_jobs", [100])
def test_concurrent_submitters(independent_job_workflow, tmp_path):
    api, num_jobs = independent_job_workflow
    mgr = WorkflowManager(api)
    mgr.start()
    cmd = [
        "python",
        "tests/scripts/run_jobs.py",
        "http://localhost:8529/_db/workflows/wms-service",
        "P0DT1H",
        str(tmp_path),
    ]
    num_submitters = 16
    pipes = [subprocess.Popen(cmd) for _ in range(num_submitters)]
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
        result = api.get_results_find_by_job_name_name(name)
        assert result.return_code == 0


def _get_job_names_by_event(events, type_):
    return sorted([x["name"] for x in events if x["category"] == "job" and x["type"] == type_])
