"""Performs resource utilization monitoring."""

import logging
import tempfile
import time
from pathlib import Path

from torc.resource_monitor.models import (
    ComputeNodeResourceStatConfig,
    IpcMonitorCommands,
)
from torc.resource_monitor.resource_stat_collector import ResourceStatCollector
from torc.resource_monitor.resource_stat_aggregator import ResourceStatAggregator
from torc.resource_monitor.resource_stat_store import ResourceStatStore


logger = logging.getLogger(__name__)


def run_monitor_async(conn, config: ComputeNodeResourceStatConfig, pids, path=None):
    """Run a ResourceStatAggregator in a loop. Must be called from a child process.

    Parameters
    ----------
    conn : multiprocessing.Pipe
        Child side of the pipe
    config : ComputeNodeResourceStatConfig
    pids : dict | None
        Process IDs to monitor ({job_key: pid})
    path : Path | None
        Path to store database if monitor_type = "periodic"

    """
    if config.process and pids is None:
        raise Exception("pids must be a dict if process monitoring is enabled")

    logger.info("Monitor resource utilization with config=%s", config)
    collector = ResourceStatCollector()
    stats = collector.get_stats(ComputeNodeResourceStatConfig.all_enabled(), pids={})
    agg = ResourceStatAggregator(config, stats)
    if config.monitor_type == "periodic" and path is None:
        raise Exception("path must be set if monitor_type is periodic")
    store = ResourceStatStore(config, path, stats) if config.monitor_type == "periodic" else None

    results = None
    cmd_poll_interval = 1
    last_job_poll_time = 0
    while True:
        cur_time = time.time()
        if cur_time - last_job_poll_time < config.interval:
            time.sleep(cmd_poll_interval)
            continue
        last_job_poll_time = cur_time
        if conn.poll():
            cmd = conn.recv()
            logger.info("Received command %s", cmd["command"].value)
            match cmd["command"]:
                case IpcMonitorCommands.COMPLETE_JOBS:
                    results = agg.complete_process_stats(cmd["completed_job_keys"])
                    conn.send(results)
                    pids = cmd["pids"]
                case IpcMonitorCommands.SELECT_STATS:
                    config = cmd["config"]
                    agg.config = config
                    if store is not None:
                        store.config = config
                    pids = cmd["pids"]
                case IpcMonitorCommands.UPDATE_PIDS:
                    pids = cmd["pids"]
                case IpcMonitorCommands.SHUTDOWN:
                    results = agg.finalize()
                    if store is not None:
                        store.flush()
                        if config.make_plots:
                            store.plot_to_file()
                    break
                case _:
                    raise Exception(f"Received unknown command: {cmd}")

        stats = collector.get_stats(config, pids=pids)
        agg.update_stats(stats)
        if store is not None:
            store.record_stats(stats)

        time.sleep(cmd_poll_interval)

    conn.send(results)
    collector.clear_cache()


def run_monitor_sync(config: ComputeNodeResourceStatConfig, pids, duration_seconds, path=None):
    """Run a ResourceStatAggregator in a loop.

    Parameters
    ----------
    config : ComputeNodeResourceStatConfig
    pids : dict | None
        Process IDs to monitor ({job_key: pid})
    path : Path | None
        Path to store database if monitor_type = "periodic"

    """
    if config.process and pids is None:
        raise Exception("pids must be a dict if process monitoring is enabled")

    collector = ResourceStatCollector()
    stats = collector.get_stats(ComputeNodeResourceStatConfig.all_enabled(), pids={})
    agg = ResourceStatAggregator(config, stats)
    if config.monitor_type == "periodic" and path is None:
        raise Exception("path must be set if monitor_type is periodic")
    store = ResourceStatStore(config, path, stats) if config.monitor_type == "periodic" else None

    end_time = time.time() + duration_seconds
    while time.time() < end_time:
        stats = collector.get_stats(config, pids=pids)
        agg.update_stats(stats)
        if store is not None:
            store.record_stats(stats)

        time.sleep(config.interval)

    results = agg.finalize()
    if store is not None:
        store.flush()
        store.plot_to_file()
    collector.clear_cache()
    return results


def _test_run_monitor_sync():
    db_file = Path(tempfile.gettempdir()) / "tmp_db.sqlite"
    config = ComputeNodeResourceStatConfig(
        process=False,
        interval=1,
        monitor_type="periodic",
    )
    try:
        results = run_monitor_sync(config, None, 10, db_file)
        print(results)
    finally:
        if db_file.exists():
            db_file.unlink()


if __name__ == "__main__":
    _test_run_monitor_sync()
