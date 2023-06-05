"""User interface to manage a workflow"""

import getpass
import logging
import socket
from pathlib import Path

from torc.api import send_api_command, iter_documents
from torc.exceptions import InvalidWorkflow


logger = logging.getLogger(__name__)


class WorkflowManager:
    """Manages the workflow across nodes."""

    def __init__(self, api, key):
        self._api = api
        self._key = key

    def restart(self, ignore_missing_data=False):
        """Restart the workflow.

        Parameters
        ----------
        ignore_missing_data : bool
            If True, ignore checks for missing files and user_data.
        """
        self._check_workflow(ignore_missing_data=ignore_missing_data)
        self._bump_run_id()
        send_api_command(self._api.post_workflows_key_reset_status, self._key)
        self._reinitialize_jobs()
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

    def start(self, auto_tune_resource_requirements=False, ignore_missing_data=False):
        """Start a workflow.

        Parameters
        ----------
        auto_tune_resource_requirements : bool
            If True, configure the workflow to auto-tune resource requirements.
        ignore_missing_data : bool
            If True, ignore checks for missing files and user_data.
        """
        self._check_workflow(ignore_missing_data=ignore_missing_data)
        self._initialize_files()
        send_api_command(self._api.post_workflows_key_reset_status, self._key)
        send_api_command(self._api.post_workflows_key_reset_job_status, self._key)
        self._bump_run_id()
        # Set every job status from uninitialized to ready or blocked.
        send_api_command(self._api.post_workflows_key_initialize_jobs, self._key)

        if auto_tune_resource_requirements:
            send_api_command(
                self._api.post_workflows_key_auto_tune_resource_requirements, self._key
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

    def _bump_run_id(self):
        status = send_api_command(self._api.get_workflows_key_status, self._key)
        status.run_id += 1
        send_api_command(self._api.put_workflows_key_status, status, self._key)

    def _check_workflow(self, ignore_missing_data=False):
        self._check_workflow_user_data(ignore_missing_data)
        self._check_workflow_files(ignore_missing_data)

    def _check_workflow_files(self, ignore_missing_data):
        if ignore_missing_data:
            return
        result = send_api_command(self._api.get_workflows_key_required_existing_files, self._key)
        for key in result.files:
            file = send_api_command(self._api.get_workflows_workflow_files_key, self._key, key)
            if not Path(file.path).exists():
                raise InvalidWorkflow(f"File {key=} {file.path=} should exist but does not.")

    def _check_workflow_user_data(self, ignore_missing_data):
        if ignore_missing_data:
            return
        result = send_api_command(self._api.get_workflows_key_missing_user_data, self._key)
        if result.user_data:
            msg = " ".join(result.user_data)
            raise InvalidWorkflow(f"User data keys are missing data: {msg}")

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
                        self._api.put_workflows_workflow_files_key,
                        file,
                        self._key,
                        file.key,
                    )
                    logger.info("File %s was removed. Cleared file stats", file.name)
                self._update_jobs_on_file_change(file)

    def _initialize_files(self):
        """Initialize the file stats in the database."""
        for file in iter_documents(self._api.get_workflows_workflow_files, self._key):
            path = Path(file.path)
            if path.exists():
                file.st_mtime = path.stat().st_mtime
                send_api_command(
                    self._api.put_workflows_workflow_files_key,
                    file,
                    self._key,
                    file.key,
                )

    def _reinitialize_jobs(self):
        self._reset_job_status()
        self._process_changed_files()
        self._update_jobs_if_output_files_are_missing()
        response = send_api_command(
            self._api.post_workflows_key_process_changed_job_inputs, self._key
        )
        if response.reinitialized_jobs:
            logger.info(
                "Changed job status to uninitialized because inputs were changed: %s",
                " ".join(response.reinitialized_jobs),
            )
        send_api_command(self._api.post_workflows_key_initialize_jobs, self._key)

    def _reset_job_status(self):
        for status in ("canceled", "submitted", "submitted_pending", "terminated"):
            for job in iter_documents(
                self._api.get_workflows_workflow_jobs_find_by_status_status,
                self._key,
                status,
            ):
                job.status = "uninitialized"
                send_api_command(
                    self._api.put_workflows_workflow_jobs_key, job, self._key, job.key
                )
                logger.info("Changed job %s from %s to uninitialized", job.key, status)

    def _update_jobs_if_output_files_are_missing(self):
        for job in send_api_command(
            self._api.get_workflows_workflow_jobs_find_by_status_status,
            self._key,
            "done",
        ).items:
            for file in send_api_command(
                self._api.get_workflows_workflow_files_produced_by_job_key,
                self._key,
                job.key,
            ).items:
                path = Path(file.path)
                if not path.exists():
                    job.status = "uninitialized"
                    send_api_command(
                        self._api.put_workflows_workflow_jobs_key,
                        job,
                        self._key,
                        job.key,
                    )
                    logger.info(
                        "Changed job %s from done to %s because output file is missing",
                        job.key,
                        job.status,
                    )
                    break

    def _update_jobs_on_file_change(self, file):
        for job in iter_documents(
            self._api.get_workflows_workflow_jobs_find_by_needs_file_key,
            self._key,
            file.key,
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
