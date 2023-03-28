"""Common functions for CLI commands"""

import logging
import shutil
import sys
from pathlib import Path

from prettytable import PrettyTable

from torc.api import iter_documents
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


def get_workflow_key_from_context(ctx, api):
    """Get the workflow ID from a click context."""
    params = ctx.find_root().params
    if params["workflow_key"] is None:
        if params["no_prompts"]:
            logger.error("--workflow-key must be set")
            sys.exit(1)
        exclude = ("id", "rev")
        workflows = []
        index_to_key = {}
        for i, workflow in enumerate(iter_documents(api.get_workflows), start=1):
            data = {"index": i}
            data.update(workflow.to_dict())
            index_to_key[i] = workflow.key
            workflows.append(data)
        table = make_text_table(workflows, "Workflows", exclude_columns=exclude)
        if table.rows:
            print(table)
        else:
            logger.info("No workflows are stored")
            sys.exit(1)
        while not params["workflow_key"]:
            key = input("Workflow key is required. Select an index from above: >>> ").strip()
            try:
                selected_index = int(key)
                params["workflow_key"] = index_to_key.get(selected_index)
            except ValueError:
                pass
            if not params["workflow_key"]:
                print(f"index={key} is an invalid choice")
    return params["workflow_key"]


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


def setup_cli_logging(ctx, name, filename=None, mode="w"):
    """Setup logging from a click context."""
    params = ctx.find_root().params
    return setup_logging(
        name,
        filename=filename,
        console_level=params["console_level"],
        file_level=params["file_level"],
        mode=mode,
    )
