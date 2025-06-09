"""Tests the cancel-workflow command."""

import subprocess
import time

from torc.api import iter_documents


def test_cancel_workflow(cancelable_workflow, tmp_path):
    """Tests the cancel-workflow command."""
    db = cancelable_workflow[0]
    api = db.api
    workflow_key = db.workflow.key
    output_dir = tmp_path / "output"

    cmd = [
        "torc",
        "-k",
        workflow_key,
        "-u",
        api.api_client.configuration.host,
        "jobs",
        "run",
        "-p",
        "1",
        "-o",
        str(output_dir),
    ]
    with subprocess.Popen(cmd) as pipe:
        time.sleep(2)
        assert pipe.poll() is None
        subprocess.run(
            [
                "torc",
                "-n",
                "-u",
                api.api_client.configuration.host,
                "workflows",
                "cancel",
                workflow_key,
            ],
            check=True,
        )
        status = api.get_workflow_status(workflow_key)
        assert status.is_canceled
        result = api.is_workflow_complete(workflow_key)
        assert result.is_complete
        pipe.communicate()
        assert pipe.returncode == 0
        for job in iter_documents(api.list_jobs, workflow_key):
            assert job.status == "canceled"
        for result in iter_documents(api.list_results, workflow_key):
            assert result.return_code != 0
            assert result.status == "canceled"
