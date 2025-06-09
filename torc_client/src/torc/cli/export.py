"""CLI commands for exporting workflows from the database"""

import json
from pathlib import Path
from typing import Any

import rich_click as click
from loguru import logger

from torc.openapi_client import DefaultApi
from torc.api import iter_documents
from torc.utils.sql import make_table, insert_rows
from .common import check_database_url, setup_cli_logging, check_output_path


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
    """Export workflows stored in the database to this SQLite file. By default, export all
    workflows. Limit the output tables by passing specific workflow keys as positional arguments.
    """
    check_database_url(api)
    check_output_path(filename, force)
    workflows: list[tuple[Any]] = []
    workflow_configs = []
    workflow_statuses = []
    tables: set[str] = set()
    if workflow_keys:
        selected_workflows = (api.get_workflow(x) for x in workflow_keys)
    else:
        selected_workflows = iter_documents(api.list_workflows)
    for workflow in selected_workflows:
        config = api.get_workflow_config(workflow.key)
        config_as_dict = config.model_dump()
        config_as_dict["compute_node_resource_stats"] = json.dumps(
            config_as_dict["compute_node_resource_stats"]
        )
        status = api.get_workflow_status(workflow.key)
        status_as_dict = status.model_dump()
        status_as_dict["auto_tune_status"] = json.dumps(status_as_dict["auto_tune_status"])
        if not workflows:
            _make_sql_table(workflow, workflow.model_dump(), filename, "workflows")
            _make_sql_table(config, config_as_dict, filename, "workflow_configs")
            _make_sql_table(status, status_as_dict, filename, "workflow_statuses")
        workflows.append(tuple(workflow.model_dump().values()))
        workflow_configs.append(tuple(config_as_dict.values()))
        workflow_statuses.append(tuple(status_as_dict.values()))

        for name in api.list_collection_names(workflow.key).names:
            _build_table(api, workflow.key, name, tables, filename)

    if workflows:
        insert_rows(filename, "workflows", workflows)
        insert_rows(filename, "workflow_configs", workflow_configs)
        insert_rows(filename, "workflow_statuses", workflow_statuses)

    if workflow_keys:
        keys = " ".join(workflow_keys)
        logger.info("Exported database to {} for workflow keys {}", filename, keys)
    else:
        logger.info("Exported database to {} for all workflows", filename)


def _build_table(
    api: DefaultApi, workflow_key: str, collection_name: str, tables: set[str], db_file: Path
) -> None:
    table_name = collection_name.split("__")[0]
    func = _get_db_documents_func(api, table_name)

    rows = []
    args = (workflow_key, table_name) if table_name in _EDGES else (workflow_key,)
    for item in iter_documents(func, *args):
        # to_dict is problematic because it drops fields with None values.
        # Not sure that we should be using pydantic directly.
        # row = item if isinstance(item, dict) else item.to_dict()
        row = item if isinstance(item, dict) else item.model_dump()
        if "to" in row:
            # Swagger converts Arango's '_to' to 'to', but leaves '_from'.
            # Persist Arango names.
            row["_to"] = row.pop("to")
        if table_name in ("events", "user_data"):
            # Put variable, user-defined names in a 'data' column as JSON.
            data = {}
            db_keys = {"_id", "_rev", "_key"}
            for field in set(row.keys()).difference(db_keys):
                data[field] = row.pop(field)
            row["data"] = json.dumps(data)
        elif table_name == "jobs":
            row.pop("internal")
        row["workflow_key"] = workflow_key
        for key, val in row.items():
            if isinstance(val, (dict, list)):
                row[key] = json.dumps(val)
        if table_name not in tables:
            _make_sql_table(item, row, db_file, table_name)
            tables.add(table_name)

        rows.append(tuple(row.values()))
    if rows:
        insert_rows(db_file, table_name, rows)


def _make_sql_table(item, row, filename, basename):
    if isinstance(item, dict):
        types = None
    else:
        types = {}
        for key, val in row.items():
            if val is None:
                types[key] = _get_type_from_schema(item.model_json_schema()["properties"][key])
            else:
                types[key] = type(val)
        types["workflow_key"] = str
        if "to" in types:
            types["_to"] = types.pop("to")
    make_table(filename, basename, row, primary_key="key", types=types)


def _get_type_from_schema(properties: dict):
    schema_type_to_python = {
        "str": str,
        "integer": int,
        "number": float,
    }
    data_type = None
    if "type" in properties:
        data_type = schema_type_to_python.get(properties["type"], str)
    elif "anyOf" in properties:
        for item in properties["anyOf"]:
            if "type" in item:
                if item["type"] == "null":
                    continue
                data_type = schema_type_to_python.get(item["type"], str)
            elif "$ref" in item:
                data_type = str
                # All nested objects need to be serialized as JSON.
                break
            elif not item:
                continue
            else:
                msg = f"Bug: {item=}"
                raise NotImplementedError(msg)
    elif "$ref" in properties:
        msg = f"Bug: $ref not supported: {properties=}"
        raise NotImplementedError(msg)
    else:
        msg = f"Bug: {properties=}"
        raise NotImplementedError(msg)
    return data_type


_DB_ACCESSOR_FUNCS = {
    "blocks": "list_edges",
    "consumes": "list_edges",
    "executed": "list_edges",
    "compute_node_stats": "list_compute_node_stats",
    "compute_nodes": "list_compute_nodes",
    "events": "list_events",
    "files": "list_files",
    "aws_schedulers": "list_aws_schedulers",
    "local_schedulers": "list_local_schedulers",
    "slurm_schedulers": "list_slurm_schedulers",
    "job_process_stats": "list_job_process_stats",
    "jobs": "list_jobs",
    "needs": "list_edges",
    "node_used": "list_edges",
    "process_used": "list_edges",
    "produces": "list_edges",
    "requires": "list_edges",
    "resource_requirements": "list_resource_requirements",
    "results": "list_results",
    "returned": "list_edges",
    "scheduled_bys": "list_edges",
    "scheduled_compute_nodes": "list_scheduled_compute_nodes",
    "stores": "list_edges",
    "user_data": "list_user_data",
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
        msg = (
            f"collection {name=} is not stored in {__file__=}. Check if the database "
            "been updated."
        )
        raise Exception(msg)
    return getattr(api, func_name)


export.add_command(sqlite)
