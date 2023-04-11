"""CLI commands to show items from the database."""

import json
import logging

import click

from torc.resource_monitor.reports import (
    list_compute_node_stats,
    make_compute_node_stats_text_tables,
)
from .common import (
    check_database_url,
    get_output_format_from_context,
    get_workflow_key_from_context,
    setup_cli_logging,
)


logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def compute_nodes(ctx):  # pylint: disable=unused-argument
    """Compute node commands"""
    setup_cli_logging(ctx, __name__)


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
@click.pass_context
def list_resource_stats(ctx, api, exclude_process):
    """Show resource statistics from a workflow run.

    \b
    Examples:
    1. List resource stats from all compute nodes in tables by resource type.
       $ torc compute-nodes list-resource-stats
    2. List resource stats from all compute nodes in JSON format -
       one array keyed by 'stats'.
       $ torc -F json compute-nodes list-resource-stats
    """
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    if output_format == "text":
        for table in make_compute_node_stats_text_tables(
            api, workflow_key, exclude_process=exclude_process
        ).values():
            print(table)
    else:
        stats = list_compute_node_stats(api, workflow_key, exclude_process=exclude_process)
        print(json.dumps({"stats": stats}))


compute_nodes.add_command(list_resource_stats)
