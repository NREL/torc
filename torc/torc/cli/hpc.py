"""HPC CLI commands"""

import logging
import math
import sys

import click

from torc.loggers import setup_logging
from .slurm import slurm


logger = logging.getLogger(__name__)


@click.group()
def hpc():
    """HPC commands"""


@click.command()
@click.option(
    "-c",
    "--num-cpus",
    type=int,
    default=36,
    help="Number of CPUs per node",
    show_default=True,
)
@click.pass_obj
def recommend_nodes(api, num_cpus):
    """Schedule nodes to run jobs.."""
    setup_logging(__name__)
    reqs = api.get_workflow_ready_job_requirements()
    if reqs.num_jobs == 0:
        print("Error: no jobs are available", file=sys.stderr)
        sys.exit(1)
    num_nodes_by_cpus = math.ceil(reqs.num_cpus / num_cpus)
    print(f"Requirements for jobs in the ready state: \n{reqs}")
    print(f"Based on CPUs, number of required nodes = {num_nodes_by_cpus}")


hpc.add_command(recommend_nodes)
hpc.add_command(slurm)
