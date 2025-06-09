"""Run a function on one set of inputs stored in the workflow database."""

import os
import sys

import rich_click as click
from loguru import logger

from torc.common import check_function
from torc.loggers import setup_logging
from .common import (
    check_database_url,
    get_workflow_key_from_context,
)


@click.command()
@click.pass_obj
@click.pass_context
def run_function(ctx, api):
    """Run a function on one set of inputs stored in the workflow database. Only called by the
    torc worker application as part of the mapped-function workflow."""
    setup_logging(
        console_level="INFO",
        mode="w",
    )
    job_key = os.environ.get("TORC_JOB_KEY")
    if job_key is None:
        logger.error("This command can only be called from the torc worker application.")
        sys.exit(1)

    check_database_url(api)
    workflow_key = get_workflow_key_from_context(ctx, api)
    resp = api.list_job_user_data_consumes(workflow_key, job_key)
    if len(resp.items) != 1:
        logger.error(
            "Received unexpected input user data from database job_key={} resp={}",
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
    logger.info("Running {}", tag)
    ret = 0
    result = None
    try:
        result = func(inputs["params"])
        logger.info("Completed {}", tag)
    except Exception:
        logger.exception("Failed to run {}", tag)
        ret = 1

    if result is not None:
        resp = api.list_job_user_data_stores(workflow_key, job_key)
        if len(resp.items) != 1:
            logger.error(
                "Received unexpected output data placeholder from database job_key={} resp={}",
                job_key,
                resp,
            )
            sys.exit(1)
        output = resp.items[0]
        output.data = result
        api.modify_user_data(workflow_key, output.key, output)
        logger.info("Stored result for {}", tag)

    sys.exit(ret)
