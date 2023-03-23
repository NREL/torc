"""Test Auto-tune feature"""

import logging

import polars as pl
import pytest
from swagger_client.models.workflow_prepare_jobs_for_submission_model import (
    WorkflowPrepareJobsForSubmissionModel,
)

from torc.common import STATS_DIR
from torc.job_runner import JobRunner
from torc.loggers import setup_logging
from torc.resource_monitor.reports import (
    make_job_process_stats_dataframe,
    make_compute_node_stats_dataframes,
)
from torc.workflow_manager import WorkflowManager
from torc.tests.common import TestApiManager


logger = logging.getLogger(__name__)


@pytest.mark.parametrize("monitor_type", ["aggregation", "periodic"])
def test_auto_tune_workflow(multi_resource_requirement_workflow):
    """Test execution of a workflow using the auto-tune feature."""
    setup_logging("torc")
    (
        api,
        scheduler_config_id,
        output_dir,
        monitor_type,
    ) = multi_resource_requirement_workflow
    test_mgr = TestApiManager(api)

    mgr = WorkflowManager(api)
    mgr.start(auto_tune_resource_requirements=True)

    # TODO: this will change when the manager can schedule nodes
    auto_tune_status = api.get_workflow_status().auto_tune_status
    auto_tune_job_keys = set(auto_tune_status.job_keys)
    assert auto_tune_job_keys == {
        test_mgr.get_job_key("job_small1"),
        test_mgr.get_job_key("job_medium1"),
        test_mgr.get_job_key("job_large1"),
    }
    num_enabled = 0
    groups = set()
    for job in api.get_jobs().items:
        if job.key in auto_tune_job_keys:
            assert job.status == "ready"
            num_enabled += 1
            rr = api.get_jobs_resource_requirements_key(job.key)
            assert rr.name not in groups
            groups.add(rr.name)
        else:
            assert job.status == "disabled"
    assert num_enabled == 3

    resources = WorkflowPrepareJobsForSubmissionModel(
        num_cpus=32,
        num_gpus=0,
        memory_gb=32,
        time_limit="P0DT24H",
    )
    runner = JobRunner(
        api,
        output_dir,
        resources=resources,
        job_completion_poll_interval=0.1,
        scheduler_config_id=scheduler_config_id,
    )
    runner.run_worker()
    assert api.get_workflow_is_complete()

    stats_by_key = {x: api.get_jobs_process_stats_key(x)[0] for x in auto_tune_job_keys}
    assert (
        stats_by_key[test_mgr.get_job_key("job_small1")].max_rss
        < stats_by_key[test_mgr.get_job_key("job_medium1")].max_rss
    )
    assert (
        stats_by_key[test_mgr.get_job_key("job_medium1")].max_rss
        < stats_by_key[test_mgr.get_job_key("job_large1")].max_rss
    )

    api.post_workflow_process_auto_tune_resource_requirements_results()
    small = api.get_resource_requirements_key("small")
    medium = api.get_resource_requirements_key("medium")
    large = api.get_resource_requirements_key("large")
    for rr in (small, medium, large):
        assert rr.runtime == "P0DT0H1M"
        # This is unreliable.
        # assert rr.num_cpus in (1, 2)
        assert rr.memory.lower() == "1g"

    for job in api.get_jobs().items:
        if job.key in auto_tune_job_keys:
            assert job.status == "done"
        else:
            assert job.status == "uninitialized"

    mgr.restart()
    runner = JobRunner(
        api,
        output_dir,
        resources=resources,
        job_completion_poll_interval=0.1,
    )
    runner.run_worker()
    assert api.get_workflow_is_complete()

    df = make_job_process_stats_dataframe(api)
    assert isinstance(df, pl.DataFrame)
    assert len(df) == 9

    dfs = make_compute_node_stats_dataframes(api)
    for df in dfs.values():
        assert isinstance(df, pl.DataFrame)

    if monitor_type == "periodic":
        stats_dir = output_dir / STATS_DIR
        files = [x for x in stats_dir.iterdir() if x.suffix == ".sqlite"]
        assert files
        for file in files:
            for table in ("cpu", "memory", "process"):
                df = pl.read_sql(f"select * from {table}", f"sqlite://{file}")
                assert len(df) > 0
            for table in ("disk", "network"):
                df = pl.read_sql(f"select * from {table}", f"sqlite://{file}")
                assert len(df) == 0
