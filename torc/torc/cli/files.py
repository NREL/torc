"""CLI commands to manage files"""

import logging

import click
from swagger_client.models.files_workflow_model import FilesWorkflowModel

from torc.api import iter_documents
from .common import (
    get_workflow_key_from_context,
    setup_cli_logging,
    make_text_table,
    parse_filters,
)


logger = logging.getLogger(__name__)


@click.group()
def files():  # pylint: disable=unused-argument
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
    workflow_key = get_workflow_key_from_context(ctx, api)
    file = FilesWorkflowModel(
        name=name,
        path=path,
    )
    file = api.post_files_workflow(file, workflow_key)
    logger.info("Added file with key=%s", file.key)


@click.command()
@click.argument("file_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def delete(ctx, api, file_keys):
    """Delete one or more files by key."""
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    for key in file_keys:
        api.delete_files_workflow_key(workflow_key, key)
        logger.info("Deleted workflow=%s file=%s", workflow_key, key)


@click.command()
@click.pass_obj
@click.pass_context
def delete_all(ctx, api):
    """Delete all files in the workflow."""
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    for file in iter_documents(api.get_files_workflow, workflow_key):
        api.delete_files_workflow_key(workflow_key, file.key)
        logger.info("Deleted file %s", file.key)


@click.command(name="list")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    type=str,
    help="Filter the values according to each key=value pair.",
)
@click.pass_obj
@click.pass_context
def list_files(ctx, api, filters):
    """List all files in a workflow.

    \b
    Examples:
    1. List all files.
       $ torc files 91388876 list files
    2. List only files with name=file1
       $ torc files 91388876 list files -f name=file1
    """
    setup_cli_logging(ctx, __name__)
    workflow_key = get_workflow_key_from_context(ctx, api)
    exclude = ("id", "rev", "file_hash")
    filters = parse_filters(filters)
    table = make_text_table(
        (x.to_dict() for x in iter_documents(api.get_files_workflow, workflow_key, **filters)),
        "files",
        exclude_columns=exclude,
    )
    if table.rows:
        print(table)
    else:
        print("No files are stored")


files.add_command(add)
# files.add_command(cancel)
files.add_command(delete)
files.add_command(delete_all)
files.add_command(list_files)
