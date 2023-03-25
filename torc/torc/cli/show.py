"""CLI commands to show items from the database."""

import logging
from pprint import pprint

import click

from torc.api import iter_documents, remove_db_keys
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
@click.argument("workflow_key")
@click.pass_obj
def events(api, workflow_key):
    """Show jobs stored in the workflow."""
    for event in api.get_events_workflow(workflow_key).items:
        pprint(remove_db_keys(event))


@click.command()
@click.argument("workflow_key")
@click.pass_obj
def files(api, workflow_key):
    """Show files stored in the workflow."""
    exclude = ("key", "id", "rev")
    table = make_text_table(
        (x.to_dict() for x in iter_documents(api.get_files_workflow, workflow_key)),
        "Files",
        exclude_columns=exclude,
    )
    if table.rows:
        print(table)
    else:
        print("No files are stored")


@click.command()
@click.argument("workflow_key")
@click.pass_obj
def process_stats(api, workflow_key):
    """Show per-job process resource statistics from a workflow run."""
    table = make_text_table(
        iter_job_process_stats(api, workflow_key), "Job Process Resource Utilization Statistics"
    )
    if table.rows:
        print(table)
    else:
        print("No stats are stored")


@click.command()
@click.argument("workflow_key")
@click.option(
    "-x",
    "--exclude-process",
    default=False,
    is_flag=True,
    show_default=True,
    help="Exclude job process stats (show compute node stats only).",
)
@click.pass_obj
def resource_stats(api, workflow_key, exclude_process):
    """Show resource statistics from a workflow run."""
    for table in make_compute_node_stats_text_tables(
        api, workflow_key, exclude_process=exclude_process
    ).values():
        print(table)


@click.command()
@click.argument("workflow_key")
@click.pass_obj
def results(api, workflow_key):
    """Show jobs stored in the workflow."""
    exclude = ("key", "id", "rev")
    table = make_text_table(
        (x.to_dict() for x in iter_documents(api.get_results_workflow, workflow_key)),
        "Results",
        exclude_columns=exclude,
    )
    if table.rows:
        print(table)
    else:
        print("No results are available")


show.add_command(events)
show.add_command(files)
show.add_command(process_stats)
show.add_command(resource_stats)
show.add_command(results)
