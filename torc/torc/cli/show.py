"""CLI commands to show items from the database."""

import json
import logging
from pprint import pprint

import click

from torc.api import iter_documents, remove_db_keys, sanitize_workflow
from torc.resource_monitor.reports import (
    iter_job_process_stats,
    make_compute_node_stats_text_tables,
)
from .common import setup_cli_logging, make_text_table


logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def show(ctx):
    """Show commands"""
    setup_cli_logging(ctx, 1, __name__)


@click.command()
@click.pass_obj
def events(api):
    """Show jobs stored in the workflow."""
    for event in api.get_events().items:
        pprint(remove_db_keys(event))


@click.command()
@click.pass_obj
def jobs(api):
    """Show jobs stored in the workflow."""
    exclude = ("key", "id", "rev", "internal")
    table = make_text_table(
        (x.to_dict() for x in iter_documents(api.get_jobs)),
        "Jobs",
        exclude_columns=exclude,
    )
    if table.rows:
        print(table)
    else:
        print("No jobs are available")


@click.command()
@click.pass_obj
def process_stats(api):
    """Show per-job process resource statistics from a workflow run."""
    table = make_text_table(
        iter_job_process_stats(api), "Job Process Resource Utilization Statistics"
    )
    if table.rows:
        print(table)
    else:
        print("No stats are available")


@click.command()
@click.option(
    "-x",
    "--exclude-process",
    default=False,
    is_flag=True,
    show_default=True,
    help="Exclude job process stats (show compute node stats only).",
)
@click.pass_obj
def resource_stats(api, exclude_process):
    """Show resource statistics from a workflow run."""
    for table in make_compute_node_stats_text_tables(
        api, exclude_process=exclude_process
    ).values():
        print(table)


@click.command()
@click.pass_obj
def results(api):
    """Show jobs stored in the workflow."""
    exclude = ("key", "id", "rev")
    table = make_text_table(
        (x.to_dict() for x in iter_documents(api.get_results)),
        "Results",
        exclude_columns=exclude,
    )
    if table.rows:
        print(table)
    else:
        print("No results are available")


@click.command(name="workflow")
@click.option(
    "--sanitize/--no-santize",
    default=True,
    is_flag=True,
    show_default=True,
    help="Remove all database fields from workflow objects.",
)
@click.pass_obj
def show_workflow(api, sanitize):
    """Show the workflow."""
    data = api.get_workflow().to_dict()
    if sanitize:
        sanitize_workflow(data)
    print(json.dumps(data, indent=2))


@click.command()
@click.pass_obj
def example_workflow(api):
    """Show the example workflow."""
    text = api.get_workflow_example().to_dict()
    print(json.dumps(text, indent=2))


show.add_command(events)
show.add_command(jobs)
show.add_command(process_stats)
show.add_command(resource_stats)
show.add_command(results)
show.add_command(show_workflow)
show.add_command(example_workflow)
