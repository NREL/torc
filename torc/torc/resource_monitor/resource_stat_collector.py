"""Monitors resource utilization statistics"""

import logging
import time

import psutil

from .models import ResourceType, ComputeNodeResourceStatConfig


logger = logging.getLogger(__name__)

ONE_MB = 1024 * 1024


class ResourceStatCollector:
    """Collects resource utilization statistics"""

    DISK_STATS = (
        "read_count",
        "write_count",
        "read_bytes",
        "write_bytes",
        "read_time",
        "write_time",
    )
    NET_STATS = (
        "bytes_recv",
        "bytes_sent",
        "dropin",
        "dropout",
        "errin",
        "errout",
        "packets_recv",
        "packets_sent",
    )

    def __init__(self):
        self._last_disk_check_time = None
        self._last_net_check_time = None
        self._update_disk_stats(psutil.disk_io_counters())
        self._update_net_stats(psutil.net_io_counters())
        self._cached_processes = {}  # pid to psutil.Process

    def _update_disk_stats(self, data):
        for stat in self.DISK_STATS:
            setattr(self, stat, getattr(data, stat, 0))
        self._last_disk_check_time = time.time()

    def _update_net_stats(self, data):
        for stat in self.NET_STATS:
            setattr(self, stat, getattr(data, stat, 0))
        self._last_net_check_time = time.time()

    def get_stats(self, config: ComputeNodeResourceStatConfig, pids=None):
        """Return a dict keyed by ResourceType of all enabled stats."""
        data = {}
        if config.cpu:
            data[ResourceType.CPU] = self.get_cpu_stats()
        if config.disk:
            data[ResourceType.DISK] = self.get_disk_stats()
        if config.memory:
            data[ResourceType.MEMORY] = self.get_memory_stats()
        if config.network:
            data[ResourceType.NETWORK] = self.get_network_stats()
        if config.process:
            if pids is None:
                raise Exception("pids cannot be None if process stats are enabled")
            data[ResourceType.PROCESS] = self.get_processes_stats(pids, config)
        return data

    def get_cpu_stats(self):
        """Gets CPU current resource stats information."""
        stats = psutil.cpu_times_percent()._asdict()
        stats["cpu_percent"] = psutil.cpu_percent()
        return stats

    def get_disk_stats(self):
        """Gets current disk stats."""
        data = psutil.disk_io_counters()
        stats = {
            "elapsed_seconds": time.time() - self._last_disk_check_time,
        }
        for stat in self.DISK_STATS:
            stats[stat] = getattr(data, stat, 0) - getattr(self, stat, 0)
        stats["read MB/s"] = self._mb_per_sec(stats["read_bytes"], stats["elapsed_seconds"])
        stats["write MB/s"] = self._mb_per_sec(stats["write_bytes"], stats["elapsed_seconds"])
        stats["read IOPS"] = float(stats["read_count"]) / stats["elapsed_seconds"]
        stats["write IOPS"] = float(stats["write_count"]) / stats["elapsed_seconds"]
        self._update_disk_stats(data)
        return stats

    def get_memory_stats(self):
        """Gets current memory resource stats."""
        return psutil.virtual_memory()._asdict()

    def get_network_stats(self):
        """Gets current network stats."""
        data = psutil.net_io_counters()
        stats = {
            "elapsed_seconds": time.time() - self._last_net_check_time,
        }
        for stat in self.NET_STATS:
            stats[stat] = getattr(data, stat, 0) - getattr(self, stat, 0)
        stats["recv MB/s"] = self._mb_per_sec(stats["bytes_recv"], stats["elapsed_seconds"])
        stats["sent MB/s"] = self._mb_per_sec(stats["bytes_sent"], stats["elapsed_seconds"])
        self._update_net_stats(data)
        return stats

    def _get_process(self, pid):
        process = self._cached_processes.get(pid)
        if process is None:
            try:
                process = psutil.Process(pid)
                # Initialize CPU utilization tracking per psutil docs.
                process.cpu_percent(interval=0.2)
                self._cached_processes[pid] = process
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                logger.debug("Tried to construct Process for invalid pid=%s", pid)
                return None

        return process

    def clear_cache(self):
        """Clear all cached data."""
        self._cached_processes.clear()

    def clear_stale_processes(self, cur_pids):
        """Remove cached process objects that are no longer running."""
        for pid in [x for x in self._cached_processes if x not in cur_pids]:
            self._cached_processes.pop(pid)

    def get_processes_stats(self, pids, config: ComputeNodeResourceStatConfig):
        """Return stats for multiple processes."""
        stats = {}
        cur_pids = set()
        for name, pid in pids.items():
            _stats, children = self.get_process_stats(pid, config)
            if _stats is not None:
                stats[name] = _stats
                cur_pids.add(pid)
                for child in children:
                    cur_pids.add(child)

        self.clear_stale_processes(cur_pids)
        return stats

    def get_process_stats(self, pid, config: ComputeNodeResourceStatConfig):
        """Return stats for one process. Returns None if the pid does not exist."""
        children = []
        process = self._get_process(pid)
        if process is None:
            return None, children
        try:
            with process.oneshot():
                stats = {
                    "rss": process.memory_info().rss,
                    "cpu_percent": process.cpu_percent(),
                }
                if config.include_child_processes:
                    for child in process.children(recursive=config.recurse_child_processes):
                        cached_child = self._get_process(child.pid)
                        if cached_child is not None:
                            stats["cpu_percent"] += cached_child.cpu_percent()
                            stats["rss"] += cached_child.memory_info().rss
                            children.append(child.pid)
                return stats, children
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            logger.debug("Tried to get process info for invalid pid=%s", pid)
            return None, []

    @staticmethod
    def _mb_per_sec(num_bytes, elapsed_seconds):
        return float(num_bytes) / ONE_MB / elapsed_seconds
