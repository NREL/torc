"""Tests the workflow CLI commands."""

import json
import re
import socket

from torc.utils.run_command import check_run_command


WORKFLOW_KEY_REGEX = re.compile(r"with key=(\d+)\s")


def test_workflow_commands(create_workflow_cli):
    """Tests workflow CLI commands."""
    key, url, output_dir = create_workflow_cli
    hostname = socket.gethostname()
    check_run_command(f"torc -k {key} -u {url} workflows start")
    check_run_command(f"torc -k {key} -u {url} local run-jobs -o {output_dir}")
    _run_and_check_output(
        f"torc -k {key} -u {url} jobs list-process-stats",
        ("max_cpu_percent", "max_memory_gb"),
    )
    _run_and_check_output(
        f"torc -k {key} -u {url} compute-nodes list-resource-stats",
        (
            hostname,
            "resource_type",
            "percent",
            "Memory",
            "CPU",
            "Process",
        ),
    )
    _run_and_check_output(
        f"torc -k {key} -u {url} compute-nodes list-resource-stats -x",
        (hostname, "resource_type", "percent", "Memory", "CPU"),
    )
    _run_and_check_output(f"torc -k {key} -u {url} results list", ("job_key", "return_code"))
    output = {}
    check_run_command(f"torc -k {key} -u {url} events list", output=output)
    data = json.loads(output["stdout"])
    assert isinstance(data, list) and data


def test_create_workflow_from_commands_file(db_api, tmp_path):
    """Tests creation of a workflow from a commands file."""
    api, url = db_api
    commands_file = tmp_path / "commands.txt"
    with open(commands_file, "w", encoding="utf-8") as f_out:
        for _ in range(5):
            f_out.write("echo hello\n")

    key = None
    try:
        output = {}
        check_run_command(
            f"torc -u {url} workflows create-from-commands-file {commands_file}",
            output=output,
        )
        match = WORKFLOW_KEY_REGEX.search(output["stderr"])
        assert match
        key = match.group(1)
        jobs = api.get_jobs_workflow(key).items
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
        output = {}
        check_run_command(f"torc -u {url} workflows create", output=output)
        match = WORKFLOW_KEY_REGEX.search(output["stderr"])
        assert match
        key = match.group(1)
        jobs = api.get_jobs_workflow(key).items
        assert len(jobs) == 0
    finally:
        if key is not None:
            api.delete_workflows_key(key)


def test_job_commands(create_workflow_cli):
    """Tests job CLI commands."""
    key, url, _ = create_workflow_cli
    add_key_regex = re.compile(r"Added job with key=(\d+)\s")
    _run_and_check_jobs_list_output(f"torc -k {key} -u {url} jobs list", 3)

    output = {}
    check_run_command(
        f"torc -k {key} -u {url} jobs add -c 'bash my_script.sh' -n new_job",
        output=output,
    )
    match = add_key_regex.search(output["stderr"])
    assert match
    job_key = match.group(1)

    _run_and_check_jobs_list_output(f"torc -k {key} -u {url} jobs list", 4)
    check_run_command(f"torc -k {key} -u {url} jobs delete {job_key}")
    _run_and_check_jobs_list_output(f"torc -k {key} -u {url} jobs list", 3)
    _run_and_check_jobs_list_output(
        f"torc -k {key} -u {url} jobs list -f name=medium -f run_id=0", 1
    )
    check_run_command(f"torc -k {key} -u {url} jobs delete-all")
    _run_and_check_jobs_list_output(
        f"torc -k {key} -u {url} jobs list -f name=medium -f run_id=0", None
    )


def _run_and_check_output(cmd, expected_strings):
    output = {}
    check_run_command(cmd, output=output)
    for string in expected_strings:
        assert string in output["stdout"]


def _run_and_check_jobs_list_output(cmd, expected_jobs):
    num_lines_for_headers = 6
    output = {}
    check_run_command(cmd, output=output)
    lines = output["stdout"].strip().split("\n")
    if expected_jobs is None:
        assert len(lines) == 1
    else:
        assert len(lines) - num_lines_for_headers == expected_jobs
