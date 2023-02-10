import abc
import logging
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from swagger_client.models.result_model import ResultModel

logger = logging.getLogger(__name__)


class AsyncJobBase(abc.ABC):
    @abc.abstractmethod
    def run(self, output_dir: Path):
        """Run a job."""

    @abc.abstractmethod
    def is_complete(self):
        """Return True if a job is complete."""

    @property
    @abc.abstractmethod
    def name(self):
        """Return the name of the job."""

    @property
    @abc.abstractmethod
    def result(self):
        """Return a Result for the job after it is completed.

        Returns
        -------
        ResultModel
        """


class AsyncCliCommand(AsyncJobBase):
    """Manages execution of an asynchronous CLI command."""

    def __init__(self, job):
        self._job = job
        self._pipe = None
        self._is_pending = False
        self._start_time = 0.0
        self._completion_time = 0.0
        self._return_code = None
        self._is_complete = False
        self._stdout_fp = None
        self._stderr_fp = None

    def __del__(self):
        if self._is_pending:
            logger.warning("job %s destructed while pending", self.command)

    @property
    def job(self):
        return self._job

    @job.setter
    def job(self, job):
        self._job = job

    @property
    def command(self):
        return self._job.command

    @property
    def name(self):
        return self._job.name

    def is_complete(self):
        if self._is_complete:
            return True

        if not self._is_pending:
            ret = self._pipe.poll()
            assert ret is None, ret
            return True

        if self._pipe.poll() is not None:
            self._is_pending = False
            self._complete()

        return not self._is_pending

    def _complete(self):
        self._return_code = self._pipe.returncode
        self._stdout_fp.close()
        self._stderr_fp.close()
        self._completion_time = datetime.now()
        self._exec_time_s = time.time() - self._start_time
        self._is_complete = True

        logger.info(
            "Job %s completed return_code=%s exec_time_s=%s",
            self.name,
            self._return_code,
            self._exec_time_s,
        )

    @property
    def result(self):
        assert self._is_complete
        return ResultModel(
            name=self.name,
            return_code=self._return_code,
            exec_time_minutes=self._exec_time_s / 60,
            completion_time=self._completion_time,
            status="done",
        )

    def run(self, output_dir: Path):
        assert self._pipe is None
        self._start_time = time.time()

        cmd = shlex.split(self.command, posix="win" not in sys.platform)
        stdout_filename = output_dir / f"{self.name}.o"
        stderr_filename = output_dir / f"{self.name}.e"
        self._stdout_fp = open(stdout_filename, "w")
        self._stderr_fp = open(stderr_filename, "w")
        self._pipe = subprocess.Popen(
            cmd, stdout=self._stdout_fp, stderr=self._stderr_fp
        )
        self._is_pending = True
