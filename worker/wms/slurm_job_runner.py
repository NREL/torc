import logging
import subprocess
import os

from datetime import datetime, timedelta
from pathlib import Path

import click
from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration

from wms.job_runner import JobRunner
from wms.loggers import setup_logging

logger = logging.getLogger(__name__)


@click.command()
@click.option("-u", "--database-url", help="Database URL")
@click.option(
    "-o", "--output", default="output", show_default=True, callback=lambda *x: Path(x[2])
)
def run(database_url, output):
    """Run workflow jobs on a SLURM compute node."""
    logger = setup_logging(__name__)
    end_time = get_end_time()
    configuration = Configuration()
    if database_url is None:
        configuration.host = "http://localhost:8529/_db/workflows/wms-service"
    else:
        configuration.host = database_url
    api = DefaultApi(ApiClient(configuration))
    runner = JobRunner(api, output, time_limit=end_time)
    logger.info("Start workflow")
    runner.run_worker()
    # TODO: schedule more nodes if needed


def get_end_time(buffer_minutes=2):
    slurm_job_id = os.environ["SLURM_JOB_ID"]
    cmd = ["squeue", "-j", slurm_job_id, '--format="%20e"']
    ret = subprocess.run(cmd, capture_output=True)
    if ret.returncode != 0:
        raise Exception(f"Failed to find end time:", ret)

    out = ret.stdout.decode("utf-8")
    timestamp = out.split("\n")[1].replace('"', "").strip()
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S") - timedelta(minutes=buffer_minutes)


if __name__ == "__main__":
    run()
