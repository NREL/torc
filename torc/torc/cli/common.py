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
        msg = (
            "\nThis command requires a workflow key and one was not provided. "
            "Please choose one from below.\n"
        )
        doc = prompt_user_for_document(
            "workflow", api.get_workflows, exclude_columns=("id", "rev"), msg=msg
        )
        if doc is None:
            logger.error("No workflows are stored")
            sys.exit(1)
        key = doc.key
    else:
        key = params["workflow_key"]
    return key


def prompt_user_for_document(
    doc_type,
    getter_func,
    *args,
    auto_select_one_option=False,
    exclude_columns=None,
    msg=None,
    **kwargs,
):
    """Help a user select a document by printing a table of available documents.

    Parameters
    ----------
    doc_type : string
        Ex: 'workflow', 'job'
    getter_func : function
        Database API function that can be passed to iter_documents to retrieve documents.
        *args and **kwargs are forwarded to that function.
    exclude_columns : None or tuple
        Columns to exclude from the printed table.
    auto_select_one_option : bool
        If True and there is only one document, return that document's key.
    msg : str | None
        If not None, print the message before printing the table.

    Returns
    -------
    object | None
        Swagger data model or None if no documents are stored.
    """
    docs = []
    dicts = []
    index_to_doc = {}
    for i, doc in enumerate(iter_documents(getter_func, *args, **kwargs), start=1):
        data = {"index": i}
        data.update(doc.to_dict())
        index_to_doc[i] = doc
        dicts.append(data)
        docs.append(doc)

    if not docs:
        logger.error("No items of type %s with matching criteria are stored.", doc_type)
        return None

    if len(docs) == 1 and auto_select_one_option:
        return docs[0]

    if msg:
        print(msg)

    table = make_text_table(dicts, doc_type, exclude_columns=exclude_columns)
    if table.rows:
        print(table)

    doc = None
    while not doc:
        choice = input("Select an index: >>> ").strip()
        try:
            selected_index = int(choice)
            doc = index_to_doc.get(selected_index)
        except ValueError:
            logger.error("Could not convert %s to an integer.", choice)
        if not doc:
            print(f"index={choice} is an invalid choice")

    return doc


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
