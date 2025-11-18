"""Utility functions for the Torc Dash app."""

import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional
from functools import wraps

from torc.openapi_client import (
    ApiClient,
    Configuration,
    DefaultApi,
    ApiException,
)

# Thread pool for running API calls in the background
executor = ThreadPoolExecutor(max_workers=4)


class TorcApiWrapper:
    """Wrapper for the Torc OpenAPI client with threading support."""

    def __init__(self, api_url: str, username: Optional[str] = None):
        """Initialize the API wrapper.

        Args:
            api_url: The Torc server API URL
            username: Optional username for workflow operations
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

    def list_workflows(self, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List all workflows.

        Args:
            offset: Starting offset for pagination
            limit: Maximum number of workflows to return

        Returns:
            Dictionary with workflow data
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
            return {"success": False, "error": f"Unexpected error: {str(e)}", "data": []}

    def list_jobs(self, workflow_id: int, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List jobs for a workflow.

        Args:
            workflow_id: The workflow ID
            offset: Starting offset for pagination
            limit: Maximum number of jobs to return

        Returns:
            Dictionary with job data
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
            return {"success": False, "error": f"Unexpected error: {str(e)}", "data": []}

    def list_results(self, workflow_id: int, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List results for a workflow.

        Args:
            workflow_id: The workflow ID
            offset: Starting offset for pagination
            limit: Maximum number of results to return

        Returns:
            Dictionary with result data
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
            return {"success": False, "error": f"Unexpected error: {str(e)}", "data": []}

    def list_events(self, workflow_id: int, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List events for a workflow.

        Args:
            workflow_id: The workflow ID
            offset: Starting offset for pagination
            limit: Maximum number of events to return

        Returns:
            Dictionary with event data
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
            return {"success": False, "error": f"Unexpected error: {str(e)}", "data": []}

    def list_files(self, workflow_id: int, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List files for a workflow.

        Args:
            workflow_id: The workflow ID
            offset: Starting offset for pagination
            limit: Maximum number of files to return

        Returns:
            Dictionary with file data
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
            return {"success": False, "error": f"Unexpected error: {str(e)}", "data": []}

    def list_user_data(self, workflow_id: int, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List user data for a workflow.

        Args:
            workflow_id: The workflow ID
            offset: Starting offset for pagination
            limit: Maximum number of user data items to return

        Returns:
            Dictionary with user data
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
            return {"success": False, "error": f"Unexpected error: {str(e)}", "data": []}

    def list_compute_nodes(self, workflow_id: int, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List compute nodes for a workflow.

        Args:
            workflow_id: The workflow ID
            offset: Starting offset for pagination
            limit: Maximum number of compute nodes to return

        Returns:
            Dictionary with compute node data
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
            return {"success": False, "error": f"Unexpected error: {str(e)}", "data": []}

    def list_resource_requirements(self, workflow_id: int, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List resource requirements for a workflow.

        Args:
            workflow_id: The workflow ID
            offset: Starting offset for pagination
            limit: Maximum number of resource requirements to return

        Returns:
            Dictionary with resource requirement data
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
            return {"success": False, "error": f"Unexpected error: {str(e)}", "data": []}

    @staticmethod
    def _model_to_dict(model: Any) -> Dict[str, Any]:
        """Convert a Pydantic model to a dictionary.

        Args:
            model: The Pydantic model to convert

        Returns:
            Dictionary representation of the model
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

    def __init__(self, torc_cli_path: str = "torc"):
        """Initialize the CLI wrapper.

        Args:
            torc_cli_path: Path to the torc CLI binary (default: "torc" in PATH)
        """
        self.torc_cli_path = torc_cli_path

    def run_workflow(self, spec_path: str, api_url: Optional[str] = None) -> Dict[str, Any]:
        """Run a workflow locally using the torc CLI.

        Args:
            spec_path: Path to the workflow specification file or workflow ID
            api_url: Optional API URL to override the default

        Returns:
            Dictionary with command output and status
        """
        cmd = [self.torc_cli_path, "run", spec_path]
        env = None

        if api_url:
            import os
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

    def submit_workflow(self, spec_path: str, api_url: Optional[str] = None) -> Dict[str, Any]:
        """Submit a workflow to HPC/Slurm using the torc CLI.

        Args:
            spec_path: Path to the workflow specification file or workflow ID
            api_url: Optional API URL to override the default

        Returns:
            Dictionary with command output and status
        """
        cmd = [self.torc_cli_path, "submit", spec_path]
        env = None

        if api_url:
            import os
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

    def create_workflow(self, spec_path: str, api_url: Optional[str] = None) -> Dict[str, Any]:
        """Create a workflow from a specification file.

        Args:
            spec_path: Path to the workflow specification file
            api_url: Optional API URL to override the default

        Returns:
            Dictionary with command output and status
        """
        cmd = [self.torc_cli_path, "workflows", "create", spec_path]
        env = None

        if api_url:
            import os
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


def format_table_columns(data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Generate column definitions for a Dash DataTable from data.

    Args:
        data: List of dictionaries containing table data

    Returns:
        List of column definitions for DataTable
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
