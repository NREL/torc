"""Callback functions for the Torc Dash app."""

import base64
import tempfile
import os
import json
from concurrent.futures import Future
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from dash import callback, Input, Output, State, html, no_update, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from .layouts import create_view_tab_layout, create_run_tab_layout, create_dag_tab_layout, create_monitor_tab_layout, create_resource_plots_tab_layout, create_data_table, create_execution_plan_view
from .utils import TorcApiWrapper, TorcCliWrapper, format_table_columns, executor


# ============================================================================
# Configuration Callbacks
# ============================================================================

@callback(
    Output("config-collapse", "is_open"),
    Input("config-collapse-button", "n_clicks"),
    State("config-collapse", "is_open"),
)
def toggle_config_collapse(n_clicks: int, is_open: bool) -> bool:
    """Toggle the configuration panel."""
    if n_clicks:
        return not is_open
    return is_open


@callback(
    Output("api-config-store", "data"),
    Output("config-status-message", "children"),
    Input("save-config-button", "n_clicks"),
    State("api-url-input", "value"),
    State("username-input", "value"),
    prevent_initial_call=True,
)
def save_configuration(
    n_clicks: int,
    api_url: str,
    username: str,
) -> Tuple[Dict[str, str], html.Div]:
    """Save the API configuration."""
    if not n_clicks:
        raise PreventUpdate

    if not api_url:
        return no_update, dbc.Alert(
            "API URL is required",
            color="danger",
            dismissable=True,
        )

    config = {
        "url": api_url.rstrip("/"),
        "username": username or "",
    }

    return config, dbc.Alert(
        [html.I(className="fas fa-check-circle me-2"), "Configuration saved successfully"],
        color="success",
        dismissable=True,
    )


# ============================================================================
# Global Workflow Selection Callbacks
# ============================================================================

@callback(
    Output("workflow-selection-collapse", "is_open"),
    Input("workflow-selection-collapse-button", "n_clicks"),
    State("workflow-selection-collapse", "is_open"),
)
def toggle_workflow_selection_collapse(n_clicks: int, is_open: bool) -> bool:
    """Toggle the workflow selection panel."""
    if n_clicks:
        return not is_open
    return is_open


@callback(
    Output("global-workflows-table-container", "children"),
    Output("global-refresh-interval", "disabled"),
    Input("global-refresh-workflows-button", "n_clicks"),
    Input("global-refresh-interval", "n_intervals"),
    State("api-config-store", "data"),
    State("global-auto-refresh-toggle", "value"),
    prevent_initial_call=False,
)
def update_global_workflows_table(
    n_clicks: int,
    n_intervals: int,
    config: Dict[str, str],
    auto_refresh: List[str],
) -> Tuple[html.Div, bool]:
    """Update the global workflows table."""
    # Only update on interval if auto-refresh is enabled
    from dash import ctx
    if ctx.triggered_id == "global-refresh-interval" and "auto" not in auto_refresh:
        raise PreventUpdate

    if not config:
        return html.Div("Please configure the API URL first"), True

    api_wrapper = TorcApiWrapper(config["url"], config.get("username"))
    result = api_wrapper.list_workflows(limit=1000)

    if not result["success"]:
        error_msg = result.get("error", "Unknown error")
        return dbc.Alert(f"Error: {error_msg}", color="danger"), True

    data = result["data"]

    if not data:
        return dbc.Alert("No workflows found", color="info"), True

    # Create table with delete buttons
    table_rows = []
    for idx, w in enumerate(data):
        row_cells = [
            html.Td(w.get("id")),
            html.Td(w.get("name", "")),
            html.Td(w.get("description", ""), style={"maxWidth": "300px", "overflow": "hidden", "textOverflow": "ellipsis"}),
            html.Td(w.get("status", "")),
            html.Td(w.get("timestamp", "")),
            html.Td(w.get("user", "")),
            html.Td(
                dbc.Button(
                    html.I(className="fas fa-trash"),
                    id={"type": "delete-workflow-btn", "index": w.get("id")},
                    color="danger",
                    size="sm",
                    outline=True,
                ),
                style={"textAlign": "center"}
            ),
        ]
        table_rows.append(
            html.Tr(
                row_cells,
                id={"type": "workflow-row", "index": w.get("id")},
                style={"cursor": "pointer"},
                n_clicks=0,
            )
        )

    table = dbc.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th("ID"),
                    html.Th("Name"),
                    html.Th("Description"),
                    html.Th("Status"),
                    html.Th("Timestamp"),
                    html.Th("User"),
                    html.Th("Actions", style={"textAlign": "center"}),
                ])
            ),
            html.Tbody(table_rows),
        ],
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mb-0",
    )

    # Disable auto-refresh interval if auto-refresh is not enabled
    interval_disabled = "auto" not in auto_refresh

    return table, interval_disabled


@callback(
    Output("selected-workflow-store", "data", allow_duplicate=True),
    Input({"type": "workflow-row", "index": ALL}, "n_clicks"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def store_global_selected_workflow(
    n_clicks: List[int],
    config: Dict[str, str],
) -> Optional[Dict[str, Any]]:
    """Store the selected workflow from global table row click."""
    from dash import ctx

    if not ctx.triggered or not any(n_clicks):
        raise PreventUpdate

    # Get the clicked row's workflow ID
    triggered_id = ctx.triggered_id
    if not triggered_id or triggered_id.get("type") != "workflow-row":
        raise PreventUpdate

    workflow_id = triggered_id.get("index")
    if not workflow_id:
        raise PreventUpdate

    # Fetch workflow details from API
    api_wrapper = TorcApiWrapper(config["url"], config.get("username"))
    try:
        # Get workflows and find the selected one
        result = api_wrapper.list_workflows(limit=10000)
        if not result["success"]:
            print(f"Error fetching workflows: {result.get('error')}")
            raise PreventUpdate

        # Find the workflow by ID
        for w in result["data"]:
            if w.get("id") == workflow_id:
                return {
                    "id": w.get("id"),
                    "name": w.get("name", ""),
                    "description": w.get("description", ""),
                    "status": w.get("status", ""),
                    "timestamp": w.get("timestamp", ""),
                    "user": w.get("user", ""),
                }

        print(f"Workflow {workflow_id} not found")
        raise PreventUpdate
    except Exception as e:
        print(f"Error fetching workflow {workflow_id}: {e}")
        raise PreventUpdate


@callback(
    Output("selected-workflow-badge", "children"),
    Input("selected-workflow-store", "data"),
)
def update_selected_workflow_badge(
    selected_workflow: Optional[Dict[str, Any]],
) -> str:
    """Update the badge showing the currently selected workflow."""
    if selected_workflow and "id" in selected_workflow:
        workflow_name = selected_workflow.get("name", "Unknown")
        workflow_id = selected_workflow["id"]
        return f"{workflow_name} (ID: {workflow_id})"
    return "None selected"


# ============================================================================
# Workflow Deletion Callbacks
# ============================================================================

@callback(
    Output("delete-workflow-modal", "is_open", allow_duplicate=True),
    Output("delete-workflow-modal-body", "children"),
    Output("delete-workflow-id-store", "data"),
    Input({"type": "delete-workflow-btn", "index": ALL}, "n_clicks"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def open_delete_workflow_modal(
    n_clicks: List[int],
    config: Dict[str, str],
):
    """Open confirmation modal when delete button is clicked."""
    from dash import ctx

    if not ctx.triggered or not any(n_clicks):
        raise PreventUpdate

    # Get the clicked button's workflow ID
    triggered_id = ctx.triggered_id
    if not triggered_id or triggered_id.get("type") != "delete-workflow-btn":
        raise PreventUpdate

    workflow_id = triggered_id.get("index")
    if not workflow_id:
        raise PreventUpdate

    # Fetch workflow details to show in confirmation
    api_wrapper = TorcApiWrapper(config["url"], config.get("username"))
    try:
        # Get workflows and find the one we're deleting
        result = api_wrapper.list_workflows(limit=10000)
        if not result["success"]:
            return True, html.P(f"Error loading workflow: {result.get('error')}", className="text-danger"), workflow_id

        # Find the workflow by ID
        workflow = None
        for w in result["data"]:
            if w.get("id") == workflow_id:
                workflow = w
                break

        if not workflow:
            return True, html.P(f"Workflow {workflow_id} not found", className="text-danger"), workflow_id

        modal_body = html.Div([
            html.P([
                "Are you sure you want to delete workflow ",
                html.Strong(f"{workflow.get('name', 'Unknown')} (ID: {workflow_id})"),
                "?"
            ]),
            html.P("This action cannot be undone.", className="text-danger"),
        ])

        return True, modal_body, workflow_id
    except Exception as e:
        return True, html.P(f"Error loading workflow details: {str(e)}", className="text-danger"), workflow_id


@callback(
    Output("delete-workflow-modal", "is_open", allow_duplicate=True),
    Output("global-workflows-table-container", "children", allow_duplicate=True),
    Output("global-refresh-interval", "disabled", allow_duplicate=True),
    Input("delete-workflow-confirm-btn", "n_clicks"),
    Input("delete-workflow-cancel-btn", "n_clicks"),
    State("delete-workflow-id-store", "data"),
    State("api-config-store", "data"),
    State("global-auto-refresh-toggle", "value"),
    prevent_initial_call=True,
)
def handle_delete_workflow_modal(
    confirm_clicks: int,
    cancel_clicks: int,
    workflow_id: int,
    config: Dict[str, str],
    auto_refresh: List[str],
):
    """Handle delete confirmation or cancellation."""
    from dash import ctx

    if not ctx.triggered:
        raise PreventUpdate

    button_id = ctx.triggered_id
    print(f"Delete modal handler triggered by: {button_id}, workflow_id: {workflow_id}")

    # Cancel button clicked - just close modal
    if button_id == "delete-workflow-cancel-btn":
        return False, no_update, no_update

    # Confirm button clicked - delete workflow
    if button_id == "delete-workflow-confirm-btn":
        if not workflow_id:
            print("ERROR: workflow_id is None or falsy")
            return False, dbc.Alert("Error: No workflow selected", color="danger"), True

        # Use API wrapper instead of CLI to avoid confirmation prompt
        api_wrapper = TorcApiWrapper(config["url"], config.get("username"))
        print(f"Calling delete_workflow for workflow_id: {workflow_id}")
        result = api_wrapper.delete_workflow(workflow_id)
        print(f"Delete result: {result}")

        if result["success"]:
            # Refresh the workflows table
            workflows_result = api_wrapper.list_workflows(limit=1000)

            if workflows_result["success"]:
                data = workflows_result["data"]
                if not data:
                    return False, dbc.Alert("No workflows found", color="info"), True

                # Recreate table
                table_rows = []
                for idx, w in enumerate(data):
                    row_cells = [
                        html.Td(w.get("id")),
                        html.Td(w.get("name", "")),
                        html.Td(w.get("description", ""), style={"maxWidth": "300px", "overflow": "hidden", "textOverflow": "ellipsis"}),
                        html.Td(w.get("status", "")),
                        html.Td(w.get("timestamp", "")),
                        html.Td(w.get("user", "")),
                        html.Td(
                            dbc.Button(
                                html.I(className="fas fa-trash"),
                                id={"type": "delete-workflow-btn", "index": w.get("id")},
                                color="danger",
                                size="sm",
                                outline=True,
                            ),
                            style={"textAlign": "center"}
                        ),
                    ]
                    table_rows.append(
                        html.Tr(
                            row_cells,
                            id={"type": "workflow-row", "index": w.get("id")},
                            style={"cursor": "pointer"},
                            n_clicks=0,
                        )
                    )

                table = dbc.Table(
                    [
                        html.Thead(
                            html.Tr([
                                html.Th("ID"),
                                html.Th("Name"),
                                html.Th("Description"),
                                html.Th("Status"),
                                html.Th("Timestamp"),
                                html.Th("User"),
                                html.Th("Actions", style={"textAlign": "center"}),
                            ])
                        ),
                        html.Tbody(table_rows),
                    ],
                    striped=True,
                    bordered=True,
                    hover=True,
                    responsive=True,
                    className="mb-0",
                )

                interval_disabled = "auto" not in auto_refresh
                return False, table, interval_disabled
            else:
                return False, dbc.Alert(f"Error refreshing workflows: {workflows_result.get('error')}", color="danger"), True
        else:
            error_msg = result.get('error', 'Unknown error')
            stderr = result.get('stderr', '')
            full_error = f"Error deleting workflow: {error_msg}"
            if stderr:
                full_error += f"\n{stderr}"
            print(f"Delete failed: {full_error}")
            return False, dbc.Alert(full_error, color="danger"), True

    print(f"Unhandled case in delete modal: button_id={button_id}")
    raise PreventUpdate


# ============================================================================
# Tab Navigation Callbacks
# ============================================================================

@callback(
    Output("view-tab-content", "style"),
    Output("run-tab-content", "style"),
    Output("dag-tab-content", "style"),
    Output("monitor-tab-content", "style"),
    Output("plots-tab-content", "style"),
    Input("main-tabs", "active_tab"),
)
def control_tab_visibility(active_tab: str):
    """Control which tab content is visible without re-rendering."""
    return (
        {"display": "block", "marginTop": "1rem"} if active_tab == "view-tab" else {"display": "none"},
        {"display": "block", "marginTop": "1rem"} if active_tab == "run-tab" else {"display": "none"},
        {"display": "block", "marginTop": "1rem"} if active_tab == "dag-tab" else {"display": "none"},
        {"display": "block", "marginTop": "1rem"} if active_tab == "monitor-tab" else {"display": "none"},
        {"display": "block", "marginTop": "1rem"} if active_tab == "plots-tab" else {"display": "none"},
    )


# Initialize tab content once on startup
@callback(
    Output("view-tab-content", "children"),
    Input("api-config-store", "data"),
    prevent_initial_call=False,
)
def initialize_view_tab(config):
    """Initialize the View tab content once."""
    return create_view_tab_layout()


@callback(
    Output("run-tab-content", "children"),
    Input("api-config-store", "data"),
    prevent_initial_call=False,
)
def initialize_run_tab(config):
    """Initialize the Manage Workflows tab content once."""
    return create_run_tab_layout()


@callback(
    Output("dag-tab-content", "children"),
    Input("api-config-store", "data"),
    prevent_initial_call=False,
)
def initialize_dag_tab(config):
    """Initialize the DAG Visualization tab content once."""
    return create_dag_tab_layout()


@callback(
    Output("monitor-tab-content", "children"),
    Input("api-config-store", "data"),
    prevent_initial_call=False,
)
def initialize_monitor_tab(config):
    """Initialize the Monitor Events tab content once."""
    return create_monitor_tab_layout()


@callback(
    Output("plots-tab-content", "children"),
    Input("api-config-store", "data"),
    prevent_initial_call=False,
)
def initialize_plots_tab(config):
    """Initialize the Resource Plots tab content once."""
    return create_resource_plots_tab_layout()


# ============================================================================
# View Tab Callbacks
# ============================================================================

# Old callbacks removed - workflow selection now handled by global panel (lines 73-192)


@callback(
    Output("workflow-details-panel", "children"),
    Input("selected-workflow-store", "data"),
    Input("refresh-workflow-details-button", "n_clicks"),
    State("api-config-store", "data"),
)
def show_workflow_details_panel(
    workflow: Optional[Dict[str, Any]],
    n_clicks: int,
    config: Dict[str, str],
) -> html.Div:
    """Show the workflow details panel on the right when a workflow is selected or refresh button is clicked."""
    if not workflow:
        return dbc.Alert(
            [
                html.I(className="fas fa-info-circle me-2"),
                "Select a workflow from the list to view its details"
            ],
            color="info",
        )

    workflow_id = workflow.get("id")
    workflow_name = workflow.get("name", "Unknown")

    return dbc.Card(
        [
            dbc.CardHeader(
                html.H5(
                    [
                        html.I(className="fas fa-info-circle me-2"),
                        f"Workflow: {workflow_name} (ID: {workflow_id})"
                    ],
                    className="mb-0"
                )
            ),
            dbc.CardBody(
                [
                    # Workflow info section
                    dbc.Row(
                        [
                            dbc.Col([html.Strong("Status: "), str(workflow.get("status", "N/A"))], md=4),
                            dbc.Col([html.Strong("User: "), workflow.get("user", "N/A")], md=4),
                            dbc.Col([html.Strong("Timestamp: "), str(workflow.get("timestamp", "N/A"))], md=4),
                        ],
                        className="mb-3"
                    ),
                    dbc.Row(
                        [
                            dbc.Col([html.Strong("Description: "), html.P(workflow.get("description", "No description"), className="text-muted mb-0")]),
                        ],
                        className="mb-3"
                    ),

                    html.Hr(),

                    # Tabs for different resource types
                    dbc.Tabs(
                        [
                            dbc.Tab(label="Jobs", tab_id="jobs-tab"),
                            dbc.Tab(label="Results", tab_id="results-tab"),
                            dbc.Tab(label="Events", tab_id="events-tab"),
                            dbc.Tab(label="Files", tab_id="files-tab"),
                            dbc.Tab(label="User Data", tab_id="user_data-tab"),
                            dbc.Tab(label="Compute Nodes", tab_id="compute_nodes-tab"),
                            dbc.Tab(label="Resource Requirements", tab_id="resource_requirements-tab"),
                        ],
                        id="resource-type-tabs",
                        active_tab="jobs-tab",
                    ),

                    html.Div(id="resource-details-container", className="mt-3"),
                ]
            ),
        ]
    )


@callback(
    Output("resource-details-container", "children"),
    Input("resource-type-tabs", "active_tab"),
    Input("global-refresh-interval", "n_intervals"),
    State("selected-workflow-store", "data"),
    State("api-config-store", "data"),
    State("global-auto-refresh-toggle", "value"),
    prevent_initial_call=False,
)
def update_resource_details(
    active_tab: str,
    n_intervals: int,
    workflow: Optional[Dict[str, Any]],
    config: Dict[str, str],
    auto_refresh: List[str],
) -> html.Div:
    """Update the resource details based on selected tab."""
    # Only update on interval if auto-refresh is enabled
    from dash import ctx
    if ctx.triggered_id == "global-refresh-interval" and "auto" not in auto_refresh:
        raise PreventUpdate

    if not workflow or not config:
        raise PreventUpdate

    workflow_id = workflow.get("id")

    # Extract resource type from tab_id (e.g., "jobs-tab" -> "jobs")
    resource_type = active_tab.replace("-tab", "")

    api_wrapper = TorcApiWrapper(config["url"], config.get("username"))

    # Fetch data based on resource type
    try:
        method_map = {
            "jobs": api_wrapper.list_jobs,
            "results": api_wrapper.list_results,
            "events": api_wrapper.list_events,
            "files": api_wrapper.list_files,
            "user_data": api_wrapper.list_user_data,
            "compute_nodes": api_wrapper.list_compute_nodes,
            "resource_requirements": api_wrapper.list_resource_requirements,
        }

        if resource_type not in method_map:
            return dbc.Alert(f"Unknown resource type: {resource_type}", color="danger")

        result = method_map[resource_type](workflow_id, limit=1000)

        if not result["success"]:
            error_msg = result.get("error", "Unknown error")
            return dbc.Alert(f"Error: {error_msg}", color="danger", dismissable=True)

        data = result["data"]

        if not data:
            return dbc.Alert(f"No {resource_type} found for this workflow", color="info")

        # Filter and format data for specific resource types
        if resource_type == "jobs":
            # Limit jobs to ID, Name, Status, Command only
            filtered_data = []
            for item in data:
                filtered_data.append({
                    "id": item.get("id"),
                    "name": item.get("name", ""),
                    "status": item.get("status", ""),
                    "command": item.get("command", ""),
                })
            data = filtered_data
            # Use explicit column order for jobs
            columns = [
                {"name": "ID", "id": "id"},
                {"name": "Name", "id": "name"},
                {"name": "Status", "id": "status"},
                {"name": "Command", "id": "command"},
            ]
        elif resource_type == "events":
            # Convert event data field to JSON string for display and filter to show only selected columns
            import json
            filtered_data = []
            for item in data:
                # Convert the 'data' field to a JSON string if it exists and is not already a string
                data_field = item.get("data")
                if data_field and not isinstance(data_field, str):
                    data_str = json.dumps(data_field)
                else:
                    data_str = data_field if data_field else ""

                filtered_data.append({
                    "id": item.get("id", ""),
                    "timestamp": item.get("timestamp", ""),
                    "data": data_str,
                })

            data = filtered_data
            # Use explicit column order for events
            columns = [
                {"name": "ID", "id": "id"},
                {"name": "Timestamp", "id": "timestamp"},
                {"name": "Data", "id": "data"},
            ]
        elif resource_type == "results":
            # Add job names to results for better readability
            # First, fetch all jobs for this workflow to create a job_id -> job_name mapping
            jobs_result = api_wrapper.list_jobs(workflow_id, limit=10000)
            job_name_map = {}
            if jobs_result["success"] and jobs_result["data"]:
                for job in jobs_result["data"]:
                    job_name_map[job.get("id")] = job.get("name", "")

            # Filter and format data for results with only selected columns
            filtered_data = []
            for item in data:
                job_id = item.get("job_id")
                job_name = job_name_map.get(job_id, "-")

                # Format memory
                peak_mem_bytes = item.get("peak_memory_bytes")
                if peak_mem_bytes:
                    mb = peak_mem_bytes / (1024 * 1024)
                    if mb < 1024:
                        peak_mem = f"{mb:.1f}MB"
                    else:
                        peak_mem = f"{mb/1024:.2f}GB"
                else:
                    peak_mem = "-"

                # Format CPU
                peak_cpu = item.get("peak_cpu_percent")
                peak_cpu_str = f"{peak_cpu:.1f}%" if peak_cpu is not None else "-"

                # Format exec time
                exec_time = item.get("exec_time_minutes", 0)
                exec_time_str = f"{exec_time:.2f}"

                filtered_data.append({
                    "job_id": job_id,
                    "job_name": job_name,
                    "run_id": item.get("run_id", ""),
                    "return_code": item.get("return_code", ""),
                    "status": item.get("status", ""),
                    "exec_time": exec_time_str,
                    "peak_memory": peak_mem,
                    "peak_cpu": peak_cpu_str,
                })

            data = filtered_data
            # Use explicit column order for results
            columns = [
                {"name": "Job ID", "id": "job_id"},
                {"name": "Job Name", "id": "job_name"},
                {"name": "Run ID", "id": "run_id"},
                {"name": "Return Code", "id": "return_code"},
                {"name": "Status", "id": "status"},
                {"name": "Exec Time (min)", "id": "exec_time"},
                {"name": "Peak Mem", "id": "peak_memory"},
                {"name": "Peak CPU %", "id": "peak_cpu"},
            ]
        elif resource_type == "files":
            # Format st_mtime as human-readable timestamp and reorder columns
            from datetime import datetime
            filtered_data = []
            for item in data:
                # Convert st_mtime from Unix timestamp to readable format
                st_mtime = item.get("st_mtime")
                if st_mtime:
                    try:
                        dt = datetime.fromtimestamp(st_mtime)
                        modified_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except (ValueError, TypeError, OSError):
                        modified_time = "-"
                else:
                    modified_time = "-"

                filtered_data.append({
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "path": item.get("path", ""),
                    "modified_time": modified_time,
                })

            data = filtered_data
            # Use explicit column order for files
            columns = [
                {"name": "ID", "id": "id"},
                {"name": "Name", "id": "name"},
                {"name": "Path", "id": "path"},
                {"name": "Modified Time", "id": "modified_time"},
            ]
        elif resource_type == "compute_nodes":
            # Filter and reorder columns for compute nodes
            filtered_data = []
            for item in data:
                filtered_data.append({
                    "id": item.get("id", ""),
                    "hostname": item.get("hostname", ""),
                    "compute_node_type": item.get("compute_node_type", ""),
                    "is_active": item.get("is_active", ""),
                    "start_time": item.get("start_time", ""),
                    "time_limit": item.get("time_limit", ""),
                    "num_cpus": item.get("num_cpus", ""),
                    "memory_gb": item.get("memory_gb", ""),
                    "num_gpus": item.get("num_gpus", ""),
                    "num_nodes": item.get("num_nodes", ""),
                })

            data = filtered_data
            # Use explicit column order for compute nodes
            columns = [
                {"name": "ID", "id": "id"},
                {"name": "Hostname", "id": "hostname"},
                {"name": "Type", "id": "compute_node_type"},
                {"name": "Is Active", "id": "is_active"},
                {"name": "Start Time", "id": "start_time"},
                {"name": "Time Limit", "id": "time_limit"},
                {"name": "Num CPUs", "id": "num_cpus"},
                {"name": "Memory GB", "id": "memory_gb"},
                {"name": "Num GPUs", "id": "num_gpus"},
                {"name": "Num Nodes", "id": "num_nodes"},
            ]
        elif resource_type == "resource_requirements":
            # Filter and reorder columns for resource requirements
            filtered_data = []
            for item in data:
                filtered_data.append({
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "num_cpus": item.get("num_cpus", ""),
                    "memory": item.get("memory", ""),
                    "num_gpus": item.get("num_gpus", ""),
                    "num_nodes": item.get("num_nodes", ""),
                    "runtime": item.get("runtime", ""),
                })

            data = filtered_data
            # Use explicit column order for resource requirements
            columns = [
                {"name": "ID", "id": "id"},
                {"name": "Name", "id": "name"},
                {"name": "Num CPUs", "id": "num_cpus"},
                {"name": "Memory", "id": "memory"},
                {"name": "Num GPUs", "id": "num_gpus"},
                {"name": "Num Nodes", "id": "num_nodes"},
                {"name": "Runtime", "id": "runtime"},
            ]
        else:
            # Format columns for other resource types
            columns = format_table_columns(data)

        # Enable selection for files (for file preview)
        enable_selection = (resource_type == "files")
        table = create_data_table(data, columns, f"{resource_type}-table", enable_selection)

        # Add file preview section if this is the files tab
        content = [
            html.P(f"Total {resource_type}: {result['total']}", className="text-muted mb-2"),
            table,
        ]

        if resource_type == "files":
            content.append(html.Div(id="file-preview-container", className="mt-3"))

        return html.Div(content)

    except Exception as e:
        return dbc.Alert(f"Unexpected error: {str(e)}", color="danger", dismissable=True)


@callback(
    Output("file-preview-container", "children"),
    Input("files-table", "selected_rows"),
    State("files-table", "data"),
)
def show_file_preview(
    selected_rows: List[int],
    table_data: List[Dict[str, Any]],
) -> html.Div:
    """Show file preview when a file is selected."""
    if not selected_rows or not table_data:
        return html.Div()

    row_index = selected_rows[0]
    if row_index >= len(table_data):
        return html.Div()

    file_data = table_data[row_index]
    file_path = file_data.get("path", "")
    file_name = file_data.get("name", "Unknown")
    is_output = file_data.get("is_output", False)

    # Read file contents
    try:
        with open(file_path, "r") as f:
            content = f.read(10000)  # Read first 10KB
            truncated = len(content) == 10000

        # Pretty-print JSON files
        if file_path.lower().endswith('.json'):
            try:
                import json
                # Parse the JSON
                json_data = json.loads(content)
                # Pretty-print with indent level 2
                content = json.dumps(json_data, indent=2)
                if truncated:
                    content += "\n\n... (file truncated, showing first 10KB)"
            except json.JSONDecodeError as e:
                # If JSON parsing fails, show original content with error note
                content = f"# Warning: Invalid JSON - {str(e)}\n\n" + content
                if truncated:
                    content += "\n\n... (file truncated, showing first 10KB)"
        else:
            if truncated:
                content += "\n\n... (file truncated, showing first 10KB)"

    except Exception as e:
        content = f"Error reading file: {str(e)}"

    output_badge = ""
    if is_output:
        output_badge = dbc.Badge("Output File", color="success", className="ms-2")

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-file-alt me-2"),
                    f"File Preview: {file_name}",
                    output_badge,
                ]
            ),
            dbc.CardBody(
                [
                    html.P([html.Strong("Path: "), file_path], className="text-muted small"),
                    html.Pre(
                        content,
                        style={
                            "backgroundColor": "#f8f9fa",
                            "padding": "10px",
                            "borderRadius": "5px",
                            "maxHeight": "400px",
                            "overflowY": "auto",
                            "fontSize": "12px",
                        }
                    ),
                ]
            ),
        ],
        className="mt-3"
    )


# ============================================================================
# Run Tab Callbacks
# ============================================================================

@callback(
    Output("uploaded-spec-store", "data"),
    Output("upload-status", "children"),
    Input("upload-workflow-spec", "contents"),
    State("upload-workflow-spec", "filename"),
)
def handle_file_upload(
    contents: Optional[str],
    filename: Optional[str],
) -> Tuple[Optional[Dict[str, str]], Optional[html.Div]]:
    """Handle workflow specification file upload."""
    if contents is None:
        raise PreventUpdate

    # Decode the file contents
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string).decode("utf-8")

    return (
        {"filename": filename, "content": decoded},
        dbc.Alert(
            [
                html.I(className="fas fa-check-circle me-2"),
                f"File '{filename}' uploaded successfully"
            ],
            color="success",
            dismissable=True,
        ),
    )


@callback(
    Output("existing-workflow-info", "children"),
    Input("selected-workflow-store", "data"),
)
def show_existing_workflow_info(
    workflow: Optional[Dict[str, Any]],
) -> Optional[html.Div]:
    """Show information about the selected workflow."""
    if not workflow:
        return dbc.Card(
            dbc.CardBody(
                [
                    html.P(
                        "No workflow selected. Go to the 'View Resources' tab, "
                        "select 'Workflows' from the resource type dropdown, "
                        "and click on a workflow row to select it.",
                        className="text-muted mb-0",
                    ),
                ]
            ),
            className="mt-3",
        )

    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(
                    [
                        html.I(className="fas fa-check-circle text-success me-2"),
                        "Selected Workflow"
                    ],
                    className="mb-3"
                ),
                html.P([html.Strong("ID: "), str(workflow.get("id", "N/A"))]),
                html.P([html.Strong("Name: "), workflow.get("name", "N/A")]),
                html.P([html.Strong("User: "), workflow.get("user", "N/A")]),
                html.P([html.Strong("Status: "), str(workflow.get("status", "N/A"))]),
            ]
        ),
        className="mt-3",
        color="light",
    )


@callback(
    Output("workflow-creation-status", "children"),
    Output("workflows-store", "data"),
    Output("selected-workflow-store", "data", allow_duplicate=True),
    Input("create-workflow-button", "n_clicks"),
    State("workflow-source-tabs", "active_tab"),
    State("uploaded-spec-store", "data"),
    State("workflow-spec-path-input", "value"),
    State("initialize-workflow-checkbox", "value"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def create_workflow_from_spec(
    n_clicks: int,
    workflow_source_tab: str,
    uploaded_spec: Optional[Dict[str, str]],
    spec_path: Optional[str],
    initialize_checkbox: List[str],
    config: Dict[str, str],
) -> Tuple[html.Div, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Create a workflow from specification."""
    if not n_clicks:
        raise PreventUpdate

    cli_wrapper = TorcCliWrapper()
    workflow_spec_path = None
    temp_file = None

    try:
        # Determine workflow source
        if workflow_source_tab == "new-workflow-tab":
            if uploaded_spec:
                # Save to temp file
                temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
                temp_file.write(uploaded_spec["content"])
                temp_file.close()
                workflow_spec_path = temp_file.name
            elif spec_path:
                workflow_spec_path = spec_path
            else:
                return dbc.Alert("Error: No workflow specification provided", color="danger"), None, None
        else:
            return dbc.Alert("Error: Can only create from new workflow specification", color="warning"), None, None

        # Create workflow
        result = cli_wrapper.create_workflow(workflow_spec_path, api_url=config.get("url"))

        if not result["success"]:
            error_msg = result.get("error", "Unknown error")
            return dbc.Alert(
                [
                    html.H6("Creation Failed", className="alert-heading"),
                    html.P(f"Error: {error_msg}"),
                    html.Hr(),
                    html.P(result.get("stderr", ""), className="mb-0 small"),
                ],
                color="danger",
            ), None, None

        # Extract workflow ID from JSON output
        import json
        try:
            output_data = json.loads(result["stdout"])
            workflow_id = output_data.get("workflow_id")
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            return dbc.Alert(
                [
                    html.H6("Error parsing output", className="alert-heading"),
                    html.P(f"Could not parse workflow ID from JSON output: {str(e)}"),
                    html.Hr(),
                    html.P(f"Output: {result['stdout']}", className="mb-0 small"),
                ],
                color="danger"
            ), None, None

        if not workflow_id:
            return dbc.Alert("Error: Workflow ID not found in output", color="danger"), None, None

        # Initialize if checkbox is checked
        if "initialize" in initialize_checkbox:
            init_result = cli_wrapper.initialize_workflow(workflow_id, api_url=config.get("url"))
            if not init_result["success"]:
                # Still store the workflow even if init failed
                workflow_data = {"id": workflow_id}
                return dbc.Alert(
                    [
                        html.H6("Workflow created but initialization failed", className="alert-heading"),
                        html.P(f"Workflow ID: {workflow_id}"),
                        html.P(f"Error: {init_result.get('error', 'Unknown error')}"),
                    ],
                    color="warning",
                ), workflow_data, workflow_data

        # Fetch the full workflow data from the API to populate the selected workflow
        api_wrapper = TorcApiWrapper(config["url"], config.get("username"))
        workflows_result = api_wrapper.list_workflows(limit=1000)

        workflow_data = {"id": workflow_id}
        if workflows_result["success"]:
            # Find the created workflow in the list
            created_workflow = next(
                (w for w in workflows_result["data"] if w.get("id") == workflow_id),
                None
            )
            if created_workflow:
                workflow_data = created_workflow

        success_msg = [
            html.H6("Workflow Created Successfully", className="alert-heading"),
            html.P(f"Workflow ID: {workflow_id}"),
        ]

        if "initialize" in initialize_checkbox:
            success_msg.append(html.P("Workflow has been initialized and is ready to run.", className="mb-0"))
        else:
            success_msg.append(html.P("You can now execute this workflow below.", className="mb-0"))

        return dbc.Alert(success_msg, color="success"), workflow_data, workflow_data

    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger"), None, None

    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass


@callback(
    Output("execution-output", "children"),
    Output("cancel-execution-button", "disabled"),
    Output("execute-workflow-button", "disabled"),
    Output("execution-poll-interval", "disabled"),
    Input("execute-workflow-button", "n_clicks"),
    State("workflow-source-tabs", "active_tab"),
    State("selected-workflow-store", "data"),
    State("workflows-store", "data"),
    State("execution-mode-radio", "value"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def execute_workflow(
    n_clicks: int,
    workflow_source_tab: str,
    selected_workflow: Optional[Dict[str, Any]],
    created_workflow: Optional[Dict[str, Any]],
    execution_mode: str,
    config: Dict[str, str],
):
    """Execute or submit a workflow."""
    if not n_clicks:
        raise PreventUpdate

    cli_wrapper = TorcCliWrapper()

    # Determine which workflow to execute
    workflow_id = None

    if workflow_source_tab == "new-workflow-tab":
        # Must have created a workflow first
        if created_workflow and "id" in created_workflow:
            workflow_id = created_workflow["id"]
        else:
            return "Error: Please create the workflow first using the 'Create Workflow' button above.", True, False, True
    elif workflow_source_tab == "existing-workflow-tab":
        # Use selected workflow
        if selected_workflow and "id" in selected_workflow:
            workflow_id = selected_workflow["id"]
        else:
            return "Error: No workflow selected. Please select a workflow from the 'View Resources' tab first.", True, False, True
    else:
        return "Error: Unknown workflow source", True, False, True

    try:
        if execution_mode == "run":
            # Start process (non-blocking) with real-time output
            if cli_wrapper.start_workflow_process(workflow_id, api_url=config.get("url")):
                return f"Starting workflow {workflow_id} execution...\n", False, True, False
            else:
                return f"✗ Failed to start workflow {workflow_id}", True, False, True
        else:
            # Submit to scheduler (blocking, but usually fast)
            result = cli_wrapper.submit_workflow_by_id(
                workflow_id,
                api_url=config.get("url")
            )

            output_lines = [f"Submitting workflow {workflow_id} to HPC/Slurm...\n"]
            if result["success"]:
                output_lines.append(result["stdout"])
                if result["stderr"]:
                    output_lines.append(f"\nWarnings/Info:\n{result['stderr']}")
                output_lines.append("\n✓ Submission completed successfully")
            else:
                error_msg = result.get("error", "Unknown error")
                output_lines.append(f"\n✗ Submission failed: {error_msg}\n")
                output_lines.append(f"\nStdout:\n{result.get('stdout', '')}")
                output_lines.append(f"\nStderr:\n{result.get('stderr', '')}")

            return "\n".join(output_lines), True, False, True

    except Exception as e:
        return f"Error: {str(e)}", True, False, True


@callback(
    Output("execution-output", "children", allow_duplicate=True),
    Output("cancel-execution-button", "disabled", allow_duplicate=True),
    Input("cancel-execution-button", "n_clicks"),
    State("execution-output", "children"),
    prevent_initial_call=True,
)
def cancel_workflow_execution(n_clicks: int, current_output: Optional[str]) -> tuple:
    """Cancel an executing workflow."""
    if not n_clicks:
        raise PreventUpdate

    if current_output is None:
        current_output = ""

    cli_wrapper = TorcCliWrapper()
    if cli_wrapper.cancel_current_process():
        return current_output + "\n\n⚠ Execution cancelled by user", True
    else:
        return current_output + "\n\n⚠ No running process to cancel", True


@callback(
    Output("execution-output", "children", allow_duplicate=True),
    Output("execution-poll-interval", "disabled", allow_duplicate=True),
    Output("cancel-execution-button", "disabled", allow_duplicate=True),
    Output("execute-workflow-button", "disabled", allow_duplicate=True),
    Input("execution-poll-interval", "n_intervals"),
    State("execution-output", "children"),
    prevent_initial_call=True,
)
def poll_execution_output(n_intervals: int, current_output: Optional[str]) -> tuple:
    """Poll for new output from running process."""
    if current_output is None:
        current_output = ""

    cli_wrapper = TorcCliWrapper()
    new_output, is_complete = cli_wrapper.read_process_output()

    # Only update if there's new output or process completed
    if not new_output and not is_complete:
        # No changes - prevent unnecessary re-render
        return no_update, no_update, no_update, no_update

    # Append new output
    updated_output = current_output + new_output

    if is_complete:
        # Stop polling, re-enable buttons
        return updated_output, True, True, False
    else:
        # Keep polling, keep cancel enabled
        return updated_output, False, False, True


@callback(
    Output("workflow-management-status", "children"),
    Input("initialize-existing-workflow-button", "n_clicks"),
    Input("reinitialize-workflow-button", "n_clicks"),
    Input("reset-workflow-button", "n_clicks"),
    State("selected-workflow-store", "data"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def manage_workflow(
    init_clicks: int,
    reinit_clicks: int,
    reset_clicks: int,
    selected_workflow: Optional[Dict[str, Any]],
    config: Dict[str, str],
) -> html.Div:
    """Handle workflow management operations (initialize, reinitialize, reset)."""
    from dash import ctx

    if not ctx.triggered_id:
        raise PreventUpdate

    if not selected_workflow or "id" not in selected_workflow:
        return dbc.Alert(
            "Please select a workflow from the 'View Workflows' tab first.",
            color="warning",
            dismissable=True,
        )

    workflow_id = selected_workflow["id"]
    cli_wrapper = TorcCliWrapper()

    try:
        button_id = ctx.triggered_id

        if button_id == "initialize-existing-workflow-button":
            result = cli_wrapper.initialize_workflow(workflow_id, config.get("url"))
            operation = "Initialize"
        elif button_id == "reinitialize-workflow-button":
            result = cli_wrapper.reinitialize_workflow(workflow_id, config.get("url"))
            operation = "Re-initialize"
        elif button_id == "reset-workflow-button":
            result = cli_wrapper.reset_status_workflow(workflow_id, config.get("url"))
            operation = "Reset"
        else:
            return dbc.Alert("Unknown operation", color="danger", dismissable=True)

        if result["success"]:
            message = f"{operation} workflow {workflow_id} successful"
            if result.get("stdout"):
                message += f"\n{result['stdout']}"
            return dbc.Alert(message, color="success", dismissable=True)
        else:
            error_msg = result.get("error", "Unknown error")
            stderr = result.get("stderr", "")
            message = f"{operation} workflow {workflow_id} failed: {error_msg}"
            if stderr:
                message += f"\n{stderr}"
            return dbc.Alert(message, color="danger", dismissable=True)

    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger", dismissable=True)


# ============================================================================
# DAG Visualization Callbacks
# ============================================================================

@callback(
    Output("main-tabs", "active_tab", allow_duplicate=True),
    Output("dag-workflow-id-store", "data", allow_duplicate=True),
    Input("show-dag-button", "n_clicks"),
    State("uploaded-spec-store", "data"),
    State("selected-workflow-store", "data"),
    prevent_initial_call=True,
)
def show_dag_tab(n_clicks: int, uploaded_spec: Optional[Dict], selected_workflow: Optional[Dict]) -> Tuple[str, Optional[int]]:
    """Switch to DAG tab and set workflow ID when Show DAG button is clicked."""
    if not n_clicks:
        raise PreventUpdate

    # Try to determine workflow ID
    workflow_id = None
    if selected_workflow and "id" in selected_workflow:
        workflow_id = selected_workflow["id"]
    elif uploaded_spec and "workflow_id" in uploaded_spec:
        workflow_id = uploaded_spec["workflow_id"]

    return "dag-tab", workflow_id


@callback(
    Output("job-deps-graph-container", "children"),
    Output("file-rels-graph-container", "children"),
    Output("user-data-rels-graph-container", "children"),
    Output("dag-load-status", "children"),
    Input("selected-workflow-store", "data"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def load_dag_graphs(
    workflow_data: Optional[Dict[str, Any]],
    config: Dict[str, str]
) -> Tuple[html.Div, html.Div, html.Div, html.Div]:
    """Load and display the three types of DAG graphs when a workflow is selected."""
    if workflow_data is None:
        raise PreventUpdate

    # Extract workflow ID from the workflow data
    workflow_id = workflow_data.get("id")
    if workflow_id is None:
        raise PreventUpdate

    try:
        api_wrapper = TorcApiWrapper(config.get("url", ""), config.get("username", ""))

        # Fetch job dependencies
        job_deps_result = api_wrapper.list_job_dependencies(workflow_id, limit=1000)
        if not job_deps_result["success"]:
            error_msg = job_deps_result.get("error", "Unknown error")
            return (
                html.Div(f"Error loading job dependencies: {error_msg}"),
                html.Div(""),
                html.Div(""),
                dbc.Alert(f"Failed to load job dependencies: {error_msg}", color="danger")
            )

        # Fetch file relationships
        file_rels_result = api_wrapper.list_job_file_relationships(workflow_id, limit=1000)
        if not file_rels_result["success"]:
            error_msg = file_rels_result.get("error", "Unknown error")
            return (
                html.Div(""),
                html.Div(f"Error loading file relationships: {error_msg}"),
                html.Div(""),
                dbc.Alert(f"Failed to load file relationships: {error_msg}", color="danger")
            )

        # Fetch user data relationships
        user_data_rels_result = api_wrapper.list_job_user_data_relationships(workflow_id, limit=1000)
        if not user_data_rels_result["success"]:
            error_msg = user_data_rels_result.get("error", "Unknown error")
            return (
                html.Div(""),
                html.Div(""),
                html.Div(f"Error loading user data relationships: {error_msg}"),
                dbc.Alert(f"Failed to load user data relationships: {error_msg}", color="danger")
            )

        # Create graph visualizations using Cytoscape
        job_deps_graph = create_job_deps_graph(job_deps_result["data"])
        file_rels_graph = create_file_rels_graph(file_rels_result["data"])
        user_data_rels_graph = create_user_data_rels_graph(user_data_rels_result["data"])

        status_msg = dbc.Alert(
            [
                html.I(className="fas fa-check-circle me-2"),
                f"Successfully loaded {len(job_deps_result['data'])} job dependencies, "
                f"{len(file_rels_result['data'])} file relationships, and "
                f"{len(user_data_rels_result['data'])} user data relationships"
            ],
            color="success",
            dismissable=True,
        )

        return job_deps_graph, file_rels_graph, user_data_rels_graph, status_msg

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        return (
            html.Div(error_msg),
            html.Div(error_msg),
            html.Div(error_msg),
            dbc.Alert(error_msg, color="danger")
        )


def create_job_deps_graph(dependencies: List[Dict[str, Any]]) -> html.Div:
    """Create a Cytoscape graph for job dependencies."""
    import dash_cytoscape as cyto

    if not dependencies:
        return html.Div("No job dependencies found for this workflow", className="text-muted text-center p-5")

    # Build nodes and edges
    nodes = set()
    edges = []

    for dep in dependencies:
        job_id = dep.get("job_id")
        job_name = dep.get("job_name", f"Job {job_id}")
        blocked_by_id = dep.get("blocked_by_job_id")
        blocked_by_name = dep.get("blocked_by_job_name", f"Job {blocked_by_id}")

        nodes.add((job_id, job_name))
        nodes.add((blocked_by_id, blocked_by_name))

        edges.append({
            "data": {
                "source": str(blocked_by_id),
                "target": str(job_id),
                "label": "blocks"
            }
        })

    elements = [
        {"data": {"id": str(node_id), "label": node_name}}
        for node_id, node_name in nodes
    ] + edges

    return cyto.Cytoscape(
        id="job-deps-cytoscape",
        elements=elements,
        layout={"name": "breadthfirst", "directed": True, "fit": True},
        style={"width": "100%", "height": "600px"},
        stylesheet=[
            {
                "selector": "node",
                "style": {
                    "content": "data(label)",
                    "text-valign": "center",
                    "text-halign": "center",
                    "background-color": "#0d6efd",
                    "color": "white",
                    "width": "label",
                    "height": "label",
                    "padding": "10px",
                    "shape": "roundrectangle",
                }
            },
            {
                "selector": "edge",
                "style": {
                    "curve-style": "bezier",
                    "target-arrow-shape": "triangle",
                    "target-arrow-color": "#999",
                    "line-color": "#999",
                    "width": 2,
                }
            },
        ],
    )


def create_file_rels_graph(relationships: List[Dict[str, Any]]) -> html.Div:
    """Create a Cytoscape graph for file relationships."""
    import dash_cytoscape as cyto

    if not relationships:
        return html.Div("No file relationships found for this workflow", className="text-muted text-center p-5")

    # Build nodes and edges
    job_nodes = set()
    file_nodes = set()
    edges = []

    for rel in relationships:
        file_id = rel.get("file_id")
        file_name = rel.get("file_name", f"File {file_id}")
        producer_id = rel.get("producer_job_id")
        producer_name = rel.get("producer_job_name")
        consumer_id = rel.get("consumer_job_id")
        consumer_name = rel.get("consumer_job_name")

        file_nodes.add((file_id, file_name))

        if producer_id:
            job_nodes.add((producer_id, producer_name or f"Job {producer_id}"))
            edges.append({
                "data": {
                    "source": f"job_{producer_id}",
                    "target": f"file_{file_id}",
                    "label": "produces"
                }
            })

        if consumer_id:
            job_nodes.add((consumer_id, consumer_name or f"Job {consumer_id}"))
            edges.append({
                "data": {
                    "source": f"file_{file_id}",
                    "target": f"job_{consumer_id}",
                    "label": "consumed by"
                }
            })

    elements = [
        {"data": {"id": f"job_{node_id}", "label": node_name, "type": "job"}}
        for node_id, node_name in job_nodes
    ] + [
        {"data": {"id": f"file_{node_id}", "label": node_name, "type": "file"}}
        for node_id, node_name in file_nodes
    ] + edges

    return cyto.Cytoscape(
        id="file-rels-cytoscape",
        elements=elements,
        layout={"name": "breadthfirst", "directed": True, "fit": True},
        style={"width": "100%", "height": "600px"},
        stylesheet=[
            {
                "selector": 'node[type = "job"]',
                "style": {
                    "content": "data(label)",
                    "text-valign": "center",
                    "text-halign": "center",
                    "background-color": "#0d6efd",
                    "color": "white",
                    "width": "label",
                    "height": "label",
                    "padding": "10px",
                    "shape": "roundrectangle",
                }
            },
            {
                "selector": 'node[type = "file"]',
                "style": {
                    "content": "data(label)",
                    "text-valign": "center",
                    "text-halign": "center",
                    "background-color": "#198754",
                    "color": "white",
                    "width": "label",
                    "height": "label",
                    "padding": "10px",
                    "shape": "rectangle",
                }
            },
            {
                "selector": "edge",
                "style": {
                    "curve-style": "bezier",
                    "target-arrow-shape": "triangle",
                    "target-arrow-color": "#999",
                    "line-color": "#999",
                    "width": 2,
                }
            },
        ],
    )


def create_user_data_rels_graph(relationships: List[Dict[str, Any]]) -> html.Div:
    """Create a Cytoscape graph for user data relationships."""
    import dash_cytoscape as cyto

    if not relationships:
        return html.Div("No user data relationships found for this workflow", className="text-muted text-center p-5")

    # Build nodes and edges
    job_nodes = set()
    data_nodes = set()
    edges = []

    for rel in relationships:
        data_id = rel.get("user_data_id")
        data_name = rel.get("user_data_name", f"Data {data_id}")
        producer_id = rel.get("producer_job_id")
        producer_name = rel.get("producer_job_name")
        consumer_id = rel.get("consumer_job_id")
        consumer_name = rel.get("consumer_job_name")

        data_nodes.add((data_id, data_name))

        if producer_id:
            job_nodes.add((producer_id, producer_name or f"Job {producer_id}"))
            edges.append({
                "data": {
                    "source": f"job_{producer_id}",
                    "target": f"data_{data_id}",
                    "label": "produces"
                }
            })

        if consumer_id:
            job_nodes.add((consumer_id, consumer_name or f"Job {consumer_id}"))
            edges.append({
                "data": {
                    "source": f"data_{data_id}",
                    "target": f"job_{consumer_id}",
                    "label": "consumed by"
                }
            })

    elements = [
        {"data": {"id": f"job_{node_id}", "label": node_name, "type": "job"}}
        for node_id, node_name in job_nodes
    ] + [
        {"data": {"id": f"data_{node_id}", "label": node_name, "type": "data"}}
        for node_id, node_name in data_nodes
    ] + edges

    return cyto.Cytoscape(
        id="user-data-rels-cytoscape",
        elements=elements,
        layout={"name": "breadthfirst", "directed": True, "fit": True},
        style={"width": "100%", "height": "600px"},
        stylesheet=[
            {
                "selector": 'node[type = "job"]',
                "style": {
                    "content": "data(label)",
                    "text-valign": "center",
                    "text-halign": "center",
                    "background-color": "#0d6efd",
                    "color": "white",
                    "width": "label",
                    "height": "label",
                    "padding": "10px",
                    "shape": "roundrectangle",
                }
            },
            {
                "selector": 'node[type = "data"]',
                "style": {
                    "content": "data(label)",
                    "text-valign": "center",
                    "text-halign": "center",
                    "background-color": "#ffc107",
                    "color": "black",
                    "width": "label",
                    "height": "label",
                    "padding": "10px",
                    "shape": "diamond",
                }
            },
            {
                "selector": "edge",
                "style": {
                    "curve-style": "bezier",
                    "target-arrow-shape": "triangle",
                    "target-arrow-color": "#999",
                    "line-color": "#999",
                    "width": 2,
                }
            },
        ],
    )


# ============================================================================
# Execution Plan Callbacks
# ============================================================================

@callback(
    Output("execution-plan-modal", "is_open"),
    Output("execution-plan-modal-body", "children"),
    Input("show-execution-plan-button", "n_clicks"),
    Input("execution-plan-close-btn", "n_clicks"),
    State("execution-plan-modal", "is_open"),
    State("selected-workflow-store", "data"),
    State("uploaded-spec-store", "data"),
    State("workflow-spec-path-input", "value"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def toggle_execution_plan_modal(
    show_clicks: int,
    close_clicks: int,
    is_open: bool,
    selected_workflow: Optional[Dict],
    uploaded_spec: Optional[Dict],
    spec_path: Optional[str],
    config: Dict[str, str]
) -> Tuple[bool, html.Div]:
    """Open/close execution plan modal and load the plan when opened."""
    from dash import ctx

    # Determine which button was clicked
    triggered_id = ctx.triggered_id

    # Close button clicked
    if triggered_id == "execution-plan-close-btn":
        return False, html.Div()

    # Show button clicked
    if triggered_id == "show-execution-plan-button":
        # Determine the spec or workflow ID to use
        spec_or_id = None

        # Priority 1: Selected workflow
        if selected_workflow and "id" in selected_workflow:
            spec_or_id = str(selected_workflow["id"])
        # Priority 2: Uploaded spec file path
        elif uploaded_spec and "file_path" in uploaded_spec:
            spec_or_id = uploaded_spec["file_path"]
        # Priority 3: Manually entered spec path
        elif spec_path and spec_path.strip():
            spec_or_id = spec_path.strip()

        if not spec_or_id:
            return True, dbc.Alert(
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Please select a workflow or provide a workflow specification file."
                ],
                color="warning"
            )

        # Load execution plan
        try:
            cli_wrapper = TorcCliWrapper()
            result = cli_wrapper.get_execution_plan(spec_or_id, api_url=config.get("url"))

            if not result["success"]:
                error_msg = result.get("error", "Unknown error")
                return True, dbc.Alert(
                    [
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        f"Error generating execution plan: {error_msg}"
                    ],
                    color="danger"
                )

            plan_data = result["data"]
            plan_view = create_execution_plan_view(plan_data)

            return True, plan_view

        except Exception as e:
            return True, dbc.Alert(
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"Unexpected error: {str(e)}"
                ],
                color="danger"
            )

    raise PreventUpdate


# ============================================================================
# Monitor Events Tab Callbacks
# ============================================================================

@callback(
    Output("monitor-workflow-select", "options"),
    Input("main-tabs", "active_tab"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def populate_monitor_workflows(
    active_tab: str,
    config: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Populate the workflow dropdown when monitor tab is activated."""
    if active_tab != "monitor-tab":
        raise PreventUpdate

    api_wrapper = TorcApiWrapper(config.get("url"), config.get("username"))
    result = api_wrapper.list_workflows(limit=1000)

    if not result["success"] or not result["data"]:
        return []

    options = [
        {"label": f"{w['name']} (ID: {w['id']})", "value": w["id"]}
        for w in result["data"]
    ]
    return options


@callback(
    Output("monitor-selected-workflow-display", "children"),
    Output("monitor-workflow-select", "disabled"),
    Input("monitor-use-selected-workflow", "value"),
    State("selected-workflow-store", "data"),
)
def display_selected_workflow(
    use_selected: List[str],
    selected_workflow: Optional[Dict[str, Any]],
) -> Tuple[str, bool]:
    """Display the selected workflow from View Workflows tab."""
    if "use_selected" in use_selected:
        if selected_workflow and "id" in selected_workflow:
            workflow_name = selected_workflow.get("name", "Unknown")
            workflow_id = selected_workflow["id"]
            return f"Using workflow: {workflow_name} (ID: {workflow_id})", True
        else:
            return "No workflow selected in View Workflows tab", True
    return "", False


@callback(
    Output("monitor-is-active", "data"),
    Output("monitor-interval", "disabled"),
    Output("monitor-start-button", "disabled"),
    Output("monitor-stop-button", "disabled"),
    Output("monitor-interval", "interval"),
    Input("monitor-start-button", "n_clicks"),
    Input("monitor-stop-button", "n_clicks"),
    State("monitor-use-selected-workflow", "value"),
    State("selected-workflow-store", "data"),
    State("monitor-workflow-select", "value"),
    State("monitor-poll-interval", "value"),
    prevent_initial_call=True,
)
def control_monitoring(
    start_clicks: int,
    stop_clicks: int,
    use_selected: List[str],
    selected_workflow: Optional[Dict[str, Any]],
    dropdown_workflow_id: Optional[int],
    poll_interval: int,
) -> Tuple[bool, bool, bool, bool, int]:
    """Start or stop event monitoring."""
    from dash import ctx

    if not ctx.triggered_id:
        raise PreventUpdate

    # Ensure minimum poll interval of 10 seconds
    poll_interval = max(10, poll_interval or 10)
    interval_ms = poll_interval * 1000

    if ctx.triggered_id == "monitor-start-button":
        # Determine which workflow to use
        workflow_id = None
        if "use_selected" in use_selected:
            if selected_workflow and "id" in selected_workflow:
                workflow_id = selected_workflow["id"]
        else:
            workflow_id = dropdown_workflow_id

        if not workflow_id:
            raise PreventUpdate
        # Start monitoring
        return True, False, True, False, interval_ms
    else:
        # Stop monitoring
        return False, True, False, True, interval_ms


@callback(
    Output("monitor-events-container", "children"),
    Output("monitor-event-count", "children"),
    Output("monitor-last-event-id", "data"),
    Input("monitor-interval", "n_intervals"),
    Input("monitor-clear-button", "n_clicks"),
    State("monitor-use-selected-workflow", "value"),
    State("selected-workflow-store", "data"),
    State("monitor-workflow-select", "value"),
    State("monitor-is-active", "data"),
    State("monitor-last-event-id", "data"),
    State("monitor-events-container", "children"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def update_events(
    n_intervals: int,
    clear_clicks: int,
    use_selected: List[str],
    selected_workflow: Optional[Dict[str, Any]],
    dropdown_workflow_id: Optional[int],
    is_active: bool,
    last_event_id: Optional[int],
    current_content: str,
    config: Dict[str, str],
) -> Tuple[str, str, Optional[int]]:
    """Fetch and display new events."""
    from dash import ctx
    import json

    if not ctx.triggered_id:
        raise PreventUpdate

    # Handle clear button
    if ctx.triggered_id == "monitor-clear-button":
        return "Events cleared. Monitoring will continue...", "0", last_event_id

    # Determine which workflow to use
    workflow_id = None
    if "use_selected" in use_selected:
        if selected_workflow and "id" in selected_workflow:
            workflow_id = selected_workflow["id"]
    else:
        workflow_id = dropdown_workflow_id

    # Handle interval updates
    if not is_active or not workflow_id:
        raise PreventUpdate

    api_wrapper = TorcApiWrapper(config.get("url"), config.get("username"))
    result = api_wrapper.list_events(workflow_id, limit=1000)

    if not result["success"]:
        error_msg = result.get("error", "Unknown error")
        return f"Error fetching events: {error_msg}", "Error", last_event_id

    events = result["data"]
    
    if not events:
        return "No events found for this workflow", "0", last_event_id

    # Filter for new events only (events with ID greater than last_event_id)
    if last_event_id is not None:
        new_events = [e for e in events if e.get("id", 0) > last_event_id]
    else:
        new_events = events

    if not new_events:
        # No new events, keep existing content
        return no_update, str(len(events)), last_event_id

    # Get the maximum event ID
    max_event_id = max(e.get("id", 0) for e in events)

    # Format new events as pretty JSON
    output_lines = []
    if current_content and current_content != "Select a workflow and click 'Start Monitoring' to begin" and current_content != "Events cleared. Monitoring will continue...":
        output_lines.append(current_content)
        output_lines.append("\n" + "="*80 + "\n")

    for event in sorted(new_events, key=lambda x: x.get("id", 0)):
        output_lines.append(json.dumps(event, indent=2, sort_keys=True))
        output_lines.append("\n" + "-"*80 + "\n")

    return "\n".join(output_lines), str(len(events)), max_event_id


# ============================================================================
# Resource Plots Tab Callbacks
# ============================================================================

@callback(
    Output("db-select", "options"),
    Input("refresh-dbs-button", "n_clicks"),
    Input("main-tabs", "active_tab"),
    prevent_initial_call=True,
)
def refresh_database_list(n_clicks: Optional[int], active_tab: str) -> List[Dict[str, str]]:
    """Refresh the list of available resource monitoring databases."""
    # Only refresh when plots tab is active
    if active_tab != "plots-tab":
        raise PreventUpdate

    cli_wrapper = TorcCliWrapper()
    databases = cli_wrapper.discover_resource_databases()

    if not databases:
        return []

    return [{"label": db["name"], "value": db["path"]} for db in databases]


@callback(
    Output("generate-plots-button", "disabled"),
    Input("db-select", "value"),
)
def enable_generate_button(db_path: Optional[str]) -> bool:
    """Enable the generate plots button when a database is selected."""
    return db_path is None or db_path == ""


@callback(
    Output("plot-status-message", "children"),
    Output("plot-files-store", "data"),
    Output("plot-select", "options"),
    Input("generate-plots-button", "n_clicks"),
    State("db-select", "value"),
    prevent_initial_call=True,
)
def generate_plots(n_clicks: Optional[int], db_path: Optional[str]) -> Tuple:
    """Generate JSON plots from the selected database."""
    if not n_clicks or not db_path:
        raise PreventUpdate

    cli_wrapper = TorcCliWrapper()

    # Generate plots
    result = cli_wrapper.generate_resource_plots_json(db_path)

    if result["success"]:
        # Create options for plot selector
        plot_options = []
        for plot_file in result.get("plots", []):
            filename = os.path.basename(plot_file)
            # Extract plot type from filename
            if "_job_" in filename:
                label = f"Job Timeline: {filename.replace('resource_plot_job_', '').replace('.json', '')}"
            elif "_cpu_all_jobs" in filename:
                label = "CPU - All Jobs"
            elif "_memory_all_jobs" in filename:
                label = "Memory - All Jobs"
            elif "_summary" in filename:
                label = "Summary Dashboard"
            else:
                label = filename.replace('.json', '')

            plot_options.append({"label": label, "value": plot_file})

        success_msg = dbc.Alert(
            [
                html.I(className="fas fa-check-circle me-2"),
                f"Successfully generated {len(result.get('plots', []))} plots"
            ],
            color="success",
            className="mt-2"
        )

        return success_msg, result.get("plots", []), plot_options
    else:
        error_msg = dbc.Alert(
            [
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"Error: {result.get('error', 'Unknown error')}"
            ],
            color="danger",
            className="mt-2"
        )
        return error_msg, [], []


@callback(
    Output("resource-plot-graph", "figure"),
    Input("plot-select", "value"),
    prevent_initial_call=True,
)
def display_selected_plot(plot_file: Optional[str]) -> Dict[str, Any]:
    """Load and display the selected plot."""
    if not plot_file:
        raise PreventUpdate

    cli_wrapper = TorcCliWrapper()
    plot_data = cli_wrapper.load_plot_json(plot_file)

    if plot_data is None:
        # Return empty figure with error message
        return {
            "data": [],
            "layout": {
                "title": "Error loading plot",
                "annotations": [{
                    "text": f"Failed to load plot from {plot_file}",
                    "showarrow": False,
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                }]
            }
        }

    # Extract only data and layout for Dash Graph component
    # (config and other keys are not accepted in the figure prop)
    figure = {
        "data": plot_data.get("data", []),
        "layout": plot_data.get("layout", {})
    }

    return figure
