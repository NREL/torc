"""Tests SLURM workflows"""

import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

import pytest
from click.testing import CliRunner

from torc.api import make_api, iter_documents
from torc.cli.torc import cli
from torc.common import STATS_DIR
from torc.torc_rc import TorcRuntimeConfig
from torc.hpc.slurm_interface import SlurmInterface
from torc.hpc.common import HpcJobStatus
from torc.utils.files import load_data, dump_data


if shutil.which("squeue") is None:
    pytest.skip("skipping slurm tests", allow_module_level=True)


@pytest.fixture
def setup_api():
    """Fixture to setup an API client."""
    config = TorcRuntimeConfig.load()
    if config.database_url is None:
        print(
            f"database_url must be set in {TorcRuntimeConfig.path()} to run this test",
            file=sys.stderr,
        )
        sys.exit(1)
    api = make_api(config.database_url)
    output_dir = Path(".") / "torc-test-output-dir"  # This needs to be accessible on all nodes.
    script_output_dir = Path(".") / "output"  # Hard-coded in spec files
    if script_output_dir.exists():
        print(f"{script_output_dir=} already exists", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir()
    script_output_dir.mkdir()

    yield api, output_dir, script_output_dir

    for path in (output_dir, script_output_dir):
        if path.exists():
            shutil.rmtree(path)
    api.api_client.close()


def test_slurm_workflow(setup_api, slurm_account):  # pylint: disable=redefined-outer-name
    """Runs a slurm workflow"""
    api, output_dir, script_output_dir = setup_api
    assert slurm_account, f"{slurm_account=} must be set"

    inputs_file = script_output_dir / "inputs.json"
    inputs_file.write_text(json.dumps({"val": 5}))
    file = Path(__file__).parent.parent.parent / "examples" / "slurm_diamond_workflow.json5"
    dst_file = output_dir / file.name
    if dst_file.exists():
        dst_file.unlink()
    shutil.copyfile(file, dst_file)
    data = load_data(dst_file)
    for scheduler in data["schedulers"]["slurm_schedulers"]:
        scheduler["account"] = slurm_account
    dump_data(data, dst_file, indent=2)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli, ["-F", "json", "workflows", "create-from-json-file", str(dst_file)]
    )
    assert result.exit_code == 0
    key = json.loads(result.stdout)["key"]
    slurm_configs = [
        x
        for x in iter_documents(api.get_workflows_workflow_slurm_schedulers, key)
        if x.name == "debug"
    ]
    assert slurm_configs
    slurm_config = slurm_configs[0]

    try:
        result = runner.invoke(cli, ["-k", key, "workflows", "start"])
        assert result.exit_code == 0
        result = runner.invoke(
            cli,
            [
                "-F",
                "json",
                "-k",
                key,
                "hpc",
                "slurm",
                "schedule-nodes",
                "-s",
                slurm_config.key,
                "-n1",
                "-o",
                str(output_dir),
                "-p",
                1,
            ],
        )
        assert result.exit_code == 0

        timeout = time.time() + 600
        done = True
        while time.time() < timeout:
            response = api.get_workflows_key_is_complete(key)
            if response.is_complete:
                done = True
                break
            time.sleep(1)
        assert done

        result = runner.invoke(cli, ["-k", key, "compute-nodes", "list"])
        assert result.exit_code == 0
        nodes = json.loads(result.stdout)["compute_nodes"]
        assert len(nodes) == 2

        results = api.get_workflows_workflow_results(key).items
        assert len(results) == 4
        for result in results:
            assert result.return_code == 0

        start_events = []
        complete_events = []
        for event in iter_documents(api.get_workflows_workflow_events, key):
            if event.get("category") == "job" and event.get("type") in ("start", "complete"):
                timestamp = datetime.strptime(event["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
                item = {
                    "key": int(event["key"]),
                    "timestamp": timestamp,
                }
                events = start_events if event["type"] == "start" else complete_events
                events.append(item)

        assert len(start_events) == 4
        assert len(complete_events) == 4
        start_events.sort(key=lambda x: x["key"])
        complete_events.sort(key=lambda x: x["key"])
        work1_complete_time = complete_events[1]["timestamp"]
        work2_start_time = start_events[2]["timestamp"]
        assert work2_start_time > work1_complete_time

        assert len(results) == 4
        for result in results:
            assert result.return_code == 0

        stats_dir = output_dir / STATS_DIR
        html_files = [x for x in stats_dir.iterdir() if x.suffix == ".html"]
        assert html_files
        sqlite_files = [x for x in stats_dir.iterdir() if x.suffix == ".sqlite"]
        assert sqlite_files
        _wait_for_compute_nodes(api, key)
    finally:
        api.delete_workflows_key(key)


def _wait_for_compute_nodes(api, key):
    slurm_job_ids = {
        x.scheduler["slurm_job_id"] for x in api.get_workflows_workflow_compute_nodes(key).items
    }
    intf = SlurmInterface()
    timeout = time.time() + 300
    while time.time() < timeout and slurm_job_ids:
        print("Sleep while waiting for SLURM jobs to finish", file=sys.stderr)
        completed_jobs = set()
        time.sleep(3)
        for job_id in slurm_job_ids:
            job_info = intf.get_status(job_id)
            if job_info.status in (HpcJobStatus.COMPLETE, HpcJobStatus.NONE):
                print(f"SLURM {job_id=} is done; status={job_info.status}", file=sys.stderr)
                completed_jobs.add(job_id)
        slurm_job_ids.difference_update(completed_jobs)

    assert not slurm_job_ids, f"Timed out waiting for jobs to finish: {slurm_job_ids=}"
