"""CLI commands to show items from the database."""

import logging

import click

from torc.resource_monitor.reports import (
    make_compute_node_stats_text_tables,
)
from .common import get_workflow_key_from_context, setup_cli_logging


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
    """Show resource statistics from a workflow run."""
    workflow_key = get_workflow_key_from_context(ctx, api)
    for table in make_compute_node_stats_text_tables(
        api, workflow_key, exclude_process=exclude_process
    ).values():
        print(table)


compute_nodes.add_command(list_resource_stats)
