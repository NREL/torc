"""Common functions for CLI commands"""

import json
import logging
import shutil
import sys
from pathlib import Path

from prettytable import PrettyTable

from torc.api import iter_documents
from torc.loggers import setup_logging
from torc.torc_rc import TorcRuntimeConfig


logger = logging.getLogger(__name__)


def check_database_url(api):
    """Raises an exception if a database URL is not set."""
    if api is None:
        rc_path = TorcRuntimeConfig.path()
        print(
            "The database_url, in the format \n"
            "    http://<database_hostname>:8529/_db/<database_name>/torc-service,\n"
            "    such as http://localhost:8529/_db/workflows/torc-service,\n"
            "must be set in one of the following:\n"
            "  - CLI option:\n"
            "    $ torc -u URL\n"
            "   - environment variable TORC_DATABASE_URL\n"
            "    $ export TORC_DATABASE_URL=URL\n"
            f"  - torc runtime config file: {rc_path}\n"
            "    Set the value for the field database_url.\n",
            file=sys.stderr,
        )
        sys.exit(1)


def check_output_directory(path: Path, force: bool):
    """Ensures that the parameter path is an empty directory.

    Parameters
    ----------
    path : Path
    force : bool
        If False and the directory exists and has content, exit. If True, delete the contents.
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


def check_output_path(path: Path, force: bool):
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


def get_log_level_from_str(level):
    """Convert a log level string to logging type."""
    match level:
        case "debug":
            return logging.DEBUG
        case "info":
            return logging.INFO
        case "warning":
            return logging.WARNING
        case "error":
            return logging.ERROR
        case _:
            raise Exception(f"Unsupported level={level}")


def get_no_prompts_from_context(ctx) -> str:
    """Get the workflow ID from a click context."""
    return ctx.find_root().params["no_prompts"]


def get_output_format_from_context(ctx) -> str:
    """Get the workflow ID from a click context."""
    return ctx.find_root().params["output_format"]


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
        # TODO: filter by user. Still might have issues with hundreds of workflows
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


def print_items(
    ctx, items, table_title, json_key, exclude_columns=None, indent=None, start_index=0
):
    """Print items in either a table or JSON format, based on what is set in ctx."""
    output_format = get_output_format_from_context(ctx)
    if output_format == "text":
        table = make_text_table(
            items, table_title, exclude_columns=exclude_columns, start_index=start_index
        )
        if table.rows:
            print(table)
        else:
            logger.info("No %s are stored", json_key)
    else:
        assert output_format == "json", output_format
        rows = []
        for item in items:
            for column in exclude_columns or []:
                item.pop(column, None)
            rows.append(item)
        print(json.dumps({json_key: rows}, indent=indent))


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
    for i, doc in enumerate(iter_documents(getter_func, *args, **kwargs)):
        index_to_doc[i] = doc
        dicts.append(doc.to_dict())
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


def make_text_table(iterable, title, exclude_columns=None, start_index=0):
    """Return a PrettyTable from an iterable.

    Parameters
    ----------
    iterable : sequence
        Sequence of dicts
    title : str
    exclude_columns : None | list
        Keys of each dict in iterable to exclude. Mutates iterable.
    start_index : int

    Returns
    -------
    PrettyTable
    """
    table = PrettyTable(title=title)
    for i, item in enumerate(iterable, start=start_index):
        for column in exclude_columns or []:
            item.pop(column, None)
        if i == start_index:
            field_names = list(item.keys())
            field_names.insert(0, "index")
            table.field_names = field_names
        row = list(item.values())
        row.insert(0, i)
        table.add_row(row)
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
        val = fields[1]
        if val.isnumeric():
            val = int(val)
        final[fields[0]] = val

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
