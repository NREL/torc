"""Common definitions for HPC functionality"""

import enum
from datetime import datetime
from typing import NamedTuple, Optional


class HpcJobStatus(str, enum.Enum):
    """Represents the status of an HPC job."""

    UNKNOWN = "unknown"
    NONE = "none"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"


class HpcJobInfo(NamedTuple):
    """Defines the status of a job submitted to the HPC."""

    job_id: str
    name: str
    status: HpcJobStatus


class HpcJobStats(NamedTuple):
    """Defines the stats for an HPC job."""

    hpc_job_id: str
    name: str
    start: datetime
    end: Optional[datetime]
    state: str
    account: str
    partition: str
    qos: str


class HpcType(enum.Enum):
    """HPC types"""

    PBS = "pbs"
    SLURM = "slurm"
    FAKE = "fake"
