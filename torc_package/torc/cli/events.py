"""CLI commands to manage events"""

import json
import logging

import click

from torc.api import iter_documents, remove_db_keys
from .common import (
    check_database_url,
    get_workflow_key_from_context,
    setup_cli_logging,
    parse_filters,
)


logger = logging.getLogger(__name__)


@click.group()
def events():  # pylint: disable=unused-argument
    """Event commands"""


@click.command(name="list")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    type=str,
    help="Filter the values according to each key=value pair. Only 'category' is supported.",
)
@click.option("-l", "--limit", type=int, help="Limit the output to this number of jobs.")
@click.option("-s", "--skip", default=0, type=int, help="Skip this number of jobs.")
@click.pass_obj
@click.pass_context
def list_events(ctx, api, filters, limit, skip):
    """List all events in a workflow.

    \b
    Examples:
    1. List all events.
       $ torc events 91388876 list events
    2. List only events with a category of job.
       $ torc events 91388876 list events -f category=job
    """
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    filters = parse_filters(filters)
    data = []
    # TODO: support time ranges, greater than, less than
    filters["skip"] = skip
    if limit is not None:
        filters["limit"] = limit
    for event in iter_documents(api.get_workflows_workflow_events, workflow_key, **filters):
        data.append(remove_db_keys(event))
    print(json.dumps(data, indent=2))


events.add_command(list_events)
