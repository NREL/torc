"""Runs jobs on a compute node"""

import json
import logging
import os
import multiprocessing
import re
import socket
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import psutil
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from pydantic.json import timedelta_isoformat  # pylint: disable=no-name-in-module
from swagger_client import DefaultApi
from swagger_client.models.workflow_compute_nodes_model import WorkflowComputeNodesModel
from swagger_client.models.workflow_compute_node_stats_model import (
    WorkflowComputeNodeStatsModel,
)
from swagger_client.models.workflowsworkflowcompute_node_stats_stats import (
    WorkflowsworkflowcomputeNodeStatsStats,
)
from swagger_client.models.edges_name_model import EdgesNameModel
from swagger_client.models.workflow_job_process_stats_model import (
    WorkflowJobProcessStatsModel,
)
from swagger_client.models.prepare_jobs_for_submission_key_model import (
    PrepareJobsForSubmissionKeyModel,
)
from swagger_client.models.workflows_model import WorkflowsModel

from torc.api import send_api_command, iter_documents
from torc.common import JOB_STDIO_DIR, STATS_DIR
from torc.resource_monitor.models import (
    ComputeNodeResourceStatConfig,
    ComputeNodeResourceStatResults,
    IpcMonitorCommands,
    ProcessStatResults,
    ResourceType,
)
from torc.resource_monitor.resource_monitor import run_monitor_async
from torc.utils.filesystem_factory import make_path
from torc.utils.timing import timer_stats_collector, Timer
from .async_cli_command import AsyncCliCommand
from .common import KiB, MiB, GiB, TiB

JOB_COMPLETION_POLL_INTERVAL = 60

logger = logging.getLogger(__name__)


class JobRunner:
    """Runs jobs on a compute node"""

    def __init__(
        self,
        api: DefaultApi,
        workflow: WorkflowsModel,
        output_dir: Path,
        job_completion_poll_interval=JOB_COMPLETION_POLL_INTERVAL,
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
        resources : None | PrepareJobsForSubmissionKeyModel
            Resources of the compute node. If None, make system calls to check resources.
        scheduler_config_id : str
            ID of the scheduler config used to acquire this compute node.
            If set, use this ID to pull matching jobs. If not set, pull any job that meets the
            resource availability.
        """
        self._api = api
        self._workflow = workflow
        self._outstanding_jobs = {}
        self._poll_interval = job_completion_poll_interval
        self._db_poll_interval = database_poll_interval
        self._output_dir = output_dir
        self._scheduler_config_id = scheduler_config_id
        self._orig_resources = resources or _get_system_resources(time_limit)
        self._orig_resources.scheduler_config_id = self._scheduler_config_id
        self._resources = PrepareJobsForSubmissionKeyModel(**self._orig_resources.to_dict())
        self._last_db_poll_time = 0
        self._compute_node = None
        self._stats = ComputeNodeResourceStatConfig(
            **(
                api.get_workflows_config_key(
                    self._workflow.key
                ).compute_node_resource_stats.to_dict()
            )
        )
        self._parent_monitor_conn = None
        self._monitor_proc = None
        self._pids = {}
        self._jobs_pending_process_stat_completion = []
        self._job_stdio_dir = output_dir / JOB_STDIO_DIR
        self._stats_dir = output_dir / STATS_DIR
        self._job_stdio_dir.mkdir(exist_ok=True)
        self._stats_dir.mkdir(exist_ok=True)
        self._hostname = socket.gethostname()

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
        self._create_compute_node(scheduler)
        if self._stats.is_enabled():
            self._start_resource_monitor()

        try:
            self._run_until_complete()
        finally:
            self._complete_compute_node()
            if self._stats.process:
                self._stop_resource_monitor()

    def _run_until_complete(self):
        os.environ["TORC_WORKFLOW_KEY"] = self._workflow.key
        timeout = _get_timeout(self._resources.time_limit)
        start_time = time.time()

        result = send_api_command(self._api.get_workflows_is_complete_key, self._workflow.key)
        while not result.is_complete and not time.time() - start_time > timeout:
            num_completed = self._process_completions()
            num_started = 0
            if num_completed > 0 or self._is_time_to_poll_database() or not self._outstanding_jobs:
                num_started = self._run_ready_jobs()

            if num_started == 0 and not self._outstanding_jobs:
                if send_api_command(
                    self._api.get_workflows_is_complete_key, self._workflow.key
                ).is_complete:
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
            result = send_api_command(self._api.get_workflows_is_complete_key, self._workflow.key)

        if result.is_canceled:
            logger.info("Detected a canceled workflow. Cancel all outstanding jobs and exit.")
            self._cancel_jobs(list(self._outstanding_jobs.values()))

        self._terminate_jobs(list(self._outstanding_jobs.values()))

        self._pids.clear()
        self._handle_completed_process_stats()

    def _create_compute_node(self, scheduler):
        compute_node = WorkflowComputeNodesModel(
            hostname=self._hostname,
            start_time=str(datetime.now()),
            resources=self._orig_resources,
            is_active=True,
            scheduler=scheduler or {},
        )
        self._compute_node = send_api_command(
            self._api.post_workflows_workflow_compute_nodes,
            compute_node,
            self._workflow.key,
        )

    def _complete_compute_node(self):
        self._compute_node.is_active = False
        self._compute_node.duration_seconds = (
            time.time()
            - datetime.strptime(self._compute_node.start_time, "%Y-%m-%d %H:%M:%S.%f").timestamp()
        )
        send_api_command(
            self._api.put_workflows_workflow_compute_nodes_key,
            self._compute_node,
            self._workflow.key,
            self._compute_node.key,
        )

    def _complete_job(self, job, result, status):
        job = send_api_command(
            self._api.post_workflows_workflow_jobs_key_complete_job_status_rev,
            result,
            self._workflow.key,
            job.id,
            status,
            job._rev,  # pylint: disable=protected-access
        )
        return job

    def _current_memory_allocation_percentage(self):
        return self._resources.memory_gb / self._orig_resources.memory_gb * 100

    def _decrement_resources(self, job):
        job_resources = send_api_command(
            self._api.get_workflows_workflow_jobs_key_resource_requirements,
            self._workflow.key,
            job.key,
        )
        job_memory_gb = get_memory_gb(job_resources.memory)
        self._resources.num_cpus -= job_resources.num_cpus
        self._resources.num_gpus -= job_resources.num_gpus
        self._resources.memory_gb -= job_memory_gb
        assert self._resources.num_cpus >= 0.0, self._resources.num_cpus
        assert self._resources.num_gpus >= 0.0, self._resources.num_gpus
        assert self._resources.memory_gb >= 0.0, self._resources.memory_gb

    def _increment_resources(self, job):
        job_resources = send_api_command(
            self._api.get_workflows_workflow_jobs_key_resource_requirements,
            self._workflow.key,
            job.key,
        )
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

    def _log_job_start_event(self, job_key: str):
        send_api_command(
            self._api.post_workflows_workflow_events,
            {
                "category": "job",
                "type": "start",
                "key": job_key,
                "node_name": self._hostname,
                "message": f"Started job {job_key}",
            },
            self._workflow.key,
        )

    def _log_job_complete_event(self, job_key: str, status: str):
        send_api_command(
            self._api.post_workflows_workflow_events,
            {
                "category": "job",
                "type": "complete",
                "key": job_key,
                "status": status,
                "node_name": self._hostname,
                "message": f"Completed job {job_key}",
            },
            self._workflow.key,
        )

    def _process_completions(self):
        done_jobs = []
        for job in self._outstanding_jobs.values():
            if job.is_complete():
                done_jobs.append(job)
                # TODO: check return code first
                self._update_file_info(job)

        for job in done_jobs:
            self._cleanup_job(job, "done")

        if done_jobs:
            logger.info("Found %s completions", len(done_jobs))
        else:
            logger.debug("Found 0 completions")
        return len(done_jobs)

    def _cancel_jobs(self, jobs):
        for job in jobs:
            # Note that the database API service changes job status to canceled.
            job.cancel()
            logger.info("Canceled job key=%s name=%s", job.key, job.db_job.name)

        status = "canceled"
        for job in jobs:
            job.wait_for_completion(status)
            assert job.is_complete()
            job.db_job = send_api_command(
                self._api.get_workflows_workflow_jobs_key,
                self._workflow.key,
                job.key,
            )
            self._cleanup_job(job, status)

    def _terminate_jobs(self, jobs):
        terminated_jobs = []
        for job in jobs:
            if job.db_job.supports_termination:
                job.terminate()
                logger.info("Terminated job key=%s name=%s", job.key, job.db_job.name)
                terminated_jobs.append(job)

        status = "terminated"
        for job in terminated_jobs:
            job.wait_for_completion("terminated")
            assert job.is_complete()
            self._cleanup_job(job, status)

    def _cleanup_job(self, job: AsyncCliCommand, status):
        self._outstanding_jobs.pop(job.key)
        self._increment_resources(job.db_job)
        result = job.get_result()
        self._log_job_complete_event(job.key, status)
        self._complete_job(job.db_job, result, status)
        if self._stats.process:
            self._jobs_pending_process_stat_completion.append(job.key)
            self._pids.pop(job.key)

    def _run_job(self, job: AsyncCliCommand):
        job.run(self._output_dir)
        job.db_job.run_id += 1
        # The database changes db_job._rev on every update.
        # This reassigns job.db_job in order to stay current.
        job.db_job = send_api_command(
            self._api.put_workflows_workflow_jobs_key,
            job.db_job,
            self._workflow.key,
            job.key,
        )
        job.db_job = send_api_command(
            self._api.put_workflows_workflow_jobs_key_manage_status_change_status_rev,
            self._workflow.key,
            job.key,
            "submitted",
            job.db_job._rev,  # pylint: disable=protected-access
        )
        self._outstanding_jobs[job.key] = job
        if self._stats.process:
            self._pids[job.key] = job.pid
        send_api_command(
            self._api.post_workflows_workflow_edges_name,
            EdgesNameModel(
                _from=self._compute_node.id,
                to=job.db_job._id,  # pylint: disable=protected-access
            ),
            self._workflow.key,
            "executed",
        )
        logger.debug("Started job %s", job.key)
        self._log_job_start_event(job.key)

    def _run_ready_jobs(self):
        ready_jobs = send_api_command(
            self._api.post_workflows_prepare_jobs_for_submission_key,
            self._resources,
            self._workflow.key,
        )
        if ready_jobs.jobs:
            logger.info("%s jobs are ready for submission", len(ready_jobs.jobs))
        else:
            logger.info("Reason: %s", ready_jobs.reason)
        for job in ready_jobs.jobs:
            self._run_job(AsyncCliCommand(job))
            self._decrement_resources(job)

        self._last_db_poll_time = time.time()
        return len(ready_jobs.jobs)

    def _start_resource_monitor(self):
        self._parent_monitor_conn, child_conn = multiprocessing.Pipe()
        pids = self._pids if self._stats.process else None
        logger.info("Start resource monitor with %s", json.dumps(self._stats.dict()))
        if self._stats.monitor_type == "aggregation":
            args = (child_conn, self._stats, pids, None)
        elif self._stats.monitor_type == "periodic":
            db_file = self._stats_dir / f"compute_node_{self._compute_node.key}.sqlite"
            args = (child_conn, self._stats, pids, db_file)
        else:
            raise Exception(f"Unsupported monitor_type={self._stats.monitor_type}")
        self._monitor_proc = multiprocessing.Process(target=run_monitor_async, args=args)
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
                    "completed_job_keys": self._jobs_pending_process_stat_completion,
                }
            )
            with Timer(timer_stats_collector, "receive_process_stats"):
                results = self._parent_monitor_conn.recv()
            for result in results.results:
                self._post_job_process_stats(result)
            if results.results:
                send_api_command(
                    self._api.post_workflows_workflow_compute_node_stats,
                    WorkflowComputeNodeStatsModel(
                        hostname=self._hostname,
                        # These json methods let Pydantic run its data type conversions.
                        stats=[
                            WorkflowsworkflowcomputeNodeStatsStats(**json.loads(x.json()))
                            for x in results.results
                        ],
                        timestamp=str(datetime.now()),
                    ),
                    self._workflow.key,
                )
            self._jobs_pending_process_stat_completion.clear()

    def _update_pids_to_monitor(self):
        if self._stats.process:
            self._parent_monitor_conn.send(
                {"command": IpcMonitorCommands.UPDATE_PIDS, "pids": self._pids}
            )

    def _post_compute_node_stats(self, results: ComputeNodeResourceStatResults):
        res = send_api_command(
            self._api.post_workflows_workflow_compute_node_stats,
            WorkflowComputeNodeStatsModel(
                hostname=self._hostname,
                # These json methods let Pydantic run its data type conversions.
                stats=[
                    WorkflowsworkflowcomputeNodeStatsStats(**json.loads(x.json()))
                    for x in results.results
                ],
                timestamp=str(datetime.now()),
            ),
            self._workflow.key,
        )
        send_api_command(
            self._api.post_workflows_workflow_edges_name,
            EdgesNameModel(
                _from=self._compute_node.id,
                to=res._id,  # pylint: disable=protected-access
            ),
            self._workflow.key,
            "node_used",
        )

        for result in results.results:
            assert result.resource_type != ResourceType.PROCESS, result

    def _post_job_process_stats(self, result: ProcessStatResults):
        run_id = send_api_command(
            self._api.get_workflows_workflow_jobs_key,
            self._workflow.key,
            result.job_key,
        ).run_id
        res = send_api_command(
            self._api.post_workflows_workflow_job_process_stats,
            WorkflowJobProcessStatsModel(
                avg_cpu_percent=result.average["cpu_percent"],
                max_cpu_percent=result.maximum["cpu_percent"],
                avg_rss=result.average["rss"],
                max_rss=result.maximum["rss"],
                num_samples=result.num_samples,
                job_key=result.job_key,
                run_id=run_id,
                timestamp=str(datetime.now()),
            ),
            self._workflow.key,
        )
        send_api_command(
            self._api.post_workflows_workflow_edges_name,
            EdgesNameModel(
                _from=f"jobs__{self._workflow.key}/{result.job_key}",
                to=res._id,  # pylint: disable=protected-access
            ),
            self._workflow.key,
            "process_used",
        )

    def _update_file_info(self, job):
        for file in iter_documents(
            self._api.get_workflows_workflow_files_produced_by_job_key,
            self._workflow.key,
            job.key,
        ):
            path = make_path(file.path)
            if not path.exists():
                logger.warning(
                    "Job %s should have produced file %s, but it does not exist",
                    job.key,
                    file.path,
                )
                continue
            # file.file_hash = compute_file_hash(path)
            file.st_mtime = path.stat().st_mtime
            send_api_command(
                self._api.put_workflows_workflow_files_key,
                file,
                self._workflow.key,
                file.key,
            )


def _get_system_resources(time_limit):
    return PrepareJobsForSubmissionKeyModel(
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
    class Config:
        """Custom config"""

        json_encoders = {timedelta: timedelta_isoformat}

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
