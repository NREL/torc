"""Tests database API commands"""

import pytest

from swagger_client.rest import ApiException


def test_api_nodes_by_key(completed_workflow):
    """Tests API commands to get documents stored by the 'key' parameter."""
    db, _, _ = completed_workflow
    api = db.api
    names = [
        "compute_node_stats",
        "compute_nodes",
        "events",
        "files",
        "job_process_stats",
        "jobs",
        "local_schedulers",
        "resource_requirements",
        "results",
        "user_data",
    ]

    for name in names:
        results = getattr(api, f"get_{name}_workflow")(db.workflow.key)
        if results.items:
            item = results.items[0]
            if not isinstance(item, dict):
                item = item.to_dict()
            key = _get_key(item)
            val = getattr(api, f"get_{name}_workflow_key")(db.workflow.key, key)
            if not isinstance(val, dict):
                val = val.to_dict()
            assert val == item
            getattr(api, f"delete_{name}_workflow_key")(db.workflow.key, key)
            with pytest.raises(ApiException):
                val = getattr(api, f"get_{name}_workflow_key")(db.workflow.key, key)

        getattr(api, f"delete_{name}_workflow")(db.workflow.key)
        result = getattr(api, f"get_{name}_workflow")(db.workflow.key)
        assert len(result.items) == 0


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
        result = api.get_edges_workflow_name(db.workflow.key, name)
        if result.items:
            item = result.items[0]
            if not isinstance(item, dict):
                item = item.to_dict()
            key = _get_key(item)
            val = api.get_edges_workflow_name_key(db.workflow.key, name, key)
            if not isinstance(val, dict):
                val = val.to_dict()
            assert val == item
            api.delete_edges_workflow_name_key(db.workflow.key, name, key)
            with pytest.raises(ApiException):
                val = api.get_edges_workflow_name_key(db.workflow.key, name, key)

        api.delete_edges_workflow_name(db.workflow.key, name)
        result = api.get_edges_workflow_name(db.workflow.key, name)
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
    assert new_status.run_id == 0


def _get_key(data: dict):
    for key in ("key", "_key"):
        if key in data:
            return data[key]
    raise KeyError(f"key is not stored in {data.keys()}")
