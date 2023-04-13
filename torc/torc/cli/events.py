"""CLI commands to manage events"""

import json
import logging

import click

from torc.api import iter_documents, remove_db_keys
from .common import check_database_url, get_workflow_key_from_context, setup_cli_logging


logger = logging.getLogger(__name__)


@click.group()
def events():  # pylint: disable=unused-argument
    """event commands"""


@click.command(name="list")
@click.option("-l", "--limit", type=int, help="Limit the output to this number of jobs.")
@click.option("-s", "--skip", default=0, type=int, help="Skip this number of jobs.")
@click.pass_obj
@click.pass_context
def list_events(ctx, api, limit, skip):
    """List all events in a workflow.

    \b
    Examples:
    1. List all events.
       $ torc events 91388876 list events
    2. List only events with run_id=1 and status=done.
       $ torc events 91388876 list events -f run_id=1 -f status=done
    """
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    data = []
    kwargs = {"skip": skip}
    if limit is not None:
        kwargs["limit"] = limit
    # TODO: filtering? Not all columns are the same. Are any guaranteed? Tables?
    for event in iter_documents(api.get_workflows_workflow_events, workflow_key, **kwargs):
        data.append(remove_db_keys(event))
    print(json.dumps(data, indent=2))


events.add_command(list_events)
