"""CLI commands to manage results"""

import logging

import click

from torc.openapi_client.models.workflow_results_model import WorkflowResultsModel
from torc.api import iter_documents, map_job_keys_to_names, list_model_fields
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
@click.option(
    "-x",
    "--exclude-job-names",
    is_flag=True,
    default=False,
    show_default=True,
    help="Exclude job names from the output. Set this flag if you need "
    "to deserialize the objects into Result classes or to speed up the query.",
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
def list_results(ctx, api, filters, limit, skip, exclude_job_names, sort_by, reverse_sort):
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
    filters = parse_filters(filters)
    if "job_name" in filters:
        logger.warning("Cannot filter on job_name")
        filters.pop("job_name")
    filters["skip"] = skip
    if limit is not None:
        filters["limit"] = limit
    if sort_by is not None:
        filters["sort_by"] = sort_by
        filters["reverse_sort"] = reverse_sort
    table_title = f"Results in workflow {workflow_key}"
    mapping = None if exclude_job_names else map_job_keys_to_names(api, workflow_key)
    items = []
    for item in iter_documents(api.get_workflows_workflow_results, workflow_key, **filters):
        row = {}
        if not exclude_job_names:
            row["job_name"] = mapping[item.job_key]
        row.update(item.to_dict())
        items.append(row)

    columns = list_model_fields(WorkflowResultsModel)
    columns.remove("_id")
    columns.remove("_rev")
    print_items(
        ctx,
        items,
        table_title,
        columns,
        "results",
        start_index=skip,
    )


results.add_command(list_results)
