"""Tests the workflow CLI commands."""

import re
import socket

from torc.utils.run_command import check_run_command


def test_workflow_commands(import_workflow_cli):
    """Tests workflow CLI commands."""
    key, url, output_dir = import_workflow_cli
    hostname = socket.gethostname()
    check_run_command(f"torc -u {url} workflows start {key}")
    check_run_command(f"torc -u {url} local run-jobs {key} -o {output_dir}")
    _run_and_check_output(
        f"torc -u {url} show process-stats {key}",
        ("max_cpu_percent", "max_memory_gb"),
    )
    _run_and_check_output(
        f"torc -u {url} show resource-stats {key}",
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
        f"torc -u {url} show resource-stats {key} -x",
        (hostname, "resource_type", "percent", "Memory", "CPU"),
    )
    _run_and_check_output(f"torc -u {url} show results {key}", ("job_key", "return_code"))


def test_job_commands(import_workflow_cli):
    """Tests job CLI commands."""
    key, url, _ = import_workflow_cli
    add_key_regex = re.compile(r"Added job with key=(\d+)\s")
    _run_and_check_jobs_list_output(f"torc -u {url} jobs {key} list", 3)

    output = {}
    check_run_command(
        f"torc -u {url} jobs {key} add -c 'bash my_script.sh' -n new_job", output=output
    )
    match = add_key_regex.search(output["stderr"])
    assert match
    job_key = match.group(1)

    _run_and_check_jobs_list_output(f"torc -u {url} jobs {key} list", 4)
    check_run_command(f"torc -u {url} jobs {key} delete {job_key}")
    _run_and_check_jobs_list_output(f"torc -u {url} jobs {key} list", 3)
    _run_and_check_jobs_list_output(f"torc -u {url} jobs {key} list -f name=medium -f run_id=0", 1)
    check_run_command(f"torc -u {url} jobs {key} delete-all")
    _run_and_check_jobs_list_output(
        f"torc -u {url} jobs {key} list -f name=medium -f run_id=0", None
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
