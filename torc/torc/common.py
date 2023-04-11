"""Common definitions in this package"""

from pydantic import BaseModel  # pylint: disable=no-name-in-module

KiB = 1024
MiB = KiB * KiB
GiB = MiB * KiB
TiB = GiB * KiB
JOB_STDIO_DIR = "job-stdio"
STATS_DIR = "stats"


class TorcBaseModel(BaseModel):
    """Base model for the torc package"""

    class Config:
        """Custom config"""

        title = "TorcBaseModel"
        anystr_strip_whitespace = True
        validate_assignment = True
        validate_all = True
        extra = "forbid"
        use_enum_values = False
