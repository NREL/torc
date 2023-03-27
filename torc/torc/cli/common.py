"""Common functions for CLI commands"""

import logging
import shutil
import sys
from pathlib import Path

from prettytable import PrettyTable

from torc.api import make_api
from torc.loggers import setup_logging


logger = logging.getLogger(__name__)


def check_output_directory(path: Path, force: bool):
    """Ensures that the parameter path is an empty directory.

    Parameters
    ----------
    path : Path
    force : bool
        If False and the directory exists and has content, exit.
    """
    if path.exists():
        if not bool(path.iterdir()):
            return
        if force:
            shutil.rmtree(path)
        else:
            print(
                f"{path} already exists. Choose a different name or pass --force to overwrite it.",
                file=sys.stderr,
            )
            sys.exit(1)

    path.mkdir()


def make_api_from_click_context(ctx, levels):
    """Instantiate a Swagger API object from a click context."""
    match levels:
        case 1:
            database_url = ctx.parent.params["database_url"]
        case 2:
            database_url = ctx.parent.parent.params["database_url"]
        case _:
            raise Exception(f"levels={levels} is not supported")

    return make_api(database_url)


def make_text_table(iterable, title, exclude_columns=None):
    """Return a PrettyTable from an iterable.

    Parameters
    ----------
    iterable : sequence
        Sequence of dicts
    title : str
    exclude_columns : None | list
        Keys of each dict in iterable to exclude. Mutates iterable.

    Returns
    -------
    PrettyTable
    """
    table = PrettyTable(title=title)
    for i, item in enumerate(iterable):
        for column in exclude_columns or []:
            item.pop(column)
        if i == 0:
            table.field_names = tuple(item.keys())
        table.add_row(item.values())
    return table


def path_callback(*args) -> Path:
    """click callback to convert a string to a Path."""
    return Path(args[2])


def parse_filters(filters):
    """Parse filter options given on the command line."""
    final = {}
    for flt in filters:
        fields = flt.split("=")
        if len(fields) != 2:
            logger.error("Invalid filter format: %s. Required: name=value", flt)
            sys.exit(1)
        final[fields[0]] = fields[1]

    return final


def setup_cli_logging(ctx, depth, name, filename=None, mode="w"):
    """Setup logging from a click context."""
    match depth:
        case 1:
            params = ctx.parent.params
        case 2:
            params = ctx.parent.parent.params
        case 3:
            params = ctx.parent.parent.parent.params
        case _:
            raise Exception(f"Unsupported depth={depth}")

    return setup_logging(
        name,
        filename=filename,
        console_level=params["console_level"],
        file_level=params["file_level"],
        mode=mode,
    )
