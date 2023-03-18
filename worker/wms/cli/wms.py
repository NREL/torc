"""Entry point for CLI commands"""

import logging
from pathlib import Path

import click

from wms.loggers import setup_logging
from wms.cli.export import export
from wms.cli.hpc import hpc
from wms.cli.workflow import workflow


@click.group()
@click.option("-l", "--log-file", type=Path, default="wms.log", help="Log to this file.")
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    show_default=True,
    help="Enable verbose log output.",
)
def cli(log_file, verbose):
    """wms commands"""
    path = Path(log_file)
    level = logging.DEBUG if verbose else logging.INFO
    setup_logging("dsgrid", path, console_level=level, file_level=level, mode="w")


cli.add_command(export)
cli.add_command(hpc)
cli.add_command(workflow)
