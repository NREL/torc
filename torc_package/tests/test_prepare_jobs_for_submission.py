"""Tests for prepare_jobs_for_submission"""

from torc.openapi_client.models.compute_nodes_resources import (
    ComputeNodesResources,
)


def test_limited_by_cpu(job_requirement_uniform):
    """Ensure that the CPU limits aren't exceeded."""
    db = job_requirement_uniform
    api = db.api
    resources = ComputeNodesResources(
        num_cpus=36,
        memory_gb=92,
        num_gpus=0,
        num_nodes=1,
        time_limit="P0DT4H",
    )
    response = api.prepare_jobs_for_submission(db.workflow.key, resources)
    assert len(response.jobs) == 9


def test_limited_by_memory(job_requirement_uniform):
    """Ensure that the memory limits aren't exceeded."""
    db = job_requirement_uniform
    api = db.api
    resources = ComputeNodesResources(
        num_cpus=200,
        memory_gb=82,
        num_gpus=0,
        num_nodes=1,
        time_limit="P0DT4H",
    )
    response = api.prepare_jobs_for_submission(db.workflow.key, resources)
    assert len(response.jobs) == 82 // 4


def test_limited_by_time(job_requirement_runtime):
    """Ensure that the time limits aren't exceeded."""
    db = job_requirement_runtime
    api = db.api
    resources = ComputeNodesResources(
        num_cpus=36,
        memory_gb=92,
        num_gpus=0,
        num_nodes=1,
        time_limit="P0DT45M",
    )
    response = api.prepare_jobs_for_submission(db.workflow.key, resources)
    assert len(response.jobs) == 1
    assert response.jobs[0].name == "short_job"


def test_walltime_over_memory(job_requirement_variations):
    """Ensure that walltime is prioritized over memory by default."""
    db = job_requirement_variations
    api = db.api
    resources = ComputeNodesResources(
        num_cpus=36,
        memory_gb=92,
        num_gpus=0,
        num_nodes=1,
        time_limit="P0DT24H",
    )
    response = api.prepare_jobs_for_submission(db.workflow.key, resources)
    assert len(response.jobs) >= 1
    assert response.jobs[0].name == "long_job"


def test_memory_over_walltime(job_requirement_variations):
    """Ensure that memory is prioritized over walltime with a custom setting."""
    db = job_requirement_variations
    api = db.api
    resources = ComputeNodesResources(
        num_cpus=36,
        memory_gb=92,
        num_gpus=0,
        num_nodes=1,
        time_limit="P0DT24H",
    )
    response = api.prepare_jobs_for_submission(
        db.workflow.key,
        resources,
        sort_method="gpus_memory_runtime",
    )
    assert len(response.jobs) >= 1
    assert response.jobs[0].name == "large_job_no_scheduler"


def test_runtime_sorting(job_requirement_runtime):
    """Ensure that jobs are sorted by runtime."""
    db = job_requirement_runtime
    api = db.api
    resources = ComputeNodesResources(
        num_cpus=36,
        memory_gb=92,
        num_gpus=0,
        num_nodes=1,
        time_limit="P0DT24H",
    )
    response = api.prepare_jobs_for_submission(
        db.workflow.key,
        resources,
    )
    assert len(response.jobs) == 2
    assert response.jobs[0].name.startswith("medium")
    assert response.jobs[1].name.startswith("short")


def test_no_sorting(job_requirement_runtime):
    """Ensure that jobs can be unsorted."""
    db = job_requirement_runtime
    api = db.api
    resources = ComputeNodesResources(
        num_cpus=36,
        memory_gb=92,
        num_gpus=0,
        num_nodes=1,
        time_limit="P0DT24H",
    )
    response = api.prepare_jobs_for_submission(
        db.workflow.key,
        resources,
        sort_method="none",
    )
    assert len(response.jobs) == 2
    assert response.jobs[0].name.startswith("short")
    assert response.jobs[1].name.startswith("medium")


def test_get_by_gpu(job_requirement_variations):
    """Ensure that the GPU requests are honored."""
    db = job_requirement_variations
    api = db.api
    resources = ComputeNodesResources(
        num_cpus=1,
        memory_gb=92,
        num_gpus=1,
        num_nodes=1,
        time_limit="P0DT1H",
    )
    response = api.prepare_jobs_for_submission(db.workflow.key, resources)
    assert len(response.jobs) == 1
    assert response.jobs[0].name == "gpu_job"


def test_get_jobs_by_scheduler(job_requirement_variations):
    """Ask for jobs with a specific scheduler."""
    db = job_requirement_variations
    api = db.api
    scheduler = db.get_document("slurm_schedulers", "bigmem")
    resources = ComputeNodesResources(
        num_cpus=36,
        memory_gb=92,
        num_gpus=0,
        num_nodes=1,
        time_limit="P0DT4H",
        scheduler_config_id=scheduler.id,
    )
    response = api.prepare_jobs_for_submission(db.workflow.key, resources)
    assert len(response.jobs) == 2
    for job in response.jobs:
        assert job.name.startswith("large_job")
