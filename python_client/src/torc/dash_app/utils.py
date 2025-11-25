"""Utility functions for the Torc Dash app."""

import json
import os
import select
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from torc.openapi_client import (
    ApiClient,
    ApiException,
    Configuration,
    DefaultApi,
)

# Thread pool for running API calls in the background
executor = ThreadPoolExecutor(max_workers=4)


class TorcApiWrapper:
    """Wrapper for the Torc OpenAPI client with threading support."""

    def __init__(self, api_url: str, username: str | None = None):
        """Initialize the API wrapper.

        Parameters
        ----------
        api_url : str
            The Torc server API URL.
        username : str | None, optional
            Username for workflow operations, by default None.
        """
        self.api_url = api_url
        self.username = username
        self._client = None
        self._api = None

    def _get_api(self) -> DefaultApi:
        """Get or create the API client."""
        if self._api is None or self._client is None:
            configuration = Configuration()
            configuration.host = self.api_url
            self._client = ApiClient(configuration)
            self._api = DefaultApi(self._client)
        return self._api

    def list_workflows(self, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List all workflows.

        Parameters
        ----------
        offset : int, optional
            Starting offset for pagination, by default 0.
        limit : int, optional
            Maximum number of workflows to return, by default 100.

        Returns
        -------
        dict[str, Any]
            Dictionary with workflow data.
        """
        try:
            api = self._get_api()
            response = api.list_workflows(offset=offset, limit=limit)
            return {
                "success": True,
                "data": [self._model_to_dict(w) for w in response.items] if response.items else [],
                "total": response.total if hasattr(response, "total") else len(response.items or []),
            }
        except ApiException as e:
            return {"success": False, "error": str(e), "data": []}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg, "data": []}

    def list_jobs(self, workflow_id: int, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List jobs for a workflow.

        Parameters
        ----------
        workflow_id : int
            The workflow ID.
        offset : int, optional
            Starting offset for pagination, by default 0.
        limit : int, optional
            Maximum number of jobs to return, by default 100.

        Returns
        -------
        dict[str, Any]
            Dictionary with job data.
        """
        try:
            api = self._get_api()
            response = api.list_jobs(workflow_id, offset=offset, limit=limit)
            return {
                "success": True,
                "data": [self._model_to_dict(j) for j in response.items] if response.items else [],
                "total": response.total if hasattr(response, "total") else len(response.items or []),
            }
        except ApiException as e:
            return {"success": False, "error": str(e), "data": []}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg, "data": []}

    def list_results(self, workflow_id: int, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List results for a workflow.

        Parameters
        ----------
        workflow_id : int
            The workflow ID.
        offset : int, optional
            Starting offset for pagination, by default 0.
        limit : int, optional
            Maximum number of results to return, by default 100.

        Returns
        -------
        dict[str, Any]
            Dictionary with result data.
        """
        try:
            api = self._get_api()
            response = api.list_results(workflow_id, offset=offset, limit=limit)
            return {
                "success": True,
                "data": [self._model_to_dict(r) for r in response.items] if response.items else [],
                "total": response.total if hasattr(response, "total") else len(response.items or []),
            }
        except ApiException as e:
            return {"success": False, "error": str(e), "data": []}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg, "data": []}

    def list_events(self, workflow_id: int, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List events for a workflow.

        Parameters
        ----------
        workflow_id : int
            The workflow ID.
        offset : int, optional
            Starting offset for pagination, by default 0.
        limit : int, optional
            Maximum number of events to return, by default 100.

        Returns
        -------
        dict[str, Any]
            Dictionary with event data.
        """
        try:
            api = self._get_api()
            response = api.list_events(workflow_id, offset=offset, limit=limit)
            return {
                "success": True,
                "data": [self._model_to_dict(e) for e in response.items] if response.items else [],
                "total": response.total if hasattr(response, "total") else len(response.items or []),
            }
        except ApiException as e:
            return {"success": False, "error": str(e), "data": []}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg, "data": []}

    def list_files(self, workflow_id: int, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List files for a workflow.

        Parameters
        ----------
        workflow_id : int
            The workflow ID.
        offset : int, optional
            Starting offset for pagination, by default 0.
        limit : int, optional
            Maximum number of files to return, by default 100.

        Returns
        -------
        dict[str, Any]
            Dictionary with file data.
        """
        try:
            api = self._get_api()
            response = api.list_files(workflow_id, offset=offset, limit=limit)
            return {
                "success": True,
                "data": [self._model_to_dict(f) for f in response.items] if response.items else [],
                "total": response.total if hasattr(response, "total") else len(response.items or []),
            }
        except ApiException as e:
            return {"success": False, "error": str(e), "data": []}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg, "data": []}

    def list_user_data(self, workflow_id: int, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List user data for a workflow.

        Parameters
        ----------
        workflow_id : int
            The workflow ID.
        offset : int, optional
            Starting offset for pagination, by default 0.
        limit : int, optional
            Maximum number of user data items to return, by default 100.

        Returns
        -------
        dict[str, Any]
            Dictionary with user data.
        """
        try:
            api = self._get_api()
            response = api.list_user_data(workflow_id, offset=offset, limit=limit)
            return {
                "success": True,
                "data": [self._model_to_dict(u) for u in response.items] if response.items else [],
                "total": response.total if hasattr(response, "total") else len(response.items or []),
            }
        except ApiException as e:
            return {"success": False, "error": str(e), "data": []}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg, "data": []}

    def list_compute_nodes(self, workflow_id: int, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List compute nodes for a workflow.

        Parameters
        ----------
        workflow_id : int
            The workflow ID.
        offset : int, optional
            Starting offset for pagination, by default 0.
        limit : int, optional
            Maximum number of compute nodes to return, by default 100.

        Returns
        -------
        dict[str, Any]
            Dictionary with compute node data.
        """
        try:
            api = self._get_api()
            response = api.list_compute_nodes(workflow_id, offset=offset, limit=limit)
            return {
                "success": True,
                "data": [self._model_to_dict(c) for c in response.items] if response.items else [],
                "total": response.total if hasattr(response, "total") else len(response.items or []),
            }
        except ApiException as e:
            return {"success": False, "error": str(e), "data": []}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg, "data": []}

    def list_resource_requirements(self, workflow_id: int, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List resource requirements for a workflow.

        Parameters
        ----------
        workflow_id : int
            The workflow ID.
        offset : int, optional
            Starting offset for pagination, by default 0.
        limit : int, optional
            Maximum number of resource requirements to return, by default 100.

        Returns
        -------
        dict[str, Any]
            Dictionary with resource requirement data.
        """
        try:
            api = self._get_api()
            response = api.list_resource_requirements(workflow_id, offset=offset, limit=limit)
            return {
                "success": True,
                "data": [self._model_to_dict(r) for r in response.items] if response.items else [],
                "total": response.total if hasattr(response, "total") else len(response.items or []),
            }
        except ApiException as e:
            return {"success": False, "error": str(e), "data": []}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg, "data": []}

    def list_job_dependencies(self, workflow_id: int, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List job dependencies for a workflow.

        Parameters
        ----------
        workflow_id : int
            The workflow ID.
        offset : int, optional
            Starting offset for pagination, by default 0.
        limit : int, optional
            Maximum number of dependencies to return, by default 100.

        Returns
        -------
        dict[str, Any]
            Dictionary with job dependency data.
        """
        try:
            api = self._get_api()
            response = api.list_job_dependencies(workflow_id, offset=offset, limit=limit)
            return {
                "success": True,
                "data": [self._model_to_dict(d) for d in response.items] if response.items else [],
                "total": response.total_count if hasattr(response, "total_count") else len(response.items or []),
            }
        except ApiException as e:
            return {"success": False, "error": str(e), "data": []}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg, "data": []}

    def list_job_file_relationships(self, workflow_id: int, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List job-file relationships for a workflow.

        Parameters
        ----------
        workflow_id : int
            The workflow ID.
        offset : int, optional
            Starting offset for pagination, by default 0.
        limit : int, optional
            Maximum number of relationships to return, by default 100.

        Returns
        -------
        dict[str, Any]
            Dictionary with job-file relationship data.
        """
        try:
            api = self._get_api()
            response = api.list_job_file_relationships(workflow_id, offset=offset, limit=limit)
            return {
                "success": True,
                "data": [self._model_to_dict(r) for r in response.items] if response.items else [],
                "total": response.total_count if hasattr(response, "total_count") else len(response.items or []),
            }
        except ApiException as e:
            return {"success": False, "error": str(e), "data": []}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg, "data": []}

    def list_job_user_data_relationships(self, workflow_id: int, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List job-user_data relationships for a workflow.

        Parameters
        ----------
        workflow_id : int
            The workflow ID.
        offset : int, optional
            Starting offset for pagination, by default 0.
        limit : int, optional
            Maximum number of relationships to return, by default 100.

        Returns
        -------
        dict[str, Any]
            Dictionary with job-user_data relationship data.
        """
        try:
            api = self._get_api()
            response = api.list_job_user_data_relationships(workflow_id, offset=offset, limit=limit)
            return {
                "success": True,
                "data": [self._model_to_dict(r) for r in response.items] if response.items else [],
                "total": response.total_count if hasattr(response, "total_count") else len(response.items or []),
            }
        except ApiException as e:
            return {"success": False, "error": str(e), "data": []}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg, "data": []}

    def delete_workflow(self, workflow_id: int) -> dict[str, Any]:
        """Delete a workflow using the API.

        Parameters
        ----------
        workflow_id : int
            The workflow ID to delete.

        Returns
        -------
        dict[str, Any]
            Dictionary with success status.
        """
        try:
            api = self._get_api()
            api.delete_workflow(workflow_id)
            return {"success": True}
        except ApiException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg}

    def is_workflow_uninitialized(self, workflow_id: int) -> dict[str, Any]:
        """Check if a workflow is uninitialized.

        Parameters
        ----------
        workflow_id : int
            The workflow ID to check.

        Returns
        -------
        dict[str, Any]
            Dictionary with success status and is_uninitialized flag.
        """
        try:
            api = self._get_api()
            response = api.is_workflow_uninitialized(workflow_id)
            return {
                "success": True,
                "is_uninitialized": response.is_uninitialized,
            }
        except ApiException as e:
            return {"success": False, "error": str(e), "is_uninitialized": False}
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return {"success": False, "error": msg, "is_uninitialized": False}

    @staticmethod
    def _model_to_dict(model: Any) -> dict[str, Any]:
        """Convert a Pydantic model to a dictionary.

        Parameters
        ----------
        model : Any
            The Pydantic model to convert.

        Returns
        -------
        dict[str, Any]
            Dictionary representation of the model.
        """
        if hasattr(model, "model_dump"):
            return model.model_dump()
        elif hasattr(model, "dict"):
            return model.dict()
        else:
            # Fallback for simple objects
            return {k: v for k, v in model.__dict__.items() if not k.startswith("_")}


class TorcCliWrapper:
    """Wrapper for executing Torc CLI commands."""

    # Class variables for simple process tracking
    current_process = None
    output_buffer: list[str] = []

    def __init__(self, torc_cli_path: str = "torc"):
        """Initialize the CLI wrapper.

        Parameters
        ----------
        torc_cli_path : str, optional
            Path to the torc CLI binary, by default "torc" in PATH.
        """
        self.torc_cli_path = torc_cli_path

    def run_workflow(self, spec_path: str, api_url: str | None = None) -> dict[str, Any]:
        """Run a workflow locally using the torc CLI.

        Parameters
        ----------
        spec_path : str
            Path to the workflow specification file or workflow ID.
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        dict[str, Any]
            Dictionary with command output and status.
        """
        # Note: We don't use -f json here because run command may have real-time output
        cmd = [self.torc_cli_path, "run", spec_path]
        env = None

        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=300,  # 5 minute timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 5 minutes",
                "stdout": "",
                "stderr": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
            }

    def submit_workflow(self, spec_path: str, api_url: str | None = None) -> dict[str, Any]:
        """Submit a workflow to HPC/Slurm using the torc CLI.

        Parameters
        ----------
        spec_path : str
            Path to the workflow specification file or workflow ID.
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        dict[str, Any]
            Dictionary with command output and status.
        """
        # Note: We don't use -f json here to preserve any submission details
        cmd = [self.torc_cli_path, "submit", spec_path]
        env = None

        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60,  # 1 minute timeout for submission
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 1 minute",
                "stdout": "",
                "stderr": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
            }

    def create_workflow(self, spec_path: str, api_url: str | None = None) -> dict[str, Any]:
        """Create a workflow from a specification file.

        Parameters
        ----------
        spec_path : str
            Path to the workflow specification file.
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        dict[str, Any]
            Dictionary with command output and status.
        """
        cmd = [self.torc_cli_path, "-f", "json", "workflows", "create", spec_path]
        env = None

        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 1 minute",
                "stdout": "",
                "stderr": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
            }

    def initialize_workflow_direct(
        self, workflow_id: int, api_url: str | None = None, force: bool = False
    ) -> dict[str, Any]:
        """Initialize a workflow directly without any checks or prompts.

        Parameters
        ----------
        workflow_id : int
            The workflow ID to initialize.
        api_url : str | None, optional
            API URL to override the default, by default None.
        force : bool, optional
            Whether to use --force flag (for intermediate files), by default False.

        Returns
        -------
        dict[str, Any]
            Dictionary with command output and status.
        """
        cmd = [self.torc_cli_path, "workflows", "initialize", str(workflow_id)]
        if force:
            cmd.append("--force")

        env = None
        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 1 minute",
                "stdout": "",
                "stderr": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
            }

    def check_and_delete_files(
        self, workflow_id: int, existing_files: list[str]
    ) -> dict[str, Any]:
        """Delete existing output files and return status.

        Parameters
        ----------
        workflow_id : int
            The workflow ID.
        existing_files : list[str]
            List of file paths to delete.

        Returns
        -------
        dict[str, Any]
            Dictionary with success status, deleted_files list, and
            failed_deletions list of (file_path, error_msg) tuples.
        """
        deleted_files = []
        failed_deletions = []

        for file_path in existing_files:
            try:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
                    deleted_files.append(file_path)
            except Exception as e:
                failed_deletions.append((file_path, str(e)))

        return {
            "success": len(failed_deletions) == 0,
            "deleted_files": deleted_files,
            "failed_deletions": failed_deletions,
        }

    def _check_initialization(self, workflow_id: int, api_url: str | None = None) -> dict[str, Any]:
        """Check if initialization is safe to run (dry-run check).

        Parameters
        ----------
        workflow_id : int
            The workflow ID to check.
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        dict[str, Any]
            Dictionary with check result including success, data, and error keys.
        """
        return self._run_dry_run_check(workflow_id, "initialize", api_url)

    def _check_reinitialize(self, workflow_id: int, api_url: str | None = None) -> dict[str, Any]:
        """Check if reinitialization is safe to run (dry-run check).

        Parameters
        ----------
        workflow_id : int
            The workflow ID to check.
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        dict[str, Any]
            Dictionary with check result including success, data, and error keys.
        """
        return self._run_dry_run_check(workflow_id, "reinitialize", api_url)

    def _run_dry_run_check(
        self, workflow_id: int, command: str, api_url: str | None = None
    ) -> dict[str, Any]:
        """Run a dry-run check for initialize or reinitialize.

        Parameters
        ----------
        workflow_id : int
            The workflow ID to check.
        command : str
            Either "initialize" or "reinitialize".
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        dict[str, Any]
            Dictionary with check result including success, data, and error keys.
        """
        cmd = [
            self.torc_cli_path,
            "-f", "json",
            "workflows", command,
            str(workflow_id),
            "--dry-run"
        ]

        env = None
        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=30,
            )

            if result.returncode not in (0, 1):
                # Unexpected error
                msg = f"Dry-run check failed: {result.stderr}"
                return {
                    "success": False,
                    "error": msg,
                }

            try:
                data = json.loads(result.stdout)
                return {
                    "success": True,
                    "data": data,
                }
            except json.JSONDecodeError as e:
                msg = f"Failed to parse dry-run response: {e}"
                return {
                    "success": False,
                    "error": msg,
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Dry-run check timed out after 30 seconds",
            }
        except Exception as e:
            msg = f"Dry-run check failed: {e}"
            return {
                "success": False,
                "error": msg,
            }

    def check_workflow_needs_initialization(
        self, workflow_id: int, api_url: str | None = None
    ) -> dict[str, Any]:
        """Check if a workflow needs initialization before running.

        Parameters
        ----------
        workflow_id : int
            The workflow ID to check.
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        dict[str, Any]
            Dictionary with needs_init flag, check_data, and error keys.
        """
        try:
            # Use API wrapper to check if workflow needs initialization
            url = api_url or "http://localhost:8080/torc-service/v1"
            api_wrapper = TorcApiWrapper(url)
            result = api_wrapper.is_workflow_uninitialized(workflow_id)

            if result.get("success"):
                is_uninitialized = result.get("is_uninitialized", False)

                if is_uninitialized:
                    # Run dry-run check
                    check_result = self._check_initialization(workflow_id, api_url)
                    if not check_result["success"]:
                        return {
                            "needs_init": False,
                            "error": check_result.get("error", "Check failed"),
                        }
                    return {
                        "needs_init": True,
                        "check_data": check_result["data"],
                    }
                else:
                    return {
                        "needs_init": False,
                    }
            else:
                # API call failed, return error but assume doesn't need init
                return {
                    "needs_init": False,
                    "error": result.get("error", "API call failed"),
                }

        except Exception as e:
            return {
                "needs_init": False,
                "error": str(e),
            }

    def reinitialize_workflow_direct(
        self, workflow_id: int, api_url: str | None = None, force: bool = False
    ) -> dict[str, Any]:
        """Reinitialize a workflow directly without any checks or prompts.

        Parameters
        ----------
        workflow_id : int
            The workflow ID to reinitialize.
        api_url : str | None, optional
            API URL to override the default, by default None.
        force : bool, optional
            Whether to use --force flag, by default False.

        Returns
        -------
        dict[str, Any]
            Dictionary with command output and status.
        """
        cmd = [self.torc_cli_path, "workflows", "reinitialize", str(workflow_id)]
        if force:
            cmd.append("--force")

        env = None
        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 1 minute",
                "stdout": "",
                "stderr": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
            }

    def run_workflow_by_id(self, workflow_id: int, api_url: str | None = None) -> dict[str, Any]:
        """Run an existing workflow by ID using the torc CLI.

        Parameters
        ----------
        workflow_id : int
            The workflow ID to run.
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        dict[str, Any]
            Dictionary with command output and status.
        """
        cmd = [self.torc_cli_path, "workflows", "run", str(workflow_id)]
        env = None

        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=300,  # 5 minute timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 5 minutes",
                "stdout": "",
                "stderr": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
            }

    def submit_workflow_by_id(self, workflow_id: int, api_url: str | None = None) -> dict[str, Any]:
        """Submit an existing workflow by ID to HPC/Slurm using the torc CLI.

        Parameters
        ----------
        workflow_id : int
            The workflow ID to submit.
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        dict[str, Any]
            Dictionary with command output and status.
        """
        cmd = [self.torc_cli_path, "workflows", "submit", str(workflow_id)]
        env = None

        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60,  # 1 minute timeout for submission
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 1 minute",
                "stdout": "",
                "stderr": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
            }

    def delete_workflow(self, workflow_id: int, api_url: str | None = None) -> dict[str, Any]:
        """Delete a workflow.

        Parameters
        ----------
        workflow_id : int
            The workflow ID to delete.
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        dict[str, Any]
            Dictionary with command output and status.
        """
        cmd = [self.torc_cli_path, "workflows", "delete", str(workflow_id)]
        env = None

        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 1 minute",
                "stdout": "",
                "stderr": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
            }

    def reset_status_workflow(self, workflow_id: int, api_url: str | None = None) -> dict[str, Any]:
        """Reset the status of a workflow.

        Parameters
        ----------
        workflow_id : int
            The workflow ID to reset.
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        dict[str, Any]
            Dictionary with command output and status.
        """
        cmd = [self.torc_cli_path, "workflows", "reset-status", str(workflow_id), "--no-prompts"]
        env = None

        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 1 minute",
                "stdout": "",
                "stderr": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
            }

    def start_workflow_process(self, workflow_id: int, api_url: str | None = None) -> bool:
        """Start workflow execution process (non-blocking).

        Parameters
        ----------
        workflow_id : int
            The workflow ID to run.
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        bool
            True if process started successfully, False otherwise.
        """
        cmd = [self.torc_cli_path, "workflows", "run", str(workflow_id)]
        env = None

        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            # Clear previous state
            TorcCliWrapper.output_buffer = []

            # Start process (non-blocking)
            TorcCliWrapper.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1,  # Line buffered
            )
            return True
        except Exception:
            TorcCliWrapper.current_process = None
            return False

    def read_process_output(self) -> tuple[str, bool]:
        """Read new output from current process.

        Returns
        -------
        tuple[str, bool]
            Tuple of (new_output, is_complete).
        """
        if TorcCliWrapper.current_process is None:
            return "", True

        new_lines = []

        # Read available lines (non-blocking)
        try:
            # Check if there's data to read (Unix-like systems)
            if hasattr(select, 'select'):
                ready, _, _ = select.select([TorcCliWrapper.current_process.stdout], [], [], 0)
                if ready:
                    line = TorcCliWrapper.current_process.stdout.readline()
                    if line:
                        new_lines.append(line)
                        TorcCliWrapper.output_buffer.append(line)
            else:
                # Windows fallback - just try to read
                line = TorcCliWrapper.current_process.stdout.readline()
                if line:
                    new_lines.append(line)
                    TorcCliWrapper.output_buffer.append(line)
        except Exception:
            pass

        # Check if process finished
        returncode = TorcCliWrapper.current_process.poll()
        is_complete = returncode is not None

        if is_complete:
            # Read any remaining output
            try:
                remaining = TorcCliWrapper.current_process.stdout.read()
                if remaining:
                    new_lines.append(remaining)
                    TorcCliWrapper.output_buffer.append(remaining)
            except Exception:
                pass

            # Add completion message
            if returncode == 0:
                new_lines.append("\n✓ Execution completed successfully")
            else:
                new_lines.append(f"\n✗ Execution failed with return code {returncode}")

            TorcCliWrapper.current_process = None

        return "".join(new_lines), is_complete

    def cancel_current_process(self) -> bool:
        """Cancel the currently running process.

        Returns
        -------
        bool
            True if process was cancelled, False if no process was running.
        """
        if TorcCliWrapper.current_process is not None:
            try:
                TorcCliWrapper.current_process.terminate()
                try:
                    TorcCliWrapper.current_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    TorcCliWrapper.current_process.kill()
                TorcCliWrapper.current_process = None
                return True
            except Exception:
                pass
        return False

    def discover_resource_databases(
        self, base_dir: str = "output/resource_utilization"
    ) -> list[dict[str, str]]:
        """Discover resource monitoring database files.

        Parameters
        ----------
        base_dir : str, optional
            Directory to search for database files, by default "output/resource_utilization".

        Returns
        -------
        list[dict[str, str]]
            List of dictionaries with 'path' and 'name' keys.
        """
        databases = []
        base_path = Path(base_dir)

        if not base_path.exists():
            return databases

        # Find all .db files in the directory
        for db_file in base_path.glob("*.db"):
            databases.append({
                "path": str(db_file),
                "name": db_file.name
            })

        # Sort by modification time (newest first)
        databases.sort(key=lambda x: Path(x["path"]).stat().st_mtime, reverse=True)

        return databases

    def generate_resource_plots_json(
        self,
        db_path: str,
        output_dir: str = "output/resource_plots",
        prefix: str = "resource_plot"
    ) -> dict[str, Any]:
        """Generate JSON plots from resource monitoring database.

        Parameters
        ----------
        db_path : str
            Path to the resource monitoring database.
        output_dir : str, optional
            Directory to store generated JSON files, by default "output/resource_plots".
        prefix : str, optional
            Prefix for output filenames, by default "resource_plot".

        Returns
        -------
        dict[str, Any]
            Dictionary with success status and plot file paths or error message.
        """
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.torc_cli_path,
            "plot-resources",
            db_path,
            "--output-dir", output_dir,
            "--prefix", prefix,
            "--format", "json"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Find generated JSON files
                plot_files = list(output_path.glob(f"{prefix}*.json"))

                return {
                    "success": True,
                    "output": result.stdout,
                    "plots": [str(f) for f in sorted(plot_files)]
                }
            else:
                msg = f"Command failed with return code {result.returncode}"
                return {
                    "success": False,
                    "error": msg,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 60 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def load_plot_json(self, json_path: str) -> dict[str, Any] | None:
        """Load a Plotly JSON file.

        Parameters
        ----------
        json_path : str
            Path to the JSON file.

        Returns
        -------
        dict[str, Any] | None
            Plotly figure dictionary or None if loading fails.
        """
        try:
            path = Path(json_path)
            return json.loads(path.read_text())
        except Exception:
            return None

    def get_execution_plan(self, spec_or_id: str, api_url: str | None = None) -> dict[str, Any]:
        """Get execution plan for a workflow spec or existing workflow.

        Parameters
        ----------
        spec_or_id : str
            Path to workflow spec file OR workflow ID.
        api_url : str | None, optional
            API URL to override the default, by default None.

        Returns
        -------
        dict[str, Any]
            Dictionary with execution plan data in JSON format.
        """
        cmd = [self.torc_cli_path, "-f", "json", "workflows", "execution-plan", spec_or_id]
        env = None

        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60,
            )

            if result.returncode == 0:
                plan_data = json.loads(result.stdout)
                return {
                    "success": True,
                    "data": plan_data
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or result.stdout,
                    "stdout": result.stdout,
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 1 minute",
            }
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSON output: {e}"
            return {
                "success": False,
                "error": msg,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_job_results_report(
        self,
        workflow_id: int,
        api_url: str | None = None,
        output_dir: str = "output",
        all_runs: bool = False,
    ) -> dict[str, Any]:
        """Get job results report including log file paths.

        Parameters
        ----------
        workflow_id : int
            The workflow ID to get results for.
        api_url : str | None, optional
            API URL to override the default, by default None.
        output_dir : str, optional
            Output directory where job logs are stored, by default "output".
        all_runs : bool, optional
            Include all runs for each job, not just the latest, by default False.

        Returns
        -------
        dict[str, Any]
            Dictionary with success status and job results data.
        """
        cmd = [
            self.torc_cli_path,
            "-f", "json",
            "reports", "results",
            str(workflow_id),
            "--output-dir", output_dir,
        ]
        if all_runs:
            cmd.append("--all-runs")

        env = None
        if api_url:
            env = os.environ.copy()
            env["TORC_API_URL"] = api_url

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60,
            )

            if result.returncode == 0:
                report_data = json.loads(result.stdout)
                return {
                    "success": True,
                    "data": report_data,
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or result.stdout,
                    "stdout": result.stdout,
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 1 minute",
            }
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSON output: {e}"
            return {
                "success": False,
                "error": msg,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


def format_table_columns(data: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Generate column definitions for a Dash DataTable from data.

    Parameters
    ----------
    data : list[dict[str, Any]]
        List of dictionaries containing table data.

    Returns
    -------
    list[dict[str, str]]
        List of column definitions for DataTable.
    """
    if not data:
        return []

    # Get all unique keys from the data
    columns = set()
    for row in data:
        columns.update(row.keys())

    # Create column definitions
    return [
        {"name": col.replace("_", " ").title(), "id": col}
        for col in sorted(columns)
    ]
