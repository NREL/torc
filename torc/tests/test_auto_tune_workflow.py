"""Test Auto-tune feature"""

import logging

import polars as pl
from swagger_client.models.workflow_prepare_jobs_for_submission_model import (
    WorkflowPrepareJobsForSubmissionModel,
)

from torc.job_runner import JobRunner
from torc.loggers import setup_logging
from torc.resource_monitor.reports import (
    make_job_process_stats_dataframe,
    make_compute_node_stats_dataframes,
)
from torc.workflow_manager import WorkflowManager


logger = logging.getLogger(__name__)


def test_auto_tune_workflow(multi_resource_requirement_workflow):
    """Test execution of a workflow using the auto-tune feature."""
    setup_logging("torc")
    api, scheduler_config_id, output_dir = multi_resource_requirement_workflow

    mgr = WorkflowManager(api)
    mgr.start(auto_tune_resource_requirements=True)

    # TODO: this will change when the manager can schedule nodes
    auto_tune_status = api.get_workflow_status().auto_tune_status
    auto_tune_job_names = set(auto_tune_status.job_names)
    assert auto_tune_job_names == {"job_small1", "job_medium1", "job_large1"}
    num_enabled = 0
    groups = set()
    for job in api.get_jobs().items:
        if job.name in auto_tune_job_names:
            assert job.status == "ready"
            num_enabled += 1
            rr = api.get_jobs_resource_requirements_key(job.name)
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

    stats_by_name = {x: api.get_jobs_process_stats_key(x)[0] for x in auto_tune_job_names}
    assert stats_by_name["job_small1"].max_rss < stats_by_name["job_medium1"].max_rss
    assert stats_by_name["job_medium1"].max_rss < stats_by_name["job_large1"].max_rss

    api.post_workflow_process_auto_tune_resource_requirements_results()
    small = api.get_resource_requirements_key("small")
    medium = api.get_resource_requirements_key("medium")
    large = api.get_resource_requirements_key("large")
    for rr in (small, medium, large):
        assert rr.runtime == "P0DT0H1M"
        assert rr.num_cpus in (1, 2)
        assert rr.memory.lower() == "1g"

    for job in api.get_jobs().items:
        if job.name in auto_tune_job_names:
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
