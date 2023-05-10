"""CLI commands to run on a local compute node"""

import logging
import socket
from pathlib import Path

import click

from torc.job_runner import JobRunner, JOB_COMPLETION_POLL_INTERVAL
from .common import (
    check_database_url,
    get_workflow_key_from_context,
    path_callback,
    setup_cli_logging,
)


logger = logging.getLogger(__name__)


@click.group()
def local():
    """Local compute node commands"""


@click.command()
@click.option(
    "-c",
    "--cpu-affinity-cpus-per-job",
    type=int,
    help="Enable CPU affinity for this number of CPUs per job.",
)
@click.option(
    "-m",
    "--max-parallel-jobs",
    type=int,
    help="Maximum number of parallel jobs. Default is to use resource availability.",
)
@click.option(
    "-o",
    "--output",
    default="output",
    show_default=True,
    callback=path_callback,
)
@click.option(
    "-p",
    "--poll-interval",
    default=JOB_COMPLETION_POLL_INTERVAL,
    show_default=True,
    help="Poll interval for job completions",
)
@click.option(
    "-t",
    "--time-limit",
    help="Time limit ISO 8601 time duration format (like 'P0DT24H'), defaults to no limit.",
)
@click.pass_obj
@click.pass_context
def run_jobs(
    ctx, api, cpu_affinity_cpus_per_job, max_parallel_jobs, output: Path, poll_interval, time_limit
):
    """Run workflow jobs on a local system."""
    workflow_key = get_workflow_key_from_context(ctx, api)
    output.mkdir(exist_ok=True)
    hostname = socket.gethostname()
    log_file = output / f"worker_{hostname}.log"
    setup_cli_logging(ctx, __name__, filename=log_file, mode="a")
    check_database_url(api)
    workflow = api.get_workflows_key(workflow_key)
    runner = JobRunner(
        api,
        workflow,
        output,
        cpu_affinity_cpus_per_job=cpu_affinity_cpus_per_job,
        max_parallel_jobs=max_parallel_jobs,
        job_completion_poll_interval=poll_interval,
        time_limit=time_limit,
    )
    runner.run_worker()


local.add_command(run_jobs)
