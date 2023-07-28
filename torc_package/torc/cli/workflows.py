"""CLI commands to manage a workflow"""

import getpass
import json
import logging
import math
import sys
from pathlib import Path

import click
import json5
from torc.swagger_client.models.workflow_jobs_model import WorkflowJobsModel
from torc.swagger_client.models.workflows_model import WorkflowsModel
from torc.swagger_client.models.workflow_specifications_model import (
    WorkflowSpecificationsModel,
)

from torc.api import sanitize_workflow, iter_documents
from torc.exceptions import InvalidWorkflow
from torc.hpc.slurm_interface import SlurmInterface
from torc.torc_rc import TorcRuntimeConfig
from torc.workflow_manager import WorkflowManager
from .common import (
    check_database_url,
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
    if not workflow_keys:
        logger.error("No workflow keys were passed")
        sys.exit(1)
    check_database_url(api)

    for key in workflow_keys:
        # TODO: Handling different scheduler types needs to be at a lower level.
        for job in api.get_workflows_workflow_scheduled_compute_nodes(key).items:
            if (
                job.status != "complete"
                and job.scheduler_config_id.split("/")[0].split("__")[0] == "slurm_schedulers"
            ):
                intf = SlurmInterface()
                return_code = intf.cancel_job(job.scheduler_id)
                if return_code == 0:
                    job.status = "complete"
                    api.put_workflows_workflow_scheduled_compute_nodes_key(job, key, job.key)
                # else: Ignore all return codes and try to cancel all jobs.
        api.put_workflows_key_cancel(key)
        logger.info("Canceled workflow %s", key)


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
        api.post_workflows_workflow_jobs(
            WorkflowJobsModel(name=name, command=command), workflow.key
        )
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
    method = json5.load if filename.suffix == ".json5" else json.load
    with open(filename, "r", encoding="utf-8") as f:
        data = sanitize_workflow(method(f))
    if data.get("user") != user:
        if "user" in data:
            logger.info("Overriding user=%s with %s", data["user"], user)
        data["user"] = user
    output_format = get_output_format_from_context(ctx)
    spec = WorkflowSpecificationsModel(**data)
    workflow = api.post_workflow_specifications(spec)

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
    workflow = api.put_workflows_key(workflow, workflow_key)
    logger.info("Updated workflow %s", workflow.key)


@click.command()
@click.argument("workflow_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def delete(ctx, api, workflow_keys):
    """Delete one or more workflows by key."""
    setup_cli_logging(ctx, __name__)
    if not workflow_keys:
        logger.error("No workflow keys were passed")
        sys.exit(1)
    check_database_url(api)
    # TODO: what if nothing was passed?
    # Check all commands for this condition.
    for key in workflow_keys:
        api.delete_workflows_key(key)
        logger.info("Deleted workflow %s", key)


@click.command()
@click.pass_obj
@click.pass_context
def delete_all(ctx, api):
    """Delete all workflows."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    for workflow in iter_documents(api.get_workflows):
        api.delete_workflows_key(workflow.key)
        logger.info("Deleted workflow %s", workflow.key)


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
        method = getattr(api, f"get_workflows_workflow_{scheduler}")
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
@click.pass_obj
@click.pass_context
def list_workflows(ctx, api, filters):
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
    exclude = ("id", "rev")
    table_title = "Workflows"
    filters = parse_filters(filters)
    items = (x.to_dict() for x in iter_documents(api.get_workflows, **filters))
    print_items(
        ctx,
        items,
        table_title=table_title,
        json_key="workflows",
        exclude_columns=exclude,
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
        logger.error("No jobs are in the ready state. You many need to run 'torc workflows start'")
        sys.exit(0)

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
@click.pass_obj
@click.pass_context
def reset_status(ctx, api):
    """Reset the status of the workflow and all jobs."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    api.post_workflows_key_reset_status(workflow_key)
    logger.info("Reset workflow status")


@click.command()
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
def reset_job_status(ctx, api, failed_only):
    """Reset the status of jobs. Resets all jobs unless failed_only is true."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    api.post_workflows_key_reset_job_status(workflow_key, failed_only=failed_only)
    logger.info("Reset job status, failed_only=%s", failed_only)


@click.command()
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
def restart(ctx, api, ignore_missing_data):
    """Restart the workflow defined in the database specified by the URL."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    mgr = WorkflowManager(api, workflow_key)
    mgr.restart(ignore_missing_data=ignore_missing_data)
    # TODO: This could schedule nodes.


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
    mgr = WorkflowManager(api, workflow_key)
    try:
        mgr.start(
            auto_tune_resource_requirements=auto_tune_resource_requirements,
            ignore_missing_data=ignore_missing_data,
        )
    except InvalidWorkflow as exc:
        logger.error("Invalid workflow: %s", exc)
        sys.exit(1)
    # TODO: This could schedule nodes.


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
    text = api.get_workflow_specifications_example().to_dict()
    print(json.dumps(text, indent=2))


@click.command()
@click.pass_obj
@click.pass_context
def template(ctx, api):
    """Show the workflow template."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    data = api.get_workflow_specifications_template().to_dict()
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
workflows.add_command(delete_all)
workflows.add_command(list_scheduler_configs)
workflows.add_command(list_workflows)
workflows.add_command(process_auto_tune_resource_requirements_results)
workflows.add_command(recommend_nodes)
workflows.add_command(reset_status)
workflows.add_command(reset_job_status)
workflows.add_command(restart)
workflows.add_command(start)
workflows.add_command(show)
workflows.add_command(show_config)
workflows.add_command(show_status)
workflows.add_command(example)
workflows.add_command(template)
