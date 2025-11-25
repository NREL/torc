"""Entry point for CLI commands."""

import rich_click as click

import torc
from torc.cli.run_function import run_function
from torc.cli.run_postprocess import run_postprocess


@click.group()
@click.version_option(version=torc.__version__)
def cli():
    """Run pytorc commands."""


cli.add_command(run_function)
cli.add_command(run_postprocess)
