"""Contains logging functionality."""

import sys
from pathlib import Path
from typing import Iterable

from loguru import logger

# Logger printing formats
DEFAULT_FORMAT = "<level>{level}</level>: {message}"
DEBUG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <7}</level> | "
    "<cyan>{name}:{line}</cyan> | "
    "{message}"
)


def setup_logging(
    filename: str | Path | None = None,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    mode: str = "w",
    rotation: str | None = "10 MB",
    packages: Iterable[str] | None = None,
) -> None:
    """Configures logging to file and console.

    Parameters
    ----------
    filename
        Log filename, defaults to None for no file logging.
    console_level
        Console logging level
    file_level
        File logging level
    mode
        Mode in which to open the file
    rotation
        Size in which to rotate file. Set to None for no rotation.
    packages
        Additional packages to enable logging
    """
    logger.remove()
    logger.enable("torc")
    for pkg in packages or []:
        logger.enable(pkg)

    logger.add(sys.stderr, level=console_level, format=DEFAULT_FORMAT)
    if filename:
        logger.add(
            filename,
            level=file_level,
            mode=mode,
            rotation=rotation,
            format=DEBUG_FORMAT,
        )
