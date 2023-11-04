"""Test Auto-tune feature"""

import logging
import multiprocessing

import polars as pl
import pytest
from torc.openapi_client.models.compute_nodes_resources import (
    ComputeNodesResources,
)

from torc.api import iter_documents
from torc.common import STATS_DIR
from torc.job_runner import JobRunner
from torc.loggers import setup_logging
from torc.resource_monitor_reports import (
    make_job_process_stats_dataframe,
    make_compute_node_stats_dataframes,
)
from torc.workflow_manager import WorkflowManager


logger = logging.getLogger(__name__)


@pytest.mark.parametrize("monitor_type", ["aggregation", "periodic"])
def test_auto_tune_workflow(multi_resource_requirement_workflow):
    """Test execution of a workflow using the auto-tune feature."""
    setup_logging("torc")
    (
        db,
        output_dir,
        monitor_type,
    ) = multi_resource_requirement_workflow
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start(auto_tune_resource_requirements=True)

    # TODO: this will change when the manager can schedule nodes
    auto_tune_status = api.get_workflows_key_status(db.workflow.key).auto_tune_status
    auto_tune_job_keys = set(auto_tune_status.job_keys)
    assert auto_tune_job_keys == {
        db.get_document_key("jobs", "job_small1"),
        db.get_document_key("jobs", "job_medium1"),
        db.get_document_key("jobs", "job_large1"),
    }
    num_enabled = 0
    groups = set()
    for job in iter_documents(api.get_jobs, db.workflow.key):
        if job.key in auto_tune_job_keys:
            assert job.status == "ready"
            num_enabled += 1
            rr = api.get_jobs_key_resource_requirements(db.workflow.key, job.key)
            assert rr.name not in groups
            groups.add(rr.name)
        else:
            assert job.status == "disabled"
    assert num_enabled == 3

    resources = ComputeNodesResources(
        num_cpus=32,
        num_gpus=0,
        memory_gb=32,
        time_limit="P0DT24H",
    )
    runner = JobRunner(
        api,
        db.workflow,
        output_dir,
        resources=resources,
        job_completion_poll_interval=0.1,
    )
    runner.run_worker()
    assert api.get_workflows_key_is_complete(db.workflow.key)

    stats_by_key = {
        x: api.get_jobs_key_process_stats(db.workflow.key, x)[0] for x in auto_tune_job_keys
    }
    assert (
        stats_by_key[db.get_document_key("jobs", "job_small1")].max_rss
        < stats_by_key[db.get_document_key("jobs", "job_medium1")].max_rss
    )
    assert (
        stats_by_key[db.get_document_key("jobs", "job_medium1")].max_rss
        < stats_by_key[db.get_document_key("jobs", "job_large1")].max_rss
    )

    api.post_workflows_key_process_auto_tune_resource_requirements_results(db.workflow.key)
    small = api.get_resource_requirements_key(
        db.workflow.key, db.get_document_key("resource_requirements", "small")
    )
    medium = api.get_resource_requirements_key(
        db.workflow.key, db.get_document_key("resource_requirements", "medium")
    )
    large = api.get_resource_requirements_key(
        db.workflow.key, db.get_document_key("resource_requirements", "large")
    )
    for rr in (small, medium, large):
        assert rr.runtime == "P0DT0H1M"
        # This is totally unreliable and sometimes is high as 54 on a 16-core system.
        assert rr.num_cpus in range(1, multiprocessing.cpu_count() + 1)
        assert rr.memory.lower() == "1g"

    for job in api.get_jobs(db.workflow.key).items:
        if job.key in auto_tune_job_keys:
            assert job.status == "done"
        else:
            assert job.status == "uninitialized"

    mgr.restart()

    for job in iter_documents(api.get_jobs, db.workflow.key):
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
    assert api.get_workflows_key_is_complete(db.workflow.key).is_complete

    df = make_job_process_stats_dataframe(api, db.workflow.key)
    assert isinstance(df, pl.DataFrame)
    assert len(df) == 9

    dfs = make_compute_node_stats_dataframes(api, db.workflow.key)
    for df in dfs.values():
        assert isinstance(df, pl.DataFrame)

    stats_dir = output_dir / STATS_DIR
    sqlite_files = [x for x in stats_dir.iterdir() if x.suffix == ".sqlite"]
    html_files = [x for x in stats_dir.iterdir() if x.suffix == ".html"]
    if monitor_type == "periodic":
        assert sqlite_files
        for file in sqlite_files:
            for table in ("cpu", "memory", "process"):
                df = pl.read_database_uri(f"select * from {table}", f"sqlite://{file}")
                assert len(df) > 0
            for table in ("disk", "network"):
                df = pl.read_database_uri(f"select * from {table}", f"sqlite://{file}")
                assert len(df) == 0
        assert len(html_files) == 3 * 2  # 2 JobRunner instances, cpu + memory + process
    else:
        assert not sqlite_files
        assert not html_files
