"""User interface to manage a workflow"""

import getpass
import logging
import socket
from pathlib import Path

from torc.api import send_api_command


logger = logging.getLogger(__name__)


class WorkflowManager:
    """Manages the workflow across nodes."""

    def __init__(self, api):
        self._api = api

    def reinitialize_jobs(self):
        """Reinitialize job status to prepare for restarting the workflow.
        Users may optionally call this in order to inspect the job status before calling restart.
        """
        self._reset_job_status()
        self._process_changed_files()
        self._update_jobs_if_output_files_are_missing()
        send_api_command(self._api.post_workflow_initialize_jobs)
        # TODO: what if something about the jobs are changed? Hash all job dependencies in
        # initialize_jobs and compare at restart?
        # - input_files
        # - output_files
        # - user_data
        # TODO: ensure that this function is idempotent.

    def restart(self, reinitialize=True):
        """Restart the workflow.

        Parameters
        ----------
        reinitialize : bool, defaults to True
            If True, call reinitialize_jobs. Set False if it was already called.
        """
        status = send_api_command(self._api.get_workflow_status)
        status.run_id += 1
        send_api_command(self._api.put_workflow_status, status)
        if reinitialize:
            self.reinitialize_jobs()
        # TODO schedule workers.
        send_api_command(
            self._api.post_events,
            {
                "category": "workflow",
                "type": "restart",
                "user": getpass.getuser(),
                "node_name": socket.gethostname(),
                "message": "Restarted workflow",
            },
        )

    def start(self, auto_tune_resource_requirements=False):
        """Start a workflow.

        Parameters
        ----------
        auto_tune_resource_requirements : bool
            If True, configure the workflow to auto-tune resource requirements.
        """
        send_api_command(self._api.put_workflow_status_reset)
        # Set every job status to unknown/uninitialized.
        send_api_command(self._api.post_workflow_initialize_jobs)

        if auto_tune_resource_requirements:
            send_api_command(self._api.post_workflow_auto_tune_resource_requirements)

        send_api_command(
            self._api.post_events,
            {
                "category": "workflow",
                "type": "start",
                "user": getpass.getuser(),
                "node_name": socket.gethostname(),
                "message": "Started workflow",
            },
        )
        logger.info("Started workflow")
        # TODO schedule workers.

    def _process_changed_files(self):
        for file in send_api_command(self._api.get_files).items:
            path = Path(file.path)
            old = {
                "exists": file.st_mtime is not None,
                "st_mtime": file.st_mtime,
            }
            new = {
                "exists": path.exists(),
                "st_mtime": None,
            }
            if new["exists"]:
                new["st_mtime"] = path.stat().st_mtime
            changed = old != new
            if changed:
                if file.st_mtime and not new["exists"]:
                    file.st_mtime = None
                    send_api_command(self._api.put_files_key, file, file.name)
                    logger.info("File %s was removed. Cleared file stats", file.name)
                self._update_jobs_on_file_change(file)

    def _reset_job_status(self):
        for status in ("canceled", "submitted", "submitted_pending"):
            # TODO: This query will be throttled. Handle batching. Do it generically so that all
            # similar iterations can use it.
            for job in send_api_command(self._api.get_jobs_find_by_status_status, status).items:
                job.status = "uninitialized"
                send_api_command(self._api.put_jobs_key, job, job.name)
                logger.info("Changed job %s from %s to uninitialized", job.name, status)

    def _update_jobs_if_output_files_are_missing(self):
        for job in send_api_command(self._api.get_jobs_find_by_status_status, "done").items:
            for file in send_api_command(self._api.get_files_produced_by_job_key, job.name).items:
                path = Path(file.path)
                if not path.exists():
                    job.status = "uninitialized"
                    send_api_command(self._api.put_jobs_key, job, job.name)
                    logger.info(
                        "Changed job %s from done to %s because output file is missing",
                        job.name,
                        job.status,
                    )
                    break

    def _update_jobs_on_file_change(self, file):
        for job in send_api_command(self._api.get_jobs_find_by_needs_file_key, file.name).items:
            if job.status in ("done", "canceled"):
                status = "uninitialized"
                send_api_command(
                    self._api.put_jobs_manage_status_change_key_status_rev,
                    job.name,
                    status,
                    job._rev,  # pylint: disable=protected-access
                )
                logger.info(
                    "Changed job %s from %s to %s after input file change",
                    job.name,
                    job.status,
                    status,
                )
