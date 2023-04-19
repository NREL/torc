"""CLI commands for exporting workflows from the database"""

import json
import logging
from pathlib import Path
from pydoc import locate

import click
from swagger_client import DefaultApi

from torc.api import iter_documents
from torc.utils.sql import make_table, insert_rows
from .common import check_database_url, setup_cli_logging, check_output_path


logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def export(ctx):
    """Export commands"""
    setup_cli_logging(ctx, __name__)


@click.command()
@click.argument("workflow_keys", nargs=-1)
@click.option(
    "-F",
    "--filename",
    default="workflow.sqlite",
    show_default=True,
    callback=lambda *x: Path(x[2]),
    help="SQLite filename",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    show_default=True,
    help="Overwrite file if it exists.",
)
@click.pass_obj
def sqlite(api, workflow_keys, filename, force):
    """Export workflow database to this SQLite file."""
    check_database_url(api)
    check_output_path(filename, force)
    workflows = []
    workflow_configs = []
    workflow_statuses = []
    tables = set()
    if workflow_keys:
        selected_workflows = (api.get_workflows_key(x) for x in workflow_keys)
    else:
        selected_workflows = iter_documents(api.get_workflows)
    for workflow in selected_workflows:
        config = api.get_workflows_config_key(workflow.key)
        config_as_dict = config.to_dict()
        config_as_dict["compute_node_resource_stats"] = json.dumps(
            config_as_dict["compute_node_resource_stats"]
        )
        status = api.get_workflows_status_key(workflow.key)
        status_as_dict = status.to_dict()
        status_as_dict["auto_tune_status"] = json.dumps(status_as_dict["auto_tune_status"])
        if not workflows:
            _make_sql_table(workflow, workflow.to_dict(), filename, "workflows")
            _make_sql_table(config, config_as_dict, filename, "workflow_configs")
            _make_sql_table(status, status_as_dict, filename, "workflow_statuses")
        workflows.append(tuple(workflow.to_dict().values()))
        workflow_configs.append(tuple(config_as_dict.values()))
        workflow_statuses.append(tuple(status_as_dict.values()))

        for name in api.get_workflows_key_collection_names(workflow.key).names:
            basename = name.split("__")[0]
            func = _get_db_documents_func(api, basename)

            rows = []
            args = (workflow.key, basename) if basename in _EDGES else (workflow.key,)
            for item in iter_documents(func, *args):
                row = item if isinstance(item, dict) else item.to_dict()
                if "to" in row:
                    # Swagger converts Arango's '_to' to 'to', but leaves '_from'.
                    # Persist Arango names.
                    row["_to"] = row.pop("to")
                if basename in ("events", "user_data"):
                    # Put variable, user-defined names in a 'data' column as JSON.
                    data = {}
                    db_keys = {"_id", "_rev", "_key"}
                    for field in set(row.keys()).difference(db_keys):
                        data[field] = row.pop(field)
                    row["data"] = json.dumps(data)
                elif basename == "jobs":
                    row.pop("internal")
                row["workflow_key"] = workflow.key
                for key, val in row.items():
                    if isinstance(val, (dict, list)):
                        row[key] = json.dumps(val)
                if basename not in tables:
                    _make_sql_table(item, row, filename, basename)
                    tables.add(basename)

                rows.append(tuple(row.values()))
            if rows:
                insert_rows(filename, basename, rows)

    if workflows:
        insert_rows(filename, "workflows", workflows)
        insert_rows(filename, "workflow_configs", workflow_configs)
        insert_rows(filename, "workflow_statuses", workflow_statuses)

    if workflow_keys:
        keys = " ".join(workflow_keys)
        logger.info("Exported database to %s for workflow keys %s", filename, keys)
    else:
        logger.info("Exported database to %s for all workflows", filename)


def _make_sql_table(item, row, filename, basename):
    if isinstance(item, dict):
        types = None
    else:
        types = {}
        for key, val in type(item).swagger_types.items():
            if val == "object":
                types[key] = str
            else:
                types[key] = locate(val) or str
        types["workflow_key"] = str
        if "to" in types:
            types["_to"] = types.pop("to")
    make_table(filename, basename, row, primary_key="key", types=types)


_DB_ACCESSOR_FUNCS = {
    "blocks": "get_workflows_workflow_edges_name",
    "consumes": "get_workflows_workflow_edges_name",
    "executed": "get_workflows_workflow_edges_name",
    "compute_node_stats": "get_workflows_workflow_compute_node_stats",
    "compute_nodes": "get_workflows_workflow_compute_nodes",
    "events": "get_workflows_workflow_events",
    "files": "get_workflows_workflow_files",
    "aws_schedulers": "get_workflows_workflow_aws_schedulers",
    "local_schedulers": "get_workflows_workflow_local_schedulers",
    "slurm_schedulers": "get_workflows_workflow_slurm_schedulers",
    "job_process_stats": "get_workflows_workflow_job_process_stats",
    "jobs": "get_workflows_workflow_jobs",
    "needs": "get_workflows_workflow_edges_name",
    "node_used": "get_workflows_workflow_edges_name",
    "process_used": "get_workflows_workflow_edges_name",
    "produces": "get_workflows_workflow_edges_name",
    "requires": "get_workflows_workflow_edges_name",
    "resource_requirements": "get_workflows_workflow_resource_requirements",
    "results": "get_workflows_workflow_results",
    "returned": "get_workflows_workflow_edges_name",
    "scheduled_bys": "get_workflows_workflow_edges_name",
    "scheduled_compute_nodes": "get_workflows_workflow_scheduled_compute_nodes",
    "stores": "get_workflows_workflow_edges_name",
    "user_data": "get_workflows_workflow_user_data",
}


_EDGES = {
    "blocks",
    "consumes",
    "executed",
    "needs",
    "node_used",
    "process_used",
    "produces",
    "requires",
    "returned",
    "scheduled_bys",
    "stores",
}


def _get_db_documents_func(api: DefaultApi, name):
    func_name = _DB_ACCESSOR_FUNCS.get(name)
    if func_name is None:
        raise Exception(
            f"collection {name=} is not stored in {__file__=}. Check if the database "
            "been updated."
        )
    return getattr(api, func_name)


export.add_command(sqlite)
