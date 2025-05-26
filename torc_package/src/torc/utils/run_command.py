"""Utility functions to run commands through the system"""

import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable

from loguru import logger

from torc.exceptions import ExecutionError


def run_command(
    cmd: str,
    output: dict[str, Any] | None = None,
    cwd: str | None = None,
    num_retries: int = 0,
    retry_delay_s: float = 2.0,
    error_strings: Iterable[str] | None = None,
    **kwargs,
) -> int:
    """Runs a command as a subprocess.

    Parameters
    ----------
    cmd
        command to run
    output
        If a dict is passed then return stdout and stderr as keys.
    cwd
        Change the working directory to cwd before executing the process.
    num_retries
        Retry the command on failure this number of times.
        Return code and output are from the last command execution.
    retry_delay_s
        Number of seconds to delay in between retries.
    error_strings
        Skip retries for these known error strings. Requires output to be set.
    kwargs
        Keyword arguments to forward to the subprocess module.

    Returns
    -------
    int
        return code from system; usually zero is good, non-zero is error

    Caution: Capturing stdout and stderr in memory can be hazardous with
    long-running processes that output lots of text. In those cases consider
    running subprocess.Popen with stdout and/or stderr set to a pre-configured
    file descriptor.
    """
    if error_strings and output is None:
        msg = "output must be set if error_strings are passed"
        raise ValueError(msg)

    cmd = str(cmd) if isinstance(cmd, Path) else cmd
    logger.trace(cmd)
    # Disable posix if on Windows.
    command = shlex.split(cmd, posix="win" not in sys.platform)
    max_tries = num_retries + 1
    assert max_tries >= 1
    ret = 1
    for i in range(max_tries):
        _output: dict[str, Any] | None = {} if isinstance(output, dict) else None
        ret = _run_command(command, _output, cwd, **kwargs)
        if ret != 0 and num_retries > 0:
            if _output:
                if _should_exit_early(_output["stderr"], error_strings or []):
                    i = max_tries - 1
                else:
                    logger.warning(
                        "Command [{}] failed on iteration {}: {}: {}",
                        cmd,
                        i + 1,
                        ret,
                        _output["stderr"],
                    )
            else:
                logger.warning("Command [{}] failed on iteration {}: {}", cmd, i + 1, ret)
        if ret == 0 or i == max_tries - 1:
            if isinstance(output, dict):
                assert _output is not None
                output.update(_output)
            break
        time.sleep(retry_delay_s)

    return ret


def _should_exit_early(std_err: str, error_strings: Iterable[str]) -> bool:
    for err in error_strings:
        if err in std_err:
            return True
    return False


def _run_command(
    command: list[str], output: dict[str, Any] | None, cwd: str | None, **kwargs
) -> int:
    if output is not None:
        result = subprocess.run(
            command,
            capture_output=True,
            cwd=cwd,
            check=False,
            **kwargs,
        )
        output["stdout"] = result.stdout.decode("utf-8")
        output["stderr"] = result.stderr.decode("utf-8")
        ret = result.returncode
    else:
        ret = subprocess.call(command, cwd=cwd, **kwargs)

    return ret


def check_run_command(*args, **kwargs) -> None:
    """Same as run_command except that it raises an exception on failure.

    Raises
    ------
    ExecutionError
        Raised if the command returns a non-zero return code.
    """
    ret = run_command(*args, **kwargs)
    if ret != 0:
        msg = f"command returned error code: {ret}"
        raise ExecutionError(msg)


def get_cli_string() -> str:
    """Return the command-line arguments issued.

    Returns
    -------
    str

    """
    return os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:])
