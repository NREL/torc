import json
import logging
import multiprocessing
import re
import socket
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import psutil
from pydantic import BaseModel
from swagger_client import DefaultApi
from swagger_client.models.compute_nodes_model import ComputeNodesModel
from swagger_client.models.compute_node_stats_model import ComputeNodeStatsModel
from swagger_client.models.compute_node_stats_stats import ComputeNodeStatsStats
from swagger_client.models.edge_model import EdgeModel
from swagger_client.models.job_process_stats_model import JobProcessStatsModel
from swagger_client.models.worker_resources import WorkerResources

from .common import KiB, MiB, GiB, TiB
from .async_cli_command import AsyncCliCommand
from wms.resource_monitor import (
    ComputeNodeResourceStatConfig,
    ComputeNodeResourceStatResults,
    IpcMonitorCommands,
    ProcessStatResults,
    ResourceType,
    run_stat_aggregator,
)
from wms.utils.filesystem_factory import make_path
from wms.utils.timing import timer_stats_collector, Timer

logger = logging.getLogger(__name__)


class JobRunner:
    def __init__(
        self,
        api: DefaultApi,
        output_dir: Path,
        job_completion_poll_interval=1,
        database_poll_interval=600,
        time_limit=None,
        resources=None,
        stats=None,
    ):
        self._api = api
        self._outstanding_jobs = {}
        self._poll_interval = job_completion_poll_interval
        self._db_poll_interval = database_poll_interval
        self._output_dir = output_dir
        self._orig_resources = resources or _get_system_resources(time_limit)
        self._resources = WorkerResources(**self._orig_resources.to_dict())
        self._num_jobs = 0
        self._last_db_poll_time = 0
        self._compute_node_db_id = None
        self._stats = stats or ComputeNodeResourceStatConfig.disabled()
        self._parent_monitor_conn = None
        self._monitor_proc = None
        self._pids = {}

    def __del__(self):
        if self._outstanding_jobs:
            logger.warning("JobRunner destructed with outstanding jobs", self._outstanding_jobs)
        if self._parent_monitor_conn is not None or self._monitor_proc is not None:
            logger.warning("JobRunner destructed without stopping the resource monitor process.")

    def check_completions(self):
        done_jobs = []
        db_jobs = {}
        for job in self._outstanding_jobs.values():
            if job.is_complete():
                done_jobs.append(job.result)
                db_jobs[job.name] = job.job
                self._increment_resources(job.job)
                self._log_job_complete_event(job.name)
                self._update_file_info(job)
                self._num_jobs += 1

        for result in done_jobs:
            self._outstanding_jobs.pop(result.name)
            if self._stats.process:
                self._pids.pop(result.name)
            cur_job = send_api_command(self._api.get_jobs_name, result.name)
            # TODO: track _rev correctly
            # complete_job(self._api, db_jobs[result.name], result)
            self._complete_job(cur_job, result)

        logger.info("Found %s completions", len(done_jobs))

        return len(done_jobs)

    def run_worker(self, scheduler=None):
        if self._stats.process:
            self._start_resource_monitor()

        try:
            self._run_worker(scheduler)
        finally:
            if self._stats.process:
                self._stop_resource_monitor()

    def _run_worker(self, scheduler):
        start = time.time()
        hostname = socket.gethostname()
        event = {
            "category": "worker",
            "type": "start",
            "node_name": hostname,
            "message": f"Worker started on {hostname}",
        }
        event.update(**self._orig_resources.to_dict())
        send_api_command(self._api.post_events, event)
        compute_node = ComputeNodesModel(
            hostname=hostname,
            start_time=str(datetime.now()),
            resources=self._orig_resources,
            is_active=True,
            scheduler=scheduler or {},
        )
        compute_node = send_api_command(self._api.post_compute_nodes, compute_node)
        self._compute_node_db_id = compute_node._id
        self._run_ready_jobs()
        self.wait()
        compute_node.is_active = False
        send_api_command(self._api.put_compute_nodes_key, compute_node, compute_node._key)
        send_api_command(
            self._api.post_events,
            {
                "category": "worker",
                "type": "complete",
                "num_jobs": self._num_jobs,
                "duration_seconds": time.time() - start,
                "message": f"Worker completed on {hostname}",
            },
        )

    def wait(self):
        """Return once all jobs have completed."""
        timeout = _get_timeout(self._resources.time_limit)
        start_time = time.time()

        def timed_out():
            return time.time() - start_time > timeout

        while (
            not send_api_command(self._api.get_workflow_is_complete).is_complete or not timed_out()
        ):
            num_completed = self.check_completions()
            num_started = 0
            if num_completed > 0 or self._is_time_to_poll_database():
                num_started = self._run_ready_jobs()

            if num_started == 0 and not self._outstanding_jobs:
                if send_api_command(self._api.get_workflow_is_complete).is_complete:
                    logger.info("Workflow is complete.")
                else:
                    # TODO: if there is remaining time for this node, consider waiting for new
                    # jobs to become available.
                    logger.info(
                        "No jobs are outstanding on this node and no new jobs are available."
                    )
                break

            if num_completed > 0 or num_started > 0:
                self._update_pids_to_monitor()

            time.sleep(self._poll_interval)
            # TODO: check time remaining and then for interruptible jobs

        self._pids.clear()
        self._update_pids_to_monitor()

    def _complete_job(self, job, result):
        job.return_code = result.return_code
        job = send_api_command(
            self._api.post_jobs_complete_job_name_status_rev,
            result,
            job.name,
            "done",
            job._rev,
        )
        return job

    def _current_memory_allocation_percentage(self):
        return self._resources.memory_gb / self._orig_resources.memory_gb * 100

    def _decrement_resources(self, job):
        job_resources = send_api_command(self._api.get_jobs_resource_requirements_name, job.name)
        job_memory_gb = get_memory_gb(job_resources.memory)
        self._resources.num_cpus -= job_resources.num_cpus
        self._resources.num_gpus -= job_resources.num_gpus
        self._resources.memory_gb -= job_memory_gb
        assert self._resources.num_cpus >= 0.0, self._resources.num_cpus
        assert self._resources.num_gpus >= 0.0, self._resources.num_gpus
        assert self._resources.memory_gb >= 0.0, self._resources.memory_gb

    def _increment_resources(self, job):
        job_resources = send_api_command(self._api.get_jobs_resource_requirements_name, job.name)
        job_memory_gb = get_memory_gb(job_resources.memory)
        self._resources.num_cpus += job_resources.num_cpus
        self._resources.num_gpus += job_resources.num_gpus
        self._resources.memory_gb += job_memory_gb
        assert self._resources.num_cpus <= self._orig_resources.num_cpus, self._resources.num_cpus
        assert self._resources.num_gpus <= self._orig_resources.num_gpus, self._resources.num_gpus
        assert (
            self._resources.memory_gb <= self._orig_resources.memory_gb
        ), self._resources.memory_gb

    def _is_time_to_poll_database(self):
        if (time.time() - self._db_poll_interval) < self._last_db_poll_time:
            return False

        # TODO: needs to be more sophisticated
        # The main point is to provide a way to avoid hundreds of compute nodes unnecessarily
        # asking the database for jobs when it's highly unlikely to get any.
        # It would be better if the database or some middleware could publish events when
        # new jobs are ready to run.
        return self._resources.num_cpus > 0 and self._current_memory_allocation_percentage() > 10

    def _log_job_start_event(self, job_name: str):
        send_api_command(
            self._api.post_events,
            {
                "category": "job",
                "type": "start",
                "name": job_name,
                "node_name": socket.gethostname(),
                "message": f"Started job {job_name}",
            },
        )

    def _log_job_complete_event(self, job_name: str):
        send_api_command(
            self._api.post_events,
            {
                "category": "job",
                "type": "complete",
                "name": job_name,
                "node_name": socket.gethostname(),
                "message": f"Completed job {job_name}",
            },
        )

    def _run_job(self, job: AsyncCliCommand):
        job.run(self._output_dir)
        job.job = self._set_job_status(job.job, "submitted")
        self._outstanding_jobs[job.name] = job
        if self._stats.process:
            self._pids[job.name] = job.pid
        send_api_command(
            self._api.post_edges_name,
            EdgeModel(_from=self._compute_node_db_id, to=job.job._id),
            "executed",
        )
        logger.debug("Started job %s", job.name)
        self._log_job_start_event(job.name)

    def _run_ready_jobs(self):
        ready_jobs = send_api_command(
            self._api.post_workflow_prepare_jobs_for_submission,
            self._resources,
        )
        logger.info("%s jobs are ready for submission", len(ready_jobs))
        for job in ready_jobs:
            self._run_job(AsyncCliCommand(job))
            self._decrement_resources(job)

        self._last_db_poll_time = time.time()
        return len(ready_jobs)

    def _set_job_status(self, job, status):
        job.status = status
        try:
            job = send_api_command(self._api.put_jobs_name, job, job.name)
        except Exception:
            logger.exception("Fail to set job %s status to %s", job.name, job.status)
            raise
        logger.info("Set job %s status=%s", job._id, status)
        return job

    def _start_resource_monitor(self):
        self._parent_monitor_conn, child_conn = multiprocessing.Pipe()
        pids = self._pids if self._stats.process else None
        self._monitor_proc = multiprocessing.Process(
            target=run_stat_aggregator, args=(child_conn, self._stats, pids)
        )
        self._monitor_proc.start()

    def _stop_resource_monitor(self):
        self._parent_monitor_conn.send({"command": IpcMonitorCommands.SHUTDOWN})
        has_results = False
        for _ in range(30):
            if self._parent_monitor_conn.poll():
                has_results = True
                break
            time.sleep(1)
        if has_results:
            results = self._parent_monitor_conn.recv()
            if results.results:
                self._post_compute_node_stats(results)
            self._monitor_proc.join()
        else:
            logger.error("Failed to receive results from resource monitor.")
        self._parent_monitor_conn = None
        self._monitor_proc = None

    def _update_pids_to_monitor(self):
        if self._stats.process:
            self._parent_monitor_conn.send(
                {"command": IpcMonitorCommands.SET_PIDS, "pids": self._pids}
            )

    def _post_compute_node_stats(self, results: ComputeNodeResourceStatResults):
        res = send_api_command(
            self._api.post_compute_node_stats,
            ComputeNodeStatsModel(
                name=results.name,
                hostname=results.name,
                # These json methods let Pydantic run its data type conversions.
                stats=[ComputeNodeStatsStats(**json.loads(x.json())) for x in results.results],
                timestamp=str(datetime.now()),
            ),
        )
        send_api_command(
            self._api.post_edges_name,
            EdgeModel(_from=self._compute_node_db_id, to=res._id),
            "node_used",
        )

        for result in results.results:
            if result.resource_type == ResourceType.PROCESS:
                self._post_job_process_stats(result)

    def _post_job_process_stats(self, result: ProcessStatResults):
        # TODO: need to connect this to specific job runs
        # TODO: Run this whenever a job completes
        res = send_api_command(
            self._api.post_job_process_stats,
            JobProcessStatsModel(
                avg_cpu_percent=result.average["cpu_percent"],
                max_cpu_percent=result.maximum["cpu_percent"],
                avg_rss=result.average["rss"],
                max_rss=result.maximum["rss"],
                num_samples=result.num_samples,
                job_name=result.job_name,
                timestamp=str(datetime.now()),
            ),
        )
        send_api_command(
            self._api.post_edges_name,
            EdgeModel(_from=f"jobs/{result.job_name}", to=res._id),
            "process_used",
        )

    def _update_file_info(self, job):
        for file in send_api_command(self._api.get_files_produced_by_job_name, job.name).items:
            path = make_path(file.path)
            # file.file_hash = compute_file_hash(path)
            file.st_mtime = path.stat().st_mtime
            send_api_command(self._api.put_files_name, file, file.name)


def _get_system_resources(time_limit):
    return WorkerResources(
        num_cpus=psutil.cpu_count(),
        memory_gb=psutil.virtual_memory().total / GiB,
        num_nodes=1,
        time_limit=time_limit,
        num_gpus=0,  # TODO
    )


def get_memory_gb(memory):
    return get_memory_in_bytes(memory) / GiB


def get_memory_in_bytes(memory: str):
    match = re.search(r"^([0-9]+)$", memory)
    if match is not None:
        return int(match.group(1))

    match = re.search(r"^([0-9]+)\s*([kmgtKMGT])$", memory)
    if match is None:
        raise ValueError(f"{memory} is an invalid memory value")

    size = int(match.group(1))
    units = match.group(2).lower()
    if units == "k":
        size *= KiB
    elif units == "m":
        size *= MiB
    elif units == "g":
        size *= GiB
    elif units == "t":
        size *= TiB
    else:
        raise ValueError(f"{units} is an invalid memory unit")

    return size


# This pydantic code will convert ISO 8601 duration strings to timedelta.
class _TimeLimitModel(BaseModel):
    time_limit: timedelta


def convert_end_time_to_duration_str(end_time: datetime):
    duration = end_time - datetime.now()
    return json.loads(_TimeLimitModel(time_limit=duration).json())["time_limit"]


def _get_timeout(time_limit):
    return (
        sys.maxsize
        if time_limit is None
        else _TimeLimitModel(time_limit=time_limit).time_limit.total_seconds()
    )


def send_api_command(func, *args, **kwargs):
    with Timer(timer_stats_collector, func.__name__):
        return func(*args, **kwargs)
