"""Run a function on one set of inputs stored in the workflow database."""

import sys

import rich_click as click
from loguru import logger

from torc.api import make_api
from torc.cli.common import get_job_env_vars
from torc.common import check_function
from torc.loggers import setup_logging
from torc.openapi_client import DefaultApi


@click.command()
def run_function():
    """Run a function on one set of inputs stored in the workflow database. Only called by the
    torc worker application as part of the mapped-function workflow."""
    setup_logging(console_level="INFO")
    vars = get_job_env_vars()
    api = make_api(vars["url"])
    workflow_id = vars["workflow_id"]
    job_id = vars["job_id"]

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
