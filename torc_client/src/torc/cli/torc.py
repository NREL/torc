"""Entry point for CLI commands"""

import getpass

import rich_click as click

import torc
from torc.api import make_api
from torc.cli.collections import collections
from torc.cli.compute_nodes import compute_nodes
from torc.cli.config import config
from torc.cli.events import events
from torc.cli.export import export
from torc.cli.files import files
from torc.cli.graphs import graphs
from torc.cli.hpc import hpc
from torc.cli.jobs import jobs
from torc.cli.reports import reports
from torc.cli.resource_requirements import resource_requirements
from torc.cli.results import results
from torc.cli.stats import stats
from torc.cli.tui import tui
from torc.cli.user_data import user_data
from torc.cli.workflows import workflows
from torc.common import timer_stats_collector
from torc.config import torc_settings


@click.group()
@click.option(
    "-c",
    "--console-level",
    help="Console log level.",
)
@click.option(
    "-f",
    "--file-level",
    help="File log level. Set to 'trace' for increased verbosity.",
)
@click.option(
    "-k",
    "--workflow-key",
    type=str,
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
    type=click.Choice(["text", "csv", "json"]),
    help="Output format for get/list commands. Not all commands support all formats.",
)
@click.option(
    "--timings",
    type=click.Choice(["true", "false"]),
    help="Enable tracking of function timings.",
)
@click.option(
    "-U",
    "--user",
    default=getpass.getuser(),
    show_default=True,
    type=str,
    help="Username",
)
@click.option(
    "-u",
    "--database-url",
    type=str,
    envvar="TORC_DATABASE_URL",
    help="Database URL. Ex: http://localhost:8529/_db/workflows/torc-service",
)
@click.version_option(
    version=torc.__version__,
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
    user,
    database_url,
):
    """torc commands"""
    for param in (
        "console_level",
        "file_level",
        "database_url",
        "output_format",
        "workflow_key",
    ):
        if ctx.params[param] is None:
            ctx.params[param] = getattr(torc_settings, param)

    if timings is None:
        ctx.params["timings"] = torc_settings.timings
    else:
        ctx.params["timings"] = timings == "true"

    if ctx.params["timings"]:
        timer_stats_collector.enable()
    else:
        timer_stats_collector.disable()
    ctx.params["console_level"] = ctx.params["console_level"].upper()
    ctx.params["file_level"] = ctx.params["file_level"].upper()
    if ctx.params["database_url"]:
        ctx.obj = make_api(ctx.params["database_url"])


@cli.result_callback()
@click.pass_obj
def callback(api, *args, **kwargs):
    """Log timer stats at exit."""
    if timer_stats_collector.is_enabled:
        timer_stats_collector.log_stats()
        # TODO
        # timer_file = path.parent / f"{path.stem}_timer_stats.json"
        # timer_stats_collector.log_json_stats(timer_file)


cli.add_command(collections)
cli.add_command(compute_nodes)
cli.add_command(config)
cli.add_command(events)
cli.add_command(export)
cli.add_command(files)
cli.add_command(graphs)
cli.add_command(hpc)
cli.add_command(jobs)
cli.add_command(reports)
cli.add_command(resource_requirements)
cli.add_command(results)
cli.add_command(stats)
cli.add_command(tui)
cli.add_command(user_data)
cli.add_command(workflows)
