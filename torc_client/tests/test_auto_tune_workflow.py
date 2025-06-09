"""Test Auto-tune feature"""

import multiprocessing
from pathlib import Path

import pytest
from rmon.utils.sql import read_table_as_dict

from torc.openapi_client.api.default_api import DefaultApi
from torc.openapi_client.models.compute_nodes_resources import (
    ComputeNodesResources,
)
from torc.api import iter_documents
from torc.common import STATS_DIR
from torc.job_runner import JobRunner
from torc.loggers import setup_logging
from torc.resource_monitor_reports import (
    make_job_process_stats_records,
    make_compute_node_stats_records,
)
from torc.tests.database_interface import DatabaseInterface
from torc.workflow_manager import WorkflowManager


@pytest.mark.parametrize("monitor_type", ["aggregation", "periodic"])
def test_auto_tune_workflow(multi_resource_requirement_workflow):
    """Test execution of a workflow using the auto-tune feature."""
    setup_logging()
    (
        db,
        output_dir,
        monitor_type,
    ) = multi_resource_requirement_workflow
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start(auto_tune_resource_requirements=True)

    # TODO: this will change when the manager can schedule nodes
    auto_tune_status = api.get_workflow_status(db.workflow.key).auto_tune_status
    auto_tune_job_keys = set(auto_tune_status.job_keys)
    assert auto_tune_job_keys == {
        db.get_document_key("jobs", "job_small1"),
        db.get_document_key("jobs", "job_medium1"),
        db.get_document_key("jobs", "job_large1"),
    }
    _check_initial_job_status(api, db.workflow.key, auto_tune_job_keys)

    resources = ComputeNodesResources(
        num_cpus=32,
        num_gpus=0,
        num_nodes=1,
        memory_gb=32,
        time_limit="P0DT24H",
    )
    _run_first_iteration(db, resources, auto_tune_job_keys, output_dir)
    _check_auto_tune_results(db, auto_tune_job_keys)

    mgr.restart()

    _run_second_iteration(db, resources, auto_tune_job_keys, output_dir)

    data = make_job_process_stats_records(api, db.workflow.key)
    assert len(data) == 9

    for val in make_compute_node_stats_records(api, db.workflow.key).values():
        assert val

    stats_dir = output_dir / STATS_DIR
    sqlite_files = list(stats_dir.rglob("*.sqlite"))
    html_files = list(stats_dir.rglob("*.html"))
    if monitor_type == "periodic":
        assert sqlite_files
        for file in sqlite_files:
            for table in ("cpu", "memory", "process"):
                table = read_table_as_dict(file, table)  # type: ignore
                assert table
            for table in ("disk", "network"):
                table = read_table_as_dict(file, table)  # type: ignore
                assert table
        assert len(html_files) == 3 * 2  # 2 JobRunner instances, cpu + memory + process
    else:
        assert not sqlite_files
        assert not html_files


def _check_initial_job_status(
    api: DefaultApi, workflow_key: str, auto_tune_job_keys: set[str]
) -> None:
    num_enabled = 0
    groups = set()
    for job in iter_documents(api.list_jobs, workflow_key):
        if job.key in auto_tune_job_keys:
            assert job.status == "ready"
            num_enabled += 1
            rr = api.get_job_resource_requirements(workflow_key, job.key)
            assert rr.name not in groups
            groups.add(rr.name)
        else:
            assert job.status == "disabled"
    assert num_enabled == 3


def _run_first_iteration(
    db: DatabaseInterface,
    resources: ComputeNodesResources,
    auto_tune_job_keys: set[str],
    output_dir: Path,
) -> None:
    api = db.api
    workflow = db.workflow
    runner = JobRunner(
        api,
        workflow,
        output_dir,
        resources=resources,
        job_completion_poll_interval=0.1,
    )
    assert workflow.key is not None
    runner.run_worker()
    assert api.is_workflow_complete(workflow.key)

    stats_by_key = {
        x: api.get_process_stats_for_job(workflow.key, x)[0] for x in auto_tune_job_keys
    }
    assert (
        stats_by_key[db.get_document_key("jobs", "job_small1")].max_rss
        < stats_by_key[db.get_document_key("jobs", "job_medium1")].max_rss
    )
    assert (
        stats_by_key[db.get_document_key("jobs", "job_medium1")].max_rss
        < stats_by_key[db.get_document_key("jobs", "job_large1")].max_rss
    )


def _run_second_iteration(
    db: DatabaseInterface,
    resources: ComputeNodesResources,
    auto_tune_job_keys: set[str],
    output_dir: Path,
) -> None:
    api = db.api
    for job in iter_documents(api.list_jobs, db.workflow.key):
        if job.key in auto_tune_job_keys:
            assert job.status == "done"
        else:
            assert job.status == "ready"

    runner = JobRunner(
        api,
        db.workflow,
        output_dir,
        resources=resources,
        job_completion_poll_interval=1,
    )
    runner.run_worker()
    assert api.is_workflow_complete(db.workflow.key).is_complete


def _check_auto_tune_results(db: DatabaseInterface, auto_tune_job_keys: set[str]):
    api = db.api
    api.process_auto_tune_resource_requirements_results(db.workflow.key)
    small = api.get_resource_requirements(
        db.workflow.key, db.get_document_key("resource_requirements", "small")
    )
    medium = api.get_resource_requirements(
        db.workflow.key, db.get_document_key("resource_requirements", "medium")
    )
    large = api.get_resource_requirements(
        db.workflow.key, db.get_document_key("resource_requirements", "large")
    )
    for rr in (small, medium, large):
        assert rr.runtime == "P0DT0H1M"
        # This is totally unreliable and sometimes is high as 54 on a 16-core system.
        assert rr.num_cpus in range(1, multiprocessing.cpu_count() + 1)
        assert rr.memory is not None
        assert rr.memory.lower() == "1g"

    result = api.list_jobs(db.workflow.key)
    assert result.items is not None
    for job in result.items:
        if job.key in auto_tune_job_keys:
            assert job.status == "done"
        else:
            assert job.status == "uninitialized"
