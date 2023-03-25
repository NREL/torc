"""CLI commands to manage a workflow"""

import json
import logging
import sys

import click
from swagger_client.models.workflow_specifications_model import WorkflowSpecificationsModel

from torc.api import sanitize_workflow, iter_documents
from torc.utils.files import load_data
from torc.workflow_manager import WorkflowManager
from .common import setup_cli_logging, make_text_table


logger = logging.getLogger(__name__)


@click.group()
def workflows():
    """Workflow commands"""


@click.command(name="import")
@click.argument("filename", type=click.Path(exists=True))
@click.pass_obj
@click.pass_context
def import_workflow(ctx, api, filename):
    """Import a workflow from a JSON/JSON5 file. Deletes any existing workflow."""
    setup_cli_logging(ctx, 2, __name__)
    spec = WorkflowSpecificationsModel(**sanitize_workflow(load_data(filename)))
    workflow = api.post_workflow_specifications(spec)
    logger.info("Imported the workflow from %s into key=%s", filename, workflow.key)


@click.command()
@click.argument("workflow_key")
@click.pass_obj
@click.pass_context
def cancel(ctx, api, workflow_key):
    """Cancel all jobs that are currently active in the workflow."""
    setup_cli_logging(ctx, 2, __name__)
    # TODO: find active nodes by scheduler type and send cancel commands
    print(f"Cannot cancel workflow {api} {workflow_key}: not implemented yet:")
    sys.exit(1)


@click.command()
@click.argument("workflow_key")
@click.pass_obj
@click.pass_context
def delete(ctx, api, workflow_key):
    """Delete the workflow."""
    setup_cli_logging(ctx, 2, __name__)
    api.delete_workflows_key(workflow_key)
    print(f"Deleted workflow {workflow_key}")


@click.command()
@click.pass_obj
@click.pass_context
def delete_all(ctx, api):
    """Delete all workflows."""
    setup_cli_logging(ctx, 2, __name__)
    for workflow in iter_documents(api.get_workflows):
        api.delete_workflows_key(workflow.key)
        print(f"Deleted workflow {workflow.key}")


@click.command(name="list")
@click.pass_obj
@click.pass_context
def list_workflows(ctx, api):
    """List all workflows."""
    setup_cli_logging(ctx, 2, __name__)
    exclude = ("id", "rev")
    table = make_text_table(
        (x.to_dict() for x in iter_documents(api.get_workflows)),
        "Workflows",
        exclude_columns=exclude,
    )
    if table.rows:
        print(table)
    else:
        print("No workflows are stored")


@click.command()
@click.argument("workflow_key")
@click.pass_obj
@click.pass_context
def reset_status(ctx, api, workflow_key):
    """Reset the status of the workflow and all jobs."""
    setup_cli_logging(ctx, 2, __name__)
    api.post_workflows_reset_status(workflow_key)
    sys.exit(1)


@click.command()
@click.argument("workflow_key")
@click.pass_obj
@click.pass_context
def restart(ctx, api, workflow_key):
    """Restart the workflow defined in the database specified by the URL."""
    setup_cli_logging(ctx, 2, __name__)
    mgr = WorkflowManager(api, workflow_key)
    mgr.restart()
    # TODO: This could schedule nodes.


@click.command()
@click.argument("workflow_key")
@click.pass_obj
@click.pass_context
def start(ctx, api, workflow_key):
    """Start the workflow defined in the database specified by the URL."""
    setup_cli_logging(ctx, 2, __name__)
    mgr = WorkflowManager(api, workflow_key)
    mgr.start()
    # TODO: This could schedule nodes.


@click.command()
@click.argument("workflow_key")
@click.option(
    "--sanitize/--no-santize",
    default=True,
    is_flag=True,
    show_default=True,
    help="Remove all database fields from workflow objects.",
)
@click.pass_obj
@click.pass_context
def show(ctx, api, workflow_key, sanitize):
    """Show the workflow."""
    setup_cli_logging(ctx, 2, __name__)
    data = api.get_workflow_specifications_key(workflow_key).to_dict()
    if sanitize:
        sanitize_workflow(data)
    print(json.dumps(data, indent=2))


@click.command()
@click.pass_obj
@click.pass_context
def example(ctx, api):
    """Show the example workflow."""
    setup_cli_logging(ctx, 2, __name__)
    text = api.get_workflow_specifications_example().to_dict()
    print(json.dumps(text, indent=2))


workflows.add_command(cancel)
workflows.add_command(delete)
workflows.add_command(delete_all)
workflows.add_command(import_workflow)
workflows.add_command(list_workflows)
workflows.add_command(reset_status)
workflows.add_command(restart)
workflows.add_command(start)
workflows.add_command(show)
workflows.add_command(example)
