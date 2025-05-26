"""HPC management functionality"""

from pathlib import Path

from loguru import logger

from torc.exceptions import ExecutionError
from torc.hpc.common import HpcType, HpcJobStatus, HpcJobStats
from torc.hpc.hpc_interface import HpcInterface
from torc.hpc.slurm_interface import SlurmInterface


class HpcManager:
    """Manages HPC job submission and monitoring."""

    def __init__(self, config: dict[str, str], hpc_type: HpcType, output) -> None:
        self._output = output
        self._config = config
        self._hpc_type = hpc_type
        self._intf = self.create_hpc_interface(hpc_type)

        logger.trace("Constructed HpcManager with output={}", output)

    def cancel_job(self, job_id: str) -> int:
        """Cancel the job."""
        ret = self._intf.cancel_job(job_id)
        if ret == 0:
            logger.info("Successfully cancelled job ID {}", job_id)
        else:
            logger.info("Failed to cancel job ID {}", job_id)

        return ret

    def get_status(self, job_id: str) -> HpcJobStatus:
        """Return the status of a job by ID."""
        info = self._intf.get_status(job_id=job_id)
        logger.trace("info={}", info)
        return info.status

    def get_statuses(self) -> dict[str, HpcJobStatus]:
        """Check the statuses of all user jobs.

        Returns
        -------
        dict
            key is job_id, value is HpcJobStatus
        """
        return self._intf.get_statuses()

    def get_job_stats(self, job_id: str) -> HpcJobStats:
        """Get stats for job ID."""
        return self._intf.get_job_stats(job_id)

    def get_local_scratch(self) -> str:
        """Get path to local storage space."""
        return self._intf.get_local_scratch()

    @property
    def hpc_type(self) -> HpcType:
        """Return the type of HPC management system."""
        return self._hpc_type

    def list_active_nodes(self, job_id: str) -> list[str]:
        """Return the node hostnames currently participating in the job. Order should be
        deterministic.
        """
        return self._intf.list_active_nodes(job_id)

    def submit(
        self,
        directory: Path,
        name: str,
        command: str,
        keep_submission_script: bool = False,
        start_one_worker_per_node: bool = False,
    ) -> str:
        """Submits scripts to the queue for execution.

        Parameters
        ----------
        directory
            directory to contain the submission script
        name
            job name
        command
            Command to execute.
        keep_submission_script
            Whether to keep the submission script, defaults to False.
        start_one_worker_per_node
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
        logger.trace("Created submission script {}", filename)

        ret, job_id, err = self._intf.submit(filename)

        if ret == 0:
            logger.info("job '{}' with ID={} submitted successfully", name, job_id)
            if not keep_submission_script:
                filename.unlink()
        else:
            logger.error("Failed to submit job '{}': ret={}: {}", name, ret, err)
            msg = f"Failed to submit HPC job {name}: {ret}"
            raise ExecutionError(msg)

        return job_id

    @staticmethod
    def create_hpc_interface(hpc_type: HpcType) -> HpcInterface:
        """Returns an HPC implementation instance appropriate for the current
        environment.
        """
        match hpc_type:
            case HpcType.SLURM:
                intf = SlurmInterface()
            # case HpcType.FAKE:
            #    intf = FakeManager(config)
            case _:
                msg = f"Unsupported HPC type: {hpc_type}"
                raise ValueError(msg)

        logger.trace("HPC manager type={}", hpc_type)
        return intf
