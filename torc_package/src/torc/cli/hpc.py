"""HPC CLI commands"""

import click

from .slurm import slurm


@click.group()
def hpc():
    """HPC commands"""


hpc.add_command(slurm)
