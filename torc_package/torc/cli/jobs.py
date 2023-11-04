"""CLI commands to manage jobs"""

import json
import logging
import socket
from pathlib import Path

import click

from torc.openapi_client.models.jobs_model import JobsModel
from torc.api import iter_documents, list_model_fields, wait_for_healthy_database
from torc.common import JobStatus
from torc.exceptions import DatabaseOffline
from torc.job_runner import JobRunner, JOB_COMPLETION_POLL_INTERVAL
from torc.resource_monitor_reports import iter_job_process_stats
from torc.utils.run_command import get_cli_string
from .common import (
    check_database_url,
    confirm_change,
    get_output_format_from_context,
    get_workflow_key_from_context,
    setup_cli_logging,
    parse_filters,
    path_callback,
    print_items,
)
from .run_function import run_function
from .run_postprocess import run_postprocess


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
    # TODO: This doesn't support lots of things like files and blocked_by.
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    job = JobsModel(
        cancel_on_blocking_job_failure=cancel_on_blocking_job_failure,
        command=command,
        key=key,
        name=name,
    )
    job = api.post_jobs(workflow_key, job)
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
        method = api.get_jobs_key_user_data_stores
    else:
        method = api.get_jobs_key_user_data_consumes
    resp = method(workflow_key, job_key)
    items = []
    for item in resp.items:
        item = item.to_dict()
        item.pop("_id")
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
    if not job_keys:
        logger.warning("No job keys were passed")
        return

    workflow_key = get_workflow_key_from_context(ctx, api)
    msg = f"This command will delete {len(job_keys)} jobs in workflow {workflow_key}."
    confirm_change(ctx, msg)
    for key in job_keys:
        api.delete_jobs_key(workflow_key, key)
        logger.info("Deleted workflow=%s job=%s", workflow_key, key)


@click.command()
@click.pass_obj
@click.pass_context
def delete_all(ctx, api):
    """Delete all jobs in the workflow."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    job_keys = [x.key for x in iter_documents(api.get_jobs, workflow_key)]
    msg = f"This command will delete the {len(job_keys)} jobs in workflow {workflow_key}."
    confirm_change(ctx, msg)
    for key in job_keys:
        api.delete_jobs_key(workflow_key, key)
        logger.info("Deleted job %s", key)


@click.command()
@click.argument("job_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def disable(ctx, api, job_keys):
    """Set the status of one or more jobs to disabled."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    if not job_keys:
        logger.warning("No job keys were passed")
        return

    workflow_key = get_workflow_key_from_context(ctx, api)
    msg = (
        f"This command will set the status of {len(job_keys)} jobs to 'disabled' "
        f"in workflow {workflow_key}."
    )
    confirm_change(ctx, msg)
    count = 0
    for key in job_keys:
        job = api.get_jobs_key(workflow_key, key)
        if job.status != "disabled":
            job.status = "disabled"
            api.put_jobs_key(workflow_key, key, job)
            count += 1
            logger.info("Set job status of job key=%s name=%s to 'disabled.'", job.key, job.name)


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
@click.option(
    "--sort-by",
    type=str,
    help="Sort results by this column.",
)
@click.option(
    "--reverse-sort",
    is_flag=True,
    default=False,
    show_default=True,
    help="Reverse the sort order if --sort-by is set.",
)
@click.pass_obj
@click.pass_context
def list_jobs(ctx, api, filters, exclude, limit, skip, sort_by, reverse_sort):
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
    if sort_by is not None:
        filters["sort_by"] = sort_by
        filters["reverse_sort"] = reverse_sort
    items = (x.to_dict() for x in iter_documents(api.get_jobs, workflow_key, **filters))
    exclude.update(
        {
            "_id",
            "_rev",
            "cancel_on_blocking_job_failure",
            "internal",
            "invocation_script",
            "supports_termination",
        }
    )
    columns = [x for x in list_model_fields(JobsModel) if x not in exclude]
    table_title = f"Jobs in workflow {workflow_key}"
    print_items(
        ctx,
        items,
        table_title,
        columns,
        "jobs",
        start_index=skip + 1,
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
    items = list(iter_job_process_stats(api, workflow_key, **kwargs))
    table_title = f"Job Process Resource Utilization Statistics for workflow {workflow_key}"
    columns = items[0].keys()
    print_items(ctx, items, table_title, columns, "stats", start_index=skip + 1)


@click.command()
@click.argument("resource_requirements_key")
@click.argument("job_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def assign_resource_requirements(ctx, api, resource_requirements_key, job_keys):
    """Assign resource requirements to one or more jobs."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    if not job_keys:
        logger.warning("No job keys were passed")
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    edges = []
    for job_key in job_keys:
        edge = api.put_jobs_key_resource_requirements_rr_key(
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
    if not job_keys:
        logger.warning("No job keys were passed")
        return

    workflow_key = get_workflow_key_from_context(ctx, api)
    msg = (
        f"This command will reset the status of {len(job_keys)} jobs to 'uninitialized' "
        f"in workflow {workflow_key}."
    )
    confirm_change(ctx, msg)
    count = 0
    run_id = api.get_workflows_key_status(workflow_key).run_id
    for key in job_keys:
        job = api.get_jobs_key(workflow_key, key)
        if job.status != JobStatus.UNINITIALIZED.value:
            match job.status:
                case JobStatus.UNINITIALIZED.value:
                    pass
                case JobStatus.DONE.value | JobStatus.CANCELED.value | JobStatus.TERMINATED.value:
                    api.put_jobs_key_manage_status_change_status_rev_run_id(
                        workflow_key,
                        job.key,
                        JobStatus.UNINITIALIZED.value,
                        job.rev,
                        run_id,
                    )
                case _:
                    job.status = JobStatus.UNINITIALIZED.value
                    api.put_jobs_key(workflow_key, key, job)
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
@click.option("-l", "--log-suffix", default="", type=str, help="Log file suffix")
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
@click.option(
    "-w",
    "--wait-for-healthy-database-minutes",
    type=int,
    default=0,
    show_default=True,
    help="Wait this number of minutes if the database is offline. Applies only to the initial "
    "connection.",
)
@click.pass_obj
@click.pass_context
def run(
    ctx,
    api,
    cpu_affinity_cpus_per_job,
    log_suffix,
    max_parallel_jobs,
    output: Path,
    poll_interval,
    time_limit,
    wait_for_healthy_database_minutes,
):
    """Run workflow jobs on the current system."""
    try:
        # NOTE: Ensure that this is the first API command that gets sent.
        api.get_ping()
    except DatabaseOffline:
        wait_for_healthy_database(api, wait_for_healthy_database_minutes)

    workflow_key = get_workflow_key_from_context(ctx, api)
    output.mkdir(exist_ok=True)
    hostname = socket.gethostname()
    check_database_url(api)
    log_file = output / f"worker_{hostname}_{log_suffix}.log"
    my_logger = setup_cli_logging(ctx, __name__, filename=log_file, mode="a")
    my_logger.info(get_cli_string())
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
    try:
        runner.run_worker()
    except Exception:
        logger.exception("Torc worker failed")
        raise


jobs.add_command(add)
jobs.add_command(list_user_data)
# jobs.add_command(cancel)
jobs.add_command(delete)
jobs.add_command(delete_all)
jobs.add_command(disable)
jobs.add_command(list_jobs)
jobs.add_command(list_process_stats)
jobs.add_command(assign_resource_requirements)
jobs.add_command(reset_status)
jobs.add_command(run)
jobs.add_command(run_function)
jobs.add_command(run_postprocess)
