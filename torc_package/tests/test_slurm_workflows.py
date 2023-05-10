"""Tests SLURM workflows"""

import json
import shutil
import subprocess
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
    dst_file = _fix_slurm_account(file, output_dir, slurm_account)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli, ["-F", "json", "workflows", "create-from-json-file", str(dst_file)]
    )
    assert result.exit_code == 0
    key = json.loads(result.stdout)["key"]
    slurm_config = _get_scheduler_by_name(api, key)

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
                "-p1",
            ],
        )
        assert result.exit_code == 0
        _wait_for_workflow_complete(api, key)

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
        # work1 key is lower than work2 key, but either could have started first.
        # Need to verify that the two jobs ran in serial because of CPU requirements.
        start_events.sort(key=lambda x: int(x["key"]))
        complete_events.sort(key=lambda x: int(x["key"]))
        if start_events[1]["timestamp"] < start_events[2]["timestamp"]:
            first = 1
            second = 2
        else:
            first = 2
            second = 1
        assert start_events[second]["timestamp"] > complete_events[first]["timestamp"]

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


def test_cpu_affinity_workflow(setup_api, slurm_account):  # pylint: disable=redefined-outer-name
    """Runs a slurm workflow while setting CPU affinity."""
    api, output_dir, _ = setup_api
    key = _create_cpu_affinity_workflow(output_dir, slurm_account)
    slurm_config = _get_scheduler_by_name(api, key)

    try:
        runner = CliRunner(mix_stderr=False)
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
                "-c9",
                "-o",
                str(output_dir),
                "-p1",
            ],
        )
        assert result.exit_code == 0
        _wait_for_workflow_complete(api, key)
        _check_cpu_affinity_results(api, key)
        _wait_for_compute_nodes(api, key)
    finally:
        api.delete_workflows_key(key)


def test_slurm_cpu_bind_workflow(setup_api, slurm_account):  # pylint: disable=redefined-outer-name
    """Runs a slurm workflow while using the cpu-bind feature."""
    api, output_dir, _ = setup_api
    key = _create_cpu_affinity_workflow(output_dir, slurm_account)
    text = f"""#!/bin/bash
#SBATCH --account={slurm_account}
#SBATCH --job-name=my_job
#SBATCH --partition=debug
#SBATCH --qos=standby
#SBATCH --time=00:10:00
#SBATCH --output={output_dir}/job_output_%j.o
#SBATCH --error={output_dir}/job_output_%j.e
#SBATCH --nodes=1

srun -c9 -n4 --cpu-bind=mask_cpu:0x1ff,0x3fe00,0x7fc0000,0xff8000000 \\
    torc -k {key} hpc slurm run-jobs -o {output_dir} --is-subtask --max-parallel-jobs=1 -p1
"""
    sbatch_script = output_dir / "sbatch.sh"
    sbatch_script.write_text(text, encoding="utf-8")

    try:
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli, ["-k", key, "workflows", "start"])
        assert result.exit_code == 0
        subprocess.run(["sbatch", str(sbatch_script)], check=True)
        _wait_for_workflow_complete(api, key)
        _check_cpu_affinity_results(api, key)
        _wait_for_compute_nodes(api, key)
    finally:
        api.delete_workflows_key(key)


def _create_cpu_affinity_workflow(output_dir, slurm_account):
    assert slurm_account, f"{slurm_account=} must be set"
    file = Path(__file__).parent.parent.parent / "examples" / "slurm_cpu_affinity_workflow.json5"
    dst_file = _fix_slurm_account(file, output_dir, slurm_account)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli, ["-F", "json", "workflows", "create-from-json-file", str(dst_file)]
    )
    assert result.exit_code == 0
    return json.loads(result.stdout)["key"]


def _check_cpu_affinity_results(api, key):
    results = api.get_workflows_workflow_results(key).items
    assert len(results) == 4
    for result in results:
        assert result.return_code == 0
    # Eagle value
    num_cpus = None
    total_cpu_affinity = set()
    for ud in api.get_workflows_workflow_user_data(key).items:
        if num_cpus is None:
            num_cpus = ud.data["num_cpus"]
        else:
            assert num_cpus == ud.data["num_cpus"]
        total_cpu_affinity.update(set(ud.data["affinity"]))
    expected_cpu_affinity = set(range(num_cpus))
    assert total_cpu_affinity == expected_cpu_affinity


def _fix_slurm_account(spec_file, output_dir, account):
    dst_file = output_dir / spec_file.name
    if dst_file.exists():
        dst_file.unlink()
    shutil.copyfile(spec_file, dst_file)
    data = load_data(dst_file)
    for scheduler in data["schedulers"]["slurm_schedulers"]:
        scheduler["account"] = account
    dump_data(data, dst_file, indent=2)
    return dst_file


def _get_scheduler_by_name(api, workflow_key):
    slurm_configs = [
        x
        for x in iter_documents(api.get_workflows_workflow_slurm_schedulers, workflow_key)
        if x.name == "debug"
    ]
    assert slurm_configs
    return slurm_configs[0]


def _wait_for_workflow_complete(api, key, timeout=600):
    timeout = time.time() + timeout
    done = True
    while time.time() < timeout:
        response = api.get_workflows_key_is_complete(key)
        if response.is_complete:
            done = True
            break
        time.sleep(1)
    assert done


def _wait_for_compute_nodes(api, key):
    slurm_job_ids = {
        x.scheduler["slurm_job_id"] for x in api.get_workflows_workflow_compute_nodes(key).items
    }
    intf = SlurmInterface()
    timeout = time.time() + 300
    while time.time() < timeout and slurm_job_ids:
        print("Sleep while waiting for Slurm jobs to finish", file=sys.stderr)
        completed_jobs = set()
        time.sleep(3)
        for job_id in slurm_job_ids:
            job_info = intf.get_status(job_id)
            if job_info.status in (HpcJobStatus.COMPLETE, HpcJobStatus.NONE):
                print(f"Slurm {job_id=} is done; status={job_info.status}", file=sys.stderr)
                completed_jobs.add(job_id)
        slurm_job_ids.difference_update(completed_jobs)

    assert not slurm_job_ids, f"Timed out waiting for jobs to finish: {slurm_job_ids=}"
