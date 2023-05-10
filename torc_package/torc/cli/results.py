"""CLI commands to manage results"""

import logging

import click

from torc.api import iter_documents
from .common import (
    check_database_url,
    get_workflow_key_from_context,
    setup_cli_logging,
    parse_filters,
    print_items,
)


logger = logging.getLogger(__name__)


@click.group()
def results():
    """Result commands"""


@click.command(name="list")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    type=str,
    help="Filter the values according to each key=value pair.",
)
@click.option("-l", "--limit", type=int, help="Limit the output to this number of jobs.")
@click.option("-s", "--skip", default=0, type=int, help="Skip this number of jobs.")
@click.pass_obj
@click.pass_context
def list_results(ctx, api, filters, limit, skip):
    """List all results in a workflow.

    \b
    Examples:
    1. List all results in a table.
       $ torc results list
    2. List only results with name=result1
       $ torc results list -f return_code=1
    3. List all results in JSON format.
       $ torc -F json results 91388876 list results
    """
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    exclude = ("id", "rev")
    filters = parse_filters(filters)
    filters["skip"] = skip
    if limit is not None:
        filters["limit"] = limit
    table_title = f"Results in workflow {workflow_key}"
    items = (
        x.to_dict()
        for x in iter_documents(api.get_workflows_workflow_results, workflow_key, **filters)
    )
    print_items(
        ctx,
        items,
        table_title=table_title,
        json_key="results",
        exclude_columns=exclude,
        start_index=skip,
    )


results.add_command(list_results)
