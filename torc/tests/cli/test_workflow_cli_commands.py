"""Tests the workflow CLI commands."""

import json
import re
import socket

from click.testing import CliRunner

from torc.cli.torc import cli


WORKFLOW_KEY_REGEX = re.compile(r"with key=(\d+)\s")


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
        "jobs",
        "add-user-data",
        job_key,
        f"'{json.dumps(user_data)}'",
    ]
    result = _run_and_convert_output_from_json(cmd)
    ud_key = result["keys"][0]
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
