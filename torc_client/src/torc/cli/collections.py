"""CLI commands to manage jobs"""

import json
from pprint import pprint
from typing import Any

import rich_click as click
from loguru import logger

from torc.api import iter_documents
from .common import (
    check_database_url,
    get_output_format_from_context,
    get_workflow_key_from_context,
    setup_cli_logging,
    print_items,
    parse_filters,
)


@click.group()
def collections():
    """Collections commands"""


@click.command()
@click.argument("collection")
@click.argument("edge")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    type=str,
    help="Filter the values according to each key=value pair on the primary collection.",
)
@click.option(
    "--outbound/--inbound",
    is_flag=True,
    default=True,
    show_default=True,
    help="Inbound or outbound edge.",
)
@click.option("-l", "--limit", type=int, help="Limit the output to this number of jobs.")
@click.option("-s", "--skip", default=0, type=int, help="Skip this number of jobs.")
@click.option(
    "-x",
    "--exclude-from",
    multiple=True,
    type=str,
    help="Exclude this base column name on the from side. Accepts multiple",
    callback=lambda *x: set(x[2]),
)
@click.option(
    "-y",
    "--exclude-to",
    multiple=True,
    type=str,
    help="Exclude this base column name on the to side. Accepts multiple",
    callback=lambda *x: set(x[2]),
)
@click.pass_obj
@click.pass_context
def join_by_edge(
    ctx, api, collection, edge, filters, outbound, limit, skip, exclude_from, exclude_to
):
    """Join a collection with one or more other collections connected by an edge.

    \b
    Examples:
    1. Show jobs and results in a table.
       $ torc collections join-by-edge jobs returned
    2. Show jobs and results in JSON format.
       $ torc -F json collections join-by-edge jobs returned
    """
    _join_by_edge(
        ctx, api, collection, edge, filters, outbound, limit, skip, exclude_from, exclude_to
    )


def _join_by_edge(
    ctx, api, collection, edge, filters, outbound, limit, skip, exclude_from, exclude_to
):
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    filters = parse_filters(filters)
    kwargs = {"skip": skip}
    if limit is not None:
        kwargs["limit"] = limit
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    func = (
        api.join_collections_by_outbound_edge if outbound else api.join_collections_by_inbound_edge
    )
    iterable = iter_documents(func, workflow_key, collection, edge, filters, **kwargs)
    base_exclude = ["_id", "_rev", "_oldRev"]
    items = []
    if output_format == "text":
        # Flatten the columns to make a table.
        for item in iterable:
            row = {f"from_{k}": v for k, v in item["from"].items() if k not in exclude_from}
            row.update({f"to_{k}": v for k, v in item["to"].items() if k not in exclude_to})
            items.append(row)
        exclude = {f"{x}_{y}" for x in ("from", "to") for y in base_exclude}
    else:
        for item in iterable:
            for exc in exclude_from.union(base_exclude):
                item["from"].pop(exc, None)
            for exc in exclude_to.union(base_exclude):
                item["to"].pop(exc, None)
            items.append(item)
        exclude = set()

    direction = "outbound" if outbound else "inbound"
    table_title = f"{collection} with {edge=} {direction=} in workflow {workflow_key}"
    columns = [x for x in items[0].keys() if x not in exclude] if items else []
    print_items(
        ctx,
        items,
        table_title,
        columns,
        "items",
        start_index=skip + 1,
    )


JOIN_COLLECTIONS: dict[str, dict[str, Any]] = {
    "compute-node-executed-jobs": {
        "collection": "compute_nodes",
        "edge": "executed",
        "outbound": True,
        "exclude_from": [],
        "exclude_to": [
            "command",
            "invocation_script",
            "internal",
            "cancel_on_blocking_job_failure",
            "status",
            "supports_termination",
        ],
    },
    "compute-node-utilization": {
        "collection": "compute_nodes",
        "edge": "node_used",
        "outbound": True,
        "exclude_from": [],
        "exclude_to": [],
    },
    "job-blocks": {
        "collection": "jobs",
        "edge": "blocks",
        "outbound": True,
        "exclude_from": [
            "command",
            "invocation_script",
            "internal",
            "cancel_on_blocking_job_failure",
            "status",
            "supports_termination",
        ],
        "exclude_to": [
            "command",
            "invocation_script",
            "internal",
            "cancel_on_blocking_job_failure",
            "status",
            "supports_termination",
        ],
    },
    "job-needs-file": {
        "collection": "jobs",
        "edge": "needs",
        "outbound": True,
        "exclude_from": [
            "command",
            "invocation_script",
            "internal",
            "cancel_on_blocking_job_failure",
            "status",
            "supports_termination",
        ],
        "exclude_to": [],
    },
    "job-produces-file": {
        "collection": "jobs",
        "edge": "produces",
        "outbound": True,
        "exclude_from": [
            "command",
            "invocation_script",
            "internal",
            "cancel_on_blocking_job_failure",
            "status",
            "supports_termination",
        ],
        "exclude_to": [],
    },
    "job-requirements": {
        "collection": "resource_requirements",
        "edge": "requires",
        "outbound": False,
        "exclude_from": [
            "invocation_script",
            "internal",
            "cancel_on_blocking_job_failure",
            "status",
            "supports_termination",
        ],
        "exclude_to": [],
    },
    "job-results": {
        "collection": "results",
        "edge": "returned",
        "outbound": False,
        "exclude_from": [
            "command",
            "invocation_script",
            "internal",
            "cancel_on_blocking_job_failure",
            "status",
            "supports_termination",
        ],
        "exclude_to": ["job_key", "job_name"],
    },
    "job-schedulers": {
        "collection": "jobs",
        "edge": "scheduled_bys",
        "outbound": True,
        "exclude_from": [
            "command",
            "invocation_script",
            "internal",
            "cancel_on_blocking_job_failure",
            "status",
            "supports_termination",
        ],
        "exclude_to": [],
    },
    "job-process-utilization": {
        "collection": "job_process_stats",
        "edge": "process_used",
        "outbound": False,
        "exclude_from": [
            "command",
            "invocation_script",
            "internal",
            "cancel_on_blocking_job_failure",
            "status",
            "supports_termination",
        ],
        "exclude_to": ["job_key"],
    },
    "job-consumes-data": {
        "collection": "jobs",
        "edge": "consumes",
        "outbound": True,
        "exclude_from": [
            "command",
            "invocation_script",
            "internal",
            "cancel_on_blocking_job_failure",
            "status",
            "supports_termination",
        ],
        "exclude_to": [],
    },
    "job-stores-data": {
        "collection": "jobs",
        "edge": "stores",
        "outbound": True,
        "exclude_from": [
            "command",
            "invocation_script",
            "internal",
            "cancel_on_blocking_job_failure",
            "status",
            "supports_termination",
        ],
        "exclude_to": [],
    },
}


@click.command()
@click.argument("name", type=click.Choice(list(JOIN_COLLECTIONS.keys())))
@click.option(
    "-f",
    "--filters",
    multiple=True,
    type=str,
    help="Filter the values according to each key=value pair on the primary collection.",
)
@click.option("-l", "--limit", type=int, help="Limit the output to this number of jobs.")
@click.option("-s", "--skip", default=0, type=int, help="Skip this number of jobs.")
@click.pass_obj
@click.pass_context
def join(ctx, api, name, filters, limit, skip):
    """Perform a join of collections from a pre-defined configuration.
    Refer to show-join-configurations command for details.

    \b
    Examples:
    1. Show jobs and results in a table.
       $ torc collections join job-results
    2. Show jobs and results in JSON format.
       $ torc -F json collections join job-results
    3. Show results for one job. This uses the job key.
       $ torc -F json collections join job-results -f return_code=0
    """
    # TODO: consider doing this on the server side so that other apps can leverage the logic.
    join_def = JOIN_COLLECTIONS[name]
    return _join_by_edge(
        ctx=ctx,
        api=api,
        collection=join_def["collection"],
        edge=join_def["edge"],
        filters=filters,
        outbound=join_def["outbound"],
        limit=limit,
        skip=skip,
        exclude_from=set(join_def["exclude_from"]),
        exclude_to=set(join_def["exclude_to"]),
    )


@click.command()
def show_join_configurations():
    """Show the pre-defined configurations for use in the join command."""
    pprint(JOIN_COLLECTIONS)


@click.command(name="list")
@click.option("-r", "--raw", is_flag=True, default=False, show_default=True, help="List raw names")
@click.pass_obj
@click.pass_context
def list_collections(ctx, api, raw):
    """List workflow collections."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    output_format = get_output_format_from_context(ctx)
    workflow_key = get_workflow_key_from_context(ctx, api)
    results = api.list_collection_names(workflow_key)
    if not raw:
        for i, name in enumerate(results.names):
            results.names[i] = name.split("__")[0]
    if output_format == "text":
        logger.info("Workflow collection names = \n{}", "\n".join(results.names))
    else:
        print(json.dumps(results.to_dict()))


collections.add_command(join)
collections.add_command(show_join_configurations)
collections.add_command(join_by_edge)
collections.add_command(list_collections)
