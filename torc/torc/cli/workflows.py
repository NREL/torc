"""CLI commands to manage a workflow"""

import getpass
import json
import logging
import sys

import click
from swagger_client.models.jobs_workflow_model import JobsWorkflowModel
from swagger_client.models.workflows_model import WorkflowsModel
from swagger_client.models.workflow_specifications_model import WorkflowSpecificationsModel

from torc.api import sanitize_workflow, iter_documents
from torc.utils.files import load_data
from torc.workflow_manager import WorkflowManager
from .common import get_workflow_key_from_context, setup_cli_logging, make_text_table


logger = logging.getLogger(__name__)


@click.group()
def workflows():
    """Workflow commands"""


@click.command()
@click.pass_obj
@click.pass_context
def cancel(ctx, api, workflow_key):
    """Cancel all jobs that are currently active in the workflow."""
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    # TODO: find active nodes by scheduler type and send cancel commands
    logger.error("Cannot cancel workflow %s %s: not implemented yet:", api, workflow_key)
    sys.exit(1)


@click.command()
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
def create(ctx, api, description, key, name, user):
    """Create a new workflow."""
    setup_cli_logging(ctx, __name__)
    workflow = WorkflowsModel(
        description=description,
        key=key,
        name=name,
        user=user,
    )
    workflow = api.post_workflows(workflow)
    logger.info("Created workflow with key=%s", workflow.key)


@click.command()
@click.argument("filename", type=click.Path(exists=True))
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
def create_from_commands_file(ctx, api, filename, description, key, name, user):
    """Create a workflow from a text file containing job CLI commands."""
    setup_cli_logging(ctx, __name__)
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
    logger.info("Created workflow with key=%s", workflow.key)
    for i, command in enumerate(commands, start=1):
        name = str(i)
        job = api.post_jobs_workflow(JobsWorkflowModel(name=name, command=command), workflow.key)
        logger.info("Added job %s", job.key)


@click.command()
@click.argument("filename", type=click.Path(exists=True))
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
def create_from_json_file(ctx, api, filename, user):
    """Create a workflow from a JSON/JSON5 file."""
    setup_cli_logging(ctx, __name__)
    data = sanitize_workflow(load_data(filename))
    if data.get("user") != user:
        if "user" in data:
            logger.info("Overriding user=%s with %s", data["user"], user)
        data["user"] = user
    spec = WorkflowSpecificationsModel(**data)
    workflow = api.post_workflow_specifications(spec)
    logger.info("Created a workflow from %s with key=%s", filename, workflow.key)


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
    for key in workflow_keys:
        api.delete_workflows_key(key)
        logger.info("Deleted workflow %s", key)


@click.command()
@click.pass_obj
@click.pass_context
def delete_all(ctx, api):
    """Delete all workflows."""
    setup_cli_logging(ctx, __name__)
    for workflow in iter_documents(api.get_workflows):
        api.delete_workflows_key(workflow.key)
        logger.info("Deleted workflow %s", workflow.key)


@click.command(name="list")
@click.pass_obj
@click.pass_context
def list_workflows(ctx, api):
    """List all workflows."""
    setup_cli_logging(ctx, __name__)
    exclude = ("id", "rev")
    table = make_text_table(
        (x.to_dict() for x in iter_documents(api.get_workflows)),
        "Workflows",
        exclude_columns=exclude,
    )
    if table.rows:
        print(table)
    else:
        logger.info("No workflows are stored")


@click.command()
@click.pass_obj
@click.pass_context
def reset_status(ctx, api):
    """Reset the status of the workflow and all jobs."""
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    api.post_workflows_reset_status(workflow_key)
    sys.exit(1)


@click.command()
@click.pass_obj
@click.pass_context
def restart(ctx, api):
    """Restart the workflow defined in the database specified by the URL."""
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    mgr = WorkflowManager(api, workflow_key)
    mgr.restart()
    # TODO: This could schedule nodes.


@click.command()
@click.pass_obj
@click.pass_context
def start(ctx, api):
    """Start the workflow defined in the database specified by the URL."""
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    mgr = WorkflowManager(api, workflow_key)
    mgr.start()
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
    workflow_key = get_workflow_key_from_context(ctx, api)
    config = api.get_workflows_config_key(workflow_key)
    print(json.dumps(config.to_dict(), indent=2))


@click.command()
@click.pass_obj
@click.pass_context
def show_status(ctx, api):
    """Show the workflow status."""
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    status = api.get_workflows_status_key(workflow_key)
    print(json.dumps(status.to_dict(), indent=2))


@click.command()
@click.pass_obj
@click.pass_context
def example(ctx, api):
    """Show the example workflow."""
    setup_cli_logging(ctx, __name__)
    text = api.get_workflow_specifications_example().to_dict()
    print(json.dumps(text, indent=2))


workflows.add_command(cancel)
workflows.add_command(create)
workflows.add_command(create_from_commands_file)
workflows.add_command(create_from_json_file)
workflows.add_command(modify)
workflows.add_command(delete)
workflows.add_command(delete_all)
workflows.add_command(list_workflows)
workflows.add_command(reset_status)
workflows.add_command(restart)
workflows.add_command(start)
workflows.add_command(show)
workflows.add_command(show_config)
workflows.add_command(show_status)
workflows.add_command(example)
