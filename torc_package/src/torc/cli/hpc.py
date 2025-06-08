"""HPC CLI commands"""

import rich_click as click

from .slurm import slurm


@click.group()
def hpc():
    """HPC commands"""


hpc.add_command(slurm)
