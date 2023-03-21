"""CLI commands for exporting workflows from the database"""

import json
import logging
import shutil
import sys
from pathlib import Path

import click
from swagger_client import DefaultApi

from wms.api import iter_documents
from wms.utils.sql import make_table, insert_rows
from .common import setup_cli_logging


logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def export(ctx):
    """Export commands"""
    setup_cli_logging(ctx, 1, __name__)


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
def export_json(api, directory, force):
    """Export workflow database to this directory in JSON format."""
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
            args = (name,) if name in _EDGES else tuple()
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
def sqlite(api, filename, force):
    """Export workflow database to this SQLite file."""
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
        if name in ("compute_node_stats", "compute_nodes"):
            # TODO: determine how to record the nested data. JSON string?
            continue
        found_first = False
        rows = []
        args = (name,) if name in _EDGES else tuple()
        for item in iter_documents(func, *args):
            row = item if isinstance(item, dict) else item.to_dict()
            if "to" in row:
                row["_to"] = row.pop("to")
            if name in ("events", "user_data"):
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
        "blocks": api.get_edges_name,
        "compute_node_stats": api.get_compute_node_stats,
        "compute_nodes": api.get_compute_nodes,
        "events": api.get_events,
        "files": api.get_files,
        "aws_schedulers": api.get_aws_schedulers,
        "local_schedulers": api.get_local_schedulers,
        "slurm_schedulers": api.get_slurm_schedulers,
        "job_process_stats": api.get_job_process_stats,
        "jobs": api.get_jobs,
        "needs": api.get_edges_name,
        "node_used": api.get_edges_name,
        "process_used": api.get_edges_name,
        "produces": api.get_edges_name,
        "requires": api.get_edges_name,
        "resource_requirements": api.get_resource_requirements,
        "results": api.get_results,
        "returned": api.get_edges_name,
        "scheduled_bys": api.get_edges_name,
        "stores": api.get_edges_name,
        "user_data": api.get_user_data,
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
