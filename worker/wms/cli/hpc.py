"""HPC CLI commands"""

import logging
import math
import sys
from pathlib import Path

import click

from swagger_client.models.scheduled_compute_nodes_model import (
    ScheduledComputeNodesModel,
)

from wms.api import make_api, remove_db_keys
from wms.hpc.hpc_manager import HpcManager
from wms.loggers import setup_logging
from wms.utils.files import dump_data
from .common import check_output_directory
from .slurm_runner import slurm_runner


logger = logging.getLogger(__name__)


@click.group()
def hpc():
    """HPC commands"""


@click.command()
@click.argument("account")
@click.option(
    "-f",
    "--filename",
    default="hpc_config.json5",
    show_default=True,
    help="Config file",
    callback=lambda *x: Path(x[2]),
)
@click.option(
    "-g",
    "--gres",
    type=str,
    help="Request nodes that have at least this number of GPUs. Ex: 'gpu:2'",
)
@click.option(
    "-m",
    "--mem",
    type=str,
    help="Request nodes that have at least this amount of memory. Ex: '180G'",
)
@click.option(
    "-n",
    "--nodes",
    type=int,
    default=1,
    show_default=True,
    help="Number of nodes to use for each job",
)
@click.option("-p", "--partition", help="HPC partition. Default is determinted by the scheduler")
@click.option(
    "-q",
    "--qos",
    default="normal",
    show_default=True,
    help="Controls priority of the jobs.",
)
@click.option(
    "-t",
    "--tmp",
    type=str,
    help="Request nodes that have at least this amount of storage scratch space.",
)
@click.option("-w", "--walltime", default="04:00:00", show_default=True, help="Per-node walltime.")
def slurm_config(account, filename, gres, mem, nodes, partition, qos, tmp, walltime):
    """Create a SLURM config file."""
    config = {
        "hpc_type": "slurm",
        "job_prefix": "node",
        "hpc": {
            "account": account,
            "gres": gres,
            "mem": mem,
            "nodes": nodes,
            "qos": qos,
            "partition": partition,
            "tmp": tmp,
            "walltime": walltime,
        },
    }
    dump_data(config, filename, indent=2)
    print(f"Created SLURM configuration in {filename}", file=sys.stderr)


@click.command()
@click.option(
    "-c",
    "--num-cpus",
    type=int,
    default=36,
    help="Number of CPUs per node",
    show_default=True,
)
@click.argument("database_url")
def recommend_nodes(database_url: str, num_cpus):
    """Schedule nodes to run jobs.."""
    setup_logging(__name__)
    api = make_api(database_url)
    reqs = api.get_workflow_ready_job_requirements()
    if reqs.num_jobs == 0:
        print("Error: no jobs are available", file=sys.stderr)
        sys.exit(1)
    num_nodes_by_cpus = math.ceil(reqs.num_cpus / num_cpus)
    print(f"Requirements for jobs in the ready state: \n{reqs}")
    print(f"Based on CPUs, number of required nodes = {num_nodes_by_cpus}")


@click.command()
@click.option(
    "-i",
    "--index",
    default=1,
    show_default=True,
    help="Starting index for HPC job names",
)
@click.option(
    "-n",
    "--num-hpc-jobs",
    type=int,
    required=True,
    help="Number of HPC jobs to schedule",
)
@click.option(
    "-o",
    "--output",
    default="output",
    show_default=True,
    help="Output directory for compute nodes",
    callback=lambda *x: Path(x[2]),
)
@click.option(
    "-s",
    "--scheduler-config-id",
    type=str,
    required=True,
    help="Scheduler config ID",
)
@click.option(
    "-u",
    "--database-url",
    type=str,
    required=True,
    envvar="WMS_DATABASE_URL",
    help="Database URL",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    show_default=True,
    help="Overwrite files if they exist.",
)
def schedule_slurm_nodes(index, num_hpc_jobs, output, scheduler_config_id, database_url, force):
    """Schedule nodes to run jobs."""
    filename = output / f"slurm_scheduler_{scheduler_config_id}.log"
    my_logger = setup_logging(__name__, filename=filename, mode="a")

    check_output_directory(output, force)
    api = make_api(database_url)
    setup_logging(__name__)

    fields = scheduler_config_id.split("/")
    if len(fields) != 2:
        my_logger.error("Invalid scheduler ID format: %s", scheduler_config_id)
        sys.exit(1)
    if fields[0] != "slurm_schedulers":
        my_logger.error("Invalid database collection name: %s", fields[0])
        sys.exit(1)

    config = remove_db_keys(api.get_slurm_schedulers_key(fields[1]).to_dict())
    config["hpc_type"] = "slurm"
    mgr = HpcManager(config, output)
    runner_script = f"wms hpc slurm-runner {database_url}"
    job_ids = []
    for i in range(index, num_hpc_jobs + 1):
        name = config["job_prefix"] + "_" + str(i)
        job_id = mgr.submit(output, name, runner_script, keep_submission_script=True)
        job_ids.append(job_id)
        api.post_scheduled_compute_nodes(
            ScheduledComputeNodesModel(
                scheduler_id=job_id, scheduler_config_id=scheduler_config_id, status="pending"
            )
        )

    api.post_events(
        {
            "category": "scheduler",
            "type": "submit",
            "num_jobs": len(job_ids),
            "job_ids": job_ids,
            "scheduler_config_id": scheduler_config_id,
            "message": f"Submitted {len(job_ids)} job requests to {config['hpc_type']}",
        }
    )


hpc.add_command(recommend_nodes)
hpc.add_command(schedule_slurm_nodes)
hpc.add_command(slurm_config)
hpc.add_command(slurm_runner)
