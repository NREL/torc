"""User interface to manage a workflow"""

import getpass
import socket
from pathlib import Path
from typing import Any

from loguru import logger

from torc.api import make_job_label, send_api_command, iter_documents
from torc.common import JobStatus
from torc.exceptions import InvalidWorkflow, TorcOperationNotAllowed
from torc.openapi_client.api import DefaultApi
from torc.openapi_client.models.file_model import FileModel
from torc.utils.run_command import check_run_command


class WorkflowManager:
    """Manages the workflow across nodes."""

    def __init__(self, api: DefaultApi, key: str) -> None:
        self._api = api
        self._key = key

    def restart(
        self,
        ignore_missing_data: bool = False,
        only_uninitialized: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Restart the workflow.

        Parameters
        ----------
        ignore_missing_data : bool
            If True, ignore checks for missing files and user_data.
        only_uninitialized : bool
            If True, only initialize jobs with a status of uninitialized.
        dry_run : bool
            If True, report changes to jobs and files but don't change anything in the database.
            The workflow startup script will not be executed if dry_run is True.
        """
        # TODO: should this delete all output files that will get overwritten?
        config = send_api_command(self._api.get_workflow_config, self._key)
        if not dry_run:
            if config.workflow_startup_script is not None:
                check_run_command(config.workflow_startup_script)

            self._bump_run_id()
            send_api_command(self._api.reset_workflow_status, self._key)

        self.reinitialize_jobs(
            ignore_missing_data=ignore_missing_data,
            only_uninitialized=only_uninitialized,
            dry_run=dry_run,
        )
        if not dry_run:
            send_api_command(
                self._api.add_event,
                self._key,
                {
                    "category": "workflow",
                    "type": "restart",
                    "user": getpass.getuser(),
                    "node_name": socket.gethostname(),
                    "message": "Restarted workflow",
                },
            )

    def start(
        self, auto_tune_resource_requirements: bool = False, ignore_missing_data: bool = False
    ) -> None:
        """Start a workflow.

        Parameters
        ----------
        auto_tune_resource_requirements : bool
            If True, configure the workflow to auto-tune resource requirements.
        ignore_missing_data : bool
            If True, ignore checks for missing files and user_data.
        """
        self._check_workflow(ignore_missing_data=ignore_missing_data)
        config = send_api_command(self._api.get_workflow_config, self._key)
        if config.workflow_startup_script is not None:
            check_run_command(config.workflow_startup_script)
        self._initialize_files()
        send_api_command(self._api.reset_workflow_status, self._key)
        send_api_command(self._api.reset_job_status, self._key)
        self._bump_run_id()
        self._initialize_jobs()

        if auto_tune_resource_requirements:
            send_api_command(self._api.auto_tune_resource_requirements, self._key)
            logger.info("Enabled auto-tuning of resource requirements.")

        send_api_command(
            self._api.add_event,
            self._key,
            {
                "category": "workflow",
                "type": "start",
                "user": getpass.getuser(),
                "node_name": socket.gethostname(),
                "message": "Started workflow",
            },
        )
        logger.info("Started workflow")

    def _bump_run_id(self) -> None:
        status = send_api_command(self._api.get_workflow_status, self._key)
        status.run_id += 1
        send_api_command(self._api.modify_workflow_status, self._key, status)

    def _check_workflow(self, ignore_missing_data: bool = False) -> None:
        workflow = send_api_command(self._api.get_workflow, self._key)
        if workflow.is_archived:
            msg = "Not allowed on an archived workflow"
            raise TorcOperationNotAllowed(msg)

        self._check_workflow_user_data(ignore_missing_data)
        self._check_workflow_files(ignore_missing_data)

    def _check_workflow_files(self, ignore_missing_data: bool) -> None:
        if ignore_missing_data:
            return
        result = send_api_command(self._api.list_required_existing_files, self._key)
        for key in result.files:
            file = send_api_command(self._api.get_file, self._key, key)
            if not Path(file.path).exists():
                msg = f"File {key=} {file.path=} should exist but does not."
                raise InvalidWorkflow(msg)

    def _check_workflow_user_data(self, ignore_missing_data: bool) -> None:
        if ignore_missing_data:
            return
        result = send_api_command(self._api.list_missing_user_data, self._key)
        if result.user_data:
            msg = " ".join(result.user_data)
            msg2 = f"User data keys are missing data: {msg}"
            raise InvalidWorkflow(msg2)

    def _process_changed_files(self, dry_run: bool = False) -> None:
        for file in iter_documents(self._api.list_files, self._key):
            path = Path(file.path)
            old: dict[str, Any] = {
                "exists": file.st_mtime is not None,
                "st_mtime": file.st_mtime,
            }
            new: dict[str, Any] = {
                "exists": path.exists(),
                "st_mtime": None,
            }
            if new["exists"]:
                new["st_mtime"] = path.stat().st_mtime
            changed = old != new
            if changed:
                if file.st_mtime:
                    if new["exists"]:
                        msg = f"File {file.path} was changed."
                        file.st_mtime = new["st_mtime"]
                    else:
                        msg = f"File {file.path} was removed."
                        file.st_mtime = None
                    if dry_run:
                        logger.info("Dry run: {} File stats will be reset.", msg)
                    else:
                        send_api_command(
                            self._api.modify_file,
                            self._key,
                            file.key,
                            file,
                        )
                        logger.info("{} Reset file stats.", msg)
                self._update_jobs_on_file_change(file, dry_run=dry_run)

    def _initialize_files(self) -> None:
        """Initialize the file stats in the database."""
        for file in iter_documents(self._api.list_files, self._key):
            path = Path(file.path)
            if path.exists():
                file.st_mtime = path.stat().st_mtime
                send_api_command(
                    self._api.modify_file,
                    self._key,
                    file.key,
                    file,
                )

    def _initialize_jobs(self, only_uninitialized: bool = False) -> None:
        """Change all uninitialized jobs to ready or blocked."""
        send_api_command(
            self._api.initialize_jobs,
            self._key,
            only_uninitialized=only_uninitialized,
        )
        logger.info("Changed all uninitialized jobs to ready or blocked.")

    def reinitialize_jobs(
        self,
        ignore_missing_data: bool = False,
        only_uninitialized: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Reinitialize jobs. Account for jobs that are new or have been reset.

        Parameters
        ----------
        ignore_missing_data : bool
            If True, ignore checks for missing files and user_data.
        only_uninitialized : bool
            If True, only initialize jobs with a status of uninitialized.
        dry_run : bool
            If True, report changes to jobs and files but don't change anything in the database.
        """
        self._check_workflow(ignore_missing_data=ignore_missing_data)
        self._process_changed_files(dry_run=dry_run)
        self._update_jobs_if_output_files_are_missing(dry_run=dry_run)
        response = send_api_command(
            self._api.process_changed_job_inputs, self._key, dry_run=dry_run
        )
        if response.reinitialized_jobs:
            logger.info(
                "Changed job status to uninitialized because inputs were changed: {}",
                " ".join(response.reinitialized_jobs),
            )
        if not dry_run:
            self._initialize_jobs(only_uninitialized=only_uninitialized)

    def _update_jobs_if_output_files_are_missing(self, dry_run: bool = False) -> None:
        run_id = None
        for job in send_api_command(
            self._api.list_jobs_by_status,
            self._key,
            JobStatus.DONE.value,
        ).items:
            for file in send_api_command(
                self._api.list_files_produced_by_job,
                self._key,
                job.key,
            ).items:
                path = Path(file.path)
                if not path.exists():
                    if run_id is None:
                        run_id = send_api_command(self._api.get_workflow_status, self._key).run_id
                    status = JobStatus.UNINITIALIZED.value
                    if dry_run:
                        logger.info(
                            "Dry run: {} will change from {} to {} because output file {} is missing. ",
                            make_job_label(job),
                            job.status,
                            status,
                            file.path,
                        )
                        for job in iter_documents(
                            self._api.list_downstream_jobs, self._key, job.key
                        ):
                            if job.status != status:
                                logger.info(
                                    "Dry run downstream job: {} will change from {} to {}",
                                    make_job_label(job),
                                    job.status,
                                    status,
                                )
                    else:
                        send_api_command(
                            self._api.manage_status_change,
                            self._key,
                            job.key,
                            status,
                            job.rev,
                            run_id,
                        )
                        logger.info(
                            "Changed {} from done to {} because output file {} is missing",
                            make_job_label(job),
                            status,
                            file.path,
                        )
                    break

    def _update_jobs_on_file_change(self, file: FileModel, dry_run: bool = False) -> None:
        run_id = send_api_command(self._api.get_workflow_status, self._key).run_id
        for job in iter_documents(
            self._api.list_jobs_by_needs_file,
            self._key,
            file.key,
        ):
            if job.status in (JobStatus.DONE.value, JobStatus.CANCELED.value):
                status = JobStatus.UNINITIALIZED.value
                if dry_run:
                    logger.info(
                        "Dry run: {} will change from {} to {} because input file {} changed. "
                        "Downstream jobs will also have their statuses reset.",
                        make_job_label(job),
                        job.status,
                        status,
                        file.path,
                    )
                    for job in iter_documents(self._api.list_downstream_jobs, self._key, job.key):
                        if job.status != status:
                            logger.info(
                                "Dry run downstream job: {} will change from {} to {}",
                                make_job_label(job),
                                job.status,
                                status,
                            )
                else:
                    send_api_command(
                        self._api.manage_status_change,
                        self._key,
                        job.key,
                        status,
                        job.rev,
                        run_id,
                    )
                    logger.info(
                        "Changed job {} / {} from {} to {} because input file {} changed",
                        job.name,
                        job.key,
                        job.status,
                        status,
                        file.path,
                    )
