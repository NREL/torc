"""HPC management functionality"""

import logging
from pathlib import Path

from torc.exceptions import ExecutionError
from torc.hpc.common import HpcType
from torc.hpc.slurm_interface import SlurmInterface


logger = logging.getLogger(__name__)


class HpcManager:
    """Manages HPC job submission and monitoring."""

    def __init__(self, config, hpc_type: HpcType, output):
        self._output = output
        self._config = config
        self._hpc_type = hpc_type
        self._intf = self.create_hpc_interface(hpc_type)

        logger.debug("Constructed HpcManager with output=%s", output)

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
        ret = self._intf.cancel_job(job_id)
        if ret == 0:
            logger.info("Successfully cancelled job ID %s", job_id)
        else:
            logger.info("Failed to cancel job ID %s", job_id)

        return ret

    def get_status(self, job_id=None):
        """Return the status of a job by ID.

        Parameters
        ----------
        job_id : str
            job ID

        Returns
        -------
        HpcJobStatus

        """
        info = self._intf.get_status(job_id=job_id)
        logger.debug("info=%s", info)
        return info.status

    def get_statuses(self):
        """Check the statuses of all user jobs.

        Returns
        -------
        dict
            key is job_id, value is HpcJobStatus

        """
        return self._intf.get_statuses()

    def get_job_stats(self, job_id):
        """Get stats for job ID.

        Parameters
        ----------
        job_id : str

        Returns
        -------
        HpcJobStats

        """
        return self._intf.get_job_stats(job_id)

    def get_local_scratch(self):
        """Get path to local storage space.

        Returns
        -------
        str

        """
        return self._intf.get_local_scratch()

    @property
    def hpc_type(self):
        """Return the type of HPC management system.

        Returns
        -------
        HpcType

        """
        return self._hpc_type

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
        return self._intf.list_active_nodes(job_id)

    def submit(
        self,
        directory: Path,
        name: str,
        command: str,
        keep_submission_script=False,
        start_one_worker_per_node=False,
    ):
        """Submits scripts to the queue for execution.

        Parameters
        ----------
        directory : Path
            directory to contain the submission script
        name : str
            job name
        command : str
            Command to execute.
        keep_submission_script : bool
            Whether to keep the submission script, defaults to False.
        start_one_worker_per_node : bool
            If True, start a torc worker on each compute node, defaults to False.
            The default behavior defers control of a multi-node job to the user job.

        Returns
        -------
        str
            job_id
        """
        filename = directory / (name + ".sh")
        self._intf.create_submission_script(
            name,
            command,
            filename,
            self._output,
            self._config,
            start_one_worker_per_node=start_one_worker_per_node,
        )
        logger.debug("Created submission script %s", filename)

        ret, job_id, err = self._intf.submit(filename)

        if ret == 0:
            logger.info("job '%s' with ID=%s submitted successfully", name, job_id)
            if not keep_submission_script:
                filename.unlink()
        else:
            logger.error("Failed to submit job '%s': ret=%s: %s", name, ret, err)
            raise ExecutionError(f"Failed to submit HPC job {name}: {ret}")

        return job_id

    @staticmethod
    def create_hpc_interface(hpc_type):
        """Returns an HPC implementation instance appropriate for the current
        environment.

        """
        match hpc_type:
            case HpcType.SLURM:
                intf = SlurmInterface()
            # case HpcType.FAKE:
            #    intf = FakeManager(config)
            case _:
                raise ValueError(f"Unsupported HPC type: {hpc_type}")

        logger.debug("HPC manager type=%s", hpc_type)
        return intf
