"""HPC CLI commands"""

import logging

import click

from .slurm import slurm


logger = logging.getLogger(__name__)


@click.group()
def hpc():
    """HPC commands"""


hpc.add_command(slurm)
