"""Tests SLURM workflows"""

import itertools
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from torc import torc_settings
from torc.api import make_api, iter_documents
from torc.cli.torc import cli
from torc.hpc.slurm_interface import SlurmInterface
from torc.hpc.common import HpcJobStatus
from torc.utils.run_command import check_run_command


@pytest.fixture
def setup_api(tmp_path):
    """Fixture to setup an API client."""
    if torc_settings.database_url is None:
        print(
            "database_url must be set in the torc config file to run this test",
            file=sys.stderr,
        )
        sys.exit(1)
    api = make_api(torc_settings.database_url)
    output_dir = tmp_path / "torc-test-output-dir"  # This needs to be accessible on all nodes.

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    yield api, output_dir

    for path in (output_dir,):
        if path.exists():
            shutil.rmtree(path)


def test_fake_slurm_workflow(setup_api):
    """Runs a fake slurm workflow"""
    api, output_dir = setup_api
    inputs_file = Path("inputs.json")
    inputs_file.write_text(json.dumps({"val": 5}))
    builder = Path(__file__).parents[2] / "examples" / "diamond_workflow.py"
    output: dict[str, Any] = {}
    check_run_command(f"python {builder}", output=output)
    regex = re.compile(r"Created workflow (\d+) with")
    match = regex.search(output["stderr"])
    assert match
    key = match.group(1)
    runner = CliRunner()

    # The resource requirements in the workflow are greater than what's in CI. Decrease them.
    result = runner.invoke(
        cli,
        [
            "-k",
            key,
            "resource-requirements",
            "add",
            "--name",
            "tiny",
            "--num-cpus",
            str(1),
            "--memory",
            "1m",
            "--runtime",
            "P0DT1m",
            "--apply-to-all-jobs",
        ],
    )
    assert result.exit_code == 0, f"Failed to set resource requirements: {result.stderr}"

    slurm_config = _get_scheduler_by_name(api, key)

    try:
        result = runner.invoke(cli, ["-k", key, "workflows", "start"])
        assert result.exit_code == 0
        subprocess.run(
            [
                "torc",
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
                "-p1",
            ],
            check=True,
        )
        _wait_for_workflow_complete(api, key, output_dir)

        result = runner.invoke(cli, ["-k", key, "compute-nodes", "list"])
        assert result.exit_code == 0
        nodes = json.loads(result.stdout)["compute_nodes"]
        assert len(nodes) == 1

        job_results = api.list_jobs(key).items
        for job in job_results:
            print(f"{job=}")
        results = api.list_results(key).items
        assert len(results) == 4
        for res in results:
            assert res.return_code == 0

        result = runner.invoke(cli, ["-k", key, "reports", "results", "-o", str(output_dir)])
        assert result.exit_code == 0
        assert result.exit_code == 0
        report = json.loads(result.stdout)
        assert len(report["jobs"]) == 4
        for job_report in report["jobs"]:
            assert len(job_report["runs"]) == 1
            run = job_report["runs"][0]
            assert run["return_code"] == 0
            assert Path(run["job_runner_log_file"]).exists()
            for file in itertools.chain(run["slurm_stdio_files"], run["job_stdio_files"]):
                assert Path(file).exists()

        start_events: list[dict[str, Any]] = []
        complete_events: list[dict[str, Any]] = []
        for event in iter_documents(api.list_events, key):
            if event.get("category") == "job" and event.get("type") in ("start", "complete"):
                timestamp = event["timestamp"]
                item = {
                    "key": int(event["job_key"]),
                    "timestamp": timestamp,
                }
                events = start_events if event["type"] == "start" else complete_events
                events.append(item)

        assert len(start_events) == 4
        assert len(complete_events) == 4
        assert len(results) == 4
        for res in results:
            assert res.return_code == 0
        _wait_for_compute_nodes(api, key)
    finally:
        api.remove_workflow(key)


def _get_scheduler_by_name(api, workflow_key):
    slurm_configs = [
        x for x in iter_documents(api.list_slurm_schedulers, workflow_key) if x.name == "short"
    ]
    assert slurm_configs
    return slurm_configs[0]


def _wait_for_workflow_complete(api, key, output_dir, timeout=60):
    timeout = time.time() + timeout
    done = False
    while time.time() < timeout:
        response = api.is_workflow_complete(key)
        if response.is_complete:
            done = True
            break
        time.sleep(1)
    if not done:
        for path in output_dir.iterdir():
            if path.is_file():
                print(f"Output file: {path} - {path.read_text()}", file=sys.stderr)
    assert done


def _wait_for_compute_nodes(api, key):
    slurm_job_ids = {x.scheduler["slurm_job_id"] for x in api.list_compute_nodes(key).items}
    intf = SlurmInterface()
    timeout = time.time() + 300
    while time.time() < timeout and slurm_job_ids:
        print("Sleep while waiting for Slurm jobs to finish", file=sys.stderr)
        completed_jobs = set()
        time.sleep(1)
        for job_id in slurm_job_ids:
            job_info = intf.get_status(job_id)
            if job_info.status in (HpcJobStatus.COMPLETE, HpcJobStatus.NONE):
                print(f"Slurm {job_id=} is done; status={job_info.status}", file=sys.stderr)
                completed_jobs.add(job_id)
        slurm_job_ids.difference_update(completed_jobs)

    assert not slurm_job_ids, f"Timed out waiting for jobs to finish: {slurm_job_ids=}"
