"""Entry point for CLI commands"""

import logging

import click

from torc.api import make_api
from torc.cli.export import export
from torc.cli.hpc import hpc
from torc.cli.jobs import jobs
from torc.cli.local import local
from torc.cli.show import show
from torc.cli.workflows import workflows
from torc.utils.timing import timer_stats_collector


def _get_log_level_from_str(*args):
    level = args[2]
    match level:
        case "debug":
            return logging.DEBUG
        case "info":
            return logging.INFO
        case "warning":
            return logging.WARNING
        case "error":
            return logging.ERROR
        case _:
            raise Exception(f"Unsupported level={level}")


@click.group()
@click.option(
    "-c",
    "--console-level",
    default="info",
    show_default=True,
    help="Console log level.",
    callback=_get_log_level_from_str,
)
@click.option(
    "-f",
    "--file-level",
    default="info",
    show_default=True,
    help="File log level.",
    callback=_get_log_level_from_str,
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
    required=True,
    envvar="TORC_DATABASE_URL",
    help="Database URL. Ex: http://localhost:8529/_db/workflows/torc-service",
)
@click.pass_context
def cli(ctx, console_level, file_level, timings, database_url):  # pylint: disable=unused-argument
    """torc commands"""
    if timings:
        timer_stats_collector.enable()
    else:
        timer_stats_collector.disable()
    ctx.obj = make_api(database_url)


@cli.result_callback()
def callback(*args, **kwargs):  # pylint: disable=unused-argument
    """Log timer stats at exit."""
    timer_stats_collector.log_stats()


cli.add_command(export)
cli.add_command(hpc)
cli.add_command(jobs)
cli.add_command(local)
cli.add_command(show)
cli.add_command(workflows)
