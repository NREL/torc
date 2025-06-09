"""Slurm CLI commands"""

import json
import math
import socket
import sys
from datetime import timedelta
from pathlib import Path

import isodate
import rich_click as click
from loguru import logger

from torc.openapi_client import (
    ApiException,
    ComputeNodesResources,
    DefaultApi,
    SlurmSchedulerModel,
    ScheduledComputeNodesModel,
)

import torc
from torc.api import (
    iter_documents,
    remove_db_keys,
    list_model_fields,
    wait_for_healthy_database,
    send_api_command,
)
from torc.common import JOB_STDIO_DIR
from torc.hpc.common import HpcType
from torc.exceptions import DatabaseOffline
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


DEFAULT_JOB_PREFIX = "worker"
DEFAULT_OUTPUT_DIR = "output"


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
@click.option("-p", "--partition", help="HPC partition. Default is determined by the scheduler")
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
    "-w",
    "--walltime",
    default="04:00:00",
    show_default=True,
    help="Slurm job walltime.",
)
@click.option(
    "-e",
    "--extra",
    help="Add extra Slurm parameters, for example --extra='--reservation=my-reservation'.",
)
@click.pass_obj
@click.pass_context
def add_config(ctx, api, name, account, gres, mem, nodes, partition, qos, tmp, walltime, extra):
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
    if extra:
        config["extra"] = extra
    scheduler = api.add_slurm_scheduler(workflow_key, SlurmSchedulerModel(name=name, **config))
    if output_format == "text":
        logger.info("Added Slurm configuration {} to the database", name)
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
@click.option("-p", "--partition", help="HPC partition. Default is determined by the scheduler")
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
    scheduler = api.get_slurm_scheduler(workflow_key, slurm_config_key)
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
        scheduler = api.modify_slurm_scheduler(workflow_key, slurm_config_key, scheduler)
        if output_format == "text":
            logger.info("Modified Slurm configuration {} to the database", slurm_config_key)
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
    items = (x.to_dict() for x in iter_documents(api.list_slurm_schedulers, workflow_key))
    columns = list_model_fields(SlurmSchedulerModel)
    columns.remove("_rev")
    print_items(ctx, items, table_title, columns, "configs")


@click.command()
@click.option(
    "-c",
    "--cpu-affinity-cpus-per-job",
    type=int,
    help="Enable CPU affinity for this number of CPUs per job.",
)
@click.option(
    "-j",
    "--job-prefix",
    default=DEFAULT_JOB_PREFIX,
    type=str,
    show_default=True,
    help="Prefix for HPC job names",
)
@click.option(
    "-k",
    "--keep-submission-scripts",
    is_flag=True,
    default=False,
    show_default=True,
    help="Keep Slurm submission scripts on the filesystem.",
)
@click.option(
    "-m",
    "--max-parallel-jobs",
    type=int,
    help="Maximum number of parallel jobs. Default is to use resource availability.",
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
    default=DEFAULT_OUTPUT_DIR,
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
    cpu_affinity_cpus_per_job,
    job_prefix,
    keep_submission_scripts,
    max_parallel_jobs,
    num_hpc_jobs,
    output,
    poll_interval,
    scheduler_config_key,
    start_one_worker_per_node,
):
    """Schedule nodes with Slurm to run jobs."""
    check_database_url(api)
    output.mkdir(exist_ok=True)
    log_file = output / "schedule_nodes.log"
    setup_cli_logging(ctx, __name__, filename=log_file, mode="a")
    logger.info(get_cli_string())
    logger.info("torc version {}", torc.__version__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)

    _check_schedule_params(api, workflow_key)
    config = _get_scheduler_config(ctx, api, workflow_key, scheduler_config_key)
    schedule_slurm_nodes(
        api,
        workflow_key,
        config,
        output,
        cpu_affinity_cpus_per_job=cpu_affinity_cpus_per_job,
        job_prefix=job_prefix,
        keep_submission_scripts=keep_submission_scripts,
        max_parallel_jobs=max_parallel_jobs,
        num_hpc_jobs=num_hpc_jobs,
        poll_interval=poll_interval,
        start_one_worker_per_node=start_one_worker_per_node,
        output_format=output_format,
    )


def schedule_slurm_nodes(
    api,
    workflow_key,
    config,
    output: Path,
    job_prefix=DEFAULT_JOB_PREFIX,
    max_parallel_jobs=None,
    cpu_affinity_cpus_per_job=None,
    num_hpc_jobs=1,
    start_one_worker_per_node=False,
    keep_submission_scripts=False,
    poll_interval=JOB_COMPLETION_POLL_INTERVAL,
    output_format="text",
):
    """Schedule Slurm jobs"""
    output.mkdir(exist_ok=True)
    data = remove_db_keys(config.to_dict())
    data.pop("name", None)
    hpc_type = HpcType("slurm")
    mgr = HpcManager(data, hpc_type, output)
    database_url = api.api_client.configuration.host
    workflow_config = api.get_workflow_config(workflow_key)

    runner_script = (
        f"torc -k {workflow_key} -u {database_url} --console-level=error hpc slurm run-jobs "
        f"-o {output} -p {poll_interval} "
        f"-w {workflow_config.compute_node_wait_for_healthy_database_minutes}"
    )
    if max_parallel_jobs:
        runner_script += f" --max-parallel-jobs {max_parallel_jobs}"
    if cpu_affinity_cpus_per_job:
        runner_script += f" --cpu-affinity-cpus-per-job {cpu_affinity_cpus_per_job}"
    job_ids = []
    node_keys = []
    for _ in range(num_hpc_jobs):
        node = api.add_scheduled_compute_node(
            workflow_key,
            ScheduledComputeNodesModel(scheduler_config_id=config.id, status="uninitialized"),
        )
        name = f"{job_prefix}_{node.key}"
        try:
            job_id = mgr.submit(
                output,
                name,
                runner_script,
                keep_submission_script=keep_submission_scripts,
                start_one_worker_per_node=start_one_worker_per_node,
            )
        except Exception:
            api.remove_scheduled_compute_node(workflow_key, node.key)
            raise

        node.scheduler_id = job_id
        node.status = "pending"
        api.modify_scheduled_compute_node(workflow_key, node.key, node)
        job_ids.append(job_id)
        node_keys.append(node.key)

    api.add_event(
        workflow_key,
        {
            "category": "scheduler",
            "type": "submit",
            "num_jobs": len(job_ids),
            "job_ids": job_ids,
            "scheduler_config_id": config.id,
            "torc_version": torc.__version__,
            "message": f"Submitted {len(job_ids)} job request(s) to {hpc_type.value}",
        },
    )

    if output_format == "text":
        logger.info("Scheduled compute node job IDs: {}", " ".join(job_ids))
    else:
        print(json.dumps({"job_ids": job_ids, "keys": node_keys}))


def _check_schedule_params(api, workflow_key):
    ready_jobs = api.list_jobs(workflow_key, status="ready", limit=1)
    if not ready_jobs.items:
        ready_jobs = api.list_jobs(workflow_key, status="scheduled", limit=1)
    if not ready_jobs.items:
        logger.error("No jobs are in the ready state. Did you run 'torc workflows start'?")
        sys.exit(1)


def _get_scheduler_config(ctx, api, workflow_key, scheduler_config_key) -> SlurmSchedulerModel:
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
            api.list_slurm_schedulers,
            workflow_key,
            auto_select_one_option=True,
            exclude_columns=("_id", "_rev"),
            msg=msg,
        )
        if config is None:
            logger.error("No schedulers are stored")
            sys.exit(1)
    else:
        config = api.get_slurm_scheduler(workflow_key, scheduler_config_key)

    return config


@click.command()
@click.option(
    "-c",
    "--num-cpus",
    type=int,
    default=104,
    help="Number of CPUs per node",
    show_default=True,
)
@click.option(
    "-m",
    "--memory-gb",
    type=int,
    default=240,
    help="Amount of memory in GB per node",
    show_default=True,
)
@click.option(
    "-s",
    "--scheduler-config-key",
    type=str,
    help="Limit output to jobs assigned this scheduler config key.",
)
@click.pass_obj
@click.pass_context
def recommend_nodes(
    ctx: click.Context, api: DefaultApi, num_cpus: int, memory_gb, scheduler_config_key: str | None
) -> None:
    """Recommend compute nodes to schedule."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    output_format = get_output_format_from_context(ctx)
    workflow_key = get_workflow_key_from_context(ctx, api)
    config = _get_scheduler_config(ctx, api, workflow_key, scheduler_config_key)
    reqs = api.get_ready_job_requirements(workflow_key, scheduler_config_id=config.id)
    if reqs.num_jobs == 0:
        logger.error("No jobs are in the ready state. You may need to run 'torc workflows start'")
        sys.exit(1)

    max_runtime_s = isodate.parse_duration(reqs.max_runtime).total_seconds()
    assert config.walltime is not None, "Slurm walltime must be set in the config"
    node_duration = slurm_time_to_timedelta(config.walltime).total_seconds()
    if max_runtime_s > node_duration:
        logger.error(
            "The max job runtime of {} is greater than the Slurm walltime of {}. "
            "This configuration is invalid",
            reqs.max_runtime,
            config.walltime,
        )
        sys.exit(1)
    jobs_per_node_by_duration = math.ceil(node_duration / max_runtime_s)

    num_nodes_by_cpus = math.ceil(reqs.num_cpus / num_cpus / jobs_per_node_by_duration)
    num_nodes_by_memory = math.ceil(reqs.memory_gb / memory_gb / jobs_per_node_by_duration)
    if num_nodes_by_cpus >= num_nodes_by_memory:
        limiter = "CPU"
        num_nodes = num_nodes_by_cpus
    else:
        limiter = "memory"
        num_nodes = num_nodes_by_memory
    if output_format == "text":
        print(f"Requirements for jobs in the ready state: \n{reqs}")
        print(f"  Based on CPUs, number of required nodes = {num_nodes_by_cpus}")
        print(f"  Based on memory, number of required nodes = {num_nodes_by_memory}")
        print(f"  Max job runtime: {reqs.max_runtime}")
        print(f"  Slurm walltime: {config.walltime}")
        print(f"  Jobs per node by duration: {jobs_per_node_by_duration}\n")
        print(
            f"After accounting for a max runtime and a limiter based on {limiter}, "
            f"torc recommends scheduling {num_nodes} nodes.\n"
            "Please perform a sanity check on this number before scheduling jobs.\n"
            "The algorithm is most accurate when the jobs have uniform requirements."
        )
    else:
        print(
            json.dumps(
                {
                    "num_nodes": num_nodes,
                    "details": {
                        "ready_job_requirements": reqs.to_dict(),
                        "num_nodes_by_cpus": num_nodes_by_cpus,
                        "num_nodes_by_memory": num_nodes_by_memory,
                        "jobs_per_node_by_duration": jobs_per_node_by_duration,
                        "limiter": limiter,
                    },
                }
            )
        )


@click.command()
@click.option(
    "-c",
    "--cpu-affinity-cpus-per-job",
    type=int,
    help="Enable CPU affinity for this number of CPUs per job.",
)
@click.option(
    "-m",
    "--max-parallel-jobs",
    type=int,
    help="Maximum number of parallel jobs. Default is to use resource availability.",
)
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
@click.option(
    "--is-subtask",
    is_flag=True,
    default=False,
    show_default=True,
    help="Set to True if this is a subtask and multiple workers are running on one node.",
)
@click.option(
    "-w",
    "--wait-for-healthy-database-minutes",
    type=int,
    default=0,
    show_default=True,
    help="Wait this number of minutes if the database is offline.",
)
@click.pass_obj
@click.pass_context
def run_jobs(
    ctx,
    api,
    cpu_affinity_cpus_per_job,
    max_parallel_jobs,
    output,
    poll_interval,
    is_subtask,
    wait_for_healthy_database_minutes,
):
    """Run workflow jobs on a Slurm compute node."""
    try:
        # NOTE: Ensure that this is the first API command that gets sent.
        send_api_command(api.ping)
    except DatabaseOffline:
        wait_for_healthy_database(api, wait_for_healthy_database_minutes)

    workflow_key = get_workflow_key_from_context(ctx, api)
    check_database_url(api)
    intf = SlurmInterface()
    slurm_job_id = intf.get_current_job_id()
    hostname = socket.gethostname()
    slurm_node_id = intf.get_node_id()
    slurm_task_pid = intf.get_task_pid()
    log_file = get_slurm_job_runner_log_file(output, slurm_job_id, slurm_node_id, slurm_task_pid)
    setup_cli_logging(ctx, __name__, filename=Path(log_file))
    logger.info(get_cli_string())
    scheduler = {
        "node_names": intf.list_active_nodes(slurm_job_id),
        "environment_variables": intf.get_environment_variables(),
        "scheduler_type": "hpc",
        "slurm_job_id": slurm_job_id,
        "hpc_type": HpcType.SLURM.value,
    }
    config = send_api_command(api.get_workflow_config, workflow_key)
    buffer = timedelta(seconds=config.compute_node_expiration_buffer_seconds)
    end_time = intf.get_job_end_time() + buffer
    node = None if is_subtask else _get_scheduled_compute_node(api, workflow_key, slurm_job_id)

    workflow = send_api_command(api.get_workflow, workflow_key)
    log_prefix = _get_torc_job_log_prefix_slurm(slurm_job_id, slurm_node_id, slurm_task_pid)
    logger.info(
        "Start workflow on compute node {} end_time={} buffer={}",
        hostname,
        end_time,
        buffer,
    )

    scheduler_config_id = None
    # Note that there could be multiple compute nodes under this slurm_job_id.
    activated_slurm_job = False
    if node is not None:
        scheduler_config_id = node.scheduler_config_id
        if node.status != "active":
            node.status = "active"
            try:
                node = send_api_command(
                    api.modify_scheduled_compute_node, workflow_key, node.key, node
                )
                activated_slurm_job = True
            except ApiException:
                # Another node sent the command first.
                pass

    resources = _create_node_resources(intf, scheduler_config_id, is_subtask)

    runner = JobRunner(
        api,
        workflow,
        output,
        cpu_affinity_cpus_per_job=cpu_affinity_cpus_per_job,
        max_parallel_jobs=max_parallel_jobs,
        end_time=end_time,
        resources=resources,
        job_completion_poll_interval=poll_interval,
        log_prefix=log_prefix,
    )
    try:
        runner.run_worker(scheduler=scheduler)
    except Exception:
        logger.exception("Slurm worker failed")
        raise
    finally:
        if activated_slurm_job:
            # TODO: This is not very accurate. Other nodes in the allocation could still be
            # active. It would be better to do this from the caller of this command.
            assert node is not None
            node.status = "complete"
            send_api_command(api.modify_scheduled_compute_node, workflow_key, node.key, node)


def _get_scheduled_compute_node(api, workflow_key, slurm_job_id):
    nodes = send_api_command(
        api.list_scheduled_compute_nodes, workflow_key, scheduler_id=slurm_job_id
    ).items
    num_nodes = len(nodes)
    if num_nodes == 0:
        node = None
    elif num_nodes == 1:
        node = nodes[0]
    else:
        logger.error("num_nodes with {} cannot be {}", slurm_job_id, num_nodes)
        sys.exit(1)

    return node


def _create_node_resources(intf, scheduler_config_id, is_subtask):
    # Get resources from the Slurm environment because the job may only have a portion of overall
    # system resources.
    num_cpus_in_node = intf.get_num_cpus()
    memory_gb_in_node = intf.get_memory_gb()
    if is_subtask:
        num_cpus = intf.get_num_cpus_per_task()
        num_workers = num_cpus_in_node // num_cpus
        memory_gb = memory_gb_in_node / num_workers
        # TODO: should GPUs use SLURM_STEP_GPUS instead?
    else:
        num_cpus = num_cpus_in_node
        memory_gb = memory_gb_in_node

    return ComputeNodesResources(
        num_cpus=num_cpus,
        num_gpus=intf.get_num_gpus(),
        memory_gb=memory_gb,
        num_nodes=intf.get_num_nodes(),
        scheduler_config_id=scheduler_config_id,
        time_limit=None,
    )


def get_slurm_job_runner_log_file(output_dir, job_id, node_id, task_pid) -> str:
    """Return the name of the job runner file for Slurm schedulers."""
    return f"{output_dir}/job_runner_slurm_{job_id}_{node_id}_{task_pid}.log"


def get_slurm_stdio_files(output_dir, job_id) -> list[str]:
    """Return the names of the stdout/stderr log files written by Slurm."""
    return [f"{output_dir}/job_output_{job_id}{x}" for x in (".e", ".o")]


def _get_torc_job_log_prefix_slurm(slurm_job_id, slurm_node_id, slurm_task_pid):
    """Return the names of the stdout/stderr log files written by Slurm."""
    return f"slurm_{slurm_job_id}_{slurm_node_id}_{slurm_task_pid}"


def get_torc_job_stdio_files_slurm(
    output_dir, slurm_job_id, slurm_node_id, slurm_task_pid, job_key, run_id
):
    """Return the names of the stdout/stderr log files for a torc job."""
    files = []
    for ext in (".e", ".o"):
        prefix = _get_torc_job_log_prefix_slurm(slurm_job_id, slurm_node_id, slurm_task_pid)
        files.append(f"{output_dir}/{JOB_STDIO_DIR}/{prefix}_{job_key}_{run_id}{ext}")
    return files


def slurm_time_to_timedelta(walltime: str) -> timedelta:
    if "-" in walltime:
        days_part, time_part = walltime.split("-")
        days = int(days_part)
    else:
        days = 0
        time_part = walltime
    h, m, s = map(int, time_part.split(":"))
    return timedelta(days=days, hours=h, minutes=m, seconds=s)


slurm.add_command(add_config)
slurm.add_command(modify_config)
slurm.add_command(list_configs)
slurm.add_command(recommend_nodes)
slurm.add_command(run_jobs)
slurm.add_command(schedule_nodes)
