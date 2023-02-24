import logging
import multiprocessing
import os
import socket
import sys
import time
from collections import defaultdict

from wms.resource_monitor.models import (
    ComputeNodeResourceStatResults,
    IpcMonitorCommands,
    ProcessStatResults,
    ResourceStatResults,
    ResourceType,
    ComputeNodeResourceStatConfig,
)
from wms.resource_monitor.resource_monitor import ResourceMonitor


logger = logging.getLogger(__name__)


class ResourceMonitorAggregator:
    """Aggregates resource utilization stats in memory."""

    def __init__(
        self,
        stats: ComputeNodeResourceStatConfig,
    ):
        self._stats = stats
        self._count = 0
        self._monitor = ResourceMonitor(stats.name)
        self._last_stats = self._get_stats()
        self._summaries = {
            "average": defaultdict(dict),
            "maximum": defaultdict(dict),
            "minimum": defaultdict(dict),
            "sum": defaultdict(dict),
        }
        for resource_type, stat_dict in self._last_stats.items():
            for stat_name in stat_dict:
                self._summaries["average"][resource_type][stat_name] = 0.0
                self._summaries["maximum"][resource_type][stat_name] = 0.0
                self._summaries["minimum"][resource_type][stat_name] = sys.maxsize
                self._summaries["sum"][resource_type][stat_name] = 0.0

        self._process_summaries = {
            "average": defaultdict(dict),
            "maximum": defaultdict(dict),
            "minimum": defaultdict(dict),
            "sum": defaultdict(dict),
        }
        self._process_sample_count = {}

    def _get_stats(self):
        data = {}
        if self._stats.cpu:
            data[ResourceType.CPU] = self._monitor.get_cpu_stats()
        if self._stats.disk:
            data[ResourceType.DISK] = self._monitor.get_disk_stats()
        if self._stats.memory:
            data[ResourceType.MEMORY] = self._monitor.get_memory_stats()
        if self._stats.network:
            data[ResourceType.NETWORK] = self._monitor.get_network_stats()
        return data

    def _get_process_stats(self, pids):
        stats = {}
        cur_pids = set()
        for name, pid in pids.items():
            _stats, children = self._monitor.get_process_stats(
                pid,
                include_children=self._stats.include_child_processes,
                recurse_children=self._stats.recurse_child_processes,
            )
            if _stats is not None:
                stats[name] = _stats
                cur_pids.add(pid)
                for child in children:
                    cur_pids.add(child)

        self._monitor.clear_stale_processes(cur_pids)
        return stats

    def complete_process_stats(self, completed_job_names):
        """Finalize stat summaries for completed processes.

        Parameters
        ----------
        completed_job_names : list[str]

        Returns
        -------
        ComputeNodeResourceStatResults
        """
        # Note that short-lived jobs may not be present.
        jobs = set(completed_job_names).intersection(self._process_sample_count)
        results = []
        for job_name in jobs:
            stat_dict = self._process_summaries["sum"][job_name]
            for stat_name, val in stat_dict.items():
                self._process_summaries["average"][job_name][stat_name] = (
                    val / self._process_sample_count[job_name]
                )

        for job_name in jobs:
            samples = self._process_sample_count[job_name]
            result = ProcessStatResults(
                job_name=job_name,
                num_samples=samples,
                resource_type=ResourceType.PROCESS,
                average=self._process_summaries["average"][job_name],
                minimum=self._process_summaries["minimum"][job_name],
                maximum=self._process_summaries["maximum"][job_name],
            )
            results.append(result)

        for job_name in jobs:
            for stat_dict in self._process_summaries.values():
                stat_dict.pop(job_name)
            self._process_sample_count.pop(job_name)

        return ComputeNodeResourceStatResults(
            name=self.name,
            hostname=socket.gethostname(),
            results=results,
        )

    def finalize(self):
        """Finalize the stat summaries and return the results.

        Returns
        -------
        ComputeNodeResourceStatResults
        """
        hostname = socket.gethostname()
        results = []
        resource_types = []

        if self._count == 0:
            return ComputeNodeResourceStatResults(
                name=self.name,
                hostname=hostname,
                results=results,
            )

        for resource_type, stat_dict in self._summaries["sum"].items():
            for stat_name, val in stat_dict.items():
                self._summaries["average"][resource_type][stat_name] = val / self._count

        self._summaries.pop("sum")
        if self._stats.cpu:
            resource_types.append(ResourceType.CPU)
        if self._stats.disk:
            resource_types.append(ResourceType.DISK)
        if self._stats.memory:
            resource_types.append(ResourceType.MEMORY)
        if self._stats.network:
            resource_types.append(ResourceType.NETWORK)
        for resource_type in resource_types:
            results.append(
                ResourceStatResults(
                    resource_type=resource_type,
                    average=self._summaries["average"][resource_type],
                    minimum=self._summaries["minimum"][resource_type],
                    maximum=self._summaries["maximum"][resource_type],
                    num_samples=self._count,
                ),
            )

        return ComputeNodeResourceStatResults(
            name=self.name,
            hostname=hostname,
            results=results,
        )

    @property
    def name(self):
        """Return the name of the monitor."""
        return self._monitor.name

    @property
    def stats(self):
        """Return the selected stats."""
        return self._stats

    @stats.setter
    def stats(self, stats: ComputeNodeResourceStatConfig):
        """Set the selected stats."""
        self._stats = stats

    def update_resource_stats(self, pids=None):
        """Update resource stats information for the current interval."""
        cur_stats = self._get_stats()
        for resource_type, stat_dict in self._last_stats.items():
            for stat_name, val in stat_dict.items():
                if val > self._summaries["maximum"][resource_type][stat_name]:
                    self._summaries["maximum"][resource_type][stat_name] = val
                elif val < self._summaries["minimum"][resource_type][stat_name]:
                    self._summaries["minimum"][resource_type][stat_name] = val
                self._summaries["sum"][resource_type][stat_name] += val

        if self._stats.process:
            if pids is None:
                raise Exception("pids cannot be None if process stats are enabled")
            cur_process_stats = self._get_process_stats(pids)
            for job_name, stat_dict in cur_process_stats.items():
                if job_name in self._process_summaries["maximum"]:
                    for stat_name, val in stat_dict.items():
                        if val > self._process_summaries["maximum"][job_name][stat_name]:
                            self._process_summaries["maximum"][job_name][stat_name] = val
                        elif val < self._process_summaries["minimum"][job_name][stat_name]:
                            self._process_summaries["minimum"][job_name][stat_name] = val
                        self._process_summaries["sum"][job_name][stat_name] += val
                    self._process_sample_count[job_name] += 1
                else:
                    for stat_name, val in stat_dict.items():
                        self._process_summaries["maximum"][job_name][stat_name] = val
                        self._process_summaries["minimum"][job_name][stat_name] = val
                        self._process_summaries["sum"][job_name][stat_name] = val
                    self._process_sample_count[job_name] = 1

        self._count += 1
        self._last_stats = cur_stats


def run_stat_aggregator(conn, stats, pids):
    """Run a ResourceMonitorAggregator in a loop. Must be called from a child process.

    Parameters
    ----------
    conn : multiprocessing.Pipe
        Child side of the pipe
    stats : ComputeNodeResourceStatConfig
    pids : dict | None
        Process IDs to monitor ({job_name: pid})

    """
    if stats.process and pids is None:
        raise Exception("pids must be a dict if process monitoring is enabled")

    agg = ResourceMonitorAggregator(stats)
    results = None
    while True:
        if conn.poll():
            cmd = conn.recv()
            logger.info("Received command %s", cmd["command"].value)
            match cmd["command"]:
                case IpcMonitorCommands.COMPLETE_JOBS:
                    results = agg.complete_process_stats(cmd["completed_job_names"])
                    conn.send(results)
                    pids = cmd["pids"]
                case IpcMonitorCommands.SELECT_STATS:
                    agg.stats = cmd["stats"]
                    pids = cmd["pids"]
                case IpcMonitorCommands.UPDATE_STATS:
                    pids = cmd["pids"]
                    agg.update_resource_stats(pids=pids)
                case IpcMonitorCommands.SHUTDOWN:
                    logger.info("Received shutdown command")
                    results = agg.finalize()
                    break
                case _:
                    raise Exception(f"Received unknown command: {cmd}")

        time.sleep(stats.interval)

    conn.send(results)


if __name__ == "__main__":
    name = "test_node"
    stats = ComputeNodeResourceStatConfig(process=False, name=name, interval=1)
    parent, child = multiprocessing.Pipe()
    proc = multiprocessing.Process(target=run_stat_aggregator, args=(child, stats, None))
    proc.start()
    time.sleep(2)
    stats.process = True
    parent.send(
        {
            "command": IpcMonitorCommands.SELECT_STATS,
            "stats": stats,
            "pids": {"my_process": os.getpid()},
        }
    )
    time.sleep(10)
    parent.send({"command": IpcMonitorCommands.SHUTDOWN})
    results = parent.recv()
    proc.join()
    print(results)
