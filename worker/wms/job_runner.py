"""Runs jobs on a compute node"""

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
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from swagger_client import DefaultApi
from swagger_client.models.compute_nodes_model import ComputeNodesModel
from swagger_client.models.compute_node_stats_model import ComputeNodeStatsModel
from swagger_client.models.compute_node_stats_stats import ComputeNodeStatsStats
from swagger_client.models.edge_model import EdgeModel
from swagger_client.models.job_process_stats_model import JobProcessStatsModel
from swagger_client.models.workflow_prepare_jobs_for_submission_model import (
    WorkflowPrepareJobsForSubmissionModel,
)

from wms.api import send_api_command
from wms.resource_monitor import (
    ComputeNodeResourceStatResults,
    IpcMonitorCommands,
    ProcessStatResults,
    ResourceType,
    run_stat_aggregator,
)
from wms.utils.filesystem_factory import make_path
from wms.utils.timing import timer_stats_collector, Timer
from .async_cli_command import AsyncCliCommand
from .common import KiB, MiB, GiB, TiB

logger = logging.getLogger(__name__)


class JobRunner:
    """Runs jobs on a compute node"""

    def __init__(
        self,
        api: DefaultApi,
        output_dir: Path,
        job_completion_poll_interval=10,
        database_poll_interval=600,
        time_limit=None,
        resources=None,
        scheduler_config_id=None,
    ):
        """Constructs a JobRunner.

        Parameters
        ----------
        api : DefaultApi
        output_dir : Path
            Directory for output files
        job_completion_poll_interval : int
            Interval in seconds in which to poll for job completions.
        database_poll_interval : int
            Max time in seconds in which the code should poll for job updates in the database.
        time_limit : None | str
            ISO 8601 time duration string. If None then there is no time limit.
        resources : None | WorkflowPrepareJobsForSubmissionModel
            Resources of the compute node. If None, make system calls to check resources.
        scheduler_config_id : str
            ID of the scheduler config used to acquire this compute node.
            If set, use this ID to pull matching jobs. If not set, pull any job that meets the
            resource availability.
        """
        self._api = api
        self._outstanding_jobs = {}
        self._poll_interval = job_completion_poll_interval
        self._db_poll_interval = database_poll_interval
        self._output_dir = output_dir
        self._scheduler_config_id = scheduler_config_id
        self._orig_resources = resources or _get_system_resources(time_limit)
        self._orig_resources.scheduler_config_id = self._scheduler_config_id
        self._resources = WorkflowPrepareJobsForSubmissionModel(**self._orig_resources.to_dict())
        self._num_jobs = 0
        self._last_db_poll_time = 0
        self._compute_node_db_id = None
        self._stats = api.get_workflow_config().compute_node_resource_stats
        self._parent_monitor_conn = None
        self._monitor_proc = None
        self._pids = {}
        self._jobs_pending_process_stat_completion = []

    def __del__(self):
        if self._outstanding_jobs:
            logger.warning(
                "JobRunner destructed with outstanding jobs: %s",
                self._outstanding_jobs.keys(),
            )
        if self._parent_monitor_conn is not None or self._monitor_proc is not None:
            logger.warning("JobRunner destructed without stopping the resource monitor process.")

    def run_worker(self, scheduler=None):
        """Run jobs from a worker process.

        Parameters
        ----------
        scheduler : None | dict
            Scheduler configuration parameters. Used only for logs and events.

        """
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
        self._compute_node_db_id = compute_node._id  # pylint: disable=protected-access
        self.wait()
        compute_node.is_active = False
        send_api_command(
            self._api.put_compute_nodes_key, compute_node, compute_node.key
        )  # ,  # pylint: disable=protected-access)
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
            status = send_api_command(self._api.get_workflow_status)
            if status.is_canceled:
                logger.info("Detected a canceled workflow. Cancel all outstanding jobs and exit.")
                num_completed = self._cancel_outstanding_jobs()
                break

            num_completed = self._process_completions(cancel=False)
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

            if num_started > 0:
                self._update_pids_to_monitor()
            if num_completed > 0:
                self._handle_completed_process_stats()
                self._update_pids_to_monitor()

            time.sleep(self._poll_interval)
            # TODO: check time remaining and then for interruptible jobs

        self._pids.clear()
        self._handle_completed_process_stats()
        self._update_pids_to_monitor()

    def _cancel_outstanding_jobs(self):
        return self._process_completions(cancel=True)

    def _complete_job(self, job, result):
        job = send_api_command(
            self._api.post_jobs_complete_job_key_status_rev,
            result,
            job.name,
            "done",
            job._rev,  # pylint: disable=protected-access
        )
        return job

    def _current_memory_allocation_percentage(self):
        return self._resources.memory_gb / self._orig_resources.memory_gb * 100

    def _decrement_resources(self, job):
        job_resources = send_api_command(self._api.get_jobs_resource_requirements_key, job.name)
        job_memory_gb = get_memory_gb(job_resources.memory)
        self._resources.num_cpus -= job_resources.num_cpus
        self._resources.num_gpus -= job_resources.num_gpus
        self._resources.memory_gb -= job_memory_gb
        assert self._resources.num_cpus >= 0.0, self._resources.num_cpus
        assert self._resources.num_gpus >= 0.0, self._resources.num_gpus
        assert self._resources.memory_gb >= 0.0, self._resources.memory_gb

    def _increment_resources(self, job):
        job_resources = send_api_command(self._api.get_jobs_resource_requirements_key, job.name)
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

    def _log_job_complete_event(self, job_name: str, status: str):
        send_api_command(
            self._api.post_events,
            {
                "category": "job",
                "type": "complete",
                "name": job_name,
                "status": status,
                "node_name": socket.gethostname(),
                "message": f"Completed job {job_name}",
            },
        )

    def _process_completions(self, cancel=False):
        done_jobs = []
        db_jobs = {}
        for job in self._outstanding_jobs.values():
            if cancel:
                job.cancel()
            if job.is_complete():
                result = job.get_result()
                done_jobs.append(result)
                db_jobs[job.name] = job.db_job
                self._increment_resources(job.db_job)
                self._log_job_complete_event(job.name, result.status)
                if not cancel:
                    self._update_file_info(job)
                    self._num_jobs += 1

        for result in done_jobs:
            self._outstanding_jobs.pop(result.name)
            if self._stats.process:
                self._jobs_pending_process_stat_completion.append(result.name)
                self._pids.pop(result.name)
            self._complete_job(db_jobs[result.name], result)

        if done_jobs:
            logger.info("Found %s completions", len(done_jobs))
        else:
            logger.debug("Found 0 completions")
        return len(done_jobs)

    def _run_job(self, job: AsyncCliCommand):
        job.run(self._output_dir)
        job.db_job.run_id += 1
        # The database changes db_job._rev on every update.
        # This reassigns job.db_job in order to stay current.
        job.db_job = send_api_command(self._api.put_jobs_key, job.db_job, job.name)
        job.db_job = send_api_command(
            self._api.put_jobs_manage_status_change_key_status_rev,
            job.name,
            "submitted",
            job.db_job._rev,  # pylint: disable=protected-access
        )
        self._outstanding_jobs[job.name] = job
        if self._stats.process:
            self._pids[job.name] = job.pid
        send_api_command(
            self._api.post_edges_name,
            EdgeModel(
                _from=self._compute_node_db_id,
                to=job.db_job._id,  # pylint: disable=protected-access
            ),
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

    def _handle_completed_process_stats(self):
        if self._stats.process:
            self._parent_monitor_conn.send(
                {
                    "command": IpcMonitorCommands.COMPLETE_JOBS,
                    "pids": self._pids,
                    "completed_job_names": self._jobs_pending_process_stat_completion,
                }
            )
            with Timer(timer_stats_collector, "receive_process_stats"):
                results = self._parent_monitor_conn.recv()
            for result in results.results:
                self._post_job_process_stats(result)
            if results.results:
                send_api_command(
                    self._api.post_compute_node_stats,
                    ComputeNodeStatsModel(
                        name=results.name,
                        hostname=results.name,
                        # These json methods let Pydantic run its data type conversions.
                        stats=[
                            ComputeNodeStatsStats(**json.loads(x.json())) for x in results.results
                        ],
                        timestamp=str(datetime.now()),
                    ),
                )
            self._jobs_pending_process_stat_completion.clear()

    def _update_pids_to_monitor(self):
        if self._stats.process:
            self._parent_monitor_conn.send(
                {"command": IpcMonitorCommands.UPDATE_STATS, "pids": self._pids}
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
            EdgeModel(
                _from=self._compute_node_db_id,
                to=res._id,  # pylint: disable=protected-access
            ),
            "node_used",
        )

        for result in results.results:
            assert result.resource_type != ResourceType.PROCESS, result

    def _post_job_process_stats(self, result: ProcessStatResults):
        run_id = send_api_command(self._api.get_jobs_key, result.job_name).run_id
        res = send_api_command(
            self._api.post_job_process_stats,
            JobProcessStatsModel(
                avg_cpu_percent=result.average["cpu_percent"],
                max_cpu_percent=result.maximum["cpu_percent"],
                avg_rss=result.average["rss"],
                max_rss=result.maximum["rss"],
                num_samples=result.num_samples,
                job_name=result.job_name,
                run_id=run_id,
                timestamp=str(datetime.now()),
            ),
        )
        send_api_command(
            self._api.post_edges_name,
            EdgeModel(
                _from=f"jobs/{result.job_name}",
                to=res._id,  # pylint: disable=protected-access
            ),
            "process_used",
        )

    def _update_file_info(self, job):
        for file in send_api_command(self._api.get_files_produced_by_job_key, job.name).items:
            path = make_path(file.path)
            # file.file_hash = compute_file_hash(path)
            file.st_mtime = path.stat().st_mtime
            send_api_command(self._api.put_files_key, file, file.name)


def _get_system_resources(time_limit):
    return WorkflowPrepareJobsForSubmissionModel(
        num_cpus=psutil.cpu_count(),
        memory_gb=psutil.virtual_memory().total / GiB,
        num_nodes=1,
        time_limit=time_limit,
        num_gpus=0,  # TODO
    )


def get_memory_gb(memory):
    """Converts a memory defined as a string to GiB.

    Parameters
    ----------
    memory : str
        Memory as string with units, such as '10g'

    Returns
    -------
    int
    """
    return get_memory_in_bytes(memory) / GiB


def get_memory_in_bytes(memory: str):
    """Converts a memory defined as a string to bytes.

    Parameters
    ----------
    memory : str
        Memory as string with units, such as '10g'

    Returns
    -------
    int
    """
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
    """Convert an end time timestamp to an ISO 8601 duration string, relative to current time."""
    duration = end_time - datetime.now()
    return json.loads(_TimeLimitModel(time_limit=duration).json())["time_limit"]


def _get_timeout(time_limit):
    return (
        sys.maxsize
        if time_limit is None
        else _TimeLimitModel(time_limit=time_limit).time_limit.total_seconds()
    )
