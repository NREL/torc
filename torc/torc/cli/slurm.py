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
from swagger_client.models.key_prepare_jobs_for_submission_model import (
    KeyPrepareJobsForSubmissionModel,
)

import torc.version
from torc.api import iter_documents, remove_db_keys
from torc.hpc.common import HpcType
from torc.hpc.hpc_manager import HpcManager
from torc.hpc.slurm_interface import SlurmInterface
from torc.job_runner import (
    JobRunner,
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
        logger.info("Added Slurm configuration %s to the database", name)
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
            logger.info("Modified Slurm configuration %s to the database", slurm_config_key)
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
@click.option(
    "-S",
    "--start-one-worker-per-node",
    is_flag=True,
    default=False,
    help="Start a torc worker on each compute node. "
    "The default behavior starts a worker on the first compute node but no others. That "
    "defers control of the nodes to the user job. "
    "Setting this flag means that every compute node in the allocation will run jobs "
    "concurrently. This flag has no effect if each Slurm allocation has one compute node "
    "(default).",
)
@click.pass_obj
@click.pass_context
def schedule_nodes(
    ctx,
    api,
    job_prefix,
    num_hpc_jobs,
    output,
    poll_interval,
    scheduler_config_key,
    start_one_worker_per_node,
):
    """Schedule nodes with Slurm to run jobs."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    logger.info(get_cli_string())
    logger.info("torc version %s", torc.version.__version__)
    workflow_key = get_workflow_key_from_context(ctx, api)

    ready_jobs = api.get_workflows_workflow_jobs(workflow_key, status="ready", limit=1)
    if not ready_jobs.items:
        ready_jobs = api.get_workflows_workflow_jobs(workflow_key, status="scheduled", limit=1)
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
            job_id = mgr.submit(
                output,
                name,
                runner_script,
                keep_submission_script=False,
                start_one_worker_per_node=start_one_worker_per_node,
            )
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
            "torc_version": torc.version.__version__,
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
    slurm_node_id = intf.get_node_id()
    log_file = output / f"job_runner_slurm_{slurm_job_id}_{slurm_node_id}.log"
    my_logger = setup_cli_logging(ctx, __name__, filename=log_file)
    check_database_url(api)
    my_logger.info(get_cli_string())
    my_logger.info("torc version %s", torc.version.__version__)
    my_logger.info("Run jobs on %s for workflow %s", hostname, api.api_client.configuration.host)
    scheduler = {
        "node_names": intf.list_active_nodes(slurm_job_id),
        "environment_variables": intf.get_environment_variables(),
        "scheduler_type": "hpc",
        "slurm_job_id": slurm_job_id,
        "hpc_type": HpcType.SLURM.value,
    }
    config = api.get_workflows_key_config(workflow_key)
    buffer = timedelta(seconds=config.compute_node_worker_buffer_seconds)
    end_time = intf.get_job_end_time() - buffer
    nodes = api.get_workflows_workflow_scheduled_compute_nodes(
        workflow_key, scheduler_id=slurm_job_id
    ).items
    num_nodes = len(nodes)
    if num_nodes == 0:
        node = None
    elif num_nodes == 1:
        node = nodes[0]
    else:
        raise Exception(f"num_nodes with {slurm_job_id=} cannot be {num_nodes=}")

    # Get resources from the Slurm environment because the job may only have a portion of overall
    # system resources.
    resources = KeyPrepareJobsForSubmissionModel(
        num_cpus=intf.get_num_cpus(),
        num_gpus=intf.get_num_gpus(),
        memory_gb=intf.get_memory_gb(),
        num_nodes=intf.get_num_nodes(),
        scheduler_config_id=node.scheduler_config_id,
        time_limit=None,
    )
    workflow = api.get_workflows_key(workflow_key)
    runner = JobRunner(
        api,
        workflow,
        output,
        end_time=end_time,
        resources=resources,
        job_completion_poll_interval=poll_interval,
        log_prefix=f"slurm_{slurm_job_id}_{slurm_node_id}",
    )

    if node is not None:
        node.status = "active"
        node = api.put_workflows_workflow_scheduled_compute_nodes_key(node, workflow_key, node.key)

    my_logger.info("Start workflow on compute node %s", hostname)
    runner.run_worker(scheduler=scheduler)

    if node is not None:
        node.status = "complete"
        api.put_workflows_workflow_scheduled_compute_nodes_key(node, workflow_key, node.key)


slurm.add_command(add_config)
slurm.add_command(modify_config)
slurm.add_command(list_configs)
slurm.add_command(run_jobs)
slurm.add_command(schedule_nodes)
