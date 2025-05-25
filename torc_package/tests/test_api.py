"""Tests database API commands"""

from typing import Any

import pytest
from torc.openapi_client.rest import ApiException

from torc.api import make_api, remove_db_keys


def test_api_nodes_by_key(create_workflow_cli):
    """Tests API commands to get documents stored by the 'key' parameter."""
    workflow_key, url, _ = create_workflow_cli
    api = make_api(url)
    names: dict[str, dict[str, Any]] = {
        "compute_node_stats": {"field": "hostname", "singular_remove_last_char": False},
        "job_process_stats": {"field": "job_key", "singular_remove_last_char": False},
        "resource_requirements": {"field": "name", "singular_remove_last_char": False},
        "user_data": {"field": None, "singular_remove_last_char": False},
        "compute_nodes": {"field": "hostname", "singular_remove_last_char": True},
        "events": {"field": "timestamp", "singular_remove_last_char": True},
        "files": {"field": "name", "singular_remove_last_char": True},
        "jobs": {"field": "name", "singular_remove_last_char": True},
        "local_schedulers": {"field": "name", "singular_remove_last_char": True},
        "results": {"field": "status", "singular_remove_last_char": True},
        "slurm_schedulers": {"field": "name", "singular_remove_last_char": True},
    }

    for name, metadata in names.items():
        singular = name[:-1] if metadata["singular_remove_last_char"] else name
        list_all = getattr(api, f"list_{name}")
        get_one = getattr(api, f"get_{singular}")
        add_one = getattr(api, f"add_{singular}")
        remove_one = getattr(api, f"remove_{singular}")
        delete_all = getattr(api, f"delete_{name}")
        modify_one = getattr(api, f"modify_{singular}")
        results = list_all(workflow_key)
        if results.items:
            item = results.items[0]
            if not isinstance(item, dict):
                item = item.to_dict()
            key = _get_key(item)
            val = get_one(workflow_key, key)
            if not isinstance(val, dict):
                val = val.to_dict()
            assert val == item
            remove_one(workflow_key, key)
            with pytest.raises(ApiException):
                get_one(workflow_key, key)
            val = _fix_fields(name, remove_db_keys(val))
            val2 = add_one(workflow_key, val)
            if not isinstance(val2, dict):
                val2 = val2.to_dict()
            key = _get_key(val2)
            field_to_change = metadata["field"]
            if field_to_change is None:
                val2["test_val"] = "abc"
            else:
                val2[field_to_change] = "abc"

            modify_one(workflow_key, key, _fix_fields(name, val2))

        delete_all(workflow_key)
        result = list_all(workflow_key)
        assert len(result.items) == 0


def _fix_fields(collection_name, val):
    if "id" in val:
        val["_key"] = val.pop("key")
        val["_id"] = val.pop("id")
        val["_rev"] = val.pop("rev")

    match collection_name:
        case "jobs":
            val.pop("internal")
        case "slurm_schedulers":
            for field in ("tmp", "mem", "gres", "partition"):
                if field in val and val[field] is None:
                    val.pop(field)
    return val


def test_api_edges(completed_workflow):
    """Tests API commands for edges."""
    db, _, _ = completed_workflow
    api = db.api
    names = [
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
    ]
    for name in names:
        result = api.list_edges(db.workflow.key, name)
        if result.items:
            item = result.items[0]
            if not isinstance(item, dict):
                item = item.to_dict()
            key = _get_key(item)
            val = api.get_edge(db.workflow.key, name, key)
            if not isinstance(val, dict):
                val = val.to_dict()
            assert val == item
            api.remove_edge(db.workflow.key, name, key)
            with pytest.raises(ApiException):
                val = api.get_edge(db.workflow.key, name, key)

        api.delete_edges(db.workflow.key, name)
        result = api.list_edges(db.workflow.key, name)
        assert len(result.items) == 0


def test_api_workflow_status(completed_workflow):
    """Tests API commands to manage workflow status."""
    db, _, _ = completed_workflow
    api = db.api
    status = api.get_workflow_status(db.workflow.key)
    orig = status.run_id
    status.run_id += 1
    api.modify_workflow_status(db.workflow.key, status)
    new_status = api.get_workflow_status(db.workflow.key)
    assert new_status.run_id == orig + 1
    api.reset_workflow_status(db.workflow.key)
    api.reset_job_status(db.workflow.key)
    api.reset_job_status(db.workflow.key, failed_only=True)
    new_status = api.get_workflow_status(db.workflow.key)
    assert new_status.run_id == orig + 1


def _get_key(data: dict):
    for key in ("key", "_key"):
        if key in data:
            return data[key]
    msg = f"key is not stored in {data.keys()}"
    raise KeyError(msg)
