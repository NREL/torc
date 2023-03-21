"""CLI commands to manage a workflow"""

import logging
import sys

import click
from swagger_client.models.workflow_model import WorkflowModel

from torc.api import sanitize_workflow
from torc.utils.files import load_data
from torc.workflow_manager import WorkflowManager
from .common import setup_cli_logging


logger = logging.getLogger(__name__)


@click.group()
def workflow():
    """Workflow commands"""


@click.command(name="import")
@click.argument("filename", type=click.Path(exists=True))
@click.pass_obj
@click.pass_context
def import_workflow(ctx, api, filename):
    """Import a workflow from a JSON/JSON5 file. Deletes any existing workflow."""
    setup_cli_logging(ctx, 2, __name__)
    api.delete_workflow()
    wflow = WorkflowModel(**sanitize_workflow(load_data(filename)))
    api.post_workflow(wflow)
    logger.info("Imported the workflow from %s", filename)


@click.command()
@click.pass_obj
@click.pass_context
def cancel(ctx, api):
    """Cancel all jobs that are currently active in the workflow."""
    setup_cli_logging(ctx, 2, __name__)
    # TODO: find active nodes by scheduler type and send cancel commands
    print(f"Cannot cancel workflow {api}: not implemented yet:")
    sys.exit(1)


@click.command()
@click.pass_obj
@click.pass_context
def delete(ctx, api):
    """Delete the workflow."""
    setup_cli_logging(ctx, 2, __name__)
    api.delete_workflow()
    print("Deleted the workflow")


@click.command()
@click.pass_obj
@click.pass_context
def reset_status(ctx, api):
    """Reset the status of the workflow and all jobs."""
    setup_cli_logging(ctx, 2, __name__)
    api.post_workflow_reset_status()
    sys.exit(1)


@click.command()
@click.pass_obj
@click.pass_context
def restart(ctx, api):
    """Restart the workflow defined in the database specified by the URL."""
    setup_cli_logging(ctx, 2, __name__)
    mgr = WorkflowManager(api)
    mgr.restart()
    # TODO: This could schedule nodes.


@click.command()
@click.pass_obj
@click.pass_context
def start(ctx, api):
    """Start the workflow defined in the database specified by the URL."""
    setup_cli_logging(ctx, 2, __name__)
    mgr = WorkflowManager(api)
    mgr.start()
    # TODO: This could schedule nodes.


workflow.add_command(cancel)
workflow.add_command(delete)
workflow.add_command(import_workflow)
workflow.add_command(reset_status)
workflow.add_command(restart)
workflow.add_command(start)
