"""CLI commands to manage a workflow"""

import getpass
import json
import logging
import math
import sys
from pathlib import Path

import click
import json5
from torc.openapi_client.models.jobs_model import JobsModel
from torc.openapi_client.models.workflows_model import WorkflowsModel
from torc.openapi_client.models.workflow_specifications_model import (
    WorkflowSpecificationsModel,
)

from torc.api import remove_db_keys, sanitize_workflow, iter_documents, list_model_fields
from torc.exceptions import InvalidWorkflow
from torc.hpc.slurm_interface import SlurmInterface
from torc.torc_rc import TorcRuntimeConfig
from torc.workflow_manager import WorkflowManager
from .common import (
    check_database_url,
    confirm_change,
    get_workflow_key_from_context,
    get_output_format_from_context,
    setup_cli_logging,
    parse_filters,
    print_items,
)


logger = logging.getLogger(__name__)


@click.group()
def workflows():
    """Workflow commands"""


@click.command()
@click.argument("workflow_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def cancel(ctx, api, workflow_keys):
    """Cancel one or more workflows."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    if not workflow_keys:
        logger.warning("No workflow keys were passed")
        return

    msg = "This command will cancel all specified workflows."
    confirm_change(ctx, msg)

    for key in workflow_keys:
        cancel_workflow(api, key)


@click.command()
@click.option(
    "-U",
    "--update-rc-with-key",
    is_flag=True,
    default=False,
    show_default=True,
    help="Update torc runtime config file with the created workflow key.",
)
@click.option(
    "-d",
    "--description",
    type=str,
    help="Workflow description",
)
@click.option(
    "-k",
    "--key",
    type=str,
    help="Workflow key. Default is to auto-generate",
)
@click.option(
    "-n",
    "--name",
    type=str,
    help="Workflow name",
)
@click.option(
    "-u",
    "--user",
    type=str,
    default=getpass.getuser(),
    show_default=True,
    help="Username",
)
@click.pass_obj
@click.pass_context
def create(ctx, api, update_rc_with_key, description, key, name, user):
    """Create a new workflow."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow = WorkflowsModel(
        description=description,
        key=key,
        name=name,
        user=user,
    )
    output_format = get_output_format_from_context(ctx)
    workflow = api.post_workflows(workflow)
    if output_format == "text":
        logger.info("Created a workflow with key=%s", workflow.key)
    else:
        print(json.dumps({"key": workflow.key}))
    if update_rc_with_key:
        _update_torc_rc(api, workflow)


@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option(
    "-U",
    "--update-rc-with-key",
    is_flag=True,
    default=False,
    show_default=True,
    help="Update torc runtime config file with the created workflow key.",
)
@click.option(
    "-d",
    "--description",
    type=str,
    help="Workflow description",
)
@click.option(
    "-k",
    "--key",
    type=str,
    help="Workflow key. Default is to auto-generate",
)
@click.option(
    "-n",
    "--name",
    type=str,
    help="Workflow name",
)
@click.option(
    "-u",
    "--user",
    type=str,
    default=getpass.getuser(),
    show_default=True,
    help="Username",
)
@click.pass_obj
@click.pass_context
def create_from_commands_file(
    ctx, api, update_rc_with_key, filename, description, key, name, user
):
    """Create a workflow from a text file containing job CLI commands."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    output_format = get_output_format_from_context(ctx)
    commands = []
    with open(filename, encoding="utf-8") as f_in:
        for line in f_in:
            line = line.strip()
            if line:
                commands.append(line)
    workflow = WorkflowsModel(
        description=description,
        key=key,
        name=name,
        user=user,
    )
    workflow = api.post_workflows(workflow)
    if output_format == "text":
        logger.info("Created a workflow from %s with key=%s", filename, workflow.key)
    else:
        print(json.dumps({"filename": filename, "key": workflow.key}))
    for i, command in enumerate(commands, start=1):
        name = str(i)
        api.post_jobs(workflow.key, JobsModel(name=name, command=command))
    if update_rc_with_key:
        _update_torc_rc(api, workflow)


@click.command()
@click.argument("filename", type=click.Path(exists=True), callback=lambda *x: Path(x[2]))
@click.option(
    "-U",
    "--update-rc-with-key",
    is_flag=True,
    default=False,
    show_default=True,
    help="Update torc runtime config file with the created workflow key.",
)
@click.option(
    "-u",
    "--user",
    type=str,
    default=getpass.getuser(),
    show_default=True,
    help="Username",
)
@click.pass_obj
@click.pass_context
def create_from_json_file(ctx, api, filename, update_rc_with_key, user):
    """Create a workflow from a JSON/JSON5 file."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow = create_workflow_from_json_file(api, filename, user=user)

    output_format = get_output_format_from_context(ctx)
    if output_format == "text":
        logger.info("Created a workflow from %s with key=%s", filename, workflow.key)
    else:
        print(json.dumps({"filename": str(filename), "key": workflow.key}))
    if update_rc_with_key:
        _update_torc_rc(api, workflow)


@click.command()
@click.option(
    "-d",
    "--description",
    type=str,
    help="Workflow description",
)
@click.option(
    "-n",
    "--name",
    type=str,
    help="Workflow name",
)
@click.option(
    "-u",
    "--user",
    type=str,
    default=getpass.getuser(),
    show_default=True,
    help="Username",
)
@click.pass_obj
@click.pass_context
def modify(ctx, api, description, name, user):
    """Modify the workflow parameters."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    workflow = api.get_workflows_key(workflow_key)
    if description is not None:
        workflow.description = description
    if name is not None:
        workflow.name = name
    if user is not None:
        workflow.user = user
    workflow = api.put_workflows_key(workflow_key, workflow)
    logger.info("Updated workflow %s", workflow.key)


@click.command()
@click.argument("workflow_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def delete(ctx, api, workflow_keys):
    """Delete one or more workflows by key."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    if not workflow_keys:
        logger.warning("No workflow keys were passed")
        return

    _delete_workflows_with_warning(ctx, api, workflow_keys)


@click.command()
@click.argument("user")
@click.pass_obj
@click.pass_context
def delete_by_user(ctx, api, user):
    """Delete all workflows for a user."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    keys = [x.key for x in iter_documents(api.get_workflows, user=user)]
    _delete_workflows_with_warning(ctx, api, keys)


@click.command()
@click.pass_obj
@click.pass_context
def delete_all(ctx, api):
    """Delete all workflows."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    keys = [x.key for x in iter_documents(api.get_workflows)]
    _delete_workflows_with_warning(ctx, api, keys)


def _delete_workflows_with_warning(ctx, api, keys):
    items = (api.get_workflows_key(x).to_dict() for x in keys)
    columns = list_model_fields(WorkflowsModel)
    columns.remove("_id")
    columns.remove("_rev")
    print_items(
        ctx,
        items,
        "Workflows",
        columns,
        "workflows",
    )
    msg = "This command will delete the workflows above. Continue?"
    confirm_change(ctx, msg)
    for key in keys:
        api.delete_workflows_key(key)
        logger.info("Deleted workflow %s", key)


@click.command()
@click.pass_obj
@click.pass_context
def list_scheduler_configs(ctx, api):
    """List the scheduler configs in the database."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    output_format = get_output_format_from_context(ctx)
    workflow_key = get_workflow_key_from_context(ctx, api)
    items = []
    for scheduler in ("aws_schedulers", "local_schedulers", "slurm_schedulers"):
        method = getattr(api, f"get_{scheduler}")
        for doc in iter_documents(method, workflow_key):
            items.append(doc.id)

    if output_format == "text":
        logger.info("Scheduler configs in workflow %s", workflow_key)
        for item in items:
            print(item)
    else:
        print(json.dumps({"ids": items}))


@click.command(name="list")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    type=str,
    help="Filter the values according to each key=value pair.",
)
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
def list_workflows(ctx, api, filters, sort_by, reverse_sort):
    """List all workflows.

    \b
    1. List all workflows in a table.
       $ torc workflows list
    2. List all workflows created by user jdoe.
       $ torc workflows list -f user=jdoe
    3. List all workflows in JSON format.
       $ torc -o json workflows list
    """
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    table_title = "Workflows"
    filters = parse_filters(filters)
    if sort_by is not None:
        filters["sort_by"] = sort_by
        filters["reverse_sort"] = reverse_sort
    items = (x.to_dict() for x in iter_documents(api.get_workflows, **filters))
    columns = list_model_fields(WorkflowsModel)
    columns.remove("_id")
    columns.remove("_rev")
    print_items(
        ctx,
        items,
        table_title,
        columns,
        "workflows",
    )


@click.command()
@click.pass_obj
@click.pass_context
def process_auto_tune_resource_requirements_results(ctx, api):
    """Process the results of the first round of auto-tuning resource requirements."""
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    api.post_workflows_key_process_auto_tune_resource_requirements_results(workflow_key)
    url = api.api_client.configuration.host
    rr_cmd = f"torc -k {workflow_key} -u {url} resource-requirements list"
    events_cmd = f"torc -k {workflow_key} -u {url} events list -f category=resource_requirements"
    logger.info(
        "Updated resource requirements. Look at current requirements with "
        "\n  '%s'\n and at "
        "changes by reading the events with \n  '%s'\n",
        rr_cmd,
        events_cmd,
    )


@click.command()
@click.option(
    "-c",
    "--num-cpus",
    type=int,
    default=36,
    help="Number of CPUs per node",
    show_default=True,
)
@click.option(
    "-s",
    "--scheduler-config-id",
    type=str,
    help="Limit output to jobs assigned this scheduler config ID. Refer to list-scheduler-configs.",
)
@click.pass_obj
@click.pass_context
def recommend_nodes(ctx, api, num_cpus, scheduler_config_id):
    """Recommend compute nodes to schedule."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    output_format = get_output_format_from_context(ctx)
    workflow_key = get_workflow_key_from_context(ctx, api)
    if scheduler_config_id is None:
        reqs = api.get_workflows_key_ready_job_requirements(workflow_key)
    else:
        reqs = api.get_workflows_key_ready_job_requirements(
            workflow_key, scheduler_config_id=scheduler_config_id
        )
    if reqs.num_jobs == 0:
        logger.error("No jobs are in the ready state. You may need to run 'torc workflows start'")
        sys.exit(1)

    num_nodes_by_cpus = math.ceil(reqs.num_cpus / num_cpus)
    if output_format == "text":
        print(f"Requirements for jobs in the ready state: \n{reqs}")
        print(f"Based on CPUs, number of required nodes = {num_nodes_by_cpus}")
    else:
        print(
            json.dumps(
                {
                    "ready_job_requirements": reqs.to_dict(),
                    "num_nodes_by_cpus": num_nodes_by_cpus,
                }
            )
        )


@click.command()
@click.argument("workflow_key")
@click.option(
    "-f",
    "--failed-only",
    is_flag=True,
    default=False,
    show_default=True,
    help="Only reset the status of failed jobs.",
)
@click.pass_obj
@click.pass_context
def reset_status(ctx, api, workflow_key, failed_only):
    """Reset the status of the workflow and all jobs."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow = api.get_workflows_key(workflow_key)
    msg = f"""This command will reset the status of this workflow:
    key: {workflow_key}
    user: {workflow.user}
    name: {workflow.name}
    description: {workflow.description}
"""
    confirm_change(ctx, msg)
    reset_workflow_status(api, workflow_key)
    reset_workflow_job_status(api, workflow_key, failed_only=failed_only)


@click.command()
@click.option(
    "-i",
    "--ignore-missing-data",
    is_flag=True,
    default=False,
    show_default=True,
    help="Ignore checks for missing files and user data documents.",
)
@click.option(
    "--only-uninitialized",
    is_flag=True,
    default=False,
    show_default=True,
    help="Only initialize jobs with a status of uninitialized.",
)
@click.pass_obj
@click.pass_context
def restart(ctx, api, ignore_missing_data, only_uninitialized):
    """Restart the workflow defined in the database specified by the URL. Resets all jobs with
    a status of canceled, submitted, submitted_pending, and terminated. Does not affect jobs with
    a status of done.
    """
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    _exit_if_jobs_are_running(api, workflow_key)
    workflow = api.get_workflows_key(workflow_key)
    types = "uninitialized" if only_uninitialized else "failed/incomplete"
    msg = f"""This command will restart this workflow and reset {types} job statuses.
    key: {workflow_key}
    user: {workflow.user}
    name: {workflow.name}
    description: {workflow.description}
"""
    confirm_change(ctx, msg)
    restart_workflow(
        api,
        workflow_key,
        ignore_missing_data=ignore_missing_data,
        only_uninitialized=only_uninitialized,
    )


@click.command()
@click.option(
    "-a",
    "--auto-tune-resource-requirements",
    is_flag=True,
    default=False,
    show_default=True,
    help="Setup the workflow such that only one job from each resource group is run in the first "
    "round. Upon completion torc will look at actual resource utilization of those jobs and "
    "apply the results to the resource requirements definitions. When jobs finish, please call "
    "'torc workflows process_auto_tune_resource_requirements_results' to update the requirements.",
)
@click.option(
    "-i",
    "--ignore-missing-data",
    is_flag=True,
    default=False,
    show_default=True,
    help="Ignore checks for missing files and user data documents.",
)
@click.pass_obj
@click.pass_context
def start(ctx, api, auto_tune_resource_requirements, ignore_missing_data):
    """Start the workflow defined in the database specified by the URL."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    _exit_if_jobs_are_running(api, workflow_key)
    done_jobs = api.get_jobs(workflow_key, status="done", limit=1).items
    if done_jobs:
        workflow = api.get_workflows_key(workflow_key)
        msg = f"""This workflow has one or more jobs with a status of 'done.' This command will
reset all job statuses to 'uninitialized' and then 'ready' or 'blocked.'
    key: {workflow_key}
    user: {workflow.user}
    name: {workflow.name}
    description: {workflow.description}
"""
        confirm_change(ctx, msg)

    try:
        start_workflow(
            api,
            workflow_key,
            auto_tune_resource_requirements=auto_tune_resource_requirements,
            ignore_missing_data=ignore_missing_data,
        )
    except InvalidWorkflow as exc:
        logger.error("Invalid workflow: %s", exc)
        sys.exit(1)


# The functions below exist apart from the CLI functions so that the TUI can call them.


def create_workflow_from_json_file(api, filename: Path, user=None):
    """Create a workflow from a JSON/JSON5 file."""
    if user is None:
        user = getpass.getuser()

    method = json5.load if filename.suffix == ".json5" else json.load
    with open(filename, "r", encoding="utf-8") as f:
        data = sanitize_workflow(method(f))
    if data.get("user") != user:
        if "user" in data:
            logger.info("Overriding user=%s with %s", data["user"], user)
        data["user"] = user
    spec = WorkflowSpecificationsModel(**data)
    return api.post_workflow_specifications(spec)


def start_workflow(
    api, workflow_key, auto_tune_resource_requirements=False, ignore_missing_data=False
):
    """Starts the workflow."""
    mgr = WorkflowManager(api, workflow_key)
    mgr.start(
        auto_tune_resource_requirements=auto_tune_resource_requirements,
        ignore_missing_data=ignore_missing_data,
    )
    api.post_events(
        workflow_key,
        {
            "category": "workflow",
            "type": "start",
            "key": workflow_key,
            "message": f"Started workflow {workflow_key}",
        },
    )
    # TODO: This could schedule nodes.


def restart_workflow(api, workflow_key, only_uninitialized=False, ignore_missing_data=False):
    """Restarts the workflow."""
    mgr = WorkflowManager(api, workflow_key)
    mgr.restart(ignore_missing_data=ignore_missing_data, only_uninitialized=only_uninitialized)
    api.post_events(
        workflow_key,
        {
            "category": "workflow",
            "type": "restart",
            "key": workflow_key,
            "message": f"Restarted workflow {workflow_key}",
        },
    )
    # TODO: This could schedule nodes.


def reset_workflow_status(api, workflow_key):
    """Resets the status of the workflow."""
    api.post_workflows_key_reset_status(workflow_key)
    logger.info("Reset workflow status")
    api.post_events(
        workflow_key,
        {
            "category": "workflow",
            "type": "reset_status",
            "key": workflow_key,
            "message": f"Reset workflow {workflow_key}",
        },
    )


def reset_workflow_job_status(api, workflow_key, failed_only=False):
    """Resets the status of the workflow jobs."""
    api.post_workflows_key_reset_job_status(workflow_key, failed_only=failed_only)
    logger.info("Reset job status, failed_only=%s", failed_only)
    api.post_events(
        workflow_key,
        {
            "category": "workflow",
            "type": "reset_job_status",
            "key": workflow_key,
            "message": f"Reset workflow {workflow_key} job status",
        },
    )


def cancel_workflow(api, workflow_key):
    """Cancels the workflow."""
    # TODO: Handling different scheduler types needs to be at a lower level.
    for job in api.get_scheduled_compute_nodes(workflow_key).items:
        if (
            job.status != "complete"
            and job.scheduler_config_id.split("/")[0].split("__")[0] == "slurm_schedulers"
            and job.scheduler_id is not None
        ):
            intf = SlurmInterface()
            return_code = intf.cancel_job(job.scheduler_id)
            if return_code == 0:
                job.status = "complete"
                api.put_scheduled_compute_nodes_key(workflow_key, job.key, job)
            # else: Ignore all return codes and try to cancel all jobs.
    api.put_workflows_key_cancel(workflow_key)
    logger.info("Canceled workflow %s", workflow_key)
    api.post_events(
        workflow_key,
        {
            "category": "workflow",
            "type": "cancel",
            "key": workflow_key,
            "message": f"Canceled workflow {workflow_key}",
        },
    )


def has_running_jobs(api, workflow_key) -> bool:
    """Returns True if jobs are running."""
    submitted = api.get_jobs(workflow_key, status="submitted", limit=1)
    sub_pend = api.get_jobs(workflow_key, status="submitted_pending", limit=1)
    return len(submitted.items) > 0 or len(sub_pend.items) > 0


def _exit_if_jobs_are_running(api, workflow_key):
    if has_running_jobs(api, workflow_key):
        logger.error(
            "This operation is not allowed on a workflow with 'submitted' jobs. Please allow "
            "the jobs to finish or cancel them."
        )
        sys.exit(1)


@click.command()
@click.option(
    "--sanitize/--no-santize",
    default=True,
    is_flag=True,
    show_default=True,
    help="Remove all database fields from workflow objects.",
)
@click.pass_obj
@click.pass_context
def show(ctx, api, sanitize):
    """Show the workflow."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    data = api.get_workflow_specifications_key(workflow_key).to_dict()
    if sanitize:
        sanitize_workflow(data)
    print(json.dumps(data, indent=2))


@click.command()
@click.option(
    "-e",
    "--expiration-buffer",
    type=int,
    help="Set the number of seconds before the expiration time at which torc will terminate jobs.",
)
@click.option(
    "-h",
    "--wait-for-healthy-db",
    type=int,
    help="Set the number of minutes that torc will tolerate an offline database.",
)
@click.option(
    "-i",
    "--ignore-workflow-completion",
    type=str,
    help="Set to 'true' to cause torc to ignore workflow completions and hold onto compute node "
    "allocations indefinitely. Useful for debugging failed jobs. Set to 'false' to revert to "
    "the default behavior.",
)
@click.option(
    "-w",
    "--wait-for-new-jobs",
    type=int,
    help="Set the number of seconds that torc will wait for new jobs before exiting. Does not "
    "apply if the workflow is complete.",
)
@click.pass_obj
@click.pass_context
def set_compute_node_parameters(
    ctx, api, expiration_buffer, wait_for_healthy_db, ignore_workflow_completion, wait_for_new_jobs
):
    """Set parameters that control how the torc worker app behaves on compute nodes.
    Run 'torc workflows show-config' to see the current values."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    config = api.get_workflows_key_config(workflow_key)
    changed = False
    if (
        expiration_buffer is not None
        and expiration_buffer != config.compute_node_expiration_buffer_seconds
    ):
        config.compute_node_expiration_buffer_seconds = expiration_buffer
        changed = True
    if (
        wait_for_healthy_db is not None
        and wait_for_healthy_db != config.compute_node_wait_for_healthy_database_minutes
    ):
        config.compute_node_wait_for_healthy_database_minutes = wait_for_healthy_db
        changed = True
    if ignore_workflow_completion is not None:
        lowered = ignore_workflow_completion.lower()
        if lowered not in ("true", "false"):
            logger.error(
                "Invalid value for ignore_workflow_completion: %s", ignore_workflow_completion
            )
            sys.exit(1)
        val = lowered == "true"
        if val != config.compute_node_ignore_workflow_completion:
            config.compute_node_ignore_workflow_completion = val
            changed = True
    if (
        wait_for_new_jobs is not None
        and wait_for_new_jobs != config.compute_node_wait_for_new_jobs_seconds
    ):
        config.compute_node_wait_for_new_jobs_seconds = wait_for_new_jobs
        changed = True

    if changed:
        config = api.put_workflows_key_config(workflow_key, config)
        print(json.dumps(config.to_dict(), indent=2))
    else:
        logger.warning("No parameters were changed")


@click.command()
@click.pass_obj
@click.pass_context
def show_config(ctx, api):
    """Show the workflow config."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    config = api.get_workflows_key_config(workflow_key)
    print(json.dumps(config.to_dict(), indent=2))


@click.command(name="status")
@click.pass_obj
@click.pass_context
def show_status(ctx, api):
    """Show the workflow status."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    status = api.get_workflows_key_status(workflow_key)
    print(json.dumps(status.to_dict(), indent=2))


@click.command()
@click.pass_obj
@click.pass_context
def example(ctx, api):
    """Show the example workflow."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    data = api.get_workflow_specifications_example().to_dict()
    sanitize_workflow(data)
    print(json.dumps(data, indent=2))


@click.command()
@click.pass_obj
@click.pass_context
def template(ctx, api):
    """Show the workflow template."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    data = api.get_workflow_specifications_template().to_dict()
    data = remove_db_keys(data)
    data["config"] = remove_db_keys(data["config"])
    data.pop("key", None)
    print(json.dumps(data, indent=2))


def _update_torc_rc(api, workflow):
    config = TorcRuntimeConfig.load()
    config.workflow_key = workflow.key
    path = config.path()
    logger.info("Updating %s with workflow_key=%s", path, config.workflow_key)
    if config.database_url != api.api_client.configuration.host:
        config.database_url = api.api_client.configuration.host
        logger.info("Updating %s with database_url=%s", path, config.database_url)
    config.dump(path=path)


workflows.add_command(cancel)
workflows.add_command(create)
workflows.add_command(create_from_commands_file)
workflows.add_command(create_from_json_file)
workflows.add_command(modify)
workflows.add_command(delete)
workflows.add_command(delete_by_user)
workflows.add_command(delete_all)
workflows.add_command(list_scheduler_configs)
workflows.add_command(list_workflows)
workflows.add_command(process_auto_tune_resource_requirements_results)
workflows.add_command(recommend_nodes)
workflows.add_command(reset_status)
workflows.add_command(restart)
workflows.add_command(set_compute_node_parameters)
workflows.add_command(start)
workflows.add_command(show)
workflows.add_command(show_config)
workflows.add_command(show_status)
workflows.add_command(example)
workflows.add_command(template)
