"""CLI commands to manage files"""

import json

import rich_click as click
from loguru import logger

from torc.openapi_client.models.file_model import FileModel
from torc.api import iter_documents, list_model_fields
from .common import (
    check_database_url,
    get_output_format_from_context,
    get_workflow_key_from_context,
    setup_cli_logging,
    parse_filters,
    print_items,
)


@click.group()
def files():
    """File commands"""


@click.command()
@click.option(
    "-n",
    "--name",
    type=str,
    help="file name",
)
@click.option(
    "-p",
    "--path",
    type=str,
    required=True,
    help="Path of file",
)
@click.pass_obj
@click.pass_context
def add(ctx, api, name, path):
    """Add a file to the workflow."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    file = FileModel(
        name=name,
        path=path,
    )
    file = api.add_file(workflow_key, file)
    if output_format == "text":
        logger.info("Added file with key={}", file.key)
    else:
        print(json.dumps({"key": file.key}))


@click.command()
@click.argument("file_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def delete(ctx, api, file_keys):
    """Delete one or more files by key."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    if not file_keys:
        logger.warning("No file keys were passed")
    workflow_key = get_workflow_key_from_context(ctx, api)
    for key in file_keys:
        api.remove_file(workflow_key, key)
        logger.info("Deleted workflow={} file={}", workflow_key, key)


@click.command()
@click.pass_obj
@click.pass_context
def delete_all(ctx, api):
    """Delete all files in the workflow."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    for file in iter_documents(api.list_files, workflow_key):
        api.remove_file(workflow_key, file.key)
        logger.info("Deleted file {}", file.key)


@click.command(name="list")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    type=str,
    help="Filter the values according to each key=value pair.",
)
@click.option(
    "--sort-by",
    type=str,
    help="Sort results by this column.",
)
@click.option(
    "--reverse-sort",
    is_flag=True,
    default=False,
    show_default=True,
    help="Reverse the sort order if --sort-by is set.",
)
@click.pass_obj
@click.pass_context
def list_files(ctx, api, filters, sort_by, reverse_sort):
    """List all files in a workflow.

    \b
    Examples:
    1. List all files in a table.
       $ torc files list
    2. List only files with name=file1
       $ torc files list -f name=file1
    3. List all files in JSON format.
       $ torc -F json files list
    """
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    filters = parse_filters(filters)
    if sort_by is not None:
        filters["sort_by"] = sort_by
        filters["reverse_sort"] = reverse_sort
    table_title = f"Files in workflow {workflow_key}"
    items = (x.to_dict() for x in iter_documents(api.list_files, workflow_key, **filters))
    columns = list_model_fields(FileModel)
    columns.remove("_id")
    columns.remove("_rev")
    print_items(ctx, items, table_title, columns, "files")


files.add_command(add)
files.add_command(delete)
files.add_command(delete_all)
files.add_command(list_files)
