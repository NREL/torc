"""CLI command to start a JobRunner on a SLURM compute node"""

import logging
import socket
import subprocess

from datetime import datetime, timedelta
from pathlib import Path

import click

from wms.api import make_api
from wms.hpc.common import HpcType
from wms.hpc.slurm_interface import SlurmInterface
from wms.job_runner import JobRunner, convert_end_time_to_duration_str
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
    my_logger = setup_logging(__name__)
    api = make_api(database_url)
    intf = SlurmInterface()
    slurm_job_id = intf.get_current_job_id()
    scheduler = {
        "node_names": intf.list_active_nodes(slurm_job_id),
        "environment_variables": intf.get_environment_variables(),
        "scheduler_type": "hpc",
        "slurm_job_id": slurm_job_id,
        "hpc_type": HpcType.SLURM.value,
    }
    end_time = _get_end_time(slurm_job_id)
    time_limit = convert_end_time_to_duration_str(end_time)
    scheduled_compute_node = api.get_scheduled_compute_nodes_key(slurm_job_id)
    runner = JobRunner(
        api,
        output,
        time_limit=time_limit,
        scheduler_config_id=scheduled_compute_node.scheduler_config_id,
    )
    node = api.get_scheduled_compute_nodes_key(slurm_job_id)
    node.status = "active"
    node = api.put_scheduled_compute_nodes_key(node, slurm_job_id)
    my_logger.info("Start workflow on compute node %s", socket.gethostname())
    runner.run_worker(scheduler=scheduler)
    node.status = "complete"
    node = api.put_scheduled_compute_nodes_key(node, slurm_job_id)
    # TODO: schedule more nodes if needed


def _get_end_time(slurm_job_id, buffer_minutes=2):
    cmd = ["squeue", "-j", slurm_job_id, '--format="%20e"']
    ret = subprocess.run(cmd, capture_output=True, check=False)
    if ret.returncode != 0:
        raise Exception(f"Failed to find end time: return_code={ret}")

    out = ret.stdout.decode("utf-8")
    timestamp = out.split("\n")[1].replace('"', "").strip()
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S") - timedelta(minutes=buffer_minutes)


if __name__ == "__main__":
    slurm_runner()  # pylint: disable=no-value-for-parameter
