"""CLI commands to manage jobs"""

import logging

import click
from swagger_client.models.jobs_workflow_model import JobsWorkflowModel

from torc.api import iter_documents
from torc.resource_monitor.reports import (
    iter_job_process_stats,
)
from .common import (
    get_workflow_key_from_context,
    setup_cli_logging,
    make_text_table,
    parse_filters,
)


logger = logging.getLogger(__name__)


@click.group()
def jobs():  # pylint: disable=unused-argument
    """Job commands"""


# TODO: we could add this feature
# @click.command()
# @click.argument("workflow")
# @click.argument("key")
# @click.pass_obj
# @click.pass_context
# def cancel(ctx, api, workflow, key):
#    """Cancel the job in the workflow."""
#    setup_cli_logging(ctx, __name__)
#    logger.info("Canceled workflow=%s job=%s", workflow, key)


@click.command()
@click.option(
    "--cancel-on-blocking-job-failure/--no-cancel-on-blocking-job-failure",
    is_flag=True,
    default=True,
    show_default=True,
    help="Cancel the job if a blocking job fails.",
)
@click.option(
    "-c",
    "--command",
    type=str,
    required=True,
    help="Command to run",
)
@click.option(
    "-k",
    "--key",
    type=str,
    help="Job key. Default is to auto-generate",
)
@click.option(
    "-n",
    "--name",
    type=str,
    help="Job name",
)
@click.pass_obj
@click.pass_context
def add(ctx, api, cancel_on_blocking_job_failure, command, key, name):
    """Delete the job in the workflow."""
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    job = JobsWorkflowModel(
        cancel_on_blocking_job_failure=cancel_on_blocking_job_failure,
        command=command,
        key=key,
        name=name,
    )
    job = api.post_jobs_workflow(job, workflow_key)
    logger.info("Added job with key=%s", job.key)


@click.command()
@click.argument("job_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def delete(ctx, api, job_keys):
    """Delete one or more jobs by key."""
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    for key in job_keys:
        api.delete_jobs_workflow_key(workflow_key, key)
        logger.info("Deleted workflow=%s job=%s", workflow_key, key)


@click.command()
@click.pass_obj
@click.pass_context
def delete_all(ctx, api):
    """Delete all jobs in the workflow."""
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    for job in iter_documents(api.get_jobs_workflow, workflow_key):
        api.delete_jobs_workflow_key(workflow_key, job.key)
        logger.info("Deleted job %s", job.key)


@click.command(name="list")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    type=str,
    help="Filter the values according to each key=value pair.",
)
@click.pass_obj
@click.pass_context
def list_jobs(ctx, api, filters):
    """List all jobs in a workflow.

    \b
    Examples:
    1. List all jobs.
       $ torc jobs 91388876 list jobs
    2. List only jobs with run_id=1 and status=done.
       $ torc jobs 91388876 list jobs -f run_id=1 -f status=done
    """
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    # TODO: restore interruptible when it is supported
    exclude = ("id", "rev", "internal", "interruptible")
    filters = parse_filters(filters)
    table = make_text_table(
        (x.to_dict() for x in iter_documents(api.get_jobs_workflow, workflow_key, **filters)),
        "Jobs",
        exclude_columns=exclude,
    )
    if table.rows:
        print(table)
    else:
        print("No jobs are stored")


@click.command()
@click.pass_obj
@click.pass_context
def list_process_stats(ctx, api):
    """Show per-job process resource statistics from a workflow run."""
    workflow_key = get_workflow_key_from_context(ctx, api)
    table = make_text_table(
        iter_job_process_stats(api, workflow_key), "Job Process Resource Utilization Statistics"
    )
    if table.rows:
        print(table)
    else:
        logger.info("No stats are stored")


jobs.add_command(add)
# jobs.add_command(cancel)
jobs.add_command(delete)
jobs.add_command(delete_all)
jobs.add_command(list_jobs)
jobs.add_command(list_process_stats)
