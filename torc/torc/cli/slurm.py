"""SLURM CLI commands"""

import logging
import socket
import sys
from datetime import timedelta

import click
from swagger_client.models.slurm_schedulers_workflow_model import SlurmSchedulersWorkflowModel
from swagger_client.models.scheduled_compute_nodes_workflow_model import (
    ScheduledComputeNodesWorkflowModel,
)

from torc.api import iter_documents, remove_db_keys
from torc.hpc.common import HpcType
from torc.hpc.hpc_manager import HpcManager
from torc.hpc.slurm_interface import SlurmInterface
from torc.job_runner import JobRunner, convert_end_time_to_duration_str
from torc.utils.run_command import get_cli_string
from .common import make_text_table, setup_cli_logging, path_callback


logger = logging.getLogger(__name__)


@click.group()
def slurm():
    """SLURM commands"""


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
@click.option("-k", "--workflow-key", type=str, required=True, help="Workflow key")
@click.pass_obj
@click.pass_context
def add_config(
    ctx, api, name, account, gres, mem, nodes, partition, qos, tmp, walltime, workflow_key
):
    """Add a SLURM config to the database."""
    setup_cli_logging(ctx, 3, __name__)
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
    api.post_slurm_schedulers_workflow(
        SlurmSchedulersWorkflowModel(name=name, **config), workflow_key
    )
    logger.info("Added SLURM configuration %s to database", name, file=sys.stderr)


@click.command()
@click.option("-k", "--workflow-key", type=str, required=True, help="Workflow key")
@click.pass_obj
@click.pass_context
def list_configs(ctx, api, workflow_key):
    """Show the current SLURM configs in the database."""
    setup_cli_logging(ctx, 3, __name__)
    items = (x.to_dict() for x in iter_documents(api.get_slurm_schedulers_workflow, workflow_key))
    table = make_text_table(items, "SLURM Configurations", exclude_columns=["id", "rev"])
    if table.rows:
        print(table)
    else:
        logger.info("There are no SLURM configurations")


@click.command()
@click.argument("scheduler-config-key")
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
@click.option("-k", "--workflow-key", type=str, required=True, help="Workflow key")
@click.pass_obj
@click.pass_context
def schedule_nodes(ctx, api, scheduler_config_key, job_prefix, num_hpc_jobs, output, workflow_key):
    """Schedule nodes with SLURM to run jobs."""
    # TODO: if workflow isn't started, start it?
    setup_cli_logging(ctx, 3, __name__)
    logger.info(get_cli_string())
    output.mkdir(exist_ok=True)
    config = api.get_slurm_schedulers_workflow_key(workflow_key, scheduler_config_key)
    data = remove_db_keys(config.to_dict())
    data.pop("name")
    hpc_type = HpcType("slurm")
    mgr = HpcManager(data, hpc_type, output)
    database_url = api.api_client.configuration.host
    runner_script = f"torc -u {database_url} hpc slurm run-jobs -k {workflow_key}"
    job_ids = []
    for _ in range(num_hpc_jobs):
        node = api.post_scheduled_compute_nodes_workflow(
            ScheduledComputeNodesWorkflowModel(
                scheduler_config_id=config.id, status="uninitialized"
            ),
            workflow_key,
        )
        name = f"{job_prefix}_{node.key}"
        try:
            # TODO: keep_submission_script false
            job_id = mgr.submit(output, name, runner_script, keep_submission_script=True)
        except Exception:
            api.delete_scheduled_compute_nodes_workflow_key(node.key)
            raise

        node.scheduler_id = job_id
        node.status = "pending"
        api.put_scheduled_compute_nodes_workflow_key(node, workflow_key, node.key)
        job_ids.append(job_id)

    api.post_events_workflow(
        {
            "category": "scheduler",
            "type": "submit",
            "num_jobs": len(job_ids),
            "job_ids": job_ids,
            "scheduler_config_id": config.id,
            "message": f"Submitted {len(job_ids)} job requests to {hpc_type.value}",
        },
        workflow_key,
    )


@click.command()
@click.option(
    "-o",
    "--output",
    default="output",
    show_default=True,
    callback=path_callback,
)
@click.option("-k", "--workflow-key", type=str, required=True, help="Workflow key")
@click.pass_obj
@click.pass_context
def run_jobs(ctx, api, output, workflow_key):
    """Run workflow jobs on a SLURM compute node."""
    intf = SlurmInterface()
    slurm_job_id = intf.get_current_job_id()
    hostname = socket.gethostname()
    log_file = output / f"slurm_runner_{hostname}_{slurm_job_id}.log"
    my_logger = setup_cli_logging(ctx, 3, __name__, filename=log_file)
    my_logger.info(get_cli_string())
    my_logger.info("Run jobs on %s for workflow %s", hostname, api.api_client.configuration.host)
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
    nodes = api.get_scheduled_compute_nodes_workflow(workflow_key, scheduler_id=slurm_job_id).items
    num_nodes = len(nodes)
    if num_nodes == 0:
        node = None
        scheduler_config_id = None
    elif num_nodes == 1:
        node = nodes[0]
        scheduler_config_id = node.scheduler_config_id
    else:
        raise Exception(f"num_nodes with {slurm_job_id=} cannot be {num_nodes=}")

    workflow = api.get_workflows_key(workflow_key)
    runner = JobRunner(
        api,
        workflow,
        output,
        time_limit=time_limit,
        scheduler_config_id=scheduler_config_id,
    )

    if node is not None:
        node.status = "active"
        node = api.put_scheduled_compute_nodes_workflow_key(node, workflow_key, node.key)

    my_logger.info("Start workflow on compute node %s", hostname)
    runner.run_worker(scheduler=scheduler)

    if node is not None:
        node.status = "complete"
        api.put_scheduled_compute_nodes_workflow_key(node, workflow_key, node.key)
    # TODO: schedule more nodes if needed


slurm.add_command(add_config)
slurm.add_command(list_configs)
slurm.add_command(run_jobs)
slurm.add_command(schedule_nodes)
