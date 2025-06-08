"""CLI commands to manage events"""

import json
import sys
import time
from datetime import datetime

import rich_click as click
from loguru import logger

from torc.api import iter_documents
from torc.common import convert_timestamp
from .common import (
    check_database_url,
    get_output_format_from_context,
    get_workflow_key_from_context,
    setup_cli_logging,
    parse_filters,
)


@click.group()
def events():
    """Event commands"""


@click.command(name="list")
@click.option(
    "-A",
    "--after-timestamp-ms",
    type=int,
    help="Only return events that occurred after this timestamp expressed as millseconds since "
    "the epoch in UTC.",
)
@click.option(
    "-a",
    "--after-datetime",
    type=str,
    help="Only return events that occurred after this local datetime "
    "(format = YYYY-MM-DD HH:MM:SS.ddd).",
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
def list_events(ctx, api, after_datetime, after_timestamp_ms, filters, limit, skip):
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

    if after_datetime and after_timestamp_ms:
        logger.error("after_datetime and after_timestamp_ms cannot both be set")
        sys.exit(1)

    # TODO: support time ranges, greater than, less than
    filters["skip"] = skip
    if limit is not None:
        filters["limit"] = limit

    if after_datetime or after_timestamp_ms:
        if after_datetime:
            timestamp = (
                datetime.strptime(after_datetime, "%Y-%m-%d %H:%M:%S.%f").timestamp() * 1000
            )
        else:
            timestamp = after_timestamp_ms
        if "skip" in filters:
            logger.warning("Skip is ignored when a timestamp is set.")
        evts = iter_documents(api.get_events_after_timestamp, workflow_key, timestamp, **filters)
    else:
        evts = iter_documents(api.list_events, workflow_key, **filters)

    data = []
    for event in evts:
        # Leave _key
        event.pop("_id")
        event.pop("_rev")
        event["datetime"] = str(convert_timestamp(event["timestamp"]))
        data.append(event)

    print(json.dumps(data, indent=2))


@click.command()
@click.pass_obj
@click.pass_context
def get_latest_event_timestamp(ctx, api):
    """Return the timestamp of the latest event."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    data = api.get_latest_event_timestamp(workflow_key)
    latest_timestamp = data["timestamp"]
    if output_format == "text":
        print(f"The latest event timestamp is {latest_timestamp}")
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
    latest_timestamp = api.get_latest_event_timestamp(workflow_key)["timestamp"]
    logger.info(
        "Monitoring for events occurring after timestamp={} with poll_interval={}",
        convert_timestamp(latest_timestamp),
        poll_interval,
    )
    filters = {}
    if category:
        filters["category"] = category
    while time.time() < end_time:
        event_ = None
        for event in iter_documents(
            api.get_events_after_timestamp, workflow_key, latest_timestamp, **filters
        ):
            event.pop("_id")
            event.pop("_rev")
            event["datetime"] = str(convert_timestamp(event["timestamp"]))
            print(json.dumps(event, indent=2))
            event_ = event
        if event_ is not None:
            latest_timestamp = event_["timestamp"]
        time.sleep(poll_interval)


events.add_command(list_events)
events.add_command(get_latest_event_timestamp)
events.add_command(monitor)
