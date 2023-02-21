import enum

from pydantic import BaseModel, Field


class WmsBaseModel(BaseModel):
    class Config:
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

    SELECT_STATS = "select_stats"
    SET_PIDS = "set_pids"
    SHUTDOWN = "shutdown"


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
    resource_type: ResourceType
    average: dict
    minimum: dict
    maximum: dict
    num_samples: int


class ProcessStatResults(ResourceStatResults):
    job_name: str


class ComputeNodeResourceStatResults(WmsBaseModel):
    name: str
    hostname: str = Field(description="Hostname of compute node")
    results: list[ResourceStatResults]
