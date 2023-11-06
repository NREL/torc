"""Reports CLI commands"""

import json
import logging
from collections import defaultdict
from pathlib import Path

import click

from torc.api import (
    iter_documents,
)
from .common import (
    check_database_url,
    get_workflow_key_from_context,
    setup_cli_logging,
    path_callback,
)
from .slurm import (
    get_slurm_job_runner_log_file,
    get_slurm_stdio_files,
    get_torc_job_stdio_files,
)


logger = logging.getLogger(__name__)


@click.group()
def reports():
    """Report commands"""


@click.command()
@click.argument("job_keys", nargs=-1)
@click.option(
    "-o",
    "--output",
    default="output",
    show_default=True,
    type=click.Path(exists=True),
    callback=path_callback,
)
@click.option(
    "-r",
    "--run-id",
    type=int,
    multiple=True,
    help="Enter one or more run IDs to limit output to specific runs. Default is to show all.",
)
@click.pass_obj
@click.pass_context
def results(ctx, api, job_keys, output: Path, run_id):
    """Report information about job results and log files."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    workflow = api.get_workflow(workflow_key)
    run_ids = set(run_id)

    if job_keys:
        jobs = [api.get_job(workflow_key, x) for x in job_keys]
    else:
        jobs = list(iter_documents(api.list_jobs, workflow_key))
    jobs.sort(key=lambda x: int(x.key))

    job_key_to_name = {}
    results_by_job = defaultdict(list)
    report = {"workflow": workflow.model_dump(), "jobs": []}
    for job in jobs:
        job_key_to_name[job.key] = job.name
        filters = {"job_key": job.key}
        if run_ids:
            for rid in run_ids:
                filters["run_id"] = rid
                for result in iter_documents(api.list_results, workflow_key, **filters):
                    results_by_job[job.key].append(result)
        else:
            for result in iter_documents(api.list_results, workflow_key, **filters):
                results_by_job[job.key].append(result)

    lookup_by_job_and_run_id = {}
    for key in results_by_job:
        job_details = {"name": job_key_to_name[key], "key": key, "runs": []}
        results_by_job[key].sort(key=lambda x: x.run_id)
        for result in results_by_job[key]:
            run_result = {
                "run_id": result.run_id,
                "return_code": result.return_code,
                "status": result.status,
                "completion_time": result.completion_time,
                "exec_time_minutes": result.exec_time_minutes,
            }
            job_details["runs"].append(run_result)
            lookup_by_job_and_run_id[(key, result.run_id)] = run_result
        report["jobs"].append(job_details)

    for item in iter_documents(
        api.join_collections_by_outbound_edge,
        workflow_key,
        "compute_nodes",
        "executed",
        {},
    ):
        job_key = item["to"]["_key"]
        if job_key not in results_by_job:
            continue
        if run_ids and item["edge"]["data"]["run_id"] not in run_ids:
            continue

        scheduler = item["from"]["scheduler"]
        slurm_job_id = scheduler["slurm_job_id"]
        env_vars = scheduler["environment_variables"]
        slurm_node_id = env_vars["SLURM_NODEID"]
        slurm_task_pid = env_vars["SLURM_TASK_PID"]
        data = lookup_by_job_and_run_id.get((job_key, item["edge"]["data"]["run_id"]))
        if data is None:
            # This run did not complete.
            data = {"run_id": item["edge"]["data"]["run_id"]}
            results_by_job[job_key].append(data)
        if scheduler.get("hpc_type") == "slurm":
            data["job_runner_log_file"] = get_slurm_job_runner_log_file(
                output, slurm_job_id, slurm_node_id, slurm_task_pid
            )
            data["slurm_stdio_files"] = get_slurm_stdio_files(output, slurm_job_id)
            data["job_stdio_files"] = get_torc_job_stdio_files(
                output,
                slurm_job_id,
                slurm_node_id,
                slurm_task_pid,
                job_key,
                item["edge"]["data"]["run_id"],
            )

    print(json.dumps(report, indent=2))


reports.add_command(results)
