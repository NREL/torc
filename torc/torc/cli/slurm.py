"""SLURM CLI commands"""

import logging
import socket
import sys
from datetime import timedelta

import click
from swagger_client.models.slurm_schedulers_model import SlurmSchedulersModel
from swagger_client.models.scheduled_compute_nodes_model import (
    ScheduledComputeNodesModel,
)

from torc.api import iter_documents, remove_db_keys
from torc.hpc.common import HpcType
from torc.hpc.hpc_manager import HpcManager
from torc.hpc.slurm_interface import SlurmInterface
from torc.job_runner import JobRunner, convert_end_time_to_duration_str
from torc.loggers import setup_logging
from torc.utils.run_command import get_cli_string
from .common import make_text_table, setup_cli_logging, path_callback


logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def slurm(ctx):
    """SLURM commands"""
    setup_cli_logging(ctx, 2, __name__)


@click.command()
@click.option(
    "-N",
    "--name",
    required=True,
    type=str,
    help="Name to use as a primary key in the database",
)
@click.option(
    "-a",
    "--account",
    required=True,
    type=str,
    help="HPC account",
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
@click.pass_obj
def add_config(api, name, account, gres, mem, nodes, partition, qos, tmp, walltime):
    """Add a SLURM config to the database."""
    config = {
        "account": account,
        "gres": gres,
        "mem": mem,
        "nodes": nodes,
        "qos": qos,
        "partition": partition,
        "tmp": tmp,
        "walltime": walltime,
    }
    api.post_slurm_schedulers(SlurmSchedulersModel(name=name, **config))
    print(f"Added SLURM configuration {name} to database", file=sys.stderr)


@click.command()
@click.pass_obj
def show_configs(api):
    """Show the current SLURM configs in the database."""
    items = (x.to_dict() for x in iter_documents(api.get_slurm_schedulers))
    table = make_text_table(items, "SLURM Configurations", exclude_columns=["key", "rev"])
    if table.rows:
        print(table)
    else:
        print("There are no SLURM configurations", file=sys.stderr)


@click.command()
@click.argument("scheduler-config-id")
@click.option(
    "-i",
    "--index",
    default=1,
    show_default=True,
    help="Starting index for HPC job names",
)
@click.option(
    "-j",
    "--job-prefix",
    default="job",
    type=str,
    show_default=True,
    help="Prefix for HPC job names",
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
    callback=path_callback,
)
@click.pass_obj
@click.pass_context
def schedule_nodes(ctx, api, scheduler_config_id, index, job_prefix, num_hpc_jobs, output):
    """Schedule nodes with SLURM to run jobs."""
    # TODO: if workflow isn't started, start it?
    logger.info(get_cli_string())
    output.mkdir(exist_ok=True)
    fields = scheduler_config_id.split("/")
    if len(fields) != 2:
        logger.info("Invalid scheduler ID format: %s", scheduler_config_id)
        sys.exit(1)
    scheduler_type, key = fields
    if scheduler_type != "slurm_schedulers":
        logger.info("Invalid database collection name: %s", scheduler_type)
        sys.exit(1)

    config = remove_db_keys(api.get_slurm_schedulers_key(key).to_dict())
    config.pop("name")
    hpc_type = HpcType("slurm")
    mgr = HpcManager(config, hpc_type, output)
    database_url = ctx.parent.parent.parent.params["database_url"]
    runner_script = f"torc -u {database_url} hpc slurm run-jobs"
    job_ids = []
    for i in range(index, num_hpc_jobs + 1):
        name = f"{job_prefix}_{i}"
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
            "message": f"Submitted {len(job_ids)} job requests to {hpc_type.value}",
        }
    )


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
def run_jobs(ctx, api, output):
    """Run workflow jobs on a SLURM compute node."""
    # TODO: make unique
    hostname = socket.gethostname()
    filename = output / f"slurm_runner_{hostname}.log"
    my_logger = setup_logging(__name__, filename=filename, mode="a")
    my_logger.info(get_cli_string())
    my_logger.info(
        "Run jobs on %s for workflow %s", hostname, ctx.obj.api_client.configuration.host
    )
    intf = SlurmInterface()
    slurm_job_id = intf.get_current_job_id()
    scheduler = {
        "node_names": intf.list_active_nodes(slurm_job_id),
        "environment_variables": intf.get_environment_variables(),
        "scheduler_type": "hpc",
        "slurm_job_id": slurm_job_id,
        "hpc_type": HpcType.SLURM.value,
    }
    buffer = timedelta(minutes=2)
    end_time = intf.get_job_end_time() - buffer
    time_limit = convert_end_time_to_duration_str(end_time)
    # scheduled_compute_node = api.get_scheduled_compute_nodes_key(slurm_job_id)
    runner = JobRunner(
        api,
        output,
        time_limit=time_limit,
        # scheduler_config_id=scheduled_compute_node.scheduler_config_id,
    )
    # node = api.get_scheduled_compute_nodes_key(slurm_job_id)
    # node.status = "active"
    # node = api.put_scheduled_compute_nodes_key(node, slurm_job_id)
    my_logger.info("Start workflow on compute node %s", socket.gethostname())
    runner.run_worker(scheduler=scheduler)
    # node.status = "complete"
    # node = api.put_scheduled_compute_nodes_key(node, slurm_job_id)
    # TODO: schedule more nodes if needed


slurm.add_command(add_config)
slurm.add_command(run_jobs)
slurm.add_command(schedule_nodes)
slurm.add_command(show_configs)
