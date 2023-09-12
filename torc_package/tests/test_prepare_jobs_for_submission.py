"""Tests for post_workflows_key_prepare_jobs_for_submission"""

from torc.openapi_client.models.compute_nodes_resources import (
    ComputeNodesResources,
)


def test_limited_by_cpu(job_requirement_variations):
    """Ensure that the CPU limits aren't exceeded."""
    db = job_requirement_variations
    api = db.api
    resources = ComputeNodesResources(
        num_cpus=36,
        memory_gb=92,
        num_gpus=0,
        num_nodes=1,
        time_limit="P0DT4H",
    )
    response = api.post_workflows_key_prepare_jobs_for_submission(db.workflow.key, resources)
    assert len(response.jobs) == 3
    for job in response.jobs:
        assert job.name.startswith("medium_job")


def test_limited_by_memory(job_requirement_variations):
    """Ensure that the memory limits aren't exceeded."""
    db = job_requirement_variations
    api = db.api
    resources = ComputeNodesResources(
        num_cpus=200,
        memory_gb=82,
        num_gpus=0,
        num_nodes=1,
        time_limit="P0DT4H",
    )
    response = api.post_workflows_key_prepare_jobs_for_submission(db.workflow.key, resources)
    assert len(response.jobs) == 10
    for job in response.jobs:
        assert job.name.startswith("medium_job")


def test_limited_by_time(job_requirement_variations):
    """Ensure that the time limits aren't exceeded."""
    db = job_requirement_variations
    api = db.api
    resources = ComputeNodesResources(
        num_cpus=36,
        memory_gb=92,
        num_gpus=0,
        num_nodes=1,
        time_limit="P0DT45M",
    )
    response = api.post_workflows_key_prepare_jobs_for_submission(db.workflow.key, resources)
    assert len(response.jobs) == 1
    assert response.jobs[0].name == "short_job"


def test_get_by_walltime(job_requirement_variations):
    """Ensure that walltime is prioritizted."""
    db = job_requirement_variations
    api = db.api
    resources = ComputeNodesResources(
        num_cpus=36,
        memory_gb=92,
        num_gpus=0,
        num_nodes=1,
        time_limit="P0DT24H",
    )
    response = api.post_workflows_key_prepare_jobs_for_submission(db.workflow.key, resources)
    assert len(response.jobs) >= 1
    assert response.jobs[0].name == "long_job"


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
    response = api.post_workflows_key_prepare_jobs_for_submission(db.workflow.key, resources)
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
    response = api.post_workflows_key_prepare_jobs_for_submission(db.workflow.key, resources)
    assert len(response.jobs) == 2
    for job in response.jobs:
        assert job.name.startswith("large_job")
