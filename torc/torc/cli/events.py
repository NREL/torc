"""CLI commands to manage events"""

import json
import logging

import click

from torc.api import iter_documents, remove_db_keys
from .common import setup_cli_logging


logger = logging.getLogger(__name__)


@click.group()
@click.option("-k", "--workflow-key", type=str, required=True, help="Workflow key")
def events(workflow_key):  # pylint: disable=unused-argument
    """event commands"""


@click.command(name="list")
@click.pass_obj
@click.pass_context
def list_events(ctx, api):
    """List all events in a workflow.

    \b
    Examples:
    1. List all events.
       $ torc events 91388876 list events
    2. List only events with run_id=1 and status=done.
       $ torc events 91388876 list events -f run_id=1 -f status=done
    """
    setup_cli_logging(ctx, 2, __name__)
    workflow_key = ctx.parent.params["workflow_key"]
    data = []
    for event in iter_documents(api.get_events_workflow, workflow_key):
        data.append(remove_db_keys(event))
    print(json.dumps(data, indent=2))


events.add_command(list_events)
