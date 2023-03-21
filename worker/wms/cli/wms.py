"""Entry point for CLI commands"""

import logging

import click

from wms.api import make_api
from wms.cli.export import export
from wms.cli.hpc import hpc
from wms.cli.local import local
from wms.cli.show import show
from wms.cli.workflow import workflow
from wms.utils.timing import timer_stats_collector


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
    default=True,
    is_flag=True,
    show_default=True,
    help="Enable tracking of function timings.",
)
@click.option(
    "-u",
    "--database-url",
    type=str,
    required=True,
    envvar="WMS_DATABASE_URL",
    help="Database URL. Ex: http://localhost:8529/_db/workflows/wms-service",
)
@click.pass_context
def cli(ctx, console_level, file_level, timings, database_url):  # pylint: disable=unused-argument
    """wms commands"""
    if timings:
        timer_stats_collector.enable()
    ctx.obj = make_api(database_url)


cli.add_command(export)
cli.add_command(hpc)
cli.add_command(local)
cli.add_command(show)
cli.add_command(workflow)
