"""CLI commands to manage jobs"""

import json
import logging
import socket
from pathlib import Path

import click
from torc.swagger_client.models.workflow_jobs_model import WorkflowJobsModel

from torc.api import iter_documents
from torc.job_runner import JobRunner, JOB_COMPLETION_POLL_INTERVAL
from torc.resource_monitor_reports import iter_job_process_stats
from .common import (
    check_database_url,
    get_output_format_from_context,
    get_workflow_key_from_context,
    setup_cli_logging,
    parse_filters,
    path_callback,
    print_items,
)


logger = logging.getLogger(__name__)


@click.group()
def jobs():
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
    """Add a job to the workflow."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    job = WorkflowJobsModel(
        cancel_on_blocking_job_failure=cancel_on_blocking_job_failure,
        command=command,
        key=key,
        name=name,
    )
    job = api.post_workflows_workflow_jobs(job, workflow_key)
    if output_format == "text":
        logger.info("Added job with key=%s", job.key)
    else:
        print(json.dumps({"key": job.key}))


@click.command()
@click.argument("job_key")
@click.option(
    "--stores/--consumes",
    is_flag=True,
    default=True,
    show_default=True,
    help="List data that is either stored by the job or consumed by the job.",
)
@click.pass_obj
@click.pass_context
def list_user_data(ctx, api, job_key, stores):
    """List all user data stored or consumed for a job."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    if stores:
        method = api.get_workflows_workflow_jobs_key_user_data_stores
    else:
        method = api.get_workflows_workflow_jobs_key_user_data_consumes
    resp = method(workflow_key, job_key)
    items = []
    for item in resp.items:
        item = item.to_dict()
        item.pop("id")
        items.append(item)
    print(json.dumps(items, indent=2))


@click.command()
@click.argument("job_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def delete(ctx, api, job_keys):
    """Delete one or more jobs by key."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    for key in job_keys:
        api.delete_workflows_workflow_jobs_key(workflow_key, key)
        logger.info("Deleted workflow=%s job=%s", workflow_key, key)


@click.command()
@click.pass_obj
@click.pass_context
def delete_all(ctx, api):
    """Delete all jobs in the workflow."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    for job in iter_documents(api.get_workflows_workflow_jobs, workflow_key):
        api.delete_workflows_workflow_jobs_key(workflow_key, job.key)
        logger.info("Deleted job %s", job.key)


@click.command(name="list")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    type=str,
    help="Filter the values according to each key=value pair.",
)
@click.option(
    "-x",
    "--exclude",
    multiple=True,
    type=str,
    help="Exclude this column name. Accepts multiple",
    callback=lambda *x: set(x[2]),
)
@click.option("-l", "--limit", type=int, help="Limit the output to this number of jobs.")
@click.option("-s", "--skip", default=0, type=int, help="Skip this number of jobs.")
@click.pass_obj
@click.pass_context
def list_jobs(ctx, api, filters, exclude, limit, skip):
    """List all jobs in a workflow.

    \b
    Examples:
    1. List all jobs in a table.
       $ torc jobs list jobs
    2. List only jobs with run_id=1 and status=done.
       $ torc jobs list jobs -f run_id=1 -f status=done
    3. List all jobs in JSON format.
       $ torc -F json jobs list
    """
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    filters = parse_filters(filters)
    filters["skip"] = skip
    if limit is not None:
        filters["limit"] = limit
    items = (
        x.to_dict()
        for x in iter_documents(api.get_workflows_workflow_jobs, workflow_key, **filters)
    )
    exclude = [
        "id",
        "rev",
        "cancel_on_blocking_job_failure",
        "internal",
        "invocation_script",
        "supports_termination",
    ] + list(exclude)
    table_title = f"Jobs in workflow {workflow_key}"
    print_items(
        ctx,
        items,
        table_title=table_title,
        json_key="jobs",
        exclude_columns=exclude,
        start_index=skip,
    )


@click.command()
@click.option("-l", "--limit", type=int, help="Limit the output to this number of jobs.")
@click.option("-s", "--skip", default=0, type=int, help="Skip this number of jobs.")
@click.pass_obj
@click.pass_context
def list_process_stats(ctx, api, limit, skip):
    """List per-job process resource statistics from a workflow run.

    \b
    Examples:
    1. List stats for all jobs in a table.
       $ torc jobs list-process-stats
    2. List all stats in JSON format.
       $ torc -F json jobs list-process-stats
    """
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    kwargs = {"skip": skip}
    if limit is not None:
        kwargs["limit"] = limit
    items = iter_job_process_stats(api, workflow_key, **kwargs)
    table_title = f"Job Process Resource Utilization Statistics for workflow {workflow_key}"
    print_items(ctx, items, table_title=table_title, json_key="stats", start_index=skip)


@click.command()
@click.argument("resource_requirements_key")
@click.argument("job_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def assign_resource_requirements(ctx, api, resource_requirements_key, job_keys):
    """Assign resource requirements to one or more jobs."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    edges = []
    for job_key in job_keys:
        edge = api.put_workflows_workflow_jobs_key_resource_requirements_rr_key(
            workflow_key, job_key, resource_requirements_key
        )
        edges.append(edge.to_dict())

    if output_format == "text":
        logger.info("Added resource requirements with key=%s", resource_requirements_key)
        for edge in edges:
            logger.info("Stored job requirements via edge %s", edge)
    else:
        print(json.dumps({"key": resource_requirements_key, "edges": edges}))


@click.command()
@click.argument("job_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def reset_status(ctx, api, job_keys):
    """Reset the status of one or more jobs."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    count = 0
    for key in job_keys:
        job = api.get_workflows_workflow_jobs_key(workflow_key, key)
        if job.status != "uninitialized":
            job.status = "uninitialized"
            api.put_workflows_workflow_jobs_key(job, workflow_key, key)
            count += 1
            logger.info("Reset job status of job key=%s name=%s", job.key, job.name)

    if count == 0:
        logger.info("No jobs were reset.")
    else:
        logger.info("Run the command 'torc workflows restart' to initialize job status.")


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
def run(
    ctx, api, cpu_affinity_cpus_per_job, max_parallel_jobs, output: Path, poll_interval, time_limit
):
    """Run workflow jobs on the current system."""
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


jobs.add_command(add)
jobs.add_command(list_user_data)
# jobs.add_command(cancel)
jobs.add_command(delete)
jobs.add_command(delete_all)
jobs.add_command(list_jobs)
jobs.add_command(list_process_stats)
jobs.add_command(assign_resource_requirements)
jobs.add_command(reset_status)
jobs.add_command(run)
