"""Runs a CLI command asynchronously"""

import abc
import logging
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from swagger_client.models.workflow_results_model import WorkflowResultsModel

from torc.common import JOB_STDIO_DIR

logger = logging.getLogger(__name__)


class AsyncJobBase(abc.ABC):
    """Base class for async jobs"""

    @abc.abstractmethod
    def run(self, output_dir: Path):
        """Run a job."""

    @abc.abstractmethod
    def cancel(self):
        """Cancel the job. Does not wait to confirm. Call wait_for_completion afterwards."""

    @abc.abstractmethod
    def wait_for_completion(self, status, timeout_seconds=30):
        """Waits to confirm that the job has finished after being sent SIGKILL or SIGTERM."""

    @property
    @abc.abstractmethod
    def db_job(self):
        """Return the underlying job object that is stored in the database."""

    @db_job.setter
    @abc.abstractmethod
    def db_job(self, job):
        """Set the underlying job object that is stored in the database."""

    @abc.abstractmethod
    def get_result(self, run_id):
        """Return a Result for the job after it is completed.

        Parameters
        ----------
        run_id : int

        Returns
        -------
        WorkflowResultsModel
        """

    @abc.abstractmethod
    def terminate(self):
        """Terminate the job with SIGTERM to allow a graceful exit before a node times out."""

    @abc.abstractmethod
    def is_complete(self):
        """Return True if the job is complete."""

    @property
    @abc.abstractmethod
    def key(self):
        """Return the key of the job."""


class AsyncCliCommand(AsyncJobBase):
    """Manages execution of an asynchronous CLI command."""

    def __init__(self, job, log_prefix=None, cpu_affinity_tracker=None):
        self._db_job = job
        self._log_prefix = log_prefix
        self._pipe = None
        self._is_running = False
        self._start_time = 0.0
        self._completion_time = 0.0
        self._exec_time_s = 0.0
        self._return_code = None
        self._is_complete = False
        self._status = None
        self._stdout_fp = None
        self._stderr_fp = None
        self._cpu_affinity_tracker = cpu_affinity_tracker
        self._cpu_affinity_index = None

    def __del__(self):
        if self._is_running:
            logger.warning("job %s destructed while running", self._db_job.command)

    def cancel(self):
        self._pipe.kill()

    def wait_for_completion(self, status, timeout_seconds=30):
        complete = False
        for _ in range(timeout_seconds):
            if self._pipe.poll() is not None:
                complete = True
                logger.info("job %s has exited", self.key)
                break
            time.sleep(1)
        if not complete:
            logger.warning("Timed out waiting for job %s to complete", self.key)

        self._complete(status)

    @property
    def db_job(self):
        return self._db_job

    @db_job.setter
    def db_job(self, job):
        self._db_job = job

    def get_result(self, run_id):
        assert self._is_complete
        return WorkflowResultsModel(
            job_key=self.key,
            run_id=run_id,
            return_code=self._return_code,
            exec_time_minutes=self._exec_time_s / 60,
            completion_time=self._completion_time,
            status=self._status,
        )

    def terminate(self):
        self._pipe.terminate()

    def is_complete(self):
        if self._is_complete:
            return True

        if self._pipe.poll() is not None:
            self._complete("done")

        return not self._is_running

    @property
    def key(self):
        return self._db_job.key

    @property
    def pid(self) -> int:
        """Return the process ID for the job."""
        return self._pipe.pid

    def run(self, output_dir: Path):
        assert self._pipe is None
        self._start_time = time.time()

        basename = self.key if self._log_prefix is None else f"{self._log_prefix}_{self.key}"
        stdout_filename = output_dir / JOB_STDIO_DIR / f"{basename}.o"
        stderr_filename = output_dir / JOB_STDIO_DIR / f"{basename}.e"
        # pylint: disable=consider-using-with
        self._stdout_fp = open(stdout_filename, "w", encoding="utf-8")
        self._stderr_fp = open(stderr_filename, "w", encoding="utf-8")
        env = os.environ.copy()
        env["TORC_JOB_KEY"] = self._db_job.key
        # TORC_WORKFLOW_KEY is also set
        if self._db_job.invocation_script:
            self._pipe = self._run_invocation_script(env=env)
        else:
            self._pipe = self._run_command(self._db_job.command, env=env)
        if self._cpu_affinity_tracker is not None:
            self._cpu_affinity_index, mask = self._cpu_affinity_tracker.acquire_mask()
            os.sched_setaffinity(self._pipe.pid, mask)  # pylint: disable=no-member
            logger.info("Set CPU affinity for job={self._key} to {mask=}")

        # pylint: enable=consider-using-with
        self._is_running = True

    def _run_command(self, command, env):
        logger.info("Run job=%s command %s", self._db_job.key, command)
        cmd = shlex.split(command, posix="win" not in sys.platform)
        return subprocess.Popen(cmd, stdout=self._stdout_fp, stderr=self._stderr_fp, env=env)

    def _run_invocation_script(self, env):
        cmd = f"{self._db_job.invocation_script} {self._db_job.command}"
        return self._run_command(cmd, env)

    def _complete(self, status):
        self._return_code = self._pipe.returncode
        self._stdout_fp.close()
        self._stderr_fp.close()
        self._completion_time = datetime.now()
        self._exec_time_s = time.time() - self._start_time
        self._is_running = False
        self._is_complete = True
        self._status = status
        if self._cpu_affinity_index is not None:
            self._cpu_affinity_tracker.release_mask(self._cpu_affinity_index)
            self._cpu_affinity_index = None

        logger.info(
            "Job %s completed return_code=%s exec_time_s=%s status=%s",
            self.key,
            self._return_code,
            self._exec_time_s,
            self._status,
        )
