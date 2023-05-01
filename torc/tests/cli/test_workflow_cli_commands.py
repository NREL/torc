"""Tests the workflow CLI commands."""

import json
import shutil
import socket
import tempfile
from pathlib import Path

from click.testing import CliRunner

from torc.cli.torc import cli
from torc.cli.collections import JOIN_COLLECTIONS
from torc.common import STATS_DIR


def test_workflow_commands(create_workflow_cli):
    """Tests workflow CLI commands."""
    key, url, output_dir = create_workflow_cli
    hostname = socket.gethostname()
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli, ["-k", key, "-u", url, "workflows", "start"])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["-k", key, "-u", url, "local", "run-jobs", "-o", str(output_dir)])
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
    assert all(x in output["text"] for x in ("job_key", "return_code"))

    events = _run_and_convert_output_from_json(
        ["-k", key, "-u", url, "-F", "json", "events", "list"]
    )
    assert isinstance(events, list) and events
    job_key = _run_and_convert_output_from_json(
        ["-k", key, "-u", url, "-F", "json", "jobs", "list"]
    )["jobs"][0]["key"]
    # Test filtering on the collections join command.
    assert (
        _run_and_convert_output_from_json(
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
                f"key={job_key}",
            ]
        )["items"][0]["to"]["name"]
        == "small"
    )

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

    result = runner.invoke(cli, ["-k", key, "-u", url, "workflows", "reset-status"])
    assert result.exit_code == 0


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

    runner = CliRunner(mix_stderr=False)
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


def test_slurm_config_commands(create_workflow_cli):
    """Tests slurm config CLI commands."""
    key, url, _ = create_workflow_cli
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli, ["-k", key, "-u", url, "workflows", "start"])
    assert result.exit_code == 0
    output = _run_and_convert_output_from_json(
        ["-F", "json", "-k", key, "-u", url, "workflows", "list-scheduler-configs"]
    )
    assert output["ids"]
    scheduler_id = output["ids"][0]
    output = _run_and_convert_output_from_json(
        [
            "-F",
            "json",
            "-k",
            key,
            "-u",
            url,
            "workflows",
            "recommend-nodes",
            "-s",
            scheduler_id,
        ]
    )
    assert output["num_nodes_by_cpus"] == 1

    output = _run_and_convert_output_from_json(
        ["-F", "json", "-k", key, "-u", url, "hpc", "slurm", "list-configs"]
    )

    assert output["configs"]
    assert output["configs"][0]["id"] == scheduler_id
    assert output["configs"][0]["walltime"] == "04:00:00"
    config_key = output["configs"][0]["key"]

    new_walltime = "02:00:00"
    result = runner.invoke(
        cli,
        [
            "-k",
            key,
            "-u",
            url,
            "hpc",
            "slurm",
            "modify-config",
            config_key,
            "-w",
            new_walltime,
        ],
    )
    assert result.exit_code == 0

    output = _run_and_convert_output_from_json(
        ["-F", "json", "-k", key, "-u", url, "hpc", "slurm", "list-configs"]
    )
    assert output["configs"]
    assert output["configs"][0]["walltime"] == new_walltime


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
        jobs = api.get_workflows_workflow_jobs(key).items
        assert len(jobs) == 5
        assert jobs[0].command == "echo hello"
    finally:
        if key is not None:
            api.delete_workflows_key(key)


def test_create_empty_workflow(db_api):
    """Tests creation of an empty workflow."""
    api, url = db_api
    key = None
    try:
        cmd = ["-u", url, "-F", "json", "workflows", "create"]
        result = _run_and_convert_output_from_json(cmd)
        key = result["key"]
        jobs = api.get_workflows_workflow_jobs(key).items
        assert len(jobs) == 0
    finally:
        if key is not None:
            api.delete_workflows_key(key)


def test_workflow_example(db_api):
    """Tests the dump of the example workflow."""
    _, url = db_api
    cmd = ["-u", url, "-F", "json", "workflows", "example"]
    result = _run_and_convert_output_from_json(cmd)
    assert len(result["jobs"])
    with tempfile.NamedTemporaryFile() as f:
        f.close()
        Path(f.name).write_text(json.dumps(result), encoding="utf-8")
        cmd = ["-u", url, "workflows", "create-from-json-file", f.name]
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli, cmd)
        assert result.exit_code == 0


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
    _run_and_check_jobs_list_output(["-k", key, "-u", url, "-F", "json", "jobs", "list"], 3)

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
        f"'{json.dumps(user_data)}'",
    ]
    result = _run_and_convert_output_from_json(cmd)
    ud_key = result["key"]
    _run_and_check_output(
        ["-k", key, "-u", url, "jobs", "list-user-data", job_key], ("key1", "val1")
    )
    _run_and_check_output(["-k", key, "-u", url, "user-data", "get", ud_key], ("key1", "val1"))
    _run_and_check_output(["-k", key, "-u", url, "user-data", "list"], ("key1", "val1"))
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli, ["-k", key, "-u", url, "user-data", "delete", ud_key])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["-k", key, "-u", url, "jobs", "delete", job_key])
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
            "-f",
            "run_id=0",
        ],
        1,
    )
    result = runner.invoke(cli, ["-k", key, "-u", url, "jobs", "delete-all"])
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
            "-f",
            "run_id=0",
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


def _run_and_check_output(cmd, expected_strings):
    output = _run_and_get_output(cmd)
    assert all(x in output for x in expected_strings)


def _run_and_check_jobs_list_output(cmd, num_expected_jobs):
    jobs = _run_and_convert_output_from_json(cmd)["jobs"]
    assert len(jobs) == num_expected_jobs


def _run_and_get_output(cmd):
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli, cmd)
    assert result.exit_code == 0
    return result.stdout


def _run_and_convert_output_from_json(cmd):
    return json.loads(_run_and_get_output(cmd))


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
