"""Test workflow execution"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pytest
from click.testing import CliRunner
from torc.openapi_client.api.default_api import DefaultApi
from torc.openapi_client.models.user_data_model import UserDataModel
from torc.openapi_client.models.compute_node_model import ComputeNodeModel
from torc.openapi_client.models.compute_nodes_resources import ComputeNodesResources
from torc.openapi_client.models.result_model import ResultModel
from torc.openapi_client.models.job_model import JobModel
from torc.api import iter_documents, create_jobs, wait_for_healthy_database
from torc.common import GiB
from torc.exceptions import InvalidWorkflow
from torc.common import timer_stats_collector


def test_map_functions(mapped_function_workflow):
    """Test a workflow that maps a function across workers."""
    db, output_dir = mapped_function_workflow
    api = db.api
    mgr = WorkflowManager(api, db.workflow.key)
    mgr.start()
    runner = JobRunner(
        api,
        db.workflow,
        output_dir,
        time_limit="P0DT24H",
        job_completion_poll_interval=0.1,
    )
    runner.run_worker()

    assert api.is_workflow_complete(db.workflow.key).is_complete
    for i in range(1, 6):
        job_key = db.get_document_key("jobs", str(i))
        result = api.get_latest_job_result(db.workflow.key, job_key)
        assert result.return_code == 0
        output_ud = api.list_job_user_data_stores(db.workflow.key, job_key)
        assert len(output_ud.items) == 1
        assert "result" in output_ud.items[0].data
        assert "output_data_path" in output_ud.items[0].data
    pp_key = db.get_document_key("jobs", "postprocess")
    output_ud = api.list_job_user_data_stores(db.workflow.key, pp_key)
    assert len(output_ud.items) == 1
    assert "total" in output_ud.items[0].data
    assert output_ud.items[0].data["total"] == 25
    assert "output_data_paths" in output_ud.items[0].data


def test_add_bulk_jobs(diamond_workflow):
    """Test the add_jobs helper function."""
    db = diamond_workflow[0]
    api = db.api
    initial_job_keys = api.list_job_keys(db.workflow.key)["items"]
    assert len(initial_job_keys) == 4
    resource_requirements = api.list_resource_requirements(db.workflow.key).items[0]

    jobs = (
        JobModel(
            name=f"added_job{i}",
            command="python my_script.py",
            resource_requirements=resource_requirements.id,
        )
        for i in range(1, 51)
    )

    added_jobs = create_jobs(api, db.workflow.id, jobs, max_transfer_size=11)
    assert len(added_jobs) == 50
    names = [x.name for x in api.list_jobs(db.workflow.key).items[len(initial_job_keys) :]]
    assert names == [f"added_job{i}" for i in range(1, 51)]

    final_job_keys = api.list_job_ids(db.workflow.key)["items"]
    assert len(final_job_keys) == len(initial_job_keys) + 50
