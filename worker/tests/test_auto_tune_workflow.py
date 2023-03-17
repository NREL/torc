import logging

from swagger_client.models.worker_resources import WorkerResources
from swagger_client.models.workflow_config_compute_node_resource_stat_config import (
    WorkflowConfigComputeNodeResourceStatConfig,
)

from wms.job_runner import JobRunner
from wms.loggers import setup_logging
from wms.workflow_manager import WorkflowManager


logger = logging.getLogger(__name__)


def test_auto_tune_workflow(multi_resource_requirement_workflow):
    setup_logging("wms")
    api, output_dir = multi_resource_requirement_workflow

    mgr = WorkflowManager(api)
    config = api.get_workflow_config()
    config.compute_node_resource_stat_config = WorkflowConfigComputeNodeResourceStatConfig(
        cpu=True, memory=True, process=True, interval=0.1
    )
    api.put_workflow_config(config)
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
            rr = api.get_jobs_resource_requirements_name(job.name)
            assert rr.name not in groups
            groups.add(rr.name)
        else:
            assert job.status == "disabled"
    assert num_enabled == 3

    resources = WorkerResources(
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
    )
    runner.run_worker()
    assert api.get_workflow_is_complete()

    stats_by_name = {x: api.get_jobs_process_stats_name(x)[0] for x in auto_tune_job_names}
    assert stats_by_name["job_small1"].max_rss < stats_by_name["job_medium1"].max_rss
    assert stats_by_name["job_medium1"].max_rss < stats_by_name["job_large1"].max_rss

    api.post_workflow_process_auto_tune_resource_requirements_results()
    small = api.get_resource_requirements_name("small")
    medium = api.get_resource_requirements_name("medium")
    large = api.get_resource_requirements_name("large")
    for rr in (small, medium, large):
        assert rr.runtime == "P0DT0H1M"
        assert rr.num_cpus == 1
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
