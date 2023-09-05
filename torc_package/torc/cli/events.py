"""CLI commands to manage events"""

import json
import logging
import sys
import time

import click

from torc.api import iter_documents
from .common import (
    check_database_url,
    get_output_format_from_context,
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
    "-a",
    "--after-key",
    type=str,
    help="Only return events that occurred after the event with key.",
)
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
def list_events(ctx, api, after_key, filters, limit, skip):
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

    # TODO: support time ranges, greater than, less than
    filters["skip"] = skip
    if limit is not None:
        filters["limit"] = limit

    if after_key:
        if "skip" in filters:
            logger.warning("Skip is ignored when --after-key is set.")
        evts = iter_documents(api.get_events_after_key, workflow_key, after_key, **filters)
    else:
        evts = iter_documents(api.get_workflows_workflow_events, workflow_key, **filters)

    data = []
    for event in evts:
        # Leave _key
        event.pop("_id")
        event.pop("_rev")
        data.append(event)

    print(json.dumps(data, indent=2))


@click.command()
@click.pass_obj
@click.pass_context
def get_latest_event(ctx, api):
    """Return the key of the latest event."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    data = api.get_latest_event_key(workflow_key)
    latest_key = data["key"]
    if output_format == "text":
        print(f"The latest event key is {latest_key}")
    else:
        print(json.dumps(data, indent=2))


@click.command()
@click.option(
    "-c",
    "--category",
    type=str,
    help="Filter events by this category.",
)
@click.option(
    "-d",
    "--duration",
    type=int,
    help="Duration in seconds to monitor. Default is forever.",
)
@click.option(
    "-p",
    "--poll-interval",
    type=int,
    default=60,
    help="Poll interval in seconds. Please be mindful of impacts to the database.",
)
@click.pass_obj
@click.pass_context
def monitor(ctx, api, category, duration, poll_interval):
    """Monitor events."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    end_time = time.time() + duration if duration else sys.maxsize
    latest_event = api.get_latest_event_key(workflow_key)["key"]
    logger.info(
        "Monitoring for events occurring after event_key=%s with poll_interval=%s",
        latest_event,
        poll_interval,
    )
    filters = {}
    if category:
        filters["category"] = category
    while time.time() < end_time:
        event_ = None
        for event in iter_documents(
            api.get_events_after_key, workflow_key, latest_event, **filters
        ):
            event.pop("_id")
            event.pop("_rev")
            print(json.dumps(event, indent=2))
            event_ = event
        if event_ is not None:
            latest_event = event_["_key"]
        time.sleep(poll_interval)


events.add_command(list_events)
events.add_command(get_latest_event)
events.add_command(monitor)
