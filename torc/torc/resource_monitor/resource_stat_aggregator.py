"""Aggregates resource stats"""

import logging
import socket
import sys
from collections import defaultdict

from torc.resource_monitor.models import (
    ComputeNodeResourceStatResults,
    ProcessStatResults,
    ResourceStatResults,
    ResourceType,
    ComputeNodeResourceStatConfig,
)


logger = logging.getLogger(__name__)


class ResourceStatAggregator:
    """Aggregates resource utilization stats in memory."""

    def __init__(self, config: ComputeNodeResourceStatConfig, stats):
        self._config = config
        self._count = 0
        self._last_stats = stats
        self._summaries = {
            "average": defaultdict(dict),
            "maximum": defaultdict(dict),
            "minimum": defaultdict(dict),
            "sum": defaultdict(dict),
        }
        for resource_type, stat_dict in self._last_stats.items():
            if resource_type != ResourceType.PROCESS:
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
                hostname=hostname,
                results=results,
            )

        for resource_type, stat_dict in self._summaries["sum"].items():
            for stat_name, val in stat_dict.items():
                self._summaries["average"][resource_type][stat_name] = val / self._count

        self._summaries.pop("sum")
        if self._config.cpu:
            resource_types.append(ResourceType.CPU)
        if self._config.disk:
            resource_types.append(ResourceType.DISK)
        if self._config.memory:
            resource_types.append(ResourceType.MEMORY)
        if self._config.network:
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
            hostname=hostname,
            results=results,
        )

    @property
    def config(self):
        """Return the selected stats config."""
        return self._config

    @config.setter
    def config(self, config: ComputeNodeResourceStatConfig):
        """Set the selected stats config."""
        self._config = config

    def update_stats(self, cur_stats):
        """Update resource stats information for the current interval."""
        for resource_type, stat_dict in cur_stats.items():
            if resource_type == ResourceType.PROCESS:
                continue
            for stat_name, val in stat_dict.items():
                if val > self._summaries["maximum"][resource_type][stat_name]:
                    self._summaries["maximum"][resource_type][stat_name] = val
                elif val < self._summaries["minimum"][resource_type][stat_name]:
                    self._summaries["minimum"][resource_type][stat_name] = val
                self._summaries["sum"][resource_type][stat_name] += val

        if self._config.process:
            for job_name, stat_dict in cur_stats[ResourceType.PROCESS].items():
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
