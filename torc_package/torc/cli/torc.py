"""Entry point for CLI commands"""

import logging
import sys

import click

import torc.version
from torc.api import make_api
from torc.cli.common import get_log_level_from_str
from torc.cli.collections import collections
from torc.cli.compute_nodes import compute_nodes
from torc.cli.config import config
from torc.cli.events import events
from torc.cli.export import export
from torc.cli.files import files
from torc.cli.graphs import graphs
from torc.cli.hpc import hpc
from torc.cli.jobs import jobs
from torc.cli.resource_requirements import resource_requirements
from torc.cli.results import results
from torc.cli.stats import stats
from torc.cli.user_data import user_data
from torc.cli.workflows import workflows
from torc.common import timer_stats_collector
from torc.torc_rc import TorcRuntimeConfig


logger = logging.getLogger(__name__)
_config = TorcRuntimeConfig.load()


def _show_version(*args):
    version = args[2]
    if version:
        print(f"torc version {torc.version.__version__}")
        sys.exit(0)
    return version


@click.group()
@click.option(
    "-c",
    "--console-level",
    default=_config.console_level,
    show_default=True,
    help="Console log level.",
)
@click.option(
    "-f",
    "--file-level",
    default=_config.file_level,
    show_default=True,
    help="File log level.",
)
@click.option(
    "-k",
    "--workflow-key",
    type=str,
    default=_config.workflow_key,
    envvar="TORC_WORKFLOW_KEY",
    help="Workflow key, required for many commands. "
    "User will be prompted if it is missing unless --no-prompts is set.",
)
@click.option(
    "-n",
    "--no-prompts",
    default=False,
    is_flag=True,
    show_default=True,
    help="Disable all user prompts.",
)
@click.option(
    "-F",
    "--output-format",
    default=_config.output_format,
    type=click.Choice(["text", "json"]),
    show_default=True,
    help="Output format for get/list commands. Not all commands support all formats.",
)
@click.option(
    "--timings/--no-timings",
    default=_config.timings,
    is_flag=True,
    show_default=True,
    help="Enable tracking of function timings.",
)
@click.option(
    "-u",
    "--database-url",
    type=str,
    default=_config.database_url,
    envvar="TORC_DATABASE_URL",
    help="Database URL. Ex: http://localhost:8529/_db/workflows/torc-service",
)
@click.option(
    "--version",
    callback=_show_version,
    is_flag=True,
    show_default=True,
    help="Show version and exit",
)
@click.pass_context
def cli(
    ctx,
    console_level,
    file_level,
    workflow_key,
    no_prompts,
    output_format,
    timings,
    database_url,
    version,
):  # pylint: disable=unused-argument
    """torc commands"""
    if timings:
        timer_stats_collector.enable()
    else:
        timer_stats_collector.disable()
    ctx.params["console_level"] = get_log_level_from_str(console_level)
    ctx.params["file_level"] = get_log_level_from_str(file_level)
    if database_url:
        ctx.obj = make_api(database_url)


@cli.result_callback()
@click.pass_obj
def callback(api, *args, **kwargs):  # pylint: disable=unused-argument
    """Log timer stats at exit."""
    timer_stats_collector.log_stats()
    if api is not None:
        api.api_client.close()


cli.add_command(collections)
cli.add_command(compute_nodes)
cli.add_command(config)
cli.add_command(events)
cli.add_command(export)
cli.add_command(files)
cli.add_command(graphs)
cli.add_command(hpc)
cli.add_command(jobs)
cli.add_command(resource_requirements)
cli.add_command(results)
cli.add_command(stats)
cli.add_command(user_data)
cli.add_command(workflows)
