import logging
import sys

import click
from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration

from wms.loggers import setup_logging
from wms.workflow_manager import WorkflowManager


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
    print("not implemented yet")
    sys.exit(1)


workflow.add_command(start_workflow)
