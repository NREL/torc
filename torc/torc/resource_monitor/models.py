"""Defines data models used in resource monitoring code."""

import enum

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class TorcBaseModel(BaseModel):
    """Base model for all custom types"""

    class Config:
        """Custom config"""

        anystr_strip_whitespace = True
        validate_assignment = True
        validate_all = True
        extra = "forbid"
        use_enum_values = False
        json_encoders = {
            enum.Enum: lambda x: x.value,
        }


class ResourceType(enum.Enum):
    """Types of resources to monitor"""

    CPU = "cpu"
    DISK = "disk"
    MEMORY = "memory"
    NETWORK = "network"
    PROCESS = "process"


class IpcMonitorCommands(enum.Enum):
    """Monitor commands that can be sent to child processes"""

    COMPLETE_JOBS = "complete_pids"
    SELECT_STATS = "select_stats"
    SHUTDOWN = "shutdown"
    UPDATE_PIDS = "update_pids"


# This is duplicate of WorkflowsconfigkeyComputeNodeResourceStats. We want the duplicate
# so that this can be used without the Swagger API.


class ComputeNodeResourceStatConfig(TorcBaseModel):
    """Defines the stats to monitor."""

    cpu: bool = Field(
        description="Monitor CPU utilization",
        default=True,
    )
    disk: bool = Field(
        description="Monitor disk/storage utilization",
        default=False,
    )
    memory: bool = Field(
        description="Monitor memory utilization",
        default=True,
    )
    network: bool = Field(
        description="Monitor network utilization",
        default=False,
    )
    process: bool = Field(
        description="Monitor per-job process utilization",
        default=True,
    )
    include_child_processes: bool = Field(
        description="Include stats from direct child processes in utilization for each job.",
        default=True,
    )
    recurse_child_processes: bool = Field(
        description="Recurse child processes to find all descendants.",
        default=False,
    )
    monitor_type: str = Field(
        description="'aggregation' or 'periodic'. Keep aggregated stats in memory or record time-series data on an interval.",
        default=False,
    )
    make_plots: bool = Field(
        description="Make time-series plots if monitor_type is periodic.", default=True
    )
    interval: float = Field(
        description="Interval in seconds on which to collect stats", default=10
    )

    @classmethod
    def all_enabled(cls):
        """Return an instance with all stats enabled."""
        return cls(
            cpu=True,
            disk=True,
            memory=True,
            network=True,
            process=True,
        )

    @classmethod
    def disabled(cls):
        """Return an instance with all stats disabled."""
        return cls(
            cpu=False,
            disk=False,
            memory=False,
            network=False,
            process=False,
        )

    def is_enabled(self):
        """Return True if any stat is enabled."""
        return self.cpu or self.disk or self.memory or self.network or self.process


class ResourceStatResults(TorcBaseModel):
    """Results for one resource type"""

    resource_type: ResourceType
    average: dict
    minimum: dict
    maximum: dict
    num_samples: int


class ProcessStatResults(ResourceStatResults):
    """Results for one process stat"""

    job_key: str


class ComputeNodeResourceStatResults(TorcBaseModel):
    """Contains all results from one compute node"""

    hostname: str = Field(description="Hostname of compute node")
    results: list[ResourceStatResults]
