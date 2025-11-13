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
from torc.config import torc_settings
from torc.openapi_client.models.workflow_model import WorkflowModel


def check_database_url(api: DefaultApi) -> None:
    """Raises an exception if a database URL is not set."""
    if api is None:
        rc_path = torc_settings.database_url
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


def confirm_change(ctx: click.Context, msg: str, dry_run: bool = False) -> None:
    """If prompts are enabled (default), prompt the user to confirm the change."""
    if get_no_prompts_from_context(ctx) or dry_run:
        return

    print(msg, file=sys.stderr)
    response = input("Continue? (y/n) [n]: >>> ").strip().lower() or "n"
    if response == "n":
        print("Exiting", file=sys.stderr)
        sys.exit(0)


def get_no_prompts_from_context(ctx: click.Context) -> bool:
    """Get the workflow ID from a click context."""
    return ctx.find_root().params["no_prompts"]


def get_output_format_from_context(ctx: click.Context) -> str:
    """Get the workflow ID from a click context."""
    return ctx.find_root().params["output_format"]


def get_user_from_context(ctx: click.Context) -> str:
    """Get the user from a click context."""
    return ctx.find_root().params["user"]


def get_workflow_key_from_context(ctx: click.Context, api: DefaultApi) -> str:
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
            "workflow",
            api.list_workflows,
            exclude_columns=("_id", "_rev"),
            msg=msg,
            auto_select_one_option=True,
            user=get_user_from_context(ctx),
            is_archived=False,
        )
        if doc is None:
            logger.error("No workflows are stored")
            sys.exit(1)
        key = doc.key
    else:
        key = params["workflow_key"]
    return key


def print_items(
    ctx: click.Context,
    items: Iterable[dict[str, Any]],
    table_title: str,
    columns: Iterable[str],
    json_key: str,
    indent: Optional[int] = None,
    start_index: int = 1,
):
    """Print items in either a table or JSON format, based on what is set in ctx."""
    output_format = get_output_format_from_context(ctx)
    if output_format in ("text", "csv"):
        table = make_text_table(items, table_title, columns=columns, start_index=start_index)
        if table.rows:
            print(table.get_formatted_string(output_format))
        else:
            logger.info("No {} are stored", json_key)
    else:
        # PrettyTable also supports JSON but we are using a custom key here.
        assert output_format == "json", output_format
        rows = []
        for item in items:
            rows.append({x: item.get(x) for x in columns})
        print(json.dumps({json_key: rows}, indent=indent))


def prompt_user_for_document(
    doc_type: str,
    getter_func: Callable,
    *args,
    auto_select_one_option: bool = False,
    exclude_columns: Optional[Iterable[str]] = None,
    msg: Optional[str] = None,
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
        OpenAPI [pydantic] model or None if no documents are stored.
    """
    docs = []
    dicts = []
    index_to_doc = {}
    _exclude_columns = exclude_columns or []
    for i, doc in enumerate(iter_documents(getter_func, *args, **kwargs), start=1):
        index_to_doc[i] = doc
        data = doc.to_dict()
        for col in _exclude_columns:
            data.pop(col, None)
        dicts.append(data)
        docs.append(doc)

    if not docs:
        logger.error("No items of type {} with matching criteria are stored.", doc_type)
        return None

    if len(docs) == 1 and auto_select_one_option:
        return docs[0]

    if msg:
        print(msg, file=sys.stderr)

    columns = dicts[0].keys()
    table = make_text_table(dicts, doc_type, columns, start_index=1)
    if table.rows:
        print(table, file=sys.stderr)

    # The input prompt goes to stdout. We don't want that because a user may be piping the output
    # to jq as in the following example.
    # $ torc -F json jobs list | jq .
    # Redirect the input prompt to stderr so that jq can parse only the output.
    orig_stdout = sys.stdout
    try:
        sys.stdout = sys.stderr
        doc = None
        while not doc:
            choice = input("Select an index: >>> ").strip()
            try:
                selected_index = int(choice)
                doc = index_to_doc.get(selected_index)
            except ValueError:
                logger.error("Could not convert {} to an integer.", choice)
            if not doc:
                print(f"index={choice} is an invalid choice", file=sys.stderr)
    finally:
        sys.stdout = orig_stdout

    return doc


def prompt_user_for_workflow(
    ctx: click.Context, api: DefaultApi, auto_select_one_option: bool = False
) -> WorkflowModel:
    """Prompt the user to select a workflow key from table of workflows."""
    msg = (
        "\nThis command requires a workflow key and one was not provided. "
        "Please choose one from below.\n"
    )
    workflow = prompt_user_for_document(
        "workflow",
        api.list_workflows,
        exclude_columns=("_id", "_rev"),
        msg=msg,
        auto_select_one_option=auto_select_one_option,
        user=get_user_from_context(ctx),
        is_archived=False,
    )
    if workflow is None:
        logger.error("No workflows are stored")
        sys.exit(1)

    return workflow


def make_text_table(
    iterable: Iterable[Any], title: str, columns: Iterable[str], start_index: int = 1
):
    """Return a PrettyTable from an iterable.

    Parameters
    ----------
    iterable : sequence
        Sequence of dicts
    title : str
    columns : None | list
        Keys of each dict in iterable to include.
    start_index : int

    Returns
    -------
    PrettyTable
    """
    table = PrettyTable(title=title)
    for i, item in enumerate(iterable, start=start_index):
        val = {x: item.get(x) for x in columns}
        if i == start_index:
            field_names = list(columns)
            field_names.insert(0, "index")
            table.field_names = field_names
        row = list(val.values())
        row.insert(0, i)
        table.add_row(row)
    return table


def path_callback(*args: str) -> Path:
    """click callback to convert a string to a Path."""
    return Path(args[2])


def parse_filters(filters: Iterable[str]) -> dict[str, Any]:
    """Parse filter options given on the command line."""
    final: dict[str, Any] = {}
    for flt in filters:
        fields = flt.split("=")
        if len(fields) != 2:
            msg = "Invalid filter format: {flt}. Required: name=value"
            logger.error(msg)
            raise Exception(msg)
        val = fields[1]
        val_as_int = _try_parse_int(val)
        _val = val if val_as_int is None else val_as_int
        final[fields[0]] = _val

    return final


def _try_parse_int(val: str) -> int | None:
    return int(val) if val.isnumeric() else None


def setup_cli_logging(
    ctx: click.Context, name: str, filename: Optional[Path] = None, mode: str = "w"
):
    """Setup logging from a click context."""
    params = ctx.find_root().params
    setup_logging(
        filename=filename,
        console_level=params["console_level"],
        file_level=params["file_level"],
        mode=mode,
    )
