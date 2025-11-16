"""Run a function on one set of inputs stored in the workflow database."""

import os
import sys

import rich_click as click
from loguru import logger

from torc.common import check_function
from torc.loggers import setup_logging
from torc.openapi_client import DefaultApi


@click.command()
@click.pass_obj
@click.pass_context
def run_function(workflow_id: int, api: DefaultApi):
    """Run a function on one set of inputs stored in the workflow database. Only called by the
    torc worker application as part of the mapped-function workflow."""
    setup_logging(
        console_level="INFO",
        mode="w",
    )
    job_id_str = os.getenv("TORC_JOB_ID")
    if job_id_str is None:
        logger.error("This command can only be called from the torc worker application.")
        sys.exit(1)
    job_id = int(job_id_str)

    resp = api.list_user_data(workflow_id=workflow_id, consumer_job_id=job_id)
    assert resp is not None
    if len(resp.items) != 1:
        logger.error(
            "Received unexpected input user data from database job_id={} resp={}",
            job_id,
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
        resp = api.list_user_data(workflow_id=workflow_id, producer_job_id=job_id)
        assert resp is not None
        if len(resp.items) != 1:
            logger.error(
                "Received unexpected output data placeholder from database job_id={} resp={}",
                job_id,
                resp,
            )
            sys.exit(1)
        output = resp.items[0]
        output.data = result
        api.update_user_data(output.id, output)
        logger.info("Stored result for {}", tag)

    sys.exit(ret)
