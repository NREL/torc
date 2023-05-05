"""HPC management implementation functionality"""

import abc
import getpass
from datetime import datetime


class HpcInterface(abc.ABC):
    """Defines the implementation interface for managing an HPC."""

    USER = getpass.getuser()

    @abc.abstractmethod
    def cancel_job(self, job_id):
        """Cancel job.

        Parameters
        ----------
        job_id : str

        Returns
        -------
        int
            return code

        """

    @abc.abstractmethod
    def get_status(self, job_id):
        """Check the status of a job.
        Handles transient errors for up to one minute.

        Parameters
        ----------
        job_id : str
            job ID

        Returns
        -------
        HpcJobInfo

        Raises
        ------
        ExecutionError
            Raised if statuses cannot be retrieved.

        """

    @abc.abstractmethod
    def get_statuses(self):
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
        self, name, command, filename, path, config, start_one_worker_per_node=False
    ):
        """Create the script to queue the jobs to the HPC.

        Parameters
        ----------
        name : str
            job name
        command : str
            CLI command to execute on HPC
        filename : str
            submission script filename
        path : str
            path for stdout and stderr files
        config : dict[str, str]
            Configuration parameters and values for the HPC scheduler
        start_one_worker_per_node : bool
            If True, start a torc worker on each compute node, defaults to False.
            The default behavior defers control of a multi-node job to the user job.

        """

    @abc.abstractmethod
    def get_current_job_id(self):
        """Return the HPC job ID from the current job."""

    @abc.abstractmethod
    def get_environment_variables(self) -> dict[str, dict]:
        """Return a dict of all relevant HPC environment variables."""

    @abc.abstractmethod
    def get_job_end_time(self) -> datetime:
        """Return the end time for the current job."""

    @abc.abstractmethod
    def get_job_stats(self, job_id):
        """Get stats for job ID.

        Returns
        -------
        HpcJobStats

        """

    @abc.abstractmethod
    def get_local_scratch(self):
        """Get path to local storage space.

        Returns
        -------
        str

        """

    @abc.abstractmethod
    def get_memory_gb(self) -> int:
        """Return the memory available to a job in GiB."""

    @abc.abstractmethod
    def get_node_id(self) -> str:
        """Return the node ID of the current system.

        Returns
        -------
        str

        """

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
    def list_active_nodes(self, job_id):
        """Return the nodes currently participating in the job. Order should be deterministic.

        Parameters
        ----------
        job_id : str

        Returns
        -------
        list
            list of node hostnames

        """

    @abc.abstractmethod
    def submit(self, filename):
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
