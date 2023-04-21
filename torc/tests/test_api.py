"""Tests database API commands"""


import pytest
from swagger_client.rest import ApiException

from torc.api import make_api, remove_db_keys


def test_api_nodes_by_key(create_workflow_cli):
    """Tests API commands to get documents stored by the 'key' parameter."""
    workflow_key, url, _ = create_workflow_cli
    api = make_api(url)
    names = {
        "compute_node_stats": "hostname",
        "compute_nodes": "hostname",
        "events": "timestamp",
        "files": "name",
        "job_process_stats": "job_key",
        "jobs": "name",
        "local_schedulers": "name",
        "resource_requirements": "name",
        "results": "status",
        "slurm_schedulers": "name",
        "user_data": None,
    }

    for name, field in names.items():
        results = getattr(api, f"get_workflows_workflow_{name}")(workflow_key)
        if results.items:
            item = results.items[0]
            if not isinstance(item, dict):
                item = item.to_dict()
            key = _get_key(item)
            val = getattr(api, f"get_workflows_workflow_{name}_key")(workflow_key, key)
            if not isinstance(val, dict):
                val = val.to_dict()
            assert val == item
            getattr(api, f"delete_workflows_workflow_{name}_key")(workflow_key, key)
            with pytest.raises(ApiException):
                getattr(api, f"get_workflows_workflow_{name}_key")(workflow_key, key)
            val = _fix_fields(name, remove_db_keys(val))
            val2 = getattr(api, f"post_workflows_workflow_{name}")(val, workflow_key)
            if not isinstance(val2, dict):
                val2 = val2.to_dict()
            key = _get_key(val2)
            field_to_change = field
            if field_to_change is None:
                val2["test_val"] = "abc"
            else:
                val2[field_to_change] = "abc"

            getattr(api, f"put_workflows_workflow_{name}_key")(
                _fix_fields(name, val2), workflow_key, key
            )

        getattr(api, f"delete_workflows_workflow_{name}")(workflow_key)
        result = getattr(api, f"get_workflows_workflow_{name}")(workflow_key)
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
        result = api.get_workflows_workflow_edges_name(db.workflow.key, name)
        if result.items:
            item = result.items[0]
            if not isinstance(item, dict):
                item = item.to_dict()
            key = _get_key(item)
            val = api.get_workflows_workflow_edges_name_key(db.workflow.key, name, key)
            if not isinstance(val, dict):
                val = val.to_dict()
            assert val == item
            api.delete_workflows_workflow_edges_name_key(db.workflow.key, name, key)
            with pytest.raises(ApiException):
                val = api.get_workflows_workflow_edges_name_key(db.workflow.key, name, key)

        api.delete_workflows_workflow_edges_name(db.workflow.key, name)
        result = api.get_workflows_workflow_edges_name(db.workflow.key, name)
        assert len(result.items) == 0


def test_api_workflow_status(completed_workflow):
    """Tests API commands to manage workflow status."""
    db, _, _ = completed_workflow
    api = db.api
    status = api.get_workflows_status_key(db.workflow.key)
    orig = status.run_id
    status.run_id += 1
    api.put_workflows_status_key(status, db.workflow.key)
    new_status = api.get_workflows_status_key(db.workflow.key)
    assert new_status.run_id == orig + 1
    api.post_workflows_reset_status_key(db.workflow.key)
    new_status = api.get_workflows_status_key(db.workflow.key)
    assert new_status.run_id == orig + 1


def _get_key(data: dict):
    for key in ("key", "_key"):
        if key in data:
            return data[key]
    raise KeyError(f"key is not stored in {data.keys()}")
