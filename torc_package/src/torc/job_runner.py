"""Runs jobs on a compute node"""

import json
import os
import multiprocessing
import multiprocessing.connection
import multiprocessing.context
import re
import signal
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable, Optional, Union

import psutil
from loguru import logger
from pydantic import BaseModel, ConfigDict
from rmon.models import (
    ComputeNodeResourceStatConfig,
    ComputeNodeResourceStatResults,
    CompleteProcessesCommand,
    UpdatePidsCommand,
    ShutDownCommand,
    ProcessStatResults,
    ResourceType,
)
from rmon import run_monitor_async, Timer
from torc.openapi_client import DefaultApi
from torc.openapi_client.models.compute_node_model import ComputeNodeModel
from torc.openapi_client.models.compute_node_schedule_params import ComputeNodeScheduleParams
from torc.openapi_client.models.compute_node_stats_model import ComputeNodeStatsModel
from torc.openapi_client.models.compute_nodes_resources import ComputeNodesResources
from torc.openapi_client.models.compute_node_stats import ComputeNodeStats
from torc.openapi_client.models.edge_model import EdgeModel
from torc.openapi_client.models.job_model import JobModel
from torc.openapi_client.models.job_process_stats_model import JobProcessStatsModel
from torc.openapi_client.models.workflow_model import WorkflowModel

import torc
from torc.api import send_api_command, iter_documents, wait_for_healthy_database
from torc.common import JOB_STDIO_DIR, STATS_DIR, timer_stats_collector, JobStatus
from torc.exceptions import InvalidParameter, DatabaseOffline
from torc.utils.cpu_affinity_mask_tracker import CpuAffinityMaskTracker
from torc.utils.filesystem_factory import make_path
from torc.utils.run_command import check_run_command, run_command
from .async_cli_command import AsyncCliCommand
from .common import KiB, MiB, GiB, TiB

JOB_COMPLETION_POLL_INTERVAL = 60

_g_shutdown = False


class JobRunner:
    """Runs jobs on a compute node"""

    def __init__(
        self,
        api: DefaultApi,
        workflow: WorkflowModel,
        output_dir: Path,
        job_completion_poll_interval: float = JOB_COMPLETION_POLL_INTERVAL,
        max_parallel_jobs: Optional[int] = None,
        database_poll_interval: int = 600,
        time_limit: Optional[str] = None,
        end_time: Optional[datetime] = None,
        resources: Optional[ComputeNodesResources] = None,
        scheduler_config_id: Optional[str] = None,
        log_prefix: Optional[str] = None,
        cpu_affinity_cpus_per_job: Optional[int] = None,
        is_subtask: bool = False,
    ) -> None:
        """Constructs a JobRunner.

        Parameters
        ----------
        api : DefaultApi
        output_dir : Path
            Directory for output files
        job_completion_poll_interval : int
            Interval in seconds in which to poll for job completions.
        max_parallel_jobs : int | None
            Maximum number of jobs that can run in parallel. If None (default), rely on resource
            constraints.
        database_poll_interval : int
            Max time in seconds in which the code should poll for job updates in the database.
        end_time : None | datetime
            If None then there is no time limit.
        time_limit : None | str
            ISO 8601 time duration string. If None then there is no time limit.
            Mutually exclusive with end_time.
        resources : None | ComputeNodesResources
            Resources of the compute node. If None, make system calls to check resources.
        scheduler_config_id : str
            ID of the scheduler config used to acquire this compute node.
            If set, use this ID to pull matching jobs. If not set, pull any job that meets the
            resource availability.
        log_prefix : str
            Prefix to use for job-specific log files.
        is_subtask : bool
            Set to True if this is a subtask and multiple instances are running on one node.
        """
        if time_limit is not None and end_time is not None:
            msg = "time_limit and end_time are mutually exclusive"
            raise Exception(msg)

        # TODO: too many inputs and too complex. Needs refactoring.
        self._api = api
        self._workflow = workflow
        assert isinstance(self._workflow.key, str)
        self._run_id = send_api_command(api.get_workflow_status, workflow.key).run_id
        assert self._run_id > 0, self._run_id
        self._outstanding_jobs: dict[str, AsyncCliCommand] = {}
        self._pids: dict[str, int] = {}
        self._jobs_pending_process_stat_completion: list[str] = []
        self._hostname = socket.gethostname()
        self._job_stdio_dir = output_dir / JOB_STDIO_DIR
        self._poll_interval = job_completion_poll_interval
        self._max_parallel_jobs = max_parallel_jobs
        self._db_poll_interval = database_poll_interval
        self._output_dir = output_dir
        self._log_prefix = log_prefix
        self._parent_monitor_conn: Optional[multiprocessing.connection.Connection] = None
        self._monitor_proc: Optional[multiprocessing.context.Process] = None
        self._end_time = end_time
        if time_limit is not None:
            self._end_time = datetime.now() + timedelta(seconds=_get_timeout(time_limit))
        if resources is None:
            self._scheduler_config_id = scheduler_config_id
        else:
            self._scheduler_config_id = resources.scheduler_config_id

        self._orig_resources = resources or _get_system_resources()
        self._cpu_tracker: Optional[CpuAffinityMaskTracker] = None
        if cpu_affinity_cpus_per_job is not None:
            if not hasattr(os, "sched_setaffinity"):
                msg = "This platform does not support sched_setaffinity"
                raise InvalidParameter(msg)

            num_cpus = self._orig_resources.num_cpus
            if cpu_affinity_cpus_per_job > num_cpus:
                msg = f"{cpu_affinity_cpus_per_job=} cannot be greater than {num_cpus=}"
                raise InvalidParameter(msg)
            self._cpu_tracker = CpuAffinityMaskTracker(num_cpus, cpu_affinity_cpus_per_job)
            num_masks = self._cpu_tracker.get_num_masks()
            if self._max_parallel_jobs is not None and self._max_parallel_jobs < num_masks:
                msg = f"{max_parallel_jobs=} cannot be less than {num_masks=}"
                raise InvalidParameter(msg)

        config = send_api_command(api.get_workflow_config, self._workflow.key)
        assert config.compute_node_resource_stats is not None
        assert config.compute_node_wait_for_new_jobs_seconds is not None
        assert config.compute_node_wait_for_healthy_database_minutes is not None
        self._config = config
        self._wait_for_new_jobs_seconds = config.compute_node_wait_for_new_jobs_seconds
        self._ignore_completion = config.compute_node_ignore_workflow_completion
        self._orig_resources.scheduler_config_id = self._scheduler_config_id
        self._resources = ComputeNodesResources(**self._orig_resources.to_dict())
        self._last_db_poll_time = 0.0
        self._compute_node: Optional[ComputeNodeModel] = None
        self._stats = ComputeNodeResourceStatConfig(**config.compute_node_resource_stats.to_dict())
        if is_subtask:
            logger.info("Disable overall compute node stats monitoring for a subtask.")
            self._stats.disable_system_stats()
        self._stats_dir = output_dir / STATS_DIR
        self._job_stdio_dir.mkdir(exist_ok=True)
        self._stats_dir.mkdir(exist_ok=True)

    def __del__(self) -> None:
        if self._outstanding_jobs:
            logger.warning(
                "JobRunner destructed with outstanding jobs: {}",
                self._outstanding_jobs.keys(),
            )
        if self._parent_monitor_conn is not None or self._monitor_proc is not None:
            logger.warning("JobRunner destructed without stopping the resource monitor process.")

    def run_worker(self, scheduler: dict[str, Any] | None = None) -> None:
        """Run jobs from a worker process.

        Parameters
        ----------
        scheduler
            Scheduler configuration parameters. Used only for logs and events.
        """
        signal.signal(signal.SIGTERM, _sigterm_handler)
        self._log_worker_start_event()
        self._create_compute_node(scheduler)
        assert self._compute_node is not None
        logger.info(
            "Run torc worker version={} api_service_version={} db={} hostname={} output_dir={} "
            "end_time={} compute_node_key={} resources={} config={}",
            torc.__version__,
            send_api_command(self._api.get_version)["version"],
            self._api.api_client.configuration.host,
            self._hostname,
            self._output_dir,
            self._end_time,
            self._compute_node.key,
            str(self._resources).replace("\n", " "),
            self._config,
        )
        if self._ignore_completion:
            logger.warning(
                "This worker is set to ignore workflow completions and so the user must cancel the alloction."
            )
        if self._stats.is_enabled():
            self._start_resource_monitor()

        if self._config.worker_startup_script is not None:
            logger.info("Running node startup script: {}", self._config.worker_startup_script)
            check_run_command(self._config.worker_startup_script)
            logger.info("Completed node startup script")
        try:
            self._run_until_complete()
        finally:
            logger.info("Exiting worker")
            if self._parent_monitor_conn is not None:
                self._stop_resource_monitor()
            self._complete_compute_node()
            self._log_worker_stop_event()

    def _is_workflow_complete(self) -> bool:
        if self._ignore_completion:
            logger.trace("Ignore workflow completions")
            return False
        response = send_api_command(self._api.is_workflow_complete, self._workflow.key)
        if response.needs_to_run_completion_script:
            logger.info(
                "Running workflow completion script: {}", self._config.workflow_completion_script
            )
            ret = run_command(self._config.workflow_completion_script)
            if ret == 0:
                logger.info("Completed workflow completion script")
            else:
                logger.error(
                    "Failed to run workflow completion script {}",
                    self._config.workflow_completion_script,
                )
        return response.is_complete

    def _run_until_complete(self) -> None:
        assert isinstance(self._workflow.key, str)
        assert self._config.compute_node_wait_for_healthy_database_minutes is not None
        os.environ["TORC_WORKFLOW_KEY"] = self._workflow.key
        last_job_poll_time = 0.0
        extra_wait_time_start = None
        short_poll_interval = 3
        while (
            not _g_shutdown
            and not self._is_workflow_complete()
            and (self._end_time is None or datetime.now() < self._end_time)
        ):
            cur_time = time.time()
            if cur_time - last_job_poll_time < self._poll_interval:
                # This allows us to detect shutdown on a quicker interval.
                time.sleep(short_poll_interval)
                continue
            last_job_poll_time = cur_time
            try:
                is_done, extra_wait_time_start = self._run_process_completions(
                    extra_wait_time_start
                )
                if is_done:
                    break
            except DatabaseOffline:
                logger.exception("Database offline error occurred in run loop.")
                wait_for_healthy_database(
                    self._api,
                    timeout_minutes=self._config.compute_node_wait_for_healthy_database_minutes,
                )
            time.sleep(short_poll_interval)

        result = send_api_command(self._api.is_workflow_complete, self._workflow.key)
        if result.is_canceled:
            logger.info("Detected a canceled workflow. Cancel all outstanding jobs and exit.")
            self._cancel_jobs(list(self._outstanding_jobs.values()))

        self._terminate_jobs(list(self._outstanding_jobs.values()))

        if self._stats.is_enabled():
            self._pids.clear()
            self._handle_completed_process_stats()

    def _run_process_completions(
        self, extra_wait_time_start: float | None
    ) -> tuple[bool, float | None]:
        num_completed = self._process_completions()
        num_started = 0
        reason_none_started = None
        if num_completed > 0:
            schedule_result = send_api_command(
                self._api.prepare_jobs_for_scheduling,
                self._workflow.key,
            )
            for scheduler_params in schedule_result.schedulers:
                self._schedule_compute_nodes(scheduler_params)

        if (
            num_completed > 0 or self._is_time_to_poll_database() or not self._outstanding_jobs
        ) and (
            self._max_parallel_jobs is None
            or len(self._outstanding_jobs) < self._max_parallel_jobs
        ):
            num_started, reason_none_started = self._run_ready_jobs()

        if not self._ignore_completion and num_started == 0 and not self._outstanding_jobs:
            if self._is_workflow_complete():
                logger.info("Workflow is complete.")
            elif self._wait_for_new_jobs_seconds > 0 and extra_wait_time_start is None:
                logger.info("Wait {}s for new jobs", self._wait_for_new_jobs_seconds)
                extra_wait_time_start = time.time()
            elif (
                self._wait_for_new_jobs_seconds > 0
                and extra_wait_time_start is not None
                and time.time() - extra_wait_time_start < self._wait_for_new_jobs_seconds
            ):
                logger.trace(
                    "Extra wait time remaining is {} seconds",
                    self._wait_for_new_jobs_seconds - (time.time() - extra_wait_time_start),
                )
            else:
                logger.info(
                    "No jobs are outstanding on this node and no new jobs are available. "
                    "Reason no jobs started: {}",
                    reason_none_started,
                )
                return True, extra_wait_time_start

        if num_started > 0 and self._stats.is_enabled():
            self._update_pids_to_monitor()
        if num_completed > 0 and self._stats.is_enabled():
            self._handle_completed_process_stats()
            self._update_pids_to_monitor()

        return False, extra_wait_time_start

    def _schedule_compute_nodes(self, params: ComputeNodeScheduleParams) -> None:
        if params.scheduler_id.startswith("slurm_schedulers"):
            self._schedule_slurm_compute_nodes(params)
        else:
            logger.error("Compute node scheduler {} is not supported", params.scheduler_id)

    def _schedule_slurm_compute_nodes(self, params: ComputeNodeScheduleParams) -> None:
        key = params.scheduler_id.split("/")[1]
        cmd = (
            f"torc -k {self._workflow.key} -u {self._api.api_client.configuration.host} "
            f"hpc slurm schedule-nodes -n {params.num_jobs} "
            f"-o {self._output_dir} -p {self._poll_interval} -s {key}"
        )
        if params.max_parallel_jobs is not None:
            cmd += f" --max-parallel-jobs {params.max_parallel_jobs}"
        if params.start_one_worker_per_node:
            cmd += " --start-one-worker-per-node"
        ret = run_command(cmd, num_retries=2)
        if ret == 0:
            logger.info("Scheduled compute nodes with cmd={}", cmd)
            self._log_worker_schedule_event(params.scheduler_id)
        else:
            logger.error("Failed to schedule compute nodes: {}", ret)

    def _create_compute_node(self, scheduler) -> None:
        logger.info("Compute node scheduler: {}", json.dumps(scheduler or {}))
        compute_node = ComputeNodeModel(
            hostname=self._hostname,
            pid=os.getpid(),
            start_time=str(datetime.now()),
            resources=self._orig_resources,
            is_active=True,
            scheduler=scheduler or {},
        )
        self._compute_node = send_api_command(
            self._api.add_compute_node,
            self._workflow.key,
            compute_node,
        )

    def _complete_compute_node(self) -> None:
        assert self._compute_node is not None
        self._compute_node.is_active = False
        self._compute_node.duration_seconds = (
            time.time()
            - datetime.strptime(self._compute_node.start_time, "%Y-%m-%d %H:%M:%S.%f").timestamp()
        )
        send_api_command(
            self._api.modify_compute_node,
            self._workflow.key,
            self._compute_node.key,
            self._compute_node,
            raise_on_error=False,
        )

    def _complete_job(self, job, result, status) -> JobModel:
        assert self._compute_node is not None
        job = send_api_command(
            self._api.complete_job,
            self._workflow.key,
            job.id,
            status,
            job.rev,
            self._run_id,
            self._compute_node.key,
            result,
        )
        return job

    def _decrement_resources(self, job: JobModel) -> None:
        assert job.internal is not None
        assert job.internal.memory_bytes is not None
        assert job.internal.num_cpus is not None
        assert job.internal.num_gpus is not None
        job_memory_gb = job.internal.memory_bytes / GiB
        self._resources.num_cpus -= job.internal.num_cpus
        self._resources.num_gpus -= job.internal.num_gpus
        self._resources.memory_gb -= job_memory_gb
        assert self._resources.num_cpus >= 0, self._resources.num_cpus
        assert self._resources.num_gpus >= 0, self._resources.num_gpus
        assert self._resources.memory_gb >= 0.0, self._resources.memory_gb

    def _increment_resources(self, job: JobModel) -> None:
        assert job.internal is not None
        assert job.internal.memory_bytes is not None
        assert job.internal.num_cpus is not None
        assert job.internal.num_gpus is not None
        job_memory_gb = job.internal.memory_bytes / GiB
        self._resources.num_cpus += job.internal.num_cpus
        self._resources.num_gpus += job.internal.num_gpus
        self._resources.memory_gb += job_memory_gb
        assert self._resources.num_cpus <= self._orig_resources.num_cpus, self._resources.num_cpus
        assert self._resources.num_gpus <= self._orig_resources.num_gpus, self._resources.num_gpus
        assert (
            self._resources.memory_gb <= self._orig_resources.memory_gb
        ), self._resources.memory_gb

    def _is_time_to_poll_database(self) -> bool:
        if (time.time() - self._db_poll_interval) < self._last_db_poll_time:
            return False

        # TODO: needs to be more sophisticated
        # The main point is to provide a way to avoid hundreds of compute nodes unnecessarily
        # asking the database for jobs when it's highly unlikely to get any.
        # It would be better if the database or some middleware could publish events when
        # new jobs are ready to run.
        return self._resources.num_cpus > 0 and self._resources.memory_gb > 0

    def _log_worker_start_event(self) -> None:
        send_api_command(
            self._api.add_event,
            self._workflow.key,
            {
                "category": "worker",
                "type": "start",
                "node_name": self._hostname,
                "torc_version": torc.__version__,
                "message": f"Started worker {self._hostname}",
            },
            raise_on_error=False,
        )

    def _log_worker_stop_event(self) -> None:
        send_api_command(
            self._api.add_event,
            self._workflow.key,
            {
                "category": "worker",
                "type": "stop",
                "node_name": self._hostname,
                "message": f"Stopped worker {self._hostname}",
            },
            raise_on_error=False,
        )

    def _log_worker_schedule_event(self, scheduler_id: str) -> None:
        send_api_command(
            self._api.add_event,
            self._workflow.key,
            {
                "category": "worker",
                "type": "schedule",
                "node_name": self._hostname,
                "scheduler_id": scheduler_id,
                "message": f"Scheduled compute node(s) for user with {scheduler_id=}",
            },
            raise_on_error=False,
        )

    def _process_completions(self) -> int:
        done_jobs = [x for x in self._outstanding_jobs.values() if x.is_complete()]
        for job in done_jobs:
            self._cleanup_job(job, JobStatus.DONE.value)

        if done_jobs:
            logger.info("Found {} completions", len(done_jobs))
        else:
            logger.trace("Found 0 completions")
        return len(done_jobs)

    def _cancel_jobs(self, jobs: Iterable[AsyncCliCommand]) -> None:
        for job in jobs:
            # Note that the database API service changes job status to canceled.
            job.cancel()
            logger.info("Canceled job key={} name={}", job.key, job.db_job.name)

        status = JobStatus.CANCELED.value
        for job in jobs:
            job.wait_for_completion(status)
            assert job.is_complete()
            job.db_job = send_api_command(
                self._api.get_job,
                self._workflow.key,
                job.key,
            )
            self._cleanup_job(job, status)

    def _terminate_jobs(self, jobs: Iterable[AsyncCliCommand]) -> None:
        no_wait_for_exit_jobs = []
        wait_for_exit_jobs = []
        for job in jobs:
            job.terminate()
            logger.info("Terminated job key={} name={}", job.key, job.db_job.name)
            if job.db_job.supports_termination:
                wait_for_exit_jobs.append(job)
            else:
                no_wait_for_exit_jobs.append(job)

        status = JobStatus.TERMINATED.value
        for job in wait_for_exit_jobs:
            job.wait_for_completion(status)
            assert job.is_complete()
            self._cleanup_job(job, status)

        for job in no_wait_for_exit_jobs:
            job.force_complete(-15, status)
            self._cleanup_job(job, status)

    def _cleanup_job(self, job: AsyncCliCommand, status: str) -> None:
        result = job.get_result(self._run_id)

        if result.return_code == 0:
            self._update_file_info(job)

        assert job.db_job.name is not None
        self._complete_job(job.db_job, result, status)
        self._outstanding_jobs.pop(job.key)
        self._increment_resources(job.db_job)
        if self._stats.process:
            self._jobs_pending_process_stat_completion.append(job.key)
            self._pids.pop(job.key)

    def _run_job(self, job: AsyncCliCommand) -> None:
        assert self._compute_node is not None
        assert self._compute_node.id is not None
        job_id = job.db_job.id
        job_name = job.db_job.name
        assert job_id is not None
        assert job_name is not None
        job.run(self._output_dir, self._run_id, log_prefix=self._log_prefix)
        # The database changes db_job._rev on every update.
        # This reassigns job.db_job in order to stay current.
        job.db_job = send_api_command(
            self._api.start_job,
            self._workflow.key,
            job.key,
            job.db_job.rev,
            self._run_id,
            self._compute_node.id,
        )
        self._outstanding_jobs[job.key] = job
        if self._stats.process:
            self._pids[job.key] = job.pid

    def _run_ready_jobs(self) -> tuple[int, Union[str, None]]:
        run_id = send_api_command(self._api.get_workflow_status, self._workflow.key).run_id
        if run_id != self._run_id:
            if self._outstanding_jobs:
                num = len(self._outstanding_jobs)
                msg = (
                    f"Detected a change in run_id while {num} jobs are outstanding: "
                    f"current={self._run_id} new={run_id}"
                )
                raise Exception(msg)
            logger.info("Detected a change in run_id. current={} new={}", self._run_id, run_id)
            self._run_id = run_id

        reason_none_started = None
        if self._end_time is not None:
            self._resources.time_limit = _convert_end_time_to_duration_str(self._end_time)
        kwargs = {}
        if self._max_parallel_jobs is not None:
            kwargs["limit"] = self._max_parallel_jobs
        # TODO: If the database successfully processes this command but then the response
        # does not get back to this client, the jobs will be stuck in "submitted_pending"
        # until the user intervenes.
        # It's an unlikely corner case that could be handled.
        ready_jobs = send_api_command(
            self._api.prepare_jobs_for_submission,
            self._workflow.key,
            self._resources,
            sort_method=self._config.prepare_jobs_sort_method,
            **kwargs,
        )
        if ready_jobs.jobs:
            logger.info("{} jobs are ready for submission", len(ready_jobs.jobs))
        else:
            reason_none_started = ready_jobs.reason
            logger.trace("No jobs are ready: {}", reason_none_started)
        for job in ready_jobs.jobs:
            self._run_job(
                AsyncCliCommand(
                    job,
                    cpu_affinity_tracker=self._cpu_tracker,
                )
            )
            self._decrement_resources(job)

        self._last_db_poll_time = time.time()
        return len(ready_jobs.jobs), reason_none_started

    def _start_resource_monitor(self) -> None:
        assert self._compute_node is not None
        assert self._compute_node.key is not None
        self._parent_monitor_conn, child_conn = multiprocessing.Pipe()
        pids = self._pids if self._stats.process else None
        monitor_log_file = self._output_dir / f"monitor_{self._compute_node.key}.log"
        logger.info("Start resource monitor with {}", json.dumps(self._stats.model_dump()))
        if self._stats.monitor_type == "aggregation":
            args = (child_conn, self._stats, pids, monitor_log_file, None)
        elif self._stats.monitor_type == "periodic":
            db_file = self._stats_dir / f"compute_node_{self._compute_node.key}.sqlite"
            args = (child_conn, self._stats, pids, monitor_log_file, db_file)  # type: ignore
        else:
            msg = f"Unsupported monitor_type={self._stats.monitor_type}"
            raise Exception(msg)
        self._monitor_proc = multiprocessing.Process(target=run_monitor_async, args=args)
        self._monitor_proc.start()

    def _stop_resource_monitor(self) -> None:
        assert self._parent_monitor_conn is not None
        assert self._monitor_proc is not None
        self._parent_monitor_conn.send(ShutDownCommand(pids=self._pids))
        has_results = False
        for _ in range(30):
            if self._parent_monitor_conn.poll():
                has_results = True
                break
            time.sleep(1)
        if has_results:
            system_results, _ = self._parent_monitor_conn.recv()
            if system_results.results:
                self._post_compute_node_stats(system_results)
        else:
            logger.error("Failed to receive results from resource monitor.")
        self._monitor_proc.join()
        self._parent_monitor_conn = None
        self._monitor_proc = None

    def _handle_completed_process_stats(self) -> None:
        assert self._parent_monitor_conn is not None
        if self._stats.process:
            self._parent_monitor_conn.send(
                CompleteProcessesCommand(
                    pids=self._pids,
                    completed_process_keys=self._jobs_pending_process_stat_completion,
                )
            )
            with Timer(timer_stats_collector, "receive_process_stats"):
                results = self._parent_monitor_conn.recv()
            stats = []
            for result in results.results:
                self._post_job_process_stats(result)
                # These json methods let Pydantic run its data type conversions.
                x = json.loads(result.model_dump_json())
                x["job_key"] = x.pop("process_key")
                stats.append(ComputeNodeStats(**x))
            if stats:
                send_api_command(
                    self._api.add_compute_node_stats,
                    self._workflow.key,
                    ComputeNodeStatsModel(
                        hostname=self._hostname,
                        stats=stats,
                        timestamp=str(datetime.now()),
                    ),
                )
            self._jobs_pending_process_stat_completion.clear()

    def _update_pids_to_monitor(self) -> None:
        assert self._parent_monitor_conn is not None
        if self._stats.process:
            self._parent_monitor_conn.send(UpdatePidsCommand(config=self._stats, pids=self._pids))

    def _post_compute_node_stats(self, results: ComputeNodeResourceStatResults) -> None:
        assert self._compute_node is not None
        assert self._compute_node.id is not None
        res = send_api_command(
            self._api.add_compute_node_stats,
            self._workflow.key,
            ComputeNodeStatsModel(
                hostname=self._hostname,
                # These json methods let Pydantic run its data type conversions.
                stats=[
                    ComputeNodeStats(**json.loads(x.model_dump_json())) for x in results.results
                ],
                timestamp=str(datetime.now()),
            ),
        )
        send_api_command(
            self._api.add_edge,
            self._workflow.key,
            "node_used",
            EdgeModel(
                _from=self._compute_node.id,
                _to=res.id,
            ),
        )

        for result in results.results:
            assert result.resource_type != ResourceType.PROCESS, result

    def _post_job_process_stats(self, result: ProcessStatResults) -> None:
        res = send_api_command(
            self._api.add_job_process_stats,
            self._workflow.key,
            JobProcessStatsModel(
                avg_cpu_percent=result.average["cpu_percent"],
                max_cpu_percent=result.maximum["cpu_percent"],
                avg_rss=result.average["rss"],
                max_rss=result.maximum["rss"],
                num_samples=result.num_samples,
                job_key=result.process_key,
                run_id=self._run_id,
                timestamp=str(datetime.now()),
            ),
        )
        # TODO: We could remove one API command per job if we added this edge in a custom POST
        # for the command above.
        send_api_command(
            self._api.add_edge,
            self._workflow.key,
            "process_used",
            EdgeModel(
                _from=f"jobs__{self._workflow.key}/{result.process_key}",
                _to=res.id,
            ),
        )

    def _update_file_info(self, job: AsyncCliCommand) -> None:
        for file in iter_documents(
            self._api.list_files_produced_by_job,
            self._workflow.key,
            job.key,
        ):
            path = make_path(file.path)
            if not path.exists():
                logger.warning(
                    "Job {} should have produced file {}, but it does not exist",
                    job.key,
                    file.path,
                )
                continue
            # file.file_hash = compute_file_hash(path)
            file.st_mtime = path.stat().st_mtime
            send_api_command(
                self._api.modify_file,
                self._workflow.key,
                file.key,
                file,
            )


def _get_system_resources() -> ComputeNodesResources:
    num_cpus = psutil.cpu_count()
    assert isinstance(num_cpus, int)
    return ComputeNodesResources(
        num_cpus=num_cpus,
        memory_gb=psutil.virtual_memory().total / GiB,
        num_nodes=1,
        time_limit=None,
        num_gpus=_get_num_gpus(),
    )


def get_memory_gb(memory: str) -> float:
    """Converts a memory defined as a string to GiB.

    Parameters
    ----------
    memory : str
        Memory as string with units, such as '10g'
    """
    return get_memory_in_bytes(memory) / GiB


def get_memory_in_bytes(memory: str) -> int:
    """Converts a memory defined as a string to bytes.

    Parameters
    ----------
    memory : str
        Memory as string with units, such as '10g'
    """
    match = re.search(r"^([0-9]+)$", memory)
    if match is not None:
        return int(match.group(1))

    match = re.search(r"^([0-9]+)\s*([kmgtKMGT])$", memory)
    if match is None:
        msg = f"{memory} is an invalid memory value"
        raise ValueError(msg)

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
        msg = f"{units} is an invalid memory unit"
        raise ValueError(msg)

    return size


# This pydantic code will convert ISO 8601 duration strings to timedelta.
class _TimeLimitModel(BaseModel):
    model_config = ConfigDict(ser_json_timedelta="iso8601")

    time_limit: timedelta


def _convert_end_time_to_duration_str(end_time: datetime) -> str:
    """Convert an end time timestamp to an ISO 8601 duration string, relative to current time."""
    duration = end_time - datetime.now()
    return json.loads(_TimeLimitModel(time_limit=duration).model_dump_json())["time_limit"]


def _get_timeout(time_limit) -> int | float:
    return (
        sys.maxsize
        if time_limit is None
        else _TimeLimitModel(time_limit=time_limit).time_limit.total_seconds()
    )


def _get_num_gpus() -> int:
    # Here is example output:
    # nvidia-smi --list-gpus
    # GPU 0: Tesla V100-PCIE-16GB (UUID: GPU-b96a6fce-c5a4-079e-d922-5e9d21b063ce)
    # GPU 1: Tesla V100-PCIE-16GB (UUID: GPU-e57626ea-9c0c-3ceb-06e1-f926467b98ad)

    # TODO: do we need to support other GPUs? Is there a standard way to find them?
    if shutil.which("nvidia-smi") is None:
        return 0

    proc = subprocess.run(["nvidia-smi", "--list-gpus"], stdout=subprocess.PIPE, check=False)
    if proc.returncode == 0:
        gpus = [
            x
            for x in proc.stdout.decode("utf-8").strip().split("\n")
            if x.strip().startswith("GPU")
        ]
        return len(gpus)
    return 0


def _sigterm_handler(signum, frame) -> None:
    global _g_shutdown
    logger.info("Detected SIGTERM. Terminate jobs and shutdown.")
    _g_shutdown = True
