"""Tests SLURM workflows"""

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from torc.api import make_api
from torc.cli.torc import cli
from torc.common import STATS_DIR
from torc.torc_rc import TorcRuntimeConfig
from torc.hpc.slurm_interface import SlurmInterface
from torc.hpc.common import HpcJobStatus
from torc.utils.files import load_data, dump_data


try:
    subprocess.call(["squeue", "--help"])
except FileNotFoundError:
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
    file = Path(__file__).parent.parent.parent / "examples" / "diamond_workflow.json5"
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
                "-n1",
                "-o",
                str(output_dir),
                "-p",
                1,
            ],
        )
        assert result.exit_code == 0
        job_ids = json.loads(result.stdout)["job_ids"]

        intf = SlurmInterface()
        timeout = time.time() + 600
        completed_jobs = []
        print("\n", file=sys.stderr)
        while time.time() < timeout and len(completed_jobs) < len(job_ids):
            print("Sleep while waiting for SLURM jobs to finish", file=sys.stderr)
            time.sleep(10)
            for job_id in job_ids:
                job_info = intf.get_status(job_id)
                if job_info.status in (HpcJobStatus.COMPLETE, HpcJobStatus.NONE):
                    print(
                        f"SLURM {job_id=} is done; status={job_info.status}",
                        file=sys.stderr,
                    )
                    completed_jobs.append(job_id)

        assert len(completed_jobs) == len(
            job_ids
        ), f"Timed out waiting for jobs to finish: {len(completed_jobs)=} {len(job_ids)=}"

        results = api.get_workflows_workflow_results(key).items
        assert len(results) == 4
        for result in results:
            assert result.return_code == 0

        stats_dir = output_dir / STATS_DIR
        html_files = [x for x in stats_dir.iterdir() if x.suffix == ".html"]
        assert html_files
        sqlite_files = [x for x in stats_dir.iterdir() if x.suffix == ".sqlite"]
        assert sqlite_files
    finally:
        api.delete_workflows_key(key)
