"""User interface to manage a workflow"""

import getpass
import logging
import socket
from pathlib import Path

from torc.api import send_api_command, iter_documents


logger = logging.getLogger(__name__)


class WorkflowManager:
    """Manages the workflow across nodes."""

    def __init__(self, api, key):
        self._api = api
        self._key = key

    def reinitialize_jobs(self):
        """Reinitialize job status to prepare for restarting the workflow.
        Users may optionally call this in order to inspect the job status before calling restart.
        """
        self._reset_job_status()
        self._process_changed_files()
        self._update_jobs_if_output_files_are_missing()
        send_api_command(self._api.post_workflows_initialize_jobs_key, self._key)
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
        status = send_api_command(self._api.get_workflows_status_key, self._key)
        status.run_id += 1
        send_api_command(self._api.put_workflows_status_key, status, self._key)
        if reinitialize:
            self.reinitialize_jobs()
        # TODO schedule workers.
        send_api_command(
            self._api.post_workflows_workflow_events,
            {
                "category": "workflow",
                "type": "restart",
                "user": getpass.getuser(),
                "node_name": socket.gethostname(),
                "message": "Restarted workflow",
            },
            self._key,
        )

    def initialize_files(self):
        """Initialize the file stats in the database."""
        for file in iter_documents(self._api.get_workflows_workflow_files, self._key):
            path = Path(file.path)
            if path.exists():
                file.st_mtime = path.stat().st_mtime
                send_api_command(
                    self._api.put_workflows_workflow_files_key, file, self._key, file.key
                )

    def start(self, auto_tune_resource_requirements=False):
        """Start a workflow.

        Parameters
        ----------
        auto_tune_resource_requirements : bool
            If True, configure the workflow to auto-tune resource requirements.
        """
        self.initialize_files()
        send_api_command(self._api.post_workflows_reset_status_key, self._key)
        # Set every job status to unknown/uninitialized.
        send_api_command(self._api.post_workflows_initialize_jobs_key, self._key)

        if auto_tune_resource_requirements:
            send_api_command(
                self._api.post_workflows_auto_tune_resource_requirements_key, self._key
            )
            logger.info("Enabled auto-tuning of resource requirements.")

        send_api_command(
            self._api.post_workflows_workflow_events,
            {
                "category": "workflow",
                "type": "start",
                "user": getpass.getuser(),
                "node_name": socket.gethostname(),
                "message": "Started workflow",
            },
            self._key,
        )
        logger.info("Started workflow")
        # TODO schedule workers.

    def _process_changed_files(self):
        for file in iter_documents(self._api.get_workflows_workflow_files, self._key):
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
                    send_api_command(
                        self._api.put_workflows_workflow_files_key, file, self._key, file.key
                    )
                    logger.info("File %s was removed. Cleared file stats", file.name)
                self._update_jobs_on_file_change(file)

    def _reset_job_status(self):
        for status in ("canceled", "submitted", "submitted_pending", "terminated"):
            for job in iter_documents(
                self._api.get_workflows_workflow_jobs_find_by_status_status, self._key, status
            ):
                job.status = "uninitialized"
                send_api_command(
                    self._api.put_workflows_workflow_jobs_key, job, self._key, job.key
                )
                logger.info("Changed job %s from %s to uninitialized", job.key, status)

    def _update_jobs_if_output_files_are_missing(self):
        for job in send_api_command(
            self._api.get_workflows_workflow_jobs_find_by_status_status, self._key, "done"
        ).items:
            for file in send_api_command(
                self._api.get_workflows_workflow_files_produced_by_job_key, self._key, job.key
            ).items:
                path = Path(file.path)
                if not path.exists():
                    job.status = "uninitialized"
                    send_api_command(
                        self._api.put_workflows_workflow_jobs_key, job, self._key, job.key
                    )
                    logger.info(
                        "Changed job %s from done to %s because output file is missing",
                        job.key,
                        job.status,
                    )
                    break

    def _update_jobs_on_file_change(self, file):
        for job in iter_documents(
            self._api.get_workflows_workflow_jobs_find_by_needs_file_key, self._key, file.key
        ):
            if job.status in ("done", "canceled"):
                status = "uninitialized"
                send_api_command(
                    self._api.put_workflows_workflow_jobs_key_manage_status_change_status_rev,
                    self._key,
                    job.key,
                    status,
                    job._rev,  # pylint: disable=protected-access
                )
                logger.info(
                    "Changed job %s from %s to %s after input file change",
                    job.key,
                    job.status,
                    status,
                )
