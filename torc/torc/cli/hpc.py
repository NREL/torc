"""HPC CLI commands"""

import json
import logging
import math
import sys

import click

from torc.loggers import setup_logging
from .common import check_database_url, get_output_format_from_context
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
@click.pass_context
def recommend_nodes(ctx, api, num_cpus):
    """Recommend nodes to schedule."""
    setup_logging(__name__)
    check_database_url(api)
    output_format = get_output_format_from_context(ctx)
    reqs = api.get_workflow_ready_job_requirements()
    if reqs.num_jobs == 0:
        logger.error("No jobs are stored")
        sys.exit(1)
    num_nodes_by_cpus = math.ceil(reqs.num_cpus / num_cpus)
    if output_format == "text":
        print(f"Requirements for jobs in the ready state: \n{reqs}")
        print(f"Based on CPUs, number of required nodes = {num_nodes_by_cpus}")
    else:
        print(json.dumps({"ready_job_requirements": reqs, "num_nodes_by_cpus": num_nodes_by_cpus}))


hpc.add_command(recommend_nodes)
hpc.add_command(slurm)
