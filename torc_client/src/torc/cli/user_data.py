"""CLI commands to manage user_data"""

import json

import rich_click as click
import json5
from loguru import logger

from torc.openapi_client.models.user_data_model import (
    UserDataModel,
)
from torc.openapi_client.models.edge_model import EdgeModel
from torc.api import iter_documents
from .common import (
    check_database_url,
    confirm_change,
    get_output_format_from_context,
    get_workflow_key_from_context,
    parse_filters,
    setup_cli_logging,
)


@click.group()
def user_data():
    """User data commands"""


@click.command()
@click.option("-d", "--data", type=str, help="Object encoded in a JSON5 string.")
@click.option(
    "--ephemeral/--not-ephemeral",
    is_flag=True,
    default=False,
    show_default=True,
    help="Whether the data is ephemeral and should be cleared on every run of the workflow.",
)
@click.option(
    "-n",
    "--name",
    type=str,
    help="User data name",
)
@click.option(
    "-s",
    "--stores",
    type=str,
    help="Key of job that will store the data.",
)
@click.option(
    "-c",
    "--consumes",
    type=str,
    multiple=True,
    help="Key of job or jobs that will consume the data. Accepts multiple.",
)
@click.pass_obj
@click.pass_context
def add(ctx, api, data, ephemeral, name, stores, consumes):
    """Add user data to the workflow. Could be a placeholder or could contain data.

    \b
    Example:
    1. Add a placeholder for data that will be stored by one job and consumed by another.
       $ torc user-data add -n output_data_1 -s 96117190 -c 96117191 -c 96117192
    2. Add a placeholder for data that will be stored by one job and consumed by another.
       $ torc user-data add -n output_data_1 -d "{key1: 'val1', key2: 'val2'}"
    """
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    if data is None:
        ud = UserDataModel(name=name, is_ephemeral=ephemeral)
    else:
        obj = json5.loads(data)
        ud = UserDataModel(name=name, is_ephemeral=ephemeral, data=obj)

    ud = api.add_user_data(workflow_key, ud)
    stores_edge = None
    consumes_edges = []
    if stores is not None:
        stored_by_job = api.get_job(workflow_key, stores)
        assert ud.id is not None
        stores_edge = api.add_edge(
            workflow_key,
            "stores",
            EdgeModel(
                _from=stored_by_job.id,
                _to=ud.id,
            ),
        )
    if consumes:
        for job_key in consumes:
            consumed_by_job = api.get_job(workflow_key, job_key)
            assert ud.id is not None
            consumes_edge = api.add_edge(
                workflow_key,
                "consumes",
                EdgeModel(
                    _from=consumed_by_job.id,
                    _to=ud.id,
                ),
            )
            consumes_edges.append(consumes_edge.to_dict())
    if output_format == "text":
        logger.info("Added user_data key={}", ud.key)
    else:
        data = {"key": ud.key}
        if stores_edge is not None:
            data["stores_edge"] = stores_edge.to_dict()
            data["consumes_edges"] = consumes_edges
        print(json.dumps(data))


@click.command()
@click.argument("user_data_key")
@click.option(
    "-n",
    "--name",
    type=str,
    help="User data name",
)
@click.option(
    "-d",
    "--data",
    type=str,
    help="Object encoded in a JSON5 string",
)
@click.option(
    "--ephemeral/--not-ephemeral",
    is_flag=True,
    default=None,
    help="Whether the data is ephemeral and should be cleared on every run of the workflow.",
)
@click.pass_obj
@click.pass_context
def modify(ctx, api, user_data_key, name, data, ephemeral):
    """Modify user data."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    ud = api.get_user_data(workflow_key, user_data_key)
    changed = False
    if name is not None:
        ud.name = name
        changed = True
    if ephemeral is not None:
        ud.is_ephemeral = ephemeral
        changed = True
    if data is not None:
        ud.data = json5.loads(data)
        changed = True

    if changed:
        ud = api.modify_user_data(workflow_key, user_data_key, ud)
        if output_format == "text":
            logger.info("Modified user_data key = {}", user_data_key)
        else:
            print(json.dumps({"key": user_data_key}))
    else:
        logger.info("No changes requested")


@click.command()
@click.argument("user_data_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def delete(ctx, api, user_data_keys):
    """Delete one or more user_data objects by key."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    if not user_data_keys:
        logger.warning("No user data keys were passed")
        return

    msg = f"This command will delete {len(user_data_keys)} user data objects."
    confirm_change(ctx, msg)
    workflow_key = get_workflow_key_from_context(ctx, api)
    for key in user_data_keys:
        api.remove_user_data(workflow_key, key)
        logger.info("Deleted user_data={}", key)


@click.command()
@click.pass_obj
@click.pass_context
def delete_all(ctx, api):
    """Delete all user_data objects in the workflow."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    keys = [x["_key"] for x in iter_documents(api.list_user_data, workflow_key)]
    msg = f"This command will delete {len(keys)} user data objects."
    confirm_change(ctx, msg)
    for key in keys:
        api.remove_user_data(workflow_key, key)
        logger.info("Deleted user_data {}", key)


@click.command()
@click.argument("key")
@click.pass_obj
@click.pass_context
def get(ctx, api, key):
    """Get one user_data object by key."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    item = api.get_user_data(workflow_key, key).to_dict()
    item.pop("_id")
    print(json.dumps(item, indent=2))


@click.command(name="list")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    type=str,
    help="Filter the values according to each key=value pair.",
)
@click.option("-l", "--limit", type=int, help="Limit the output to this number of items.")
@click.option("-s", "--skip", default=0, type=int, help="Skip this number of items.")
@click.pass_obj
@click.pass_context
def list_user_data(ctx, api, filters, limit, skip):
    """List all user data in a workflow."""
    # TODO: add filtering by key or any contents
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    filters = parse_filters(filters)
    filters["skip"] = skip
    if limit is not None:
        filters["limit"] = limit
    data = []
    for item in iter_documents(api.list_user_data, workflow_key, **filters):
        item = item.to_dict()
        item.pop("_id")
        data.append(item)
    print(json.dumps(data, indent=2))


user_data.add_command(add)
user_data.add_command(modify)
user_data.add_command(delete)
user_data.add_command(delete_all)
user_data.add_command(get)
user_data.add_command(list_user_data)
