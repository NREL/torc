"""torc package"""

import warnings
from importlib import metadata

from torc.api import (
    create_jobs,
    iter_documents,
    make_api,
    make_job_label,
    map_function_to_jobs,
    send_api_command,
)
from torc.loggers import setup_logging


__version__ = metadata.metadata("torc-client")["Version"]

warnings.filterwarnings("once", category=DeprecationWarning)


__all__ = (
    "create_jobs",
    "iter_documents",
    "make_api",
    "make_job_label",
    "map_function_to_jobs",
    "send_api_command",
    "setup_logging",
)
