import json
import logging
import shutil
import sys
from pathlib import Path

import click
from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration

from wms.utils.sql import make_table, insert_rows


logger = logging.getLogger(__name__)


@click.group()
def export():
    """Export commands"""


@click.command(name="json")
@click.option(
    "-u",
    "--database-url",
    help="Database URL",
    default="http://localhost:8529/_db/workflows/wms-service",
    show_default=True,
)
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
def export_json(database_url, directory, force):
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
    configuration = Configuration()
    configuration.host = database_url
    api = DefaultApi(ApiClient(configuration))

    for name, func in _get_db_documents(api).items():
        if name in _EDGES:
            filename = directory / "edges" / f"{name}.json"
        else:
            filename = directory / f"{name}.json"
        with open(filename, "w") as f_out:
            for item in _iter_values(func):
                if name in ("events", "user_data"):
                    f_out.write(json.dumps(item))
                else:
                    f_out.write(json.dumps(item.to_dict()))
                f_out.write("\n")
        print(f"Exported {name} values to {filename}")


def _iter_values(func):
    skip = 0
    has_more = True
    while has_more:
        result = func(skip=skip, limit=2)
        assert result.count == len(result.items)
        for item in result.items:
            yield item
        skip += result.count
        has_more = result.has_more


@click.command()
@click.option(
    "-u",
    "--database-url",
    help="Database URL",
    default="http://localhost:8529/_db/workflows/wms-service",
    show_default=True,
)
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
def sqlite(database_url, filename, force):
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

    configuration = Configuration()
    configuration.host = database_url
    api = DefaultApi(ApiClient(configuration))

    for name, func in _get_db_documents(api).items():
        found_first = False
        rows = []
        for item in _iter_values(func):
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


def _get_db_documents(api: DefaultApi):
    return {
        "events": api.get_events,
        "jobs": api.get_jobs,
        "files": api.get_files,
        "hpc_configs": api.get_hpc_configs,
        "resource_requirements": api.get_resource_requirements,
        "results": api.get_results,
        "blocks": api.get_blocks,
        "needs": api.get_needs,
        "produces": api.get_produces,
        "requires": api.get_requires,
        "results": api.get_results,
        "returned": api.get_returned,
        "scheduled_bys": api.get_scheduled_bys,
        "stores": api.get_stores,
        "user_data": api.get_user_data,
    }


_EDGES = {"blocks", "needs", "produces", "requires", "returned", "scheduled_bys", "stores"}
_PRIMARY_KEYS = {
    "events": "key",
    "jobs": "name",
    "files": "name",
    "hpc_configs": "name",
    "resource_requirements": "name",
    "results": "name",
    "user_data": "key",
    "blocks": "key",
    "needs": "key",
    "produces": "key",
    "requires": "key",
    "results": "key",
    "returned": "key",
    "scheduled_bys": "key",
    "stores": "key",
}

export.add_command(export_json)
export.add_command(sqlite)
