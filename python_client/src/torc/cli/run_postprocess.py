"""Run a postprocess function on the results of a mapped-function workflow."""

import os
import sys

import rich_click as click
from loguru import logger

from torc.api import make_api
from torc.cli.common import get_job_env_vars
from torc.common import check_function
from torc.loggers import setup_logging


@click.command()
@click.argument("url")
def run_postprocess(url: str):
    """Run a postprocess function on the results of a mapped-function workflow."""
    setup_logging(console_level="INFO")
    vars = get_job_env_vars()
    api = make_api(vars["url"])
    workflow_id = vars["workflow_id"]
    job_id = vars["job_id"]
    api = make_api(url)
    resp = api.list_user_data(workflow_id=workflow_id, consumer_job_id=job_id)

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
        resp = api.list_user_data(workflow_id=workflow_id, producer_job_id=job_id)
        if len(resp.items) != 1:
            logger.error(
                "Received unexpected output data placeholder from database job_key={} resp={}",
                job_id,
                resp,
            )
            sys.exit(1)
        output = resp.items[0]
        output.data = result
        api.update_user_data(output.id, output)
        logger.info("Stored result for {}", tag)

    sys.exit(ret)
