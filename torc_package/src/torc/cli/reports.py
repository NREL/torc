"""Reports CLI commands"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import rich_click as click

from torc.api import (
    iter_documents,
)
from torc.common import JOB_STDIO_DIR
from torc.openapi_client.api.default_api import DefaultApi
from torc.openapi_client.models.job_model import JobModel
from torc.openapi_client.models.workflow_model import WorkflowModel
from .common import (
    check_database_url,
    get_workflow_key_from_context,
    setup_cli_logging,
    path_callback,
)
from .slurm import (
    get_slurm_job_runner_log_file,
    get_slurm_stdio_files,
    get_torc_job_stdio_files_slurm,
)


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
def results(ctx, api, job_keys, output: Path, run_id: tuple[int]):
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

    # TODO: refactor this logic into a class.
    results_by_job, job_key_to_name = _build_results_by_job(api, workflow.key, jobs, run_ids)
    report, lookup_by_job_and_run_id = _build_report(results_by_job, job_key_to_name, workflow)

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
        data = lookup_by_job_and_run_id.get((job_key, item["edge"]["data"]["run_id"]))
        if data is None:
            # This run did not complete.
            results_by_job[job_key].append({"run_id": item["edge"]["data"]["run_id"]})
            continue
        r_id = item["edge"]["data"]["run_id"]
        if scheduler.get("hpc_type") == "slurm":
            slurm_job_id = scheduler["slurm_job_id"]
            env_vars = scheduler["environment_variables"]
            slurm_node_id = env_vars["SLURM_NODEID"]
            slurm_task_pid = env_vars["SLURM_TASK_PID"]
            data["job_runner_log_file"] = get_slurm_job_runner_log_file(
                output, slurm_job_id, slurm_node_id, slurm_task_pid
            )
            data["slurm_stdio_files"] = get_slurm_stdio_files(output, slurm_job_id)
            data["job_stdio_files"] = get_torc_job_stdio_files_slurm(
                output,
                slurm_job_id,
                slurm_node_id,
                slurm_task_pid,
                job_key,
                r_id,
            )
        elif scheduler.get("scheduler_type") == "local":
            hostname = scheduler["hostname"]
            data["job_runner_log_file"] = str(
                output / f"worker_{hostname}_{workflow_key}_{r_id}.log"
            )
            data["job_stdio_files"] = get_torc_job_stdio_files_local(output, job_key, r_id)

    print(json.dumps(report, indent=2))


def get_torc_job_stdio_files_local(output_dir: Path, job_key: str, run_id: int) -> list[str]:
    files = []
    for ext in (".e", ".o"):
        files.append(f"{output_dir}/{JOB_STDIO_DIR}/{job_key}_{run_id}{ext}")
    return files


def _build_results_by_job(
    api: DefaultApi, workflow_key: str, jobs: list[JobModel], run_ids: set[int]
):
    job_key_to_name = {}
    results_by_job = defaultdict(list)
    for job in jobs:
        job_key_to_name[job.key] = job.name
        filters: dict[str, Any] = {"job_key": job.key}
        if run_ids:
            for rid in run_ids:
                filters["run_id"] = rid
                for result in iter_documents(api.list_results, workflow_key, **filters):
                    results_by_job[job.key].append(result)
        else:
            for result in iter_documents(api.list_results, workflow_key, **filters):
                results_by_job[job.key].append(result)
    return results_by_job, job_key_to_name


def _build_report(
    results_by_job: dict[str, Any], job_key_to_name: dict[str, Any], workflow: WorkflowModel
):
    report: dict[str, Any] = {"workflow": workflow.model_dump(), "jobs": []}
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

    return report, lookup_by_job_and_run_id


reports.add_command(results)
