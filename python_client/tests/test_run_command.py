"""Tests run_command"""

from typing import Any

from torc.utils.run_command import check_run_command, run_command


def test_run_command_good():
    """Test nominal case for run_command/check_run_command"""
    cmd = "torc --help"
    check_run_command(cmd)

    output: dict[str, Any] = {}
    check_run_command(cmd, output=output)
    assert "Job commands" in output["stdout"]


def test_run_command_retries():
    """Test run_command with command retries"""
    cmd = "torc --invalid"
    output: dict[str, Any] = {}
    ret = run_command(cmd, num_retries=3, retry_delay_s=0.1, output=output)
    assert ret != 0
    output = {}
    ret = run_command(
        cmd, num_retries=3, retry_delay_s=0.1, error_strings=("No such option",), output=output
    )
