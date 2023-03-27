"""CLI commands to manage results"""

import logging

import click

from torc.api import iter_documents
from .common import setup_cli_logging, make_text_table, parse_filters


logger = logging.getLogger(__name__)


@click.group()
@click.option("-k", "--workflow-key", type=str, required=True, help="Workflow key")
def results(workflow_key):  # pylint: disable=unused-argument
    """result commands"""


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
def list_results(ctx, api, filters):
    """List all results in a workflow.

    \b
    Examples:
    1. List all results.
       $ torc results 91388876 list results
    2. List only results with name=result1
       $ torc results 91388876 list results -f return_code=1
    """
    setup_cli_logging(ctx, 2, __name__)
    workflow_key = ctx.parent.params["workflow_key"]
    exclude = ("id", "rev")
    filters = parse_filters(filters)
    table = make_text_table(
        (x.to_dict() for x in iter_documents(api.get_results_workflow, workflow_key, **filters)),
        "results",
        exclude_columns=exclude,
    )
    if table.rows:
        print(table)
    else:
        print("No results are stored")


results.add_command(list_results)
