"""CLI commands to manage the torc runtime configuration"""

import logging

import click

from torc.torc_rc import TorcRuntimeConfig


logger = logging.getLogger(__name__)


@click.group()
def config():
    """Config commands"""


@click.command()
@click.option(
    "-F",
    "--output-format",
    default="text",
    type=click.Choice(["text", "json"]),
    show_default=True,
    help="Output format for get/list commands. Not all commands support all formats.",
)
@click.option(
    "-f",
    "--filter-workflows-by-user",
    is_flag=True,
    default=False,
    show_default=True,
    help="Whether to filter workflows by the current user",
)
@click.option(
    "-k",
    "--workflow-key",
    type=str,
    default=None,
    help="Workflow key. " "User will be prompted if it is missing unless --no-prompts is set.",
)
@click.option(
    "--timings/--no-timings",
    default=False,
    is_flag=True,
    show_default=True,
    help="Enable tracking of function timings.",
)
@click.option(
    "-u",
    "--database-url",
    type=str,
    default=None,
    help="Database URL. Note the database name in this example: "
    "http://localhost:8529/_db/database_name/torc-service",
)
@click.option(
    "--console-level",
    default="info",
    show_default=True,
    help="Console log level.",
)
@click.option(
    "--file-level",
    default="info",
    show_default=True,
    help="File log level.",
)
def create(
    output_format,
    filter_workflows_by_user,
    workflow_key,
    timings,
    database_url,
    console_level,
    file_level,
):
    """Create a local torc runtime configuration file."""
    torc_config = TorcRuntimeConfig(
        output_format=output_format,
        filter_workflows_by_user=filter_workflows_by_user,
        workflow_key=workflow_key,
        timings=timings,
        database_url=database_url,
        console_level=console_level,
        file_level=file_level,
    )
    torc_config.dump()


config.add_command(create)
