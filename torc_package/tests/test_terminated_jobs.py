"""Tests jobs that support termination."""

import subprocess
import time

from torc.api import iter_documents


def test_terminated_jobs(cancelable_workflow, tmp_path):
    """Tests that jobs can be terminated on a compute node timeout."""
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
        "-t",
        "P0DT5S",
        "-o",
        str(output_dir),
    ]
    with subprocess.Popen(cmd) as pipe:
        done = False
        for _ in range(100):
            if pipe.poll() is not None:
                done = True
                break
            time.sleep(1)

        if not done:
            pipe.kill()
        assert done
        result = api.is_workflow_complete(workflow_key)
        assert result.is_complete
        pipe.communicate()
        assert pipe.returncode == 0
        for job in iter_documents(api.list_jobs, workflow_key):
            assert job.status == "terminated"
        for result in iter_documents(api.list_results, workflow_key):
            assert result.return_code == 0
            assert result.status == "terminated"
