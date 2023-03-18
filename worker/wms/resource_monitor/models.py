"""Defines data models used in resource monitoring code."""

import enum

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class WmsBaseModel(BaseModel):
    """Base model for all custom types"""

    class Config:
        """Custom config"""

        json_encoders = {
            enum.Enum: lambda x: x.value,
        }


class ResourceType(enum.Enum):
    """Types of resources to monitor"""

    CPU = "CPU"
    DISK = "Disk"
    MEMORY = "Memory"
    NETWORK = "Network"
    PROCESS = "Process"


class IpcMonitorCommands(enum.Enum):
    """Monitor commands that can be sent to child processes"""

    COMPLETE_JOBS = "complete_pids"
    SELECT_STATS = "select_stats"
    SHUTDOWN = "shutdown"
    UPDATE_STATS = "update_stats"


# TODO DT: make test to assert that this is the same as WorkflowConfigComputeNodeResourceStats
# Want two versions so that this can be used without the Swagger API
class ComputeNodeResourceStatConfig(WmsBaseModel):
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
    interval: int = Field(description="Interval in seconds on which to collect stats", default=10)
    name: str

    @classmethod
    def disabled(cls):
        """Return an instance with all stats disabled."""
        return cls(
            cpu=False,
            disk=False,
            memory=False,
            network=False,
            process=False,
            name="disabled",
        )


class ResourceStatResults(WmsBaseModel):
    """Results for one resource type"""

    resource_type: ResourceType
    average: dict
    minimum: dict
    maximum: dict
    num_samples: int


class ProcessStatResults(ResourceStatResults):
    """Results for one process stat"""

    job_name: str


class ComputeNodeResourceStatResults(WmsBaseModel):
    """Contains all results from one compute node"""

    name: str
    hostname: str = Field(description="Hostname of compute node")
    results: list[ResourceStatResults]
