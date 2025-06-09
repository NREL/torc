"""CLI commands for exporting workflows from the database"""

import re
from pathlib import Path

import rich_click as click
from loguru import logger

from torc.utils.sql import union_tables
from .common import setup_cli_logging


@click.group()
@click.pass_context
def stats(ctx):
    """Stats commands"""
    setup_cli_logging(ctx, __name__)


@click.command()
@click.argument("output_dir", type=click.Path(exists=True), callback=lambda *x: Path(x[2]))
def concatenate_process(output_dir):
    """Concatenate job process stats from all compute nodes into one file.
    output_dir must be the directory that contains the existing .sqlite files."""
    regex = re.compile(r"^compute_node_(\d+)\.sqlite$")
    files = []
    for path in output_dir.iterdir():
        match = regex.search(path.name)
        if match:
            files.append(path)

    if files:
        concat_file = output_dir / "job_process_stats.sqlite"
        for path in files:
            union_tables(concat_file, path, tables=["process"])
    else:
        logger.warning("There are no SQLite stats files in {}", output_dir)


stats.add_command(concatenate_process)
