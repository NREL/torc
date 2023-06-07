"""Generates tables of resource utilization statistics for reporting."""

from collections import defaultdict

import polars as pl
from prettytable import PrettyTable

from torc.api import iter_documents, remove_db_keys, send_api_command
from torc.common import GiB


def iter_compute_node_stats(api, workflow_key, exclude_process=False):
    """Return a generator over all compute node resource utilization stats.

    Parameters
    ----------
    api : DefaultApi
    workflow_key : str
    exclude_process : bool
        If True, exclude process stats.

    Yields
    ------
    dict
    """
    for node_stats in iter_documents(api.get_workflows_workflow_compute_node_stats, workflow_key):
        hostname = node_stats.hostname
        for stat in node_stats.stats:
            if exclude_process and stat.resource_type == "Process":
                continue
            row = {
                "hostname": hostname,
                "resource_type": stat.resource_type,
                "num_samples": stat.num_samples,
            }
            if stat.resource_type == "Process":
                row["job_key"] = stat.job_key
            for stat_type in ("average", "minimum", "maximum"):
                row.update(getattr(stat, stat_type))
                row["type"] = stat_type
                yield row


def iter_job_process_stats(api, workflow_key, **kwargs):
    """Return a generator over all job process resource utilization stats.

    Parameters
    ----------
    api : DefaultApi
    workflow_key : str

    Yields
    ------
    dict
    """
    for job in iter_documents(api.get_workflows_workflow_jobs, workflow_key, **kwargs):
        for stat in send_api_command(
            api.get_workflows_workflow_jobs_key_process_stats, workflow_key, job.key
        ):
            stats = remove_db_keys(stat.to_dict())
            yield {
                "job_key": stats["job_key"],
                "run_id": int(stats["run_id"]),
                "timestamp": stats["timestamp"],
                "avg_cpu_percent": stats["avg_cpu_percent"],
                "max_cpu_percent": stats["max_cpu_percent"],
                "avg_memory_gb": stats["avg_rss"] / GiB,
                "max_memory_gb": stats["max_rss"] / GiB,
                "num_samples": int(stats["num_samples"]),
            }


def list_job_process_stats(api, workflow_key, **kwargs) -> list[dict]:
    """Return a list of all job process resource utilization stats.

    Parameters
    ----------
    api : DefaultApi
    workflow_key : str

    Returns
    ------
    list[dict]
    """
    return list(iter_job_process_stats(api, workflow_key, **kwargs))


def make_compute_node_stats_dataframes(api, workflow_key) -> pl.DataFrame:
    """Return a dict of DataFrame instances for each resource type."""
    by_resource_type = defaultdict(list)
    for stat in iter_compute_node_stats(api, workflow_key):
        by_resource_type[stat["resource_type"]].append(stat)

    return {k: pl.from_records(v) for k, v in by_resource_type.items()}


def list_compute_node_stats(api, workflow_key, exclude_process=False) -> list[dict]:
    """Return a list of resource statistics."""
    return list(iter_compute_node_stats(api, workflow_key, exclude_process=exclude_process))


def make_compute_node_stats_text_tables(
    api, workflow_key, exclude_process=False
) -> dict[str, PrettyTable]:
    """Return a dict of PrettyTable instances for each resource type."""
    by_resource_type = {}
    for stat in iter_compute_node_stats(api, workflow_key, exclude_process=exclude_process):
        rtype = stat["resource_type"]
        if rtype in by_resource_type:
            table = by_resource_type[rtype]
            table.field_names = tuple(stat.keys())
        else:
            table = PrettyTable(title=f"{rtype} Resource Utilization Statistics")
            by_resource_type[rtype] = table
        table.add_row(stat.values())

    return by_resource_type


def make_job_process_stats_dataframe(api, workflow_key) -> pl.DataFrame:
    """Return a polars DataFrame containing job process stats.

    Parameters
    ----------
    api : DefaultApi
    workflow_key : str

    Returns
    -------
    pl.DataFrame
    """
    return pl.from_records(tuple(iter_job_process_stats(api, workflow_key)))
