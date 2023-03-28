"""CLI commands for exporting workflows from the database"""

import json
import logging
import shutil
import sys
from pathlib import Path

import click
from swagger_client import DefaultApi

from torc.api import iter_documents
from torc.utils.sql import make_table, insert_rows
from .common import get_workflow_key_from_context, setup_cli_logging


logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def export(ctx):
    """Export commands"""
    setup_cli_logging(ctx, __name__)


@click.command(name="json")
@click.option(
    "-d",
    "--directory",
    default="exported_workflow_json",
    show_default=True,
    callback=lambda *x: Path(x[2]),
    help="Directory to create exported files",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    show_default=True,
    help="Overwrite directory if it exists.",
)
@click.pass_obj
@click.pass_context
def export_json(ctx, api, directory, force):
    """Export workflow database to this directory in JSON format."""
    workflow_key = get_workflow_key_from_context(ctx, api)
    if directory.exists():
        if force:
            shutil.rmtree(directory)
        else:
            print(
                f"{directory} already exists. Choose a different path or pass --force to overwrite",
                file=sys.stderr,
            )
            sys.exit(1)

    directory.mkdir()
    edges_directory = directory / "edges"
    edges_directory.mkdir()

    # TODO: Delete this and use arangodump instead.
    # TODO: This doesn't handle batching and will not get all data.
    # TODO: Get workflow_status
    for name, func in _get_db_documents(api).items():
        if name in _EDGES:
            filename = directory / "edges" / f"{name}.json"
        else:
            filename = directory / f"{name}.json"
        with open(filename, "w", encoding="utf-8") as f_out:
            args = (workflow_key, name) if name in _EDGES else (workflow_key,)
            for item in iter_documents(func, *args):
                if name in ("events", "user_data"):
                    f_out.write(json.dumps(item))
                else:
                    f_out.write(json.dumps(item.to_dict()))
                f_out.write("\n")
        print(f"Exported {name} values to {filename}")


@click.command()
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
@click.pass_context
def sqlite(ctx, api, filename, force):
    """Export workflow database to this SQLite file."""
    workflow_key = get_workflow_key_from_context(ctx, api)
    if filename.exists():
        if force:
            filename.unlink()
        else:
            print(
                f"{filename} already exists. Choose a different path or pass --force to overwrite",
                file=sys.stderr,
            )
            sys.exit(1)

    # TODO: Get workflow_status
    for name, func in _get_db_documents(api).items():
        if "compute_node_stats" in name or "compute_nodes" in name:
            # TODO: determine how to record the nested data. JSON string?
            continue
        found_first = False
        rows = []
        args = (workflow_key, name) if name in _EDGES else (workflow_key,)
        for item in iter_documents(func, *args):
            row = item if isinstance(item, dict) else item.to_dict()
            if "to" in row:
                row["_to"] = row.pop("to")
            if "events" in name or "user_data" in name:
                data = {}
                db_keys = {"_id", "_rev", "_key"}
                for field in set(row.keys()).difference(db_keys):
                    data[field] = row.pop(field)
                row["data"] = json.dumps(data)

            if not found_first:
                make_table(filename, name, row, primary_key=_PRIMARY_KEYS[name])
                found_first = True
            rows.append(tuple(row.values()))
        if rows:
            insert_rows(filename, name, rows)

    print(f"Exported workflow database to {filename}")


# TODO: make test that verifies that this list is synced with the database.


def _get_db_documents(api: DefaultApi):
    return {
        "blocks": api.get_edges_workflow_name,
        "compute_node_stats": api.get_compute_node_stats_workflow,
        "compute_nodes": api.get_compute_nodes_workflow,
        "events": api.get_events_workflow,
        "files": api.get_files_workflow,
        "aws_schedulers": api.get_aws_schedulers_workflow,
        "local_schedulers": api.get_local_schedulers_workflow,
        "slurm_schedulers": api.get_slurm_schedulers_workflow,
        "job_process_stats": api.get_job_process_stats_workflow,
        "jobs": api.get_jobs_workflow,
        "needs": api.get_edges_workflow_name,
        "node_used": api.get_edges_workflow_name,
        "process_used": api.get_edges_workflow_name,
        "produces": api.get_edges_workflow_name,
        "requires": api.get_edges_workflow_name,
        "resource_requirements": api.get_resource_requirements_workflow,
        "results": api.get_results_workflow,
        "returned": api.get_edges_workflow_name,
        "scheduled_bys": api.get_edges_workflow_name,
        "stores": api.get_edges_workflow_name,
        "user_data": api.get_user_data_workflow,
    }


_EDGES = {
    "blocks",
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
_PRIMARY_KEYS = {
    "compute_node_stats": "key",
    "compute_nodes": "key",
    "executed": "key",
    "events": "key",
    "jobs": "name",
    "files": "name",
    "aws_schedulers": "name",
    "local_schedulers": "name",
    "slurm_schedulers": "name",
    "resource_requirements": "name",
    "user_data": "key",
    "blocks": "key",
    "needs": "key",
    "node_used": "key",
    "produces": "key",
    "requires": "key",
    "results": "key",
    "returned": "key",
    "scheduled_bys": "key",
    "stores": "key",
}

export.add_command(export_json)
export.add_command(sqlite)
