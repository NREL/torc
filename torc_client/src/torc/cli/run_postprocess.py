"""Run a postprocess function on the results of a mapped-function workflow."""

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
def run_postprocess(ctx, api):
    """Run a postprocess function on the results of a mapped-function workflow."""
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
    results = []
    func = None
    module = None
    tag = None
    for item in resp.items:
        if item.name == "input_postprocess":
            inputs = item.data
            module, func = check_function(
                inputs["module"],
                inputs["func"],
                module_directory=inputs.get("module_directory"),
            )
            tag = f"user function module={module.__name__} func={func.__name__}"
        else:
            results.append(item.data)

    if func is None:
        logger.error("Did not find the 'input_postprocess' job.")
        sys.exit(1)

    # TODO: check explicitly for failed jobs in the current workflow run_id.
    logger.info("Running {}", tag)
    ret = 0
    result = None
    try:
        result = func(results)
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
