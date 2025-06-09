"""Generates tables of resource utilization statistics for reporting."""

from collections import defaultdict
from typing import Any, Generator

from prettytable import PrettyTable

from torc.api import iter_documents, remove_db_keys, send_api_command
from torc.common import GiB
from torc.openapi_client.api import DefaultApi


def iter_compute_node_stats(
    api: DefaultApi, workflow_key: str, exclude_process: bool = False
) -> Generator[dict[str, Any], None, None]:
    """Return a generator over all compute node resource utilization stats.

    Parameters
    ----------
    api : DefaultApi
    workflow_key : str
    exclude_process : bool
        If True, exclude process stats.
    """
    for node_stats in iter_documents(api.list_compute_node_stats, workflow_key):
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


def iter_job_process_stats(
    api: DefaultApi, workflow_key: str, **kwargs
) -> Generator[dict[str, Any], None, None]:
    """Return a generator over all job process resource utilization stats.

    Parameters
    ----------
    api : DefaultApi
    workflow_key : str

    Yields
    ------
    dict
    """
    for job in iter_documents(api.list_jobs, workflow_key, **kwargs):
        for stat in send_api_command(api.get_process_stats_for_job, workflow_key, job.key):
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


def list_job_process_stats(api: DefaultApi, workflow_key: str, **kwargs) -> list[dict[str, Any]]:
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


def make_compute_node_stats_records(api: DefaultApi, workflow_key: str) -> dict[str, list[dict]]:
    """Return a dict of records for each resource type.

    The returned value can be used to construct DataFrames, as in this example using Polars.

    Examples
    --------
    >>> by_resource_type = make_compute_node_stats_records(api, "123456")
    >>> dfs = {k: pl.from_records(v) for k, v in by_resource_type.items()}

    Returns
    ------
    Keys are resource type names, such as cpu, memory, process; values are list of records.
    """
    by_resource_type = defaultdict(list)
    for stat in iter_compute_node_stats(api, workflow_key):
        by_resource_type[stat["resource_type"]].append(stat)
    return by_resource_type


def list_compute_node_stats(
    api: DefaultApi, workflow_key: str, exclude_process: bool = False
) -> list[dict[str, Any]]:
    """Return a list of resource statistics."""
    return list(iter_compute_node_stats(api, workflow_key, exclude_process=exclude_process))


def make_compute_node_stats_text_tables(
    api: DefaultApi, workflow_key: str, exclude_process: bool = False
) -> dict[str, PrettyTable]:
    """Return a dict of PrettyTable instances for each resource type."""
    by_resource_type: dict[str, PrettyTable] = {}
    for stat in iter_compute_node_stats(api, workflow_key, exclude_process=exclude_process):
        rtype = stat["resource_type"]
        if rtype in by_resource_type:
            table = by_resource_type[rtype]
            table.field_names = tuple(stat.keys())
        else:
            table = PrettyTable(title=f"{rtype} Resource Utilization Statistics")
            by_resource_type[rtype] = table
        table.add_row(stat.values())  # type: ignore

    return by_resource_type


def make_job_process_stats_records(
    api: DefaultApi, workflow_key: str
) -> tuple[dict[str, Any], ...]:
    """Return a tuple of records containing job process stats.

    The returned value can be used to construct a DataFrame, as in this example using Polars.

    Examples
    ----------
    >>> records = make_job_process_stats_records(api, "123456")
    >>> df = pl.from_records(records)
    """
    return tuple(iter_job_process_stats(api, workflow_key))
