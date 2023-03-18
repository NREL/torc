"""CLI commands to manage a workflow"""

import logging
import sys
from pathlib import Path

import click
from prettytable import PrettyTable

from wms.api import make_api
from wms.job_runner import JobRunner
from wms.loggers import setup_logging
from wms.resource_monitor.reports import (
    iter_job_process_stats,
    make_compute_node_stats_text_tables,
)
from wms.workflow_manager import WorkflowManager
from .common import check_output_directory


logger = logging.getLogger(__name__)


@click.group()
def workflow():
    """Workflow commands"""


@click.command()
@click.argument("database_url")
def start(database_url):
    """Start the workflow defined in the database specified by the URL."""
    setup_logging(__name__)
    api = make_api(database_url)
    mgr = WorkflowManager(api)
    mgr.start()
    # TODO: This could schedule nodes.


@click.command()
@click.argument("database_url")
def cancel(database_url):
    """Cancel all jobs that are currently active in the workflow."""
    # TODO: find active nodes by scheduler type and send cancel commands
    print(f"Cannot cancel {database_url}: not implemented yet:")
    sys.exit(1)


@click.command()
@click.option(
    "-o",
    "--output",
    default="output",
    show_default=True,
    callback=lambda *x: Path(x[2]),
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    show_default=True,
    help="Overwrite directory if it exists.",
)
@click.argument("database_url")
def run_local(database_url, output, force):
    """Run workflow jobs on a local system."""
    setup_logging(__name__)
    check_output_directory(output, force)
    api = make_api(database_url)

    mgr = WorkflowManager(api)
    mgr.start()
    runner = JobRunner(api, output)
    runner.run_worker()


@click.command()
@click.argument("database_url")
def show_process_stats(database_url):
    """Show per-job process resource statistics from a workflow run."""
    api = make_api(database_url)
    table = PrettyTable(title="Job Process Resource Utilization Statistics")
    found_first = False
    for stats in iter_job_process_stats(api):
        if not found_first:
            table.field_names = tuple(stats.keys())
            found_first = True
        table.add_row(stats.values())
    print(table)


@click.command()
@click.option(
    "-x",
    "--exclude-process",
    default=False,
    is_flag=True,
    show_default=True,
    help="Exclude job process stats (show compute node stats only).",
)
@click.argument("database_url")
def show_resource_stats(database_url, exclude_process):
    """Show resource statistics from a workflow run."""
    api = make_api(database_url)
    for table in make_compute_node_stats_text_tables(
        api, exclude_process=exclude_process
    ).values():
        print(table)


workflow.add_command(run_local)
workflow.add_command(show_process_stats)
workflow.add_command(show_resource_stats)
workflow.add_command(start)
