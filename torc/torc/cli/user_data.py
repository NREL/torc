"""CLI commands to manage user_data"""

import json
import logging

import click
import json5

from torc.api import iter_documents
from .common import (
    check_database_url,
    get_output_format_from_context,
    get_workflow_key_from_context,
    setup_cli_logging,
)


logger = logging.getLogger(__name__)


@click.group()
def user_data():  # pylint: disable=unused-argument
    """User data commands"""


@click.command()
@click.argument("data", nargs=-1)
@click.pass_obj
@click.pass_context
def add(ctx, api, data):
    """Add user data to the workflow. Each item must be a single JSON object encoded in a JSON5
    string.

    \b
    Example:
    $ torc user-data add "{key1: 'val1', key2: 'val2'}" "{key3: 'val3'}"
    """
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    keys = []
    for item in data:
        data = json5.loads(item)
        ud = api.post_workflows_workflow_user_data(data, workflow_key)
        if output_format == "text":
            logger.info("Added user_data key=%s", ud["_key"])
        keys.append(ud["_key"])

    if output_format == "json":
        print(json.dumps({"keys": keys}))


@click.command()
@click.argument("user_data_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def delete(ctx, api, user_data_keys):
    """Delete one or more user_data objects by key."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    for key in user_data_keys:
        api.delete_workflows_workflow_user_data_key(workflow_key, key)
        logger.info("Deleted user_data=%s", key)


@click.command()
@click.pass_obj
@click.pass_context
def delete_all(ctx, api):
    """Delete all user_data objects in the workflow."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    for data in iter_documents(api.get_workflows_workflow_user_data, workflow_key):
        api.delete_workflows_workflow_user_data_key(workflow_key, data["_key"])
        logger.info("Deleted user_data %s", data["_key"])


@click.command()
@click.argument("key")
@click.pass_obj
@click.pass_context
def get(ctx, api, key):
    """Get one user_data object by key."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    item = api.get_workflows_workflow_user_data_key(workflow_key, key)
    item.pop("_id")
    print(json.dumps(item, indent=2))


@click.command(name="list")
@click.pass_obj
@click.pass_context
def list_user_data(ctx, api):
    """List all user data in a workflow."""
    # TODO: add filtering by key or any contents
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    data = []
    for item in iter_documents(api.get_workflows_workflow_user_data, workflow_key):
        item.pop("_id")
        data.append(item)
    print(json.dumps(data, indent=2))


user_data.add_command(add)
user_data.add_command(delete)
user_data.add_command(delete_all)
user_data.add_command(get)
user_data.add_command(list_user_data)
