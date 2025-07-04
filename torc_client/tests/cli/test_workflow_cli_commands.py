"""Tests the workflow CLI commands."""

import getpass
import json
import math
import os
import shutil
import socket
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from torc.cli.torc import cli
from torc.cli.collections import JOIN_COLLECTIONS
from torc.common import STATS_DIR


def test_workflow_commands(create_workflow_cli):
    """Tests workflow CLI commands."""
    key, url, output_dir = create_workflow_cli
    hostname = socket.gethostname()
    runner = CliRunner()
    result = runner.invoke(cli, ["-n", "-k", key, "-u", url, "workflows", "start"])
    assert result.exit_code == 0

    result = runner.invoke(
        cli, ["-k", key, "-u", url, "jobs", "run", "-o", str(output_dir), "-p", "1"]
    )
    assert result.exit_code == 0
    result = runner.invoke(
        cli, ["-k", key, "-u", url, "reports", "results", "-o", str(output_dir)]
    )
    assert result.exit_code == 0
    output = _get_text_and_json_outputs(["-k", key, "-u", url, "jobs", "list-process-stats"])
    assert output["json"]["stats"]
    assert all(x in output["text"] for x in ("max_cpu_percent", "max_memory_gb"))

    output = _get_text_and_json_outputs(
        ["-k", key, "-u", url, "compute-nodes", "list-resource-stats"]
    )
    assert output["json"]["stats"]
    expected = [hostname, "resource_type", "percent", "memory", "cpu", "process"]
    assert all(x in output["text"] for x in expected)

    expected.remove("process")
    output = _get_text_and_json_outputs(
        ["-k", key, "-u", url, "compute-nodes", "list-resource-stats", "-x"]
    )
    assert output["json"]["stats"]
    assert all(x in output["text"] for x in expected)

    output = _get_text_and_json_outputs(["-k", key, "-u", url, "results", "list"])
    assert output["json"]["results"]
    assert all(x in output["text"] for x in ("job_key", "return_code"))

    result = runner.invoke(
        cli,
        [
            "-k",
            key,
            "-u",
            url,
            "-n",
            "results",
            "delete",
        ],
    )
    assert result.exit_code == 0
    output = _get_text_and_json_outputs(["-k", key, "-u", url, "results", "list"])
    assert not output["json"]["results"]

    events = _run_and_convert_output_from_json(
        ["-k", key, "-u", url, "-F", "json", "events", "list"]
    )
    assert isinstance(events, list) and events
    data = _run_and_convert_output_from_json(
        [
            "-k",
            key,
            "-u",
            url,
            "-F",
            "json",
            "events",
            "get-latest-event-timestamp",
        ]
    )
    assert "timestamp" in data
    _run_and_convert_output_from_json(
        [
            "-k",
            key,
            "-u",
            url,
            "-F",
            "json",
            "jobs",
            "list",
            "--sort-by",
            "name",
            "--reverse-sort",
        ]
    )

    # Test filtering on the collections join command.
    items = [
        x["to"]["name"]
        for x in _run_and_convert_output_from_json(
            [
                "-k",
                key,
                "-u",
                url,
                "-F",
                "json",
                "collections",
                "join",
                "job-requirements",
                "-f",
                "name=small",
            ]
        )["items"]
    ]
    assert items and all(x == "small" for x in items)

    for name in JOIN_COLLECTIONS:
        _get_text_and_json_outputs(["-k", key, "-u", url, "collections", "join", name])

    stats_dir = output_dir / STATS_DIR
    stats_files = [
        x
        for x in stats_dir.iterdir()
        if x.name.startswith("compute_node") and x.suffix == ".sqlite"
    ]
    assert len(stats_files) == 1
    # Create a copy to exercise the union code.
    shutil.copyfile(stats_files[0], stats_dir / "compute_node_123.sqlite")
    result = runner.invoke(cli, ["stats", "concatenate-process", str(stats_dir)])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["-n", "-u", url, "workflows", "reset-status", key])
    assert result.exit_code == 0

    cmd = ["-k", key, "-u", url, "-F", "json", "jobs", "list"]
    jobs = _run_and_convert_output_from_json(cmd)["jobs"]
    for job in jobs:
        assert job["status"] == "uninitialized"

    cmd = ["-k", key, "-u", url, "-F", "json", "workflows", "show"]
    result = runner.invoke(cli, cmd)
    assert result.exit_code == 0
    cmd = ["-k", key, "-u", url, "-F", "json", "workflows", "show-config"]
    result = runner.invoke(cli, cmd)
    assert result.exit_code == 0
    cmd = ["-k", key, "-u", url, "-F", "json", "workflows", "show-status"]
    result = runner.invoke(cli, cmd)
    assert result.exit_code == 0
    cmd = [
        "-k",
        key,
        "-u",
        url,
        "workflows",
        "set-compute-node-parameters",
        "-e",
        "90",
        "-h",
        "12",
        "-i",
        "true",
        "-w",
        "6",
    ]
    result = runner.invoke(cli, cmd)
    assert result.exit_code == 0


def test_reset_job_status(create_workflow_cli):
    """Tests workflow CLI commands."""
    key, url, output_dir = create_workflow_cli
    runner = CliRunner()
    result = runner.invoke(cli, ["-n", "-k", key, "-u", url, "workflows", "start"])
    assert result.exit_code == 0

    result = runner.invoke(
        cli, ["-k", key, "-u", url, "jobs", "run", "-o", str(output_dir), "-p", "1"]
    )
    assert result.exit_code == 0

    cmd = ["-k", key, "-u", url, "-F", "json", "jobs", "list"]
    jobs = _run_and_convert_output_from_json(cmd)["jobs"]
    assert len(jobs) == 3
    job_keys: list[str] = []
    for job in jobs:
        assert job["status"] == "done"
        job_keys.append(job["_key"])

    result = runner.invoke(cli, ["-n", "-k", key, "-u", url, "jobs", "reset-status"] + job_keys)
    assert result.exit_code == 0

    cmd = ["-k", key, "-u", url, "-F", "json", "jobs", "list"]
    jobs = _run_and_convert_output_from_json(cmd)["jobs"]
    assert len(jobs) == 3
    for job in jobs:
        assert job["status"] == "uninitialized"

    cmd = ["-n", "-k", key, "-u", url, "-F", "json", "jobs", "disable"] + job_keys
    result = runner.invoke(cli, cmd)
    assert result.exit_code == 0

    cmd = ["-k", key, "-u", url, "-F", "json", "jobs", "list"]
    jobs = _run_and_convert_output_from_json(cmd)["jobs"]
    assert len(jobs) == 3
    for job in jobs:
        assert job["status"] == "disabled"


def test_resource_requirement_commands(create_workflow_cli):
    """Tests resource requirement CLI commands."""
    key, url, _ = create_workflow_cli
    output = _run_and_convert_output_from_json(
        ["-F", "json", "-k", key, "-u", url, "resource-requirements", "list"]
    )
    assert output["resource_requirements"]

    output_assignments = _run_and_convert_output_from_json(
        [
            "-F",
            "json",
            "-k",
            key,
            "-u",
            url,
            "resource-requirements",
            "add",
            "-n",
            "medium",
            "-c",
            "4",
            "-m",
            "5g",
            "-r",
            "P0DT1H",
            "-a",
        ]
    )
    rr_key = output_assignments["key"]

    def check_expected_rr_key(rr_key):
        output_list = _run_and_convert_output_from_json(
            [
                "-F",
                "json",
                "-k",
                key,
                "-u",
                url,
                "collections",
                "join",
                "job-requirements",
            ]
        )
        assert output_list["items"]
        for item in output_list["items"]:
            assert item["to"]["_key"] == rr_key
        return output_list["items"]

    check_expected_rr_key(rr_key)

    new_rr = _run_and_convert_output_from_json(
        [
            "-F",
            "json",
            "-k",
            key,
            "-u",
            url,
            "resource-requirements",
            "add",
            "-n",
            "large",
            "-c",
            "16",
            "-m",
            "60g",
            "-r",
            "P0DT12H",
        ]
    )
    # The jobs shouldn't have changed requirements.
    joined_items = check_expected_rr_key(rr_key)
    job_keys = [x["from"]["_key"] for x in joined_items]
    output_assignments = _run_and_convert_output_from_json(
        [
            "-F",
            "json",
            "-k",
            key,
            "-u",
            url,
            "jobs",
            "assign-resource-requirements",
            new_rr["key"],
        ]
        + job_keys
    )
    check_expected_rr_key(new_rr["key"])

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-F",
            "json",
            "-k",
            key,
            "-u",
            url,
            "resource-requirements",
            "modify",
            new_rr["key"],
            "-c",
            "36",
            "-r",
            "P0DT24H",
        ],
    )
    assert result.exit_code == 0
    for item in check_expected_rr_key(new_rr["key"]):
        assert item["to"]["num_cpus"] == 36
        assert item["to"]["runtime"] == "P0DT24H"

    result = runner.invoke(
        cli,
        [
            "-F",
            "json",
            "-k",
            key,
            "-u",
            url,
            "resource-requirements",
            "delete",
            new_rr["key"],
        ],
    )
    assert result.exit_code == 0


@pytest.mark.parametrize("memory_per_job", ["10g", "50g"])
def test_slurm_recommend_nodes(db_api, tmp_path, memory_per_job):
    """Tests slurm config CLI commands."""
    api, url = db_api
    commands_file = tmp_path / "commands.txt"
    with open(commands_file, "w", encoding="utf-8") as f_out:
        for _ in range(1000):
            f_out.write("echo hello\n")

    runner = CliRunner()
    key = None
    try:
        cmd = [
            "-u",
            url,
            "-F",
            "json",
            "workflows",
            "create-from-commands-file",
            "--cpus-per-job=8",
            "--memory-per-job",
            memory_per_job,
            "--runtime-per-job=P0DT1H",
            str(commands_file),
        ]
        result = _run_and_convert_output_from_json(cmd)
        key = result["key"]
        assert (
            runner.invoke(
                cli,
                [
                    "-u",
                    url,
                    "-k",
                    key,
                    "workflows",
                    "start",
                ],
            ).exit_code
            == 0
        )
        assert (
            runner.invoke(
                cli,
                [
                    "-u",
                    url,
                    "-k",
                    key,
                    "hpc",
                    "slurm",
                    "add-config",
                    "--account=my_account",
                    "--name=short",
                    "--mem=240G",
                    "--walltime=04:00:00",
                ],
            ).exit_code
            == 0
        )

        output = _run_and_convert_output_from_json(
            [
                "-F",
                "json",
                "-k",
                key,
                "-u",
                url,
                "hpc",
                "slurm",
                "recommend-nodes",
                "-c",
                "104",
                "-m",
                "240",
            ]
        )
        job_rounds_by_duration = 4
        match memory_per_job:
            case "10g":
                one_node_jobs = math.floor(104 / 8 * job_rounds_by_duration)
                assert output["num_nodes"] == math.ceil(1000 / one_node_jobs)
                assert output["details"]["limiter"] == "CPU"
            case "50g":
                one_node_jobs = math.floor(240 / 50 * job_rounds_by_duration)
                num_nodes = math.ceil(1000 / one_node_jobs)
                assert output["num_nodes"] == num_nodes
                assert output["details"]["limiter"] == "memory"
            case _:
                assert False, f"Unexpected memory_per_job: {memory_per_job}"
        runner.invoke(cli, ["-k", key, "-u", url, "workflows", "list-scheduler-configs"])
    finally:
        if key is not None:
            api.remove_workflow(key)


def test_create_workflow_from_commands_file(db_api, tmp_path):
    """Tests creation of a workflow from a commands file."""
    api, url = db_api
    commands_file = tmp_path / "commands.txt"
    with open(commands_file, "w", encoding="utf-8") as f_out:
        for _ in range(5):
            f_out.write("echo hello\n")

    key = None
    try:
        cmd = [
            "-u",
            url,
            "-F",
            "json",
            "workflows",
            "create-from-commands-file",
            str(commands_file),
        ]
        result = _run_and_convert_output_from_json(cmd)
        key = result["key"]
        jobs = api.list_jobs(key).items
        assert len(jobs) == 5
        assert jobs[0].command == "echo hello"

        cmd = [
            "-u",
            url,
            "-k",
            key,
            "-F",
            "json",
            "workflows",
            "add-jobs-from-commands-file",
            str(commands_file),
        ]
        result = _run_and_convert_output_from_json(cmd)
        assert result["key"] == key
        assert result["num_jobs"] == 5
        jobs = api.list_jobs(key).items
        assert len(jobs) == 10
    finally:
        if key is not None:
            api.remove_workflow(key)


def test_create_empty_workflow(db_api):
    """Tests creation of an empty workflow."""
    api, url = db_api
    key = None
    try:
        cmd = ["-u", url, "-F", "json", "workflows", "create"]
        result = _run_and_convert_output_from_json(cmd)
        key = result["key"]
        jobs = api.list_jobs(key).items
        assert len(jobs) == 0
    finally:
        if key is not None:
            api.remove_workflow(key)


def test_multi_user_workflows(create_workflow_cli):
    """Test workflow commands with multiple users."""
    key, url, _ = create_workflow_cli
    cmd_user1 = ["-u", url, "-U", getpass.getuser(), "-F", "json", "workflows", "list"]
    result1_user1 = _run_and_convert_output_from_json(cmd_user1)
    assert len(list(filter(lambda x: x["_key"] == key, result1_user1["workflows"]))) == 1
    key2 = _create_workflow_example(url, "user2")
    cmd_user2 = ["-u", url, "-U", "user2", "-F", "json", "workflows", "list"]
    result_user2 = _run_and_convert_output_from_json(cmd_user2)
    assert len(result_user2["workflows"]) == 1
    assert result_user2["workflows"][0]["_key"] == key2
    result2_user1 = _run_and_convert_output_from_json(cmd_user1)
    assert len(result2_user1["workflows"]) == len(result1_user1["workflows"])

    # There should only be one workflow for this user, and so no prompts should occur.
    os.environ.pop("TORC_WORKFLOW_KEY", None)
    cmd = ["-u", url, "-U", "user2", "-F", "json", "jobs", "list"]
    result = _run_and_convert_output_from_json(cmd)
    assert result["jobs"]


def test_archived_workflows(create_workflow_cli):
    """Test workflow commands with multiple users."""
    key, url, _ = create_workflow_cli

    def found_my_workflow(cmd):
        result = _run_and_convert_output_from_json(cmd)
        my_workflows = list(filter(lambda x: x["_key"] == key, result["workflows"]))
        return len(my_workflows) == 1

    assert found_my_workflow(["-u", url, "-F", "json", "workflows", "list"])
    assert not found_my_workflow(["-u", url, "-F", "json", "workflows", "list", "--only-archived"])

    _run_and_get_output(["-u", url, "workflows", "modify", "--archive", "true", key])

    assert not found_my_workflow(["-u", url, "-F", "json", "workflows", "list"])
    assert found_my_workflow(["-u", url, "-F", "json", "workflows", "list", "--only-archived"])

    runner = CliRunner()
    result = runner.invoke(cli, ["-k", key, "-u", url, "workflows", "start"])
    assert result.exit_code != 0
    assert "Not allowed on an archived workflow" in str(result.exception)

    _run_and_get_output(["-u", url, "workflows", "modify", "--archive", "false", key])
    assert found_my_workflow(["-u", url, "-F", "json", "workflows", "list"])


def test_workflow_template(db_api):
    """Tests the dump of the workflow template."""
    _, url = db_api
    cmd = ["-u", url, "-F", "json", "workflows", "template"]
    result = _run_and_convert_output_from_json(cmd)
    assert "name" in result
    assert "jobs" in result


def test_job_commands(create_workflow_cli):
    """Tests job CLI commands."""
    key, url, _ = create_workflow_cli
    cmd = [
        "-k",
        key,
        "-u",
        url,
        "-F",
        "json",
        "jobs",
        "add",
        "-c",
        "'bash my_script.sh'",
        "-n",
        "new_job",
    ]
    result = _run_and_convert_output_from_json(cmd)
    job_key = result["key"]

    _run_and_check_jobs_list_output(["-k", key, "-u", url, "-F", "json", "jobs", "list"], 4)

    user_data = {"key1": "val1"}
    cmd = [
        "-k",
        key,
        "-u",
        url,
        "-F",
        "json",
        "user-data",
        "add",
        "-n",
        "my-output",
        "-s",
        job_key,
        "-d",
        f"{json.dumps(user_data)}",
    ]
    result = _run_and_convert_output_from_json(cmd)
    ud_key = result["key"]
    _run_and_check_output(
        ["-k", key, "-u", url, "jobs", "list-user-data", job_key], ("key1", "val1")
    )
    _run_and_check_output(["-k", key, "-u", url, "user-data", "get", ud_key], ("key1", "val1"))
    _run_and_check_output(["-k", key, "-u", url, "user-data", "list"], ("key1", "val1"))
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-n",
            "-k",
            key,
            "-u",
            url,
            "user-data",
            "modify",
            ud_key,
            "-d",
            json.dumps({"key2": "val2"}),
        ],
    )
    assert result.exit_code == 0
    result = runner.invoke(cli, ["-n", "-k", key, "-u", url, "user-data", "delete", ud_key])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["-n", "-k", key, "-u", url, "jobs", "delete", job_key])
    assert result.exit_code == 0
    _run_and_check_jobs_list_output(["-k", key, "-u", url, "-F", "json", "jobs", "list"], 3)
    _run_and_check_jobs_list_output(
        [
            "-k",
            key,
            "-u",
            url,
            "-F",
            "json",
            "jobs",
            "list",
            "-f",
            "name=medium",
        ],
        1,
    )
    result = runner.invoke(cli, ["-n", "-k", key, "-u", url, "jobs", "delete-all"])
    assert result.exit_code == 0
    _run_and_check_jobs_list_output(
        [
            "-k",
            key,
            "-u",
            url,
            "-F",
            "json",
            "jobs",
            "list",
            "-f",
            "name=medium",
        ],
        0,
    )


def test_collections_list_command(create_workflow_cli):
    """Tests collections list CLI commands."""
    key, url, _ = create_workflow_cli
    names = _run_and_convert_output_from_json(
        ["-k", key, "-u", url, "-F", "json", "collections", "list"]
    )["names"]
    assert set(("files", "events", "jobs", "needs")).issubset(set(names))


def test_files_commands(create_workflow_cli):
    """Tests collections list CLI commands."""
    key, url, tmp_path = create_workflow_cli
    filename = tmp_path / "data.txt"
    filename.touch()
    key = _run_and_convert_output_from_json(
        ["-k", key, "-u", url, "-F", "json", "files", "add", "-n", "myfile", "-p", str(filename)]
    )["key"]
    runner = CliRunner()
    runner.invoke(cli, ["-k", key, "-u", url, "files", "delete", key])


def _run_and_check_output(cmd, expected_strings):
    output = _run_and_get_output(cmd)
    assert all(x in output for x in expected_strings)


def _run_and_check_jobs_list_output(cmd, num_expected_jobs):
    jobs = _run_and_convert_output_from_json(cmd)["jobs"]
    assert len(jobs) == num_expected_jobs


def _run_and_get_output(cmd):
    runner = CliRunner()
    result = runner.invoke(cli, cmd)
    assert result.exit_code == 0
    return result.stdout


def _run_and_convert_output_from_json(cmd):
    return json.loads(_run_and_get_output(cmd))


def _create_workflow_example(url, user=getpass.getuser()):
    """Tests the dump of the example workflow."""
    cmd = ["-u", url, "-F", "json", "workflows", "example"]
    result = _run_and_convert_output_from_json(cmd)
    assert len(result["jobs"])
    with tempfile.NamedTemporaryFile() as f:
        f.close()
        Path(f.name).write_text(json.dumps(result), encoding="utf-8")
        cmd = ["-u", url, "-U", user, "-F", "json", "workflows", "create-from-json-file", f.name]
        result = _run_and_convert_output_from_json(cmd)
        return result["key"]


def _get_text_and_json_outputs(cmd):
    cmd_text = cmd[:]
    cmd_json = cmd[:]
    cmd_text.insert(0, "-F")
    cmd_json.insert(0, "-F")
    cmd_text.insert(1, "text")
    cmd_json.insert(1, "json")
    return {
        "text": _run_and_get_output(cmd_text),
        "json": _run_and_convert_output_from_json(cmd_json),
    }
