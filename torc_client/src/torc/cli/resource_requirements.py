"""CLI commands to manage job resource requirements"""

import json

import rich_click as click
from loguru import logger

from torc.openapi_client.models.resource_requirements_model import (
    ResourceRequirementsModel,
)

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
def resource_requirements():
    """Job resource requirements commands"""


@click.command()
@click.option(
    "-n",
    "--name",
    type=str,
    help="Resource requirements name",
)
@click.option(
    "-c",
    "--num-cpus",
    default=1,
    type=int,
    show_default=True,
    help="Number of CPUs required by a job",
)
@click.option(
    "-m",
    "--memory",
    default="1m",
    show_default=True,
    type=str,
    help="Amount of memory required by a job, such as '20g'",
)
@click.option(
    "-r",
    "--runtime",
    default="P0DT1M",
    show_default=True,
    type=str,
    help="ISO 8601 encoding for job runtime",
)
@click.option(
    "-N",
    "--num-nodes",
    default=1,
    type=int,
    show_default=True,
    help="Number of compute nodes required by a job",
)
@click.option(
    "-a",
    "--apply-to-all-jobs",
    default=False,
    is_flag=True,
    show_default=True,
    help="Apply these requirements to all jobs in the workflow.",
)
@click.pass_obj
@click.pass_context
def add(ctx, api, name, num_cpus, memory, runtime, num_nodes, apply_to_all_jobs):
    """Add a resource requirements definition to the workflow."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    rr = ResourceRequirementsModel(
        name=name,
        num_cpus=num_cpus,
        memory=memory,
        runtime=runtime,
        num_nodes=num_nodes,
    )
    rr = api.add_resource_requirements(workflow_key, rr)
    edges = []
    if apply_to_all_jobs:
        for job in iter_documents(api.list_jobs, workflow_key):
            edge = api.modify_job_resource_requirements(workflow_key, job.key, rr.key)
            edges.append(edge.to_dict())

    if output_format == "text":
        logger.info("Added resource requirements with key={}", rr.key)
        for edge in edges:
            logger.info("Stored job requirements via edge {}", edge)
    else:
        print(json.dumps({"key": rr.key, "edges": edges}))


@click.command()
@click.argument("resource_requirements_key")
@click.option(
    "-n",
    "--name",
    type=str,
    help="Resource requirements name",
)
@click.option(
    "-c",
    "--num-cpus",
    type=int,
    help="Number of CPUs required by a job",
)
@click.option(
    "-m",
    "--memory",
    type=str,
    help="Amount of memory required by a job, such as '20g'",
)
@click.option(
    "-r",
    "--runtime",
    type=str,
    help="ISO 8601 encoding for job runtime",
)
@click.option(
    "-N",
    "--num-nodes",
    type=int,
    help="Number of compute nodes required by a job",
)
@click.pass_obj
@click.pass_context
def modify(ctx, api, resource_requirements_key, **kwargs):
    """Modify a resource requirements definition."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    output_format = get_output_format_from_context(ctx)
    rr = api.get_resource_requirements(workflow_key, resource_requirements_key)
    changed = False
    for param in ("name", "num_cpus", "memory", "runtime", "num_nodes"):
        val = kwargs[param]
        if val is not None:
            setattr(rr, param, val)
            changed = True

    if changed:
        rr = api.modify_resource_requirements(workflow_key, resource_requirements_key, rr)
        if output_format == "text":
            logger.info(
                "Modified resource requirements key = {}",
                resource_requirements_key,
            )
        else:
            print(json.dumps({"key": resource_requirements_key}))
    else:
        logger.info("No changes requested")


@click.command()
@click.argument("resource_requirement_keys", nargs=-1)
@click.pass_obj
@click.pass_context
def delete(ctx, api, resource_requirement_keys):
    """Delete one or more resource requirements by key."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    if not resource_requirement_keys:
        logger.warning("No resource requirement keys were passed")
    workflow_key = get_workflow_key_from_context(ctx, api)
    for key in resource_requirement_keys:
        api.remove_resource_requirements(workflow_key, key)
        logger.info("Deleted workflow={} resource_requirements={}", workflow_key, key)


@click.command()
@click.pass_obj
@click.pass_context
def delete_all(ctx, api):
    """Delete all resource_requirements in the workflow."""
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    for resource_requirement in iter_documents(api.list_resource_requirements, workflow_key):
        api.remove_resource_requirements(workflow_key, resource_requirement.key)
        logger.info("Deleted resource_requirement {}", resource_requirement.key)


@click.command(name="list")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    type=str,
    help="Filter the values according to each key=value pair.",
)
@click.option(
    "-l",
    "--limit",
    type=int,
    help="Limit the output to this number of resource_requirements.",
)
@click.option(
    "-s",
    "--skip",
    default=0,
    type=int,
    help="Skip this number of resource_requirements.",
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
def list_resource_requirements(ctx, api, filters, limit, skip, sort_by, reverse_sort):
    """List all resource_requirements in a workflow.

    \b
    Examples:
    1. List all resource_requirements in a table.
       $ torc resource_requirements list resource_requirements
    2. List only resource_requirements with num_cpus=4.
       $ torc resource_requirements list resource_requirements -f num_cpus=4
    3. List all resource_requirements in JSON format.
       $ torc -F json resource_requirements list
    """
    setup_cli_logging(ctx, __name__)
    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    filters = parse_filters(filters)
    filters["skip"] = skip
    if limit is not None:
        filters["limit"] = limit
    if sort_by is not None:
        filters["sort_by"] = sort_by
        filters["reverse_sort"] = reverse_sort
    items = (
        x.to_dict()
        for x in iter_documents(api.list_resource_requirements, workflow_key, **filters)
    )

    columns = list_model_fields(ResourceRequirementsModel)
    columns.remove("_id")
    columns.remove("_rev")
    table_title = f"Resource requirements in workflow {workflow_key}"
    print_items(
        ctx,
        items,
        table_title,
        columns,
        "resource_requirements",
        start_index=skip + 1,
    )


resource_requirements.add_command(add)
resource_requirements.add_command(modify)
resource_requirements.add_command(delete)
resource_requirements.add_command(delete_all)
resource_requirements.add_command(list_resource_requirements)
