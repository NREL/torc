"""Runs a CLI command asynchronously"""

import abc
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Optional

from loguru import logger

from torc.common import JOB_STDIO_DIR, JobStatus
from torc.openapi_client.models.job_model import JobModel
from torc.openapi_client.models.result_model import ResultModel
from torc.utils.cpu_affinity_mask_tracker import CpuAffinityMaskTracker


class AsyncJobBase(abc.ABC):
    """Base class for async jobs"""

    @abc.abstractmethod
    def run(self, output_dir: Path, run_id: int) -> None:
        """Run a job."""

    @abc.abstractmethod
    def cancel(self) -> None:
        """Cancel the job. Does not wait to confirm. Call wait_for_completion afterwards."""

    @abc.abstractmethod
    def force_complete(self, return_code, status) -> None:
        """Force the job to completion with a return code and status. Does not send anything
        to the process.
        """

    @abc.abstractmethod
    def wait_for_completion(self, status, timeout_seconds=30) -> None:
        """Waits to confirm that the job has finished after being sent SIGKILL or SIGTERM."""

    @property
    @abc.abstractmethod
    def db_job(self) -> JobModel:
        """Return the underlying job object that is stored in the database."""

    @db_job.setter
    @abc.abstractmethod
    def db_job(self, job: JobModel) -> None:
        """Set the underlying job object that is stored in the database."""

    @abc.abstractmethod
    def get_result(self, run_id: int) -> ResultModel:
        """Return a Result for the job after it is completed."""

    @abc.abstractmethod
    def terminate(self):
        """Terminate the job with SIGTERM to allow a graceful exit before a node times out."""

    @abc.abstractmethod
    def is_complete(self) -> bool:
        """Return True if the job is complete."""

    @property
    @abc.abstractmethod
    def key(self) -> str:
        """Return the key of the job."""


class AsyncCliCommand(AsyncJobBase):
    """Manages execution of an asynchronous CLI command."""

    def __init__(self, job, cpu_affinity_tracker=None) -> None:
        self._db_job = job
        self._pipe: Optional[subprocess.Popen] = None
        self._is_running = False
        self._start_time = 0.0
        self._completion_time: datetime | None = None
        self._exec_time_s = 0.0
        self._return_code: Optional[int] = None
        self._is_complete = False
        self._status: Optional[str] = None
        self._stdout_fp: Optional[TextIOWrapper] = None
        self._stderr_fp: Optional[TextIOWrapper] = None
        self._cpu_affinity_tracker: Optional[CpuAffinityMaskTracker] = cpu_affinity_tracker
        self._cpu_affinity_index: Optional[int] = None

    def __del__(self) -> None:
        if self._is_running:
            logger.warning("job {} destructed while running", self._db_job.command)

    def cancel(self) -> None:
        assert self._pipe is not None
        self._pipe.kill()

    def force_complete(self, return_code: int, status: str) -> None:
        self._complete(status, return_code=return_code)

    def wait_for_completion(self, status: str, timeout_seconds: int = 30) -> None:
        assert self._pipe is not None
        complete = False
        for _ in range(timeout_seconds):
            if self._pipe.poll() is not None:
                complete = True
                logger.info("job {} has exited", self.key)
                break
            time.sleep(1)
        if not complete:
            logger.warning("Timed out waiting for job {} to complete", self.key)

        self._complete(status)

    @property
    def db_job(self) -> JobModel:
        return self._db_job

    @db_job.setter
    def db_job(self, job: JobModel) -> None:
        self._db_job = job

    def get_result(self, run_id) -> ResultModel:
        assert self._is_complete
        assert self._return_code is not None
        assert self._status is not None
        assert self._completion_time is not None
        return ResultModel(
            job_key=self.key,
            run_id=run_id,
            return_code=self._return_code,
            exec_time_minutes=self._exec_time_s / 60,
            completion_time=self._completion_time.isoformat(),
            status=self._status,
        )

    def terminate(self) -> None:
        assert self._pipe is not None
        self._pipe.terminate()

    def is_complete(self) -> bool:
        assert self._pipe is not None
        if self._is_complete:
            return True

        if self._pipe.poll() is not None:
            self._complete(JobStatus.DONE.value)

        return not self._is_running

    @property
    def key(self) -> str:
        assert self._db_job.key is not None
        return self._db_job.key

    @property
    def pid(self) -> int:
        """Return the process ID for the job."""
        assert self._pipe is not None
        return self._pipe.pid

    def run(self, output_dir: Path, run_id: int, log_prefix=None) -> None:
        assert self._pipe is None
        self._start_time = time.time()

        prefix = "" if log_prefix is None else f"{log_prefix}_"
        basename = f"{prefix}{self.key}_{run_id}"
        stdout_filename = output_dir / JOB_STDIO_DIR / f"{basename}.o"
        stderr_filename = output_dir / JOB_STDIO_DIR / f"{basename}.e"
        self._stdout_fp = open(stdout_filename, "w", encoding="utf-8")
        self._stderr_fp = open(stderr_filename, "w", encoding="utf-8")
        env = os.environ.copy()
        env["TORC_JOB_KEY"] = self.key
        # TORC_WORKFLOW_KEY is also set
        if self._db_job.invocation_script:
            self._pipe = self._run_invocation_script(env=env)
        else:
            self._pipe = self._run_command(self._db_job.command, env=env)
        if self._cpu_affinity_tracker is not None:
            self._cpu_affinity_index, mask = self._cpu_affinity_tracker.acquire_mask()
            if not hasattr(os, "sched_setaffinity"):
                msg = f"This platform does not support sched_setaffinity: {sys.platform}."
                raise NotImplementedError(msg)
            os.sched_setaffinity(self._pipe.pid, mask)  # type: ignore
            logger.info("Set CPU affinity for job={self._key} to {mask=}")

        self._is_running = True

    def _run_command(self, command, env):
        logger.info("Run job={} command {}", self._db_job.key, command)
        cmd = shlex.split(command, posix="win" not in sys.platform)
        return subprocess.Popen(cmd, stdout=self._stdout_fp, stderr=self._stderr_fp, env=env)

    def _run_invocation_script(self, env):
        cmd = f"{self._db_job.invocation_script} {self._db_job.command}"
        return self._run_command(cmd, env)

    def _complete(self, status, return_code=None):
        assert self._pipe is not None
        assert self._stdout_fp is not None
        assert self._stderr_fp is not None
        self._return_code = self._pipe.returncode if return_code is None else return_code
        self._stdout_fp.close()
        self._stderr_fp.close()
        self._completion_time = datetime.now()
        self._exec_time_s = time.time() - self._start_time
        self._is_running = False
        self._is_complete = True
        self._status = status
        if self._cpu_affinity_index is not None:
            assert self._cpu_affinity_tracker is not None
            self._cpu_affinity_tracker.release_mask(self._cpu_affinity_index)
            self._cpu_affinity_index = None

        logger.info(
            "Job {} completed return_code={} exec_time_s={} status={}",
            self.key,
            self._return_code,
            self._exec_time_s,
            self._status,
        )
