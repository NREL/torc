"""HPC management implementation functionality"""

import abc
import getpass
from datetime import datetime
from pathlib import Path

from torc.hpc.common import HpcJobInfo, HpcJobStats, HpcJobStatus


class HpcInterface(abc.ABC):
    """Defines the implementation interface for managing an HPC."""

    USER = getpass.getuser()

    @abc.abstractmethod
    def cancel_job(self, job_id: str) -> int:
        """Cancel the job.

        Returns
        -------
        int
            Return code of the job.
        """

    @abc.abstractmethod
    def get_status(self, job_id: str) -> HpcJobInfo:
        """Check the status of a job.
        Handles transient errors for up to one minute.

        Raises
        ------
        ExecutionError
            Raised if statuses cannot be retrieved.
        """

    @abc.abstractmethod
    def get_statuses(self) -> dict[str, HpcJobStatus]:
        """Check the statuses of all user jobs.
        Handles transient errors for up to one minute.

        Returns
        -------
        dict
            key is job_id, value is HpcJobStatus

        Raises
        ------
        ExecutionError
            Raised if statuses cannot be retrieved.

        """

    @abc.abstractmethod
    def create_submission_script(
        self,
        name: str,
        command: str,
        filename: str | Path,
        path: str,
        config: dict[str, str],
        start_one_worker_per_node: bool = False,
    ) -> None:
        """Create the script to queue the jobs to the HPC.

        Parameters
        ----------
        name
            job name
        command
            CLI command to execute on HPC
        filename
            submission script filename
        path
            path for stdout and stderr files
        config
            Configuration parameters and values for the HPC scheduler
        start_one_worker_per_node
            If True, start a torc worker on each compute node, defaults to False.
            The default behavior defers control of a multi-node job to the user job.
        """

    @abc.abstractmethod
    def get_current_job_id(self) -> str:
        """Return the HPC job ID from the current job."""

    @abc.abstractmethod
    def get_environment_variables(self) -> dict[str, str]:
        """Return a dict of all relevant HPC environment variables."""

    @abc.abstractmethod
    def get_job_end_time(self) -> datetime:
        """Return the end time for the current job."""

    @abc.abstractmethod
    def get_job_stats(self, job_id) -> HpcJobStats:
        """Get stats for job ID."""

    @abc.abstractmethod
    def get_local_scratch(self) -> str:
        """Get path to local storage space."""

    @abc.abstractmethod
    def get_memory_gb(self) -> float:
        """Return the memory available to a job in GiB."""

    @abc.abstractmethod
    def get_node_id(self) -> str:
        """Return the node ID of the current system."""

    @abc.abstractmethod
    def get_num_cpus(self) -> int:
        """Return the number of CPUs on the current node."""

    @abc.abstractmethod
    def get_num_gpus(self) -> int:
        """Return the number of GPUs on the current node."""

    @abc.abstractmethod
    def get_num_nodes(self) -> int:
        """Return the number of compute nodes in the current job."""

    @abc.abstractmethod
    def list_active_nodes(self, job_id: str) -> list[str]:
        """Return the node hostname currently participating in the job. Order should be
        deterministic.
        """

    @abc.abstractmethod
    def submit(self, filename) -> tuple[int, str, str]:
        """Submit the work to the HPC queue.
        Handles transient errors for up to one minute.

        Parameters
        ----------
        filename : str
            HPC script filename

        Returns
        -------
        tuple of int, str, str
            (return_code, job_id, stderr)
        """
