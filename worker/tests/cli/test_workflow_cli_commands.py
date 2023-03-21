"""Tests the workflow CLI commands."""

import socket
from pathlib import Path

from wms.utils.run_command import check_run_command


def test_workflow_cli_commands(tmp_path):
    """Tests CLI commands."""
    file = Path(__file__).parent.parent.parent.parent / "examples" / "independent_workflow.json5"
    url = "http://localhost:8529/_db/workflows/wms-service"
    hostname = socket.gethostname()
    check_run_command(f"wms -u {url} workflow delete")
    try:
        check_run_command(f"wms -u {url} workflow import {file}")
        _run_and_check_output(f"wms -u {url} show jobs", ("small", "medium", "large", "status"))
        check_run_command(f"wms -u {url} workflow start")
        check_run_command(f"wms -u {url} local run-jobs -o {tmp_path}")
        _run_and_check_output(
            f"wms -u {url} show process-stats",
            ("small", "medium", "large", "max_cpu_percent", "max_memory_gb"),
        )
        _run_and_check_output(
            f"wms -u {url} show resource-stats",
            (
                hostname,
                "resource_type",
                "percent",
                "Memory",
                "CPU",
                "Process",
                "small",
                "medium",
                "large",
            ),
        )
        _run_and_check_output(
            f"wms -u {url} show resource-stats -x",
            (hostname, "resource_type", "percent", "Memory", "CPU"),
        )
        _run_and_check_output(
            f"wms -u {url} show results", ("small", "medium", "large", "return_code")
        )
    finally:
        check_run_command(f"wms -u {url} workflow delete")


def _run_and_check_output(cmd, expected_strings):
    output = {}
    check_run_command(cmd, output=output)
    for string in expected_strings:
        assert string in output["stdout"]
