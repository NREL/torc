"""Common definitions for HPC functionality"""

from collections import namedtuple
import enum


class HpcJobStatus(enum.Enum):
    """Represents the status of an HPC job."""

    UNKNOWN = "unknown"
    NONE = "none"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"


HpcJobInfo = namedtuple("HpcJobInfo", "job_id, name, status")
HpcJobStats = namedtuple(
    "HpcJobStats", "hpc_job_id, name, start, end, state, account, partition, qos"
)


class HpcType(enum.Enum):
    """HPC types"""

    PBS = "pbs"
    SLURM = "slurm"
    FAKE = "fake"
