"""Utility functions for the Torc Dash app."""

import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple
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

    def list_job_dependencies(self, workflow_id: int, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List job dependencies for a workflow.

        Args:
            workflow_id: The workflow ID
            offset: Starting offset for pagination
            limit: Maximum number of dependencies to return

        Returns:
            Dictionary with job dependency data
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
            return {"success": False, "error": f"Unexpected error: {str(e)}", "data": []}

    def list_job_file_relationships(self, workflow_id: int, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List job-file relationships for a workflow.

        Args:
            workflow_id: The workflow ID
            offset: Starting offset for pagination
            limit: Maximum number of relationships to return

        Returns:
            Dictionary with job-file relationship data
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
            return {"success": False, "error": f"Unexpected error: {str(e)}", "data": []}

    def list_job_user_data_relationships(self, workflow_id: int, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List job-user_data relationships for a workflow.

        Args:
            workflow_id: The workflow ID
            offset: Starting offset for pagination
            limit: Maximum number of relationships to return

        Returns:
            Dictionary with job-user_data relationship data
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
            return {"success": False, "error": f"Unexpected error: {str(e)}", "data": []}

    def delete_workflow(self, workflow_id: int) -> Dict[str, Any]:
        """Delete a workflow using the API.

        Args:
            workflow_id: The workflow ID to delete

        Returns:
            Dictionary with success status
        """
        try:
            api = self._get_api()
            api.delete_workflow(workflow_id)
            return {"success": True}
        except ApiException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

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

    # Class variables for simple process tracking
    current_process = None
    output_buffer = []

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
        # Note: We don't use -f json here because run command may have real-time output
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
        # Note: We don't use -f json here to preserve any submission details
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
        cmd = [self.torc_cli_path, "-f", "json", "workflows", "create", spec_path]
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

    def initialize_workflow(self, workflow_id: int, api_url: Optional[str] = None) -> Dict[str, Any]:
        """Initialize a workflow.

        Args:
            workflow_id: The workflow ID to initialize
            api_url: Optional API URL to override the default

        Returns:
            Dictionary with command output and status
        """
        cmd = [self.torc_cli_path, "workflows", "initialize", str(workflow_id)]
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

    def reinitialize_workflow(self, workflow_id: int, api_url: Optional[str] = None) -> Dict[str, Any]:
        """Re-initialize a workflow.

        Args:
            workflow_id: The workflow ID to re-initialize
            api_url: Optional API URL to override the default

        Returns:
            Dictionary with command output and status
        """
        cmd = [self.torc_cli_path, "workflows", "reinitialize", str(workflow_id)]
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

    def run_workflow_by_id(self, workflow_id: int, api_url: Optional[str] = None) -> Dict[str, Any]:
        """Run an existing workflow by ID using the torc CLI.

        Args:
            workflow_id: The workflow ID to run
            api_url: Optional API URL to override the default

        Returns:
            Dictionary with command output and status
        """
        cmd = [self.torc_cli_path, "workflows", "run", str(workflow_id)]
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

    def submit_workflow_by_id(self, workflow_id: int, api_url: Optional[str] = None) -> Dict[str, Any]:
        """Submit an existing workflow by ID to HPC/Slurm using the torc CLI.

        Args:
            workflow_id: The workflow ID to submit
            api_url: Optional API URL to override the default

        Returns:
            Dictionary with command output and status
        """
        cmd = [self.torc_cli_path, "workflows", "submit", str(workflow_id)]
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

    def delete_workflow(self, workflow_id: int, api_url: Optional[str] = None) -> Dict[str, Any]:
        """Delete a workflow.

        Args:
            workflow_id: The workflow ID to delete
            api_url: Optional API URL to override the default

        Returns:
            Dictionary with command output and status
        """
        cmd = [self.torc_cli_path, "workflows", "delete", str(workflow_id)]
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

    def reset_status_workflow(self, workflow_id: int, api_url: Optional[str] = None) -> Dict[str, Any]:
        """Reset the status of a workflow.

        Args:
            workflow_id: The workflow ID to reset
            api_url: Optional API URL to override the default

        Returns:
            Dictionary with command output and status
        """
        cmd = [self.torc_cli_path, "workflows", "reset-status", str(workflow_id), "--no-prompts"]
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

    def start_workflow_process(self, workflow_id: int, api_url: Optional[str] = None) -> bool:
        """Start workflow execution process (non-blocking).

        Args:
            workflow_id: The workflow ID to run
            api_url: Optional API URL to override the default

        Returns:
            True if process started successfully, False otherwise
        """
        cmd = [self.torc_cli_path, "workflows", "run", str(workflow_id)]
        env = None

        if api_url:
            import os
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

    def read_process_output(self) -> Tuple[str, bool]:
        """Read new output from current process.

        Returns:
            Tuple of (new_output, is_complete)
        """
        if TorcCliWrapper.current_process is None:
            return "", True

        new_lines = []

        # Read available lines (non-blocking)
        try:
            import select
            import sys

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
        except:
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
            except:
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

        Returns:
            True if process was cancelled, False if no process was running
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
            except:
                pass
        return False

    def discover_resource_databases(self, base_dir: str = "output/resource_utilization") -> List[Dict[str, str]]:
        """Discover resource monitoring database files.

        Args:
            base_dir: Directory to search for database files

        Returns:
            List of dictionaries with 'path' and 'name' keys
        """
        import os
        import pathlib

        databases = []
        base_path = pathlib.Path(base_dir)

        if not base_path.exists():
            return databases

        # Find all .db files in the directory
        for db_file in base_path.glob("*.db"):
            databases.append({
                "path": str(db_file),
                "name": db_file.name
            })

        # Sort by modification time (newest first)
        databases.sort(key=lambda x: os.path.getmtime(x["path"]), reverse=True)

        return databases

    def generate_resource_plots_json(
        self,
        db_path: str,
        output_dir: str = "output/resource_plots",
        prefix: str = "resource_plot"
    ) -> Dict[str, Any]:
        """Generate JSON plots from resource monitoring database.

        Args:
            db_path: Path to the resource monitoring database
            output_dir: Directory to store generated JSON files
            prefix: Prefix for output filenames

        Returns:
            Dictionary with success status and plot file paths or error message
        """
        import os
        import pathlib

        # Create output directory if it doesn't exist
        pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

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
                output_path = pathlib.Path(output_dir)
                plot_files = list(output_path.glob(f"{prefix}*.json"))

                return {
                    "success": True,
                    "output": result.stdout,
                    "plots": [str(f) for f in sorted(plot_files)]
                }
            else:
                return {
                    "success": False,
                    "error": f"Command failed with return code {result.returncode}",
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

    def load_plot_json(self, json_path: str) -> Optional[Dict[str, Any]]:
        """Load a Plotly JSON file.

        Args:
            json_path: Path to the JSON file

        Returns:
            Plotly figure dictionary or None if loading fails
        """
        import json
        import pathlib

        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None


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
