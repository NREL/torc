"""Run a function on one set of inputs stored in the workflow database."""

import importlib
import logging
import os
import sys

import click

from torc.loggers import setup_logging
from .common import (
    check_database_url,
    get_workflow_key_from_context,
)


logger = logging.getLogger(__name__)


@click.command()
@click.pass_obj
@click.pass_context
def run_function(ctx, api):
    """Run a function on one set of inputs stored in the workflow database. Only called by the
    torc worker application as part of the mapped-function workflow."""
    setup_logging(
        __name__,
        console_level=logging.INFO,
        mode="w",
    )
    job_key = os.environ.get("TORC_JOB_KEY")
    if job_key is None:
        logger.error("This command can only be called from the torc worker application.")
        sys.exit(1)

    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    resp = api.get_workflows_workflow_jobs_key_user_data_consumes(workflow_key, job_key)
    if len(resp.items) != 1:
        logger.error(
            "Received unexpected input user data from database job_key=%s resp=%s",
            job_key,
            resp,
        )
        sys.exit(1)

    inputs = resp.items[0].data
    module, func = check_function(
        inputs["module"],
        inputs["func"],
        module_directory=inputs.get("module_directory"),
    )

    tag = f"user function module={module.__name__} func={func.__name__}"
    logger.info("Running %s", tag)
    ret = 0
    result = None
    try:
        result = func(inputs["params"])
        logger.info("Completed %s", tag)
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Failed to run %s", tag)
        ret = 1

    if result is not None:
        resp = api.get_workflows_workflow_jobs_key_user_data_stores(workflow_key, job_key)
        if len(resp.items) != 1:
            logger.error(
                "Received unexpected output data placeholder from database job_key=%s resp=%s",
                job_key,
                resp,
            )
            sys.exit(1)
        output = resp.items[0]
        output.data = result
        api.put_workflows_workflow_user_data_key(output, workflow_key, output.key)
        logger.info("Stored result for %s", tag)

    sys.exit(ret)


def check_function(module_name, func_name, module_directory=None):
    """Check that func_name is importable from module name and returns the module and function
    references.

    Returns
    -------
    tuple
        module, func
    """
    cur_dir = os.getcwd()
    added_cur_dir = False
    try:
        if module_directory is not None:
            sys.path.append(module_directory)
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        sys.path.append(cur_dir)
        module = importlib.import_module(module_name)
    finally:
        if module_directory is not None:
            sys.path.remove(module_directory)
        if added_cur_dir:
            sys.path.remove(cur_dir)

    func = getattr(module, func_name)
    if func is None:
        raise ValueError(f"function={func_name} is not defined in {module_name}")
    return module, func
