"""Monitors resource utilization statistics"""

import logging
import socket
import time

import psutil


logger = logging.getLogger(__name__)

ONE_MB = 1024 * 1024


class ResourceMonitor:
    """Monitors resource utilization statistics"""

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

    def __init__(self, name=None):
        self._name = name or socket.gethostname()
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

    def clear_stale_processes(self, cur_pids):
        """Remove cached process objects that are no longer running."""
        self._cached_processes = {
            pid: proc for pid, proc in self._cached_processes.items() if pid in cur_pids
        }

    def get_process_stats(self, pid, include_children=True, recurse_children=False):
        """Gets current process stats. Returns None if the pid does not exist."""
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
                if include_children:
                    for child in process.children(recursive=recurse_children):
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

    @property
    def name(self):
        """Return the name of the monitor."""
        return self._name
