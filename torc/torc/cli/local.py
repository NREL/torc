"""CLI commands to run on a local compute node"""

import logging
import socket
from pathlib import Path

import click

from torc.job_runner import JobRunner
from .common import path_callback, setup_cli_logging


logger = logging.getLogger(__name__)


@click.group()
def local():
    """Local compute node commands"""


@click.command()
@click.option(
    "-o",
    "--output",
    default="output",
    show_default=True,
    callback=path_callback,
)
@click.pass_obj
@click.pass_context
def run_jobs(ctx, api, output: Path):
    """Run workflow jobs on a local system."""
    output.mkdir(exist_ok=True)
    hostname = socket.gethostname()
    log_file = output / f"worker_{hostname}.log"
    setup_cli_logging(ctx, 2, __name__, filename=log_file, mode="a")
    runner = JobRunner(api, output)
    runner.run_worker()


local.add_command(run_jobs)
