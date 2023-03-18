"""CLI commands to manage a workflow"""

import logging
import sys
from pathlib import Path

import click
from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration

from wms.job_runner import JobRunner
from wms.loggers import setup_logging
from wms.workflow_manager import WorkflowManager
from .common import check_output_directory


logger = logging.getLogger(__name__)


@click.group()
def workflow():
    """Workflow commands"""


@click.command()
@click.argument("database_url")
def start_workflow(database_url):
    """Start the workflow defined in the database specified by the URL."""
    setup_logging(__name__)
    configuration = Configuration()
    configuration.host = database_url
    api = DefaultApi(ApiClient(configuration))
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
    my_logger = setup_logging(__name__)
    check_output_directory(output, force)
    configuration = Configuration()
    configuration.host = database_url
    api = DefaultApi(ApiClient(configuration))

    mgr = WorkflowManager(api)
    mgr.start()
    runner = JobRunner(api, output)
    my_logger.info("Start workflow")
    runner.run_worker()


workflow.add_command(run_local)
workflow.add_command(start_workflow)
