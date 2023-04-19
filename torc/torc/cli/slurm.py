"""Slurm CLI commands"""

import json
import logging
import socket
import sys
from datetime import timedelta

import click
from swagger_client.models.workflow_slurm_schedulers_model import (
    WorkflowSlurmSchedulersModel,
)
from swagger_client.models.workflow_scheduled_compute_nodes_model import (
    WorkflowScheduledComputeNodesModel,
)

from torc.api import iter_documents, remove_db_keys
from torc.hpc.common import HpcType
from torc.hpc.hpc_manager import HpcManager
from torc.hpc.slurm_interface import SlurmInterface
from torc.job_runner import (
    JobRunner,
    convert_end_time_to_duration_str,
    JOB_COMPLETION_POLL_INTERVAL,
)
from torc.utils.run_command import get_cli_string
from .common import (
    check_database_url,
    get_output_format_from_context,
    get_workflow_key_from_context,
    prompt_user_for_document,
    print_items,
    setup_cli_logging,
    path_callback,
)


logger = logging.getLogger(__name__)


@click.group()
def slurm():
    """Slurm commands"""


@click.command()
@click.option(
    "-N",
    "--name",
    required=True,
    type=str,
    help="Name of config",
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
@click.option(
    "-w", "--walltime", default="04:00:00", show_default=True, help="Slurm job walltime."
)
@click.pass_obj
@click.pass_context
def add_config(ctx, api, name, account, gres, mem, nodes, partition, qos, tmp, walltime):
    """Add a Slurm config to the database."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
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
    scheduler = api.post_workflows_workflow_slurm_schedulers(
        WorkflowSlurmSchedulersModel(name=name, **config), workflow_key
    )
    if output_format == "text":
        logger.info("Added Slurm configuration %s to database", name)
    else:
        print(json.dumps({"key": scheduler.key}))


@click.command()
@click.argument("slurm_config_key")
@click.option(
    "-N",
    "--name",
    type=str,
    help="Name of config",
)
@click.option(
    "-a",
    "--account",
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
    help="Number of nodes to use for each job",
)
@click.option("-p", "--partition", help="HPC partition. Default is determinted by the scheduler")
@click.option(
    "-q",
    "--qos",
    show_default=True,
    help="Controls priority of the jobs.",
)
@click.option(
    "-t",
    "--tmp",
    type=str,
    help="Request nodes that have at least this amount of storage scratch space.",
)
@click.option("-w", "--walltime", show_default=True, help="Slurm job walltime.")
@click.pass_obj
@click.pass_context
def modify_config(ctx, api, slurm_config_key, **kwargs):
    """Modify a Slurm config in the database."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    scheduler = api.get_workflows_workflow_slurm_schedulers_key(workflow_key, slurm_config_key)
    changed = False
    for param in (
        "name",
        "account",
        "gres",
        "mem",
        "nodes",
        "partition",
        "qos",
        "tmp",
        "walltime",
    ):
        val = kwargs[param]
        if val is not None:
            setattr(scheduler, param, val)
            changed = True

    if changed:
        scheduler = api.put_workflows_workflow_slurm_schedulers_key(
            scheduler, workflow_key, slurm_config_key
        )
        if output_format == "text":
            logger.info("Modified Slurm configuration %s to database", slurm_config_key)
        else:
            print(json.dumps({"key": slurm_config_key}))
    else:
        logger.info("No changes requested")


@click.command()
@click.pass_obj
@click.pass_context
def list_configs(ctx, api):
    """Show the current Slurm configs in the database."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    table_title = f"Slurm configurations in workflow {workflow_key}"
    items = (
        x.to_dict()
        for x in iter_documents(api.get_workflows_workflow_slurm_schedulers, workflow_key)
    )
    exclude = ("rev",)
    print_items(ctx, items, table_title=table_title, json_key="configs", exclude_columns=exclude)


@click.command()
@click.option(
    "-j",
    "--job-prefix",
    default="node",
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
@click.option(
    "-p",
    "--poll-interval",
    default=JOB_COMPLETION_POLL_INTERVAL,
    show_default=True,
    help="Poll interval for job completions",
)
@click.option(
    "-s",
    "--scheduler-config-key",
    type=str,
    help="SlurmScheduler config key. Auto-selected if possible.",
)
@click.pass_obj
@click.pass_context
def schedule_nodes(
    ctx, api, job_prefix, num_hpc_jobs, output, poll_interval, scheduler_config_key
):
    """Schedule nodes with Slurm to run jobs."""
    # TODO: if workflow isn't started, start it?
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    logger.info(get_cli_string())
    workflow_key = get_workflow_key_from_context(ctx, api)

    ready_jobs = api.get_workflows_workflow_jobs(workflow_key, status="ready", limit=1)
    if not ready_jobs.items:
        logger.error("No jobs are in the ready state")
        sys.exit(1)

    output_format = get_output_format_from_context(ctx)
    if scheduler_config_key is None:
        params = ctx.find_root().params
        if params["no_prompts"]:
            logger.error("--scheduler-config-key must be set")
            sys.exit(1)
        # TODO: there is a lot more we could do to auto-select the config
        msg = (
            "\nThis command requires a scheduler config key and one was not provided. "
            "Please choose one from below.\n"
        )
        config = prompt_user_for_document(
            "scheduler_config",
            api.get_workflows_workflow_slurm_schedulers,
            workflow_key,
            auto_select_one_option=True,
            exclude_columns=("id", "rev"),
            msg=msg,
        )
        if config is None:
            logger.error("No schedulers are stored")
            sys.exit(1)
    else:
        config = api.get_workflows_workflow_slurm_schedulers_key(
            workflow_key, scheduler_config_key
        )

    output.mkdir(exist_ok=True)
    data = remove_db_keys(config.to_dict())
    data.pop("name")
    hpc_type = HpcType("slurm")
    mgr = HpcManager(data, hpc_type, output)
    database_url = api.api_client.configuration.host
    runner_script = f"torc -k {workflow_key} -u {database_url} hpc slurm run-jobs -o {output} -p {poll_interval}"
    job_ids = []
    node_keys = []
    for _ in range(num_hpc_jobs):
        node = api.post_workflows_workflow_scheduled_compute_nodes(
            WorkflowScheduledComputeNodesModel(
                scheduler_config_id=config.id, status="uninitialized"
            ),
            workflow_key,
        )
        name = f"{job_prefix}_{node.key}"
        try:
            # TODO: keep_submission_script false
            job_id = mgr.submit(output, name, runner_script, keep_submission_script=True)
        except Exception:
            api.delete_workflows_workflow_scheduled_compute_nodes_key(workflow_key, node.key)
            raise

        node.scheduler_id = job_id
        node.status = "pending"
        api.put_workflows_workflow_scheduled_compute_nodes_key(node, workflow_key, node.key)
        job_ids.append(job_id)
        node_keys.append(node.key)

    api.post_workflows_workflow_events(
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

    if output_format == "text":
        logger.info("Scheduled compute node job IDs: %s", " ".join(job_ids))
    else:
        print(json.dumps({"job_ids": job_ids, "keys": node_keys}))


@click.command()
@click.option(
    "-o",
    "--output",
    default="output",
    show_default=True,
    callback=path_callback,
)
@click.option(
    "-p",
    "--poll-interval",
    default=JOB_COMPLETION_POLL_INTERVAL,
    show_default=True,
    help="Poll interval for job completions",
)
@click.pass_obj
@click.pass_context
def run_jobs(ctx, api, output, poll_interval):
    """Run workflow jobs on a Slurm compute node."""
    workflow_key = get_workflow_key_from_context(ctx, api)
    intf = SlurmInterface()
    slurm_job_id = intf.get_current_job_id()
    hostname = socket.gethostname()
    log_file = output / f"slurm_runner_{hostname}_{slurm_job_id}.log"
    my_logger = setup_cli_logging(ctx, __name__, filename=log_file)
    check_database_url(api)
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
    nodes = api.get_workflows_workflow_scheduled_compute_nodes(
        workflow_key, scheduler_id=slurm_job_id
    ).items
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
        job_completion_poll_interval=poll_interval,
    )

    if node is not None:
        node.status = "active"
        node = api.put_workflows_workflow_scheduled_compute_nodes_key(node, workflow_key, node.key)

    my_logger.info("Start workflow on compute node %s", hostname)
    runner.run_worker(scheduler=scheduler)

    if node is not None:
        node.status = "complete"
        api.put_workflows_workflow_scheduled_compute_nodes_key(node, workflow_key, node.key)
    # TODO: schedule more nodes if needed


slurm.add_command(add_config)
slurm.add_command(modify_config)
slurm.add_command(list_configs)
slurm.add_command(run_jobs)
slurm.add_command(schedule_nodes)
