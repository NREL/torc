"""Utility functions to run commands through the system"""

import logging
import os
import shlex
import subprocess
import sys
import time

from wms.exceptions import ExecutionError


logger = logging.getLogger(__name__)


def run_command(
    cmd,
    output=None,
    cwd=None,
    num_retries=0,
    retry_delay_s=2.0,
    error_strings=None,
    **kwargs,
):
    """Runs a command as a subprocess.

    Parameters
    ----------
    cmd : str
        command to run
    output : dict, default=None
        If a dict is passed then return stdout and stderr as keys.
    cwd : str, default=None
        Change the working directory to cwd before executing the process.
    num_retries : int, default=0
        Retry the command on failure this number of times.
        Return code and output are from the last command execution.
    retry_delay_s : float, default=2.0
        Number of seconds to delay in between retries.
    error_strings : None | str
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
        raise ValueError("output must be set if error_strings are passed")
    if error_strings is None:
        error_strings = []

    if not isinstance(cmd, str):
        # Handle pathlib.Path.
        cmd = str(cmd)
    logger.debug(cmd)
    # Disable posix if on Windows.
    command = shlex.split(cmd, posix="win" not in sys.platform)
    max_tries = num_retries + 1
    assert max_tries >= 1
    ret = None
    for i in range(max_tries):
        _output = {} if isinstance(output, dict) else None
        ret = _run_command(command, _output, cwd, **kwargs)
        if ret != 0 and num_retries > 0:
            if _output:
                if _should_exit_early(_output["stderr"], error_strings):
                    i = max_tries - 1
                else:
                    logger.warning(
                        "Command [%s] failed on iteration %s: %s: %s",
                        cmd,
                        i + 1,
                        ret,
                        _output["stderr"],
                    )
            else:
                logger.warning("Command [%s] failed on iteration %s: %s", cmd, i + 1, ret)
        if ret == 0 or i == max_tries - 1:
            if isinstance(output, dict):
                output.update(_output)
            break
        time.sleep(retry_delay_s)

    if ret != 0:
        logger.debug("Command [%s] failed: %s", cmd, ret)
        if output:
            logger.debug(output["stderr"])

    return ret


def _should_exit_early(std_err, error_strings):
    for err in error_strings:
        if err in std_err:
            return True
    return False


def _run_command(command, output, cwd, **kwargs):
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


def check_run_command(*args, **kwargs):
    """Same as run_command except that it raises an exception on failure.

    Raises
    ------
    ExecutionError
        Raised if the command returns a non-zero return code.

    """
    ret = run_command(*args, **kwargs)
    if ret != 0:
        raise ExecutionError(f"command returned error code: {ret}")


def get_cli_string():
    """Return the command-line arguments issued.

    Returns
    -------
    str

    """
    return os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:])
