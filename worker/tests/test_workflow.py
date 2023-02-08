import json
import logging

import pytest

from wms.job_runner import JobRunner
from wms.workflow_manager import WorkflowManager


logger = logging.getLogger(__name__)


def test_run_workflow(diamond_workflow):
    api, output_dir = diamond_workflow
    user_data_work1 = api.get_jobs_get_user_data_name("work1")
    assert len(user_data_work1) == 1
    assert user_data_work1[0]["key1"] == "val1"
    mgr = WorkflowManager(api)
    mgr.run()
    runner = JobRunner(api, output_dir, time_limit="P0DT24H")
    runner.run_worker()

    assert api.get_workflow_is_complete()
    for name in ["preprocess", "work1", "work2", "postprocess"]:
        result = api.get_results_find_by_job_name_name(name)
        assert result.return_code == 0

    for name in ["inputs", "file1", "file2", "file3", "file4"]:
        file = api.get_files_name(name)
        assert file.path
        assert file.file_hash
        assert file.st_mtime

    events = api.get_events().items
    # start for workflow, start and stop for worker, start and stop for each job
    assert len(events) == 1 + 2 * 4 + 2


@pytest.mark.parametrize("cancel_on_blocking_job_failure", [True, False])
def test_cancel_with_failed_job(workflow_with_cancel):
    api, output_dir, cancel_on_blocking_job_failure = workflow_with_cancel
    mgr = WorkflowManager(api)
    mgr.run()
    runner = JobRunner(api, output_dir, time_limit="P0DT24H")
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
    runner = JobRunner(api, output_dir, time_limit="P0DT24H")
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


def _get_job_names_by_event(events, type_):
    return sorted([x["name"] for x in events if x["category"] == "job" and x["type"] == type_])
