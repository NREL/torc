"""SLURM management functionality"""

import logging
import os
import re
from datetime import datetime

from wms.exceptions import ExecutionError
from wms.utils.files import create_script
from wms.utils.run_command import check_run_command, run_command
from .common import HpcJobStats, HpcJobStatus, HpcJobInfo
from .hpc_interface import HpcInterface


logger = logging.getLogger(__name__)


class SlurmInterface(HpcInterface):
    """Manages Slurm jobs."""

    _STATUSES = {
        "PENDING": HpcJobStatus.QUEUED,
        "CONFIGURING": HpcJobStatus.QUEUED,
        "RUNNING": HpcJobStatus.RUNNING,
        "COMPLETED": HpcJobStatus.COMPLETE,
        "COMPLETING": HpcJobStatus.COMPLETE,
    }
    _REGEX_SBATCH_OUTPUT = re.compile(r"Submitted batch job (\d+)")

    def cancel_job(self, job_id):
        return run_command(f"scancel {job_id}")

    def check_status(self, job_id=None):
        field_names = ("jobid", "state")
        cmd = f"squeue -u {self.USER} --Format \"{','.join(field_names)}\" -h -j {job_id}"

        output = {}
        # Transient failures could be costly. Retry for up to one minute.
        errors = ["Invalid job id specified"]
        ret = run_command(cmd, output, num_retries=6, retry_delay_s=10, error_strings=errors)
        if ret != 0:
            if "Invalid job id specified" in output["stderr"]:
                return HpcJobInfo("", "", HpcJobStatus.NONE)

            logger.error(
                "Failed to run squeue command=[%s] ret=%s err=%s",
                cmd,
                ret,
                output["stderr"],
            )
            raise ExecutionError(f"squeue command failed: {ret}")

        stdout = output["stdout"]
        logger.debug("squeue output:  [%s]", stdout)
        fields = stdout.split()
        if not fields:
            # No jobs are currently running.
            return HpcJobInfo("", "", HpcJobStatus.NONE)

        assert len(fields) == len(field_names)
        job_info = HpcJobInfo(
            fields[0], fields[1], self._STATUSES.get(fields[2], HpcJobStatus.UNKNOWN)
        )
        return job_info

    def check_statuses(self):
        field_names = ("jobid", "state")
        cmd = f"squeue -u {self.USER} --Format \"{','.join(field_names)}\" -h"

        output = {}
        # Transient failures could be costly. Retry for up to one minute.
        ret = run_command(cmd, output, num_retries=6, retry_delay_s=10)
        if ret != 0:
            logger.error(
                "Failed to run squeue command=[%s] ret=%s err=%s",
                cmd,
                ret,
                output["stderr"],
            )
            raise ExecutionError(f"squeue command failed: {ret}")

        return self._get_statuses_from_output(output["stdout"])

    def _get_statuses_from_output(self, output):
        logger.debug("squeue output:  [%s]", output)
        lines = output.split("\n")
        if not lines:
            # No jobs are currently running.
            return {}

        statuses = {}
        for line in lines:
            if line == "":
                continue
            fields = line.strip().split()
            assert len(fields) == 2
            job_id = fields[0]
            status = fields[1]
            statuses[job_id] = self._STATUSES.get(status, HpcJobStatus.UNKNOWN)

        return statuses

    def get_current_job_id(self):
        return os.environ["SLURM_JOB_ID"]

    def create_submission_script(self, name, command, filename, path, config):
        text = self._create_submission_script_text(name, command, path, config)
        create_script(filename, text)

    def _create_submission_script_text(self, name, command, path, config):
        text = f"""#!/bin/bash
#SBATCH --account={config['account']}
#SBATCH --job-name={name}
#SBATCH --time={config['walltime']}
#SBATCH --output={path}/job_output_%j.o
#SBATCH --error={path}/job_output_%j.e
"""
        for param in set(config).difference({"account", "walltime"}):
            value = config[param]
            if value is not None:
                text += f"#SBATCH --{param}={value}\n"

        text += f"{command}\n"
        # TODO: make running through srun configurable?
        # text += f"\nsrun {command}"
        return text

    def get_environment_variables(self) -> dict[str, str]:
        return {k: v for k, v in os.environ.items() if "SLURM" in k}

    def get_job_end_time(self):
        cmd = f"squeue -j {self.get_current_job_id()} --format='%20e'"
        output = {}
        check_run_command(cmd, output=output)
        timestamp = output["stdout"].split("\n")[1].replace('"', "").strip()
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

    def get_job_stats(self, job_id):
        cmd = (
            f"sacct -j {job_id} --format=JobID,JobName%20,state,start,end,Account,Partition%15,QOS"
        )
        output = {}
        check_run_command(cmd, output=output)
        result = output["stdout"].strip().split("\n")
        if len(result) != 6:
            raise Exception(f"Unknown output for sacct: {result} length={len(result)}")

        # 8165902       COMPLETED 2022-01-16T12:10:37 2022-01-17T04:04:34
        fields = result[2].split()
        if fields[0] != job_id:
            raise Exception(f"sacct returned unexpected job_id={fields[0]}")

        state = self._STATUSES.get(fields[2], HpcJobStatus.UNKNOWN)
        fmt = "%Y-%m-%dT%H:%M:%S"
        try:
            start = datetime.strptime(fields[3], fmt)
        except ValueError:
            logger.exception("Failed to parse start_time=%s", fields[3])
            raise
        try:
            if fields[4] == "Unknown":
                end = fields[4]
            else:
                end = datetime.strptime(fields[4], fmt)
        except ValueError:
            logger.exception("Failed to parse end_time=%s", fields[4])
            raise
        stats = HpcJobStats(
            hpc_job_id=job_id,
            name=fields[1],
            state=state,
            start=start,
            end=end,
            account=fields[5],
            partition=fields[6],
            qos=fields[7],
        )
        return stats

    def get_local_scratch(self):
        return os.environ["LOCAL_SCRATCH"]

    def get_node_id(self):
        return os.environ["SLURM_NODEID"]

    @staticmethod
    def get_num_cpus():
        return int(os.environ["SLURM_CPUS_ON_NODE"])

    def list_active_nodes(self, job_id):
        out1 = {}
        # It's possible that 500 characters won't be enough, even with the compact format.
        # Compare the node count against the result to make sure we got all nodes.
        # There should be a better way to get this.
        check_run_command(f'squeue -j {job_id} --format="%5D %500N" -h', out1)
        result = out1["stdout"].strip().split()
        assert len(result) == 2, str(result)
        num_nodes = int(result[0])
        nodes_compact = result[1]
        out2 = {}
        check_run_command(f'scontrol show hostnames "{nodes_compact}"', out2)
        nodes = [x for x in out2["stdout"].split("\n") if x != ""]
        if len(nodes) != num_nodes:
            raise Exception(f"Bug in parsing node names. Found={len(nodes)} Actual={num_nodes}")
        return nodes

    def submit(self, filename):
        job_id = None
        output = {}
        # Transient failures could be costly. Retry for up to one minute.
        # TODO: Some errors are not transient. We could detect those and skip the retries.
        ret = run_command(f"sbatch {filename}", output, num_retries=6, retry_delay_s=10)
        if ret == 0:
            stdout = output["stdout"]
            match = self._REGEX_SBATCH_OUTPUT.search(stdout)
            if match:
                job_id = match.group(1)
            else:
                logger.error("Failed to interpret sbatch output [%s]", stdout)
                ret = 1
        else:
            ret = 1

        return ret, job_id, output["stderr"]
