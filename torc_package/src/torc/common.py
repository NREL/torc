"""Common definitions in this package"""

import enum
import importlib
import os
import sys
from datetime import datetime
from types import ModuleType
from typing import Callable, Optional

from pydantic import BaseModel, ConfigDict

from rmon.timing.timer_stats import TimerStatsCollector


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


class JobStatus(str, enum.Enum):
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


def check_function(
    module_name: str, func_name: str, module_directory: Optional[str] = None
) -> tuple[ModuleType, Callable]:
    """Check that func_name is importable from module name and returns the module and function
    references.
    """
    cur_dir = os.getcwd()
    added_cur_dir = False
    try:
        if module_directory is not None:
            sys.path.append(module_directory)
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        sys.path.append(cur_dir)
        module = importlib.import_module(module_name)
    finally:
        if module_directory is not None:
            sys.path.remove(module_directory)
        if added_cur_dir:
            sys.path.remove(cur_dir)

    func = getattr(module, func_name)
    if func is None:
        msg = f"function={func_name} is not defined in {module_name}"
        raise ValueError(msg)
    return module, func


def convert_timestamp(timestamp: int) -> datetime:
    """Convert the timestamp stored in the database to a datetime."""
    return datetime.fromtimestamp(timestamp / 1000)
