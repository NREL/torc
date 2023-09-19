"""Common definitions in this package"""

import enum

from pydantic import BaseModel, ConfigDict  # pylint: disable=no-name-in-module

from resource_monitor.timing.timer_stats import TimerStatsCollector


KiB = 1024
MiB = KiB * KiB
GiB = MiB * KiB
TiB = GiB * KiB
JOB_STDIO_DIR = "job-stdio"
STATS_DIR = "stats"

timer_stats_collector = TimerStatsCollector()


class TorcBaseModel(BaseModel):
    """Base model for the torc package"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        use_enum_values=False,
    )


class JobStatus(enum.Enum):
    """Defines all job statuses."""

    # Keep in sync with the JobStatus definition in the torc-service.

    UNINITIALIZED = "uninitialized"
    BLOCKED = "blocked"
    CANCELED = "canceled"
    TERMINATED = "terminated"
    DONE = "done"
    READY = "ready"
    SCHEDULED = "scheduled"
    SUBMITTED = "submitted"
    SUBMITTEDpENDING = "submitted_pending"
    DISABLED = "disabled"
