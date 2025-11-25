"""Contains logging functionality."""

import sys
from collections.abc import Iterable
from pathlib import Path

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
    """Configure logging to file and console.

    Parameters
    ----------
    filename : str | Path | None, optional
        Log filename, by default None for no file logging.
    console_level : str, optional
        Console logging level, by default "INFO".
    file_level : str, optional
        File logging level, by default "DEBUG".
    mode : str, optional
        Mode in which to open the file, by default "w".
    rotation : str | None, optional
        Size at which to rotate file, by default "10 MB". Set to None for no rotation.
    packages : Iterable[str] | None, optional
        Additional packages to enable logging, by default None.
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
