"""Common functions for CLI commands"""

import json
import sys
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

import rich_click as click
from loguru import logger
from prettytable import PrettyTable

from torc.api import iter_documents
from torc.loggers import setup_logging
from torc.openapi_client import DefaultApi
from torc.openapi_client.models.workflow_model import WorkflowModel


def check_output_path(path: Path, force: bool) -> None:
    """Ensures that the parameter path does not exist.

    Parameters
    ----------
    path : Path
    force : bool
        If True and the path exists, delete it.
    """
    if path.exists():
        if force:
            path.unlink()
        else:
            print(
                f"{path} already exists. Choose a different name or pass --force to overwrite it.",
                file=sys.stderr,
            )
            sys.exit(1)
