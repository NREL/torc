import logging
import subprocess
import os

from datetime import datetime, timedelta
from pathlib import Path

import click
from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration

from wms.hpc.common import HpcType
from wms.hpc.slurm_interface import SlurmInterface
from wms.job_runner import JobRunner
from wms.loggers import setup_logging

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "-o",
    "--output",
    default="output",
    show_default=True,
    callback=lambda *x: Path(x[2]),
)
@click.argument("database_url")
def slurm_runner(database_url, output):
    """Run workflow jobs on a SLURM compute node."""
    logger = setup_logging(__name__)
    configuration = Configuration()
    configuration.host = database_url
    api = DefaultApi(ApiClient(configuration))
    intf = SlurmInterface()
    slurm_job_id = intf.get_current_job_id()
    scheduler = {
        "node_names": intf.list_active_nodes(slurm_job_id),
        "environment_variables": intf.get_environment_variables(),
        "scheduler_type": "hpc",
        "hpc_type": HpcType.SLURM.value,
    }
    end_time = _get_end_time(slurm_job_id)
    runner = JobRunner(api, output, time_limit=end_time)
    logger.info("Start workflow")
    runner.run_worker(scheduler=scheduler)
    # TODO: schedule more nodes if needed


def _get_end_time(slurm_job_id, buffer_minutes=2):
    cmd = ["squeue", "-j", slurm_job_id, '--format="%20e"']
    ret = subprocess.run(cmd, capture_output=True)
    if ret.returncode != 0:
        raise Exception(f"Failed to find end time: return_code={ret}")

    out = ret.stdout.decode("utf-8")
    timestamp = out.split("\n")[1].replace('"', "").strip()
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S") - timedelta(
        minutes=buffer_minutes
    )


if __name__ == "__main__":
    slurm_runner()
