"""Runs a CLI command asynchronously"""

import abc
import logging
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from swagger_client.models.result_model import ResultModel

from torc.common import JOB_STDIO_DIR

logger = logging.getLogger(__name__)


class AsyncJobBase(abc.ABC):
    """Base class for async jobs"""

    @abc.abstractmethod
    def run(self, output_dir: Path):
        """Run a job."""

    @abc.abstractmethod
    def cancel(self):
        """Cancel the job."""

    @property
    @abc.abstractmethod
    def db_job(self):
        """Return the underlying job object that is stored in the database."""

    @db_job.setter
    @abc.abstractmethod
    def db_job(self, job):
        """Set the underlying job object that is stored in the database."""

    @abc.abstractmethod
    def get_result(self):
        """Return a Result for the job after it is completed.

        Returns
        -------
        ResultModel
        """

    @abc.abstractmethod
    def is_complete(self):
        """Return True if the job is complete."""

    @property
    @abc.abstractmethod
    def key(self):
        """Return the key of the job."""


class AsyncCliCommand(AsyncJobBase):
    """Manages execution of an asynchronous CLI command."""

    def __init__(self, job):
        self._db_job = job
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

    def __del__(self):
        if self._is_running:
            logger.warning("job %s destructed while running", self._db_job.command)

    def cancel(self):
        self._pipe.kill()
        killed = False
        for _ in range(10):
            if self._pipe.poll() is not None:
                killed = True
                logger.info("Killed job %s", self.key)
                break
        if not killed:
            logger.warning("Timed out waiting for job %s to complete after being killed", self.key)

        self._complete("canceled")

    @property
    def db_job(self):
        return self._db_job

    @db_job.setter
    def db_job(self, job):
        self._db_job = job

    def get_result(self):
        assert self._is_complete
        return ResultModel(
            job_key=self.key,
            run_id=self._db_job.run_id,
            return_code=self._return_code,
            exec_time_minutes=self._exec_time_s / 60,
            completion_time=self._completion_time,
            status=self._status,
        )

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

        cmd = shlex.split(self._db_job.command, posix="win" not in sys.platform)
        stdout_filename = output_dir / JOB_STDIO_DIR / f"{self.key}.o"
        stderr_filename = output_dir / JOB_STDIO_DIR / f"{self.key}.e"
        # pylint: disable=consider-using-with
        self._stdout_fp = open(stdout_filename, "w", encoding="utf-8")
        self._stderr_fp = open(stderr_filename, "w", encoding="utf-8")
        self._pipe = subprocess.Popen(cmd, stdout=self._stdout_fp, stderr=self._stderr_fp)
        # pylint: enable=consider-using-with
        self._is_running = True

    def _complete(self, status):
        self._return_code = self._pipe.returncode
        self._stdout_fp.close()
        self._stderr_fp.close()
        self._completion_time = datetime.now()
        self._exec_time_s = time.time() - self._start_time
        self._is_running = False
        self._is_complete = True
        self._status = status

        logger.info(
            "Job %s completed return_code=%s exec_time_s=%s status=%s",
            self.key,
            self._return_code,
            self._exec_time_s,
            self._status,
        )
