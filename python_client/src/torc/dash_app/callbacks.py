"""Callback functions for the Torc Dash app."""

import base64
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback, html, no_update
from dash.exceptions import PreventUpdate

from .layouts import (
    create_dag_tab_layout,
    create_data_table,
    create_debugging_tab_layout,
    create_execution_plan_view,
    create_monitor_tab_layout,
    create_resource_plots_tab_layout,
    create_run_tab_layout,
    create_view_tab_layout,
)
from .utils import TorcApiWrapper, TorcCliWrapper, format_table_columns


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
) -> tuple[dict[str, str], html.Div]:
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
# Unified Workflows Tab Callbacks
# ============================================================================

def _get_status_badge_color(status: str | None) -> str:
    """Get Bootstrap color for workflow status badge."""
    status_colors = {
        "uninitialized": "secondary",
        "ready": "primary",
        "running": "warning",
        "completed": "success",
        "failed": "danger",
        "canceled": "dark",
    }
    return status_colors.get(status or "", "secondary")


@callback(
    Output("unified-workflows-table-container", "children"),
    Output("workflows-auto-refresh-interval", "disabled"),
    Input("workflows-refresh-btn", "n_clicks"),
    Input("workflows-auto-refresh-interval", "n_intervals"),
    Input("workflow-filter-input", "value"),
    State("api-config-store", "data"),
    State("workflows-auto-refresh-toggle", "value"),
    State("selected-workflow-store", "data"),
    prevent_initial_call=False,
)
def update_unified_workflows_table(
    n_clicks: int,
    n_intervals: int,
    filter_text: str | None,
    config: dict[str, str],
    auto_refresh: list[str],
    selected_workflow: dict | None,
) -> tuple[html.Div, bool]:
    """Update the unified workflows table with inline actions."""
    from dash import ctx

    # Only update on interval if auto-refresh is enabled
    if ctx.triggered_id == "workflows-auto-refresh-interval" and "auto" not in auto_refresh:
        raise PreventUpdate

    if not config:
        return dbc.Alert("Please configure the API URL first", color="warning"), True

    api_wrapper = TorcApiWrapper(config["url"], config.get("username"))
    result = api_wrapper.list_workflows(limit=1000)

    if not result["success"]:
        error_msg = result.get("error", "Unknown error")
        return dbc.Alert(f"Error: {error_msg}", color="danger"), True

    data = result["data"]

    if not data:
        return dbc.Alert(
            [
                html.I(className="fas fa-inbox me-2"),
                "No workflows found. Click 'Create New Workflow' to get started."
            ],
            color="info"
        ), True

    # Apply filter if provided
    if filter_text:
        filter_lower = filter_text.lower()
        data = [
            w for w in data
            if filter_lower in str(w.get("name", "")).lower()
            or filter_lower in str(w.get("description", "")).lower()
            or filter_lower in str(w.get("id", "")).lower()
            or filter_lower in str(w.get("user", "")).lower()
        ]

    if not data:
        return dbc.Alert(f"No workflows match filter: '{filter_text}'", color="info"), True

    # Get selected workflow ID for highlighting
    selected_id = selected_workflow.get("id") if selected_workflow else None

    # Create table rows with inline actions
    table_rows = []
    for w in data:
        workflow_id = w.get("id")
        is_selected = workflow_id == selected_id
        status = w.get("status", "")

        row_cells = [
            html.Td(workflow_id, style={"fontFamily": "monospace", "fontSize": "0.9em"}),
            html.Td(
                html.Strong(w.get("name", "")) if is_selected else w.get("name", ""),
                style={"fontWeight": "bold"} if is_selected else {}
            ),
            html.Td(
                w.get("description", "")[:50] + ("..." if len(w.get("description", "")) > 50 else ""),
                style={"maxWidth": "200px", "overflow": "hidden", "textOverflow": "ellipsis"},
                title=w.get("description", ""),
            ),
            html.Td(w.get("user", ""), style={"fontSize": "0.9em"}),
            html.Td(
                # Inline action buttons
                html.Div(
                    [
                        dbc.Button(
                            html.I(className="fas fa-play"),
                            id={"type": "inline-run-btn", "index": workflow_id},
                            color="success",
                            size="sm",
                            outline=True,
                            className="me-1",
                            title="Run locally",
                        ),
                        dbc.Button(
                            html.I(className="fas fa-eye"),
                            id={"type": "inline-view-btn", "index": workflow_id},
                            color="info",
                            size="sm",
                            outline=True,
                            className="me-1",
                            title="View details",
                        ),
                        dbc.Button(
                            html.I(className="fas fa-trash"),
                            id={"type": "delete-workflow-btn", "index": workflow_id},
                            color="danger",
                            size="sm",
                            outline=True,
                            title="Delete",
                        ),
                    ],
                    className="d-flex justify-content-end",
                ),
                style={"textAlign": "right", "whiteSpace": "nowrap"},
            ),
        ]

        row_style = {
            "cursor": "pointer",
            "backgroundColor": "#e7f1ff" if is_selected else "inherit",
        }

        table_rows.append(
            html.Tr(
                row_cells,
                id={"type": "workflow-row", "index": workflow_id},
                style=row_style,
                n_clicks=0,
            )
        )

    table = dbc.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th("ID", style={"width": "60px"}),
                    html.Th("Name"),
                    html.Th("Description"),
                    html.Th("User", style={"width": "100px"}),
                    html.Th("Actions", style={"width": "120px", "textAlign": "right"}),
                ]),
                className="table-light",
            ),
            html.Tbody(table_rows),
        ],
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mb-0",
        style={"marginBottom": "0"},
    )

    # Disable auto-refresh interval if auto-refresh is not enabled
    interval_disabled = "auto" not in auto_refresh

    return table, interval_disabled


@callback(
    Output("workflow-detail-card", "style"),
    Output("no-workflow-selected-alert", "style"),
    Output("detail-panel-workflow-name", "children"),
    Output("detail-panel-workflow-id", "children"),
    Output("detail-panel-status-badge", "children"),
    Output("detail-panel-user", "children"),
    Output("detail-panel-timestamp", "children"),
    Output("detail-panel-description", "children"),
    Input("selected-workflow-store", "data"),
)
def update_workflow_detail_panel(
    selected_workflow: dict | None,
) -> tuple:
    """Update the workflow detail panel when a workflow is selected."""
    if not selected_workflow or "id" not in selected_workflow:
        # Hide detail card, show placeholder
        return (
            {"display": "none"},  # Hide detail card
            {"display": "block"},  # Show placeholder
            "",  # name
            "",  # id
            "",  # status badge
            "",  # user
            "",  # timestamp
            "",  # description
        )

    # Show detail card, hide placeholder
    workflow_status = selected_workflow.get("status", "unknown")
    status_badge = dbc.Badge(
        workflow_status or "unknown",
        color=_get_status_badge_color(workflow_status),
        className="fs-6",
    )

    return (
        {"display": "block"},  # Show detail card
        {"display": "none"},  # Hide placeholder
        selected_workflow.get("name", "Unknown"),
        f" (ID: {selected_workflow.get('id')})",
        status_badge,
        selected_workflow.get("user", "N/A"),
        str(selected_workflow.get("timestamp", "N/A")),
        selected_workflow.get("description", "None"),
    )


@callback(
    Output("create-workflow-modal", "is_open"),
    Output("create-workflow-status", "children"),
    Input("open-create-workflow-modal-btn", "n_clicks"),
    Input("create-workflow-cancel-btn", "n_clicks"),
    Input("create-workflow-confirm-btn", "n_clicks"),
    State("create-workflow-modal", "is_open"),
    State("create-workflow-source-tabs", "active_tab"),
    State("uploaded-spec-store", "data"),
    State("workflow-spec-path-input", "value"),
    State("create-workflow-options", "value"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def handle_create_workflow_modal(
    open_clicks: int,
    cancel_clicks: int,
    confirm_clicks: int,
    is_open: bool,
    source_tab: str,
    uploaded_spec: dict | None,
    spec_path: str | None,
    options: list[str],
    config: dict[str, str],
) -> tuple[bool, html.Div | None]:
    """Handle the create workflow modal open/close and creation."""
    from dash import ctx

    if not ctx.triggered:
        raise PreventUpdate

    trigger_id = ctx.triggered_id

    # Open modal
    if trigger_id == "open-create-workflow-modal-btn":
        return True, None

    # Cancel - close modal
    if trigger_id == "create-workflow-cancel-btn":
        return False, None

    # Create workflow
    if trigger_id == "create-workflow-confirm-btn":
        cli_wrapper = TorcCliWrapper()
        workflow_spec_path = None
        temp_file = None

        try:
            # Determine workflow source
            if source_tab == "upload-tab":
                if uploaded_spec:
                    # Save to temp file
                    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
                    temp_file.write(uploaded_spec["content"])
                    temp_file.close()
                    workflow_spec_path = temp_file.name
                else:
                    return True, dbc.Alert("Please upload a workflow spec file", color="warning")
            elif source_tab == "path-tab":
                if spec_path:
                    workflow_spec_path = spec_path
                else:
                    return True, dbc.Alert("Please enter a file path", color="warning")
            else:
                return True, dbc.Alert("Unknown source tab", color="danger")

            # Create workflow
            result = cli_wrapper.create_workflow(workflow_spec_path, api_url=config.get("url"))

            if not result["success"]:
                error_msg = result.get("error", "Unknown error")
                return True, dbc.Alert(
                    [
                        html.Strong("Creation Failed: "),
                        error_msg,
                        html.Hr() if result.get("stderr") else None,
                        html.Small(result.get("stderr", "")) if result.get("stderr") else None,
                    ],
                    color="danger",
                )

            # Extract workflow ID
            try:
                output_data = json.loads(result["stdout"])
                workflow_id = output_data.get("workflow_id")
            except (json.JSONDecodeError, KeyError) as e:
                return True, dbc.Alert(f"Could not parse workflow ID: {e}", color="danger")

            if not workflow_id:
                return True, dbc.Alert("Workflow ID not found in output", color="danger")

            # Initialize if requested
            if "initialize" in options:
                init_result = cli_wrapper.initialize_workflow_direct(workflow_id, config.get("url"), force=True)
                if not init_result["success"]:
                    return False, dbc.Alert(
                        f"Workflow created (ID: {workflow_id}) but initialization failed: {init_result.get('error')}",
                        color="warning"
                    )

            # Run immediately if requested
            if "run" in options:
                cli_wrapper.start_workflow_process(workflow_id, config.get("url"))
                return False, dbc.Alert(
                    f"Workflow {workflow_id} created and started!",
                    color="success"
                )

            # Success - close modal
            return False, None

        except Exception as e:
            return True, dbc.Alert(f"Error: {str(e)}", color="danger")

        finally:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except Exception:
                    pass

    raise PreventUpdate


@callback(
    Output("selected-workflow-store", "data", allow_duplicate=True),
    Input({"type": "inline-view-btn", "index": ALL}, "n_clicks"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def handle_inline_view_button(
    n_clicks: list[int],
    config: dict[str, str],
) -> dict | None:
    """Handle inline view button click - select the workflow."""
    from dash import ctx

    if not ctx.triggered or not any(n_clicks):
        raise PreventUpdate

    triggered_id = ctx.triggered_id
    if not triggered_id or triggered_id.get("type") != "inline-view-btn":
        raise PreventUpdate

    workflow_id = triggered_id.get("index")
    if not workflow_id:
        raise PreventUpdate

    # Fetch workflow details
    api_wrapper = TorcApiWrapper(config["url"], config.get("username"))
    result = api_wrapper.list_workflows(limit=10000)

    if result["success"]:
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

    raise PreventUpdate


@callback(
    Output("execution-output-collapse", "is_open", allow_duplicate=True),
    Output("execution-output", "children", allow_duplicate=True),
    Output("execution-poll-interval", "disabled", allow_duplicate=True),
    Input({"type": "inline-run-btn", "index": ALL}, "n_clicks"),
    Input("run-workflow-button", "n_clicks"),
    Input("submit-workflow-button", "n_clicks"),
    State("selected-workflow-store", "data"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def handle_workflow_execution(
    inline_run_clicks: list[int],
    run_btn_clicks: int,
    submit_btn_clicks: int,
    selected_workflow: dict | None,
    config: dict[str, str],
) -> tuple[bool, str, bool]:
    """Handle workflow execution from inline button or detail panel."""
    from dash import ctx

    if not ctx.triggered:
        raise PreventUpdate

    trigger_id = ctx.triggered_id
    cli_wrapper = TorcCliWrapper()

    workflow_id = None
    execution_mode = "run"

    # Determine which button was clicked and get workflow ID
    if isinstance(trigger_id, dict) and trigger_id.get("type") == "inline-run-btn":
        if not any(inline_run_clicks):
            raise PreventUpdate
        workflow_id = trigger_id.get("index")
        execution_mode = "run"
    elif trigger_id == "run-workflow-button":
        if not run_btn_clicks or not selected_workflow:
            raise PreventUpdate
        workflow_id = selected_workflow.get("id")
        execution_mode = "run"
    elif trigger_id == "submit-workflow-button":
        if not submit_btn_clicks or not selected_workflow:
            raise PreventUpdate
        workflow_id = selected_workflow.get("id")
        execution_mode = "submit"
    else:
        raise PreventUpdate

    if not workflow_id:
        return True, "Error: No workflow ID", True

    try:
        if execution_mode == "run":
            # Start local workflow execution
            cli_wrapper.start_workflow_process(workflow_id, config.get("url"))
            return True, f"Starting workflow {workflow_id}...\n", False
        else:
            # Submit to scheduler
            result = cli_wrapper.submit_workflow_by_id(workflow_id, config.get("url"))
            if result["success"]:
                return True, f"Workflow {workflow_id} submitted to scheduler.\n{result.get('stdout', '')}", True
            else:
                return True, f"Error submitting workflow: {result.get('error', 'Unknown error')}\n{result.get('stderr', '')}", True
    except Exception as e:
        return True, f"Error: {str(e)}", True


@callback(
    Output("unified-workflows-table-container", "children", allow_duplicate=True),
    Input("create-workflow-modal", "is_open"),
    State("api-config-store", "data"),
    State("workflows-auto-refresh-toggle", "value"),
    prevent_initial_call=True,
)
def refresh_table_after_modal_close(
    is_open: bool,
    config: dict[str, str],
    auto_refresh: list[str],
) -> html.Div:
    """Refresh the workflows table when the create modal closes."""
    if is_open:
        # Modal just opened, don't refresh
        raise PreventUpdate

    # Modal closed - refresh the table
    if not config:
        raise PreventUpdate

    api_wrapper = TorcApiWrapper(config["url"], config.get("username"))
    result = api_wrapper.list_workflows(limit=1000)

    if not result["success"]:
        raise PreventUpdate

    data = result["data"]
    if not data:
        return dbc.Alert(
            [
                html.I(className="fas fa-inbox me-2"),
                "No workflows found. Click 'Create New Workflow' to get started."
            ],
            color="info"
        )

    # Recreate table (simplified - full version is in update_unified_workflows_table)
    table_rows = []
    for w in data:
        workflow_id = w.get("id")

        row_cells = [
            html.Td(workflow_id, style={"fontFamily": "monospace", "fontSize": "0.9em"}),
            html.Td(w.get("name", "")),
            html.Td(
                w.get("description", "")[:50] + ("..." if len(w.get("description", "")) > 50 else ""),
                style={"maxWidth": "200px"},
            ),
            html.Td(w.get("user", ""), style={"fontSize": "0.9em"}),
            html.Td(
                html.Div(
                    [
                        dbc.Button(
                            html.I(className="fas fa-play"),
                            id={"type": "inline-run-btn", "index": workflow_id},
                            color="success", size="sm", outline=True, className="me-1",
                        ),
                        dbc.Button(
                            html.I(className="fas fa-eye"),
                            id={"type": "inline-view-btn", "index": workflow_id},
                            color="info", size="sm", outline=True, className="me-1",
                        ),
                        dbc.Button(
                            html.I(className="fas fa-trash"),
                            id={"type": "delete-workflow-btn", "index": workflow_id},
                            color="danger", size="sm", outline=True,
                        ),
                    ],
                    className="d-flex justify-content-end",
                ),
            ),
        ]

        table_rows.append(
            html.Tr(
                row_cells,
                id={"type": "workflow-row", "index": workflow_id},
                style={"cursor": "pointer"},
                n_clicks=0,
            )
        )

    return dbc.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th("ID", style={"width": "60px"}),
                    html.Th("Name"),
                    html.Th("Description"),
                    html.Th("User", style={"width": "100px"}),
                    html.Th("Actions", style={"width": "120px", "textAlign": "right"}),
                ]),
                className="table-light",
            ),
            html.Tbody(table_rows),
        ],
        striped=True, bordered=True, hover=True, responsive=True, className="mb-0",
    )


# ============================================================================
# Global Workflow Selection Callbacks (Legacy - kept for compatibility)
# ============================================================================

@callback(
    Output("workflow-selection-collapse", "is_open"),
    Input("workflow-selection-collapse-button", "n_clicks"),
    State("workflow-selection-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_workflow_selection_collapse(n_clicks: int, is_open: bool) -> bool:
    """Toggle the workflow selection panel (legacy - hidden)."""
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
    prevent_initial_call=True,  # Legacy callback - hidden elements, never runs
)
def update_global_workflows_table(
    n_clicks: int,
    n_intervals: int,
    config: dict[str, str],
    auto_refresh: list[str],
) -> tuple[html.Div, bool]:
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
    n_clicks: list[int],
    config: dict[str, str],
) -> dict[str, Any] | None:
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
    selected_workflow: dict[str, Any] | None,
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
    n_clicks: list[int],
    config: dict[str, str],
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
    config: dict[str, str],
    auto_refresh: list[str],
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
    Output("debug-tab-content", "style"),
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
        {"display": "block", "marginTop": "1rem"} if active_tab == "debug-tab" else {"display": "none"},
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


@callback(
    Output("debug-tab-content", "children"),
    Input("api-config-store", "data"),
    prevent_initial_call=False,
)
def initialize_debug_tab(config):
    """Initialize the Debugging tab content once."""
    return create_debugging_tab_layout()


# ============================================================================
# View Tab Callbacks
# ============================================================================

# Old callbacks removed - workflow selection now handled by global panel (lines 73-192)


@callback(
    Output("workflow-details-panel", "children"),
    Input("selected-workflow-store", "data"),
    Input("refresh-workflow-details-button", "n_clicks"),
    Input("main-tabs", "active_tab"),
    State("api-config-store", "data"),
)
def show_workflow_details_panel(
    workflow: dict[str, Any] | None,
    n_clicks: int,
    active_tab: str,
    config: dict[str, str],
) -> html.Div:
    """Show the workflow details panel on the right when a workflow is selected, refresh button is clicked, or view-tab is activated."""
    from dash import ctx

    # Only refresh when switching to view-tab, not when switching away from it
    if ctx.triggered_id == "main-tabs" and active_tab != "view-tab":
        raise PreventUpdate

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
    workflow: dict[str, Any] | None,
    config: dict[str, str],
    auto_refresh: list[str],
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
                    "id": item.get("id", ""),
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
                {"name": "ID", "id": "id"},
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
    selected_rows: list[int],
    table_data: list[dict[str, Any]],
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
    contents: str | None,
    filename: str | None,
) -> tuple[dict[str, str] | None, html.Div | None]:
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
    workflow: dict[str, Any] | None,
) -> html.Div | None:
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
    uploaded_spec: dict[str, str] | None,
    spec_path: str | None,
    initialize_checkbox: list[str],
    config: dict[str, str],
) -> tuple[html.Div, dict[str, Any] | None, dict[str, Any] | None]:
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
            # Run dry-run check
            check_result = cli_wrapper._check_initialization(workflow_id, config.get("url"))
            if not check_result["success"]:
                workflow_data = {"id": workflow_id}
                return dbc.Alert(
                    [
                        html.H6("Workflow created but initialization check failed", className="alert-heading"),
                        html.P(f"Workflow ID: {workflow_id}"),
                        html.P(f"Error: {check_result.get('error', 'Unknown error')}"),
                    ],
                    color="warning",
                ), workflow_data, workflow_data

            check_data = check_result["data"]

            # Handle missing input files (always fail)
            if not check_data["safe"]:
                workflow_data = {"id": workflow_id}
                missing_files = check_data["missing_input_files"]
                return dbc.Alert(
                    [
                        html.H6("Workflow created but cannot initialize", className="alert-heading"),
                        html.P(f"Workflow ID: {workflow_id}"),
                        html.P(f"{check_data['missing_input_file_count']} required input file(s) are missing:"),
                        html.Ul([html.Li(f) for f in missing_files]),
                    ],
                    color="warning",
                ), workflow_data, workflow_data

            # Auto-delete existing output files if present (user opted in with checkbox)
            use_force = False
            if check_data["existing_output_file_count"] > 0:
                delete_result = cli_wrapper.check_and_delete_files(workflow_id, check_data["existing_output_files"])
                if not delete_result["success"]:
                    workflow_data = {"id": workflow_id}
                    return dbc.Alert(
                        [
                            html.H6("Workflow created but failed to delete existing files", className="alert-heading"),
                            html.P(f"Workflow ID: {workflow_id}"),
                            html.P(f"Failed to delete {len(delete_result['failed_deletions'])} file(s)"),
                        ],
                        color="warning",
                    ), workflow_data, workflow_data
                use_force = True

            # Initialize with --force if we deleted files
            init_result = cli_wrapper.initialize_workflow_direct(workflow_id, config.get("url"), force=use_force)
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
    Output("execute-confirmation-modal", "is_open"),
    Output("execute-modal-message", "children"),
    Output("execute-check-store", "data"),
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
    selected_workflow: dict[str, Any] | None,
    created_workflow: dict[str, Any] | None,
    execution_mode: str,
    config: dict[str, str],
) -> tuple[str, bool, bool, bool, bool, html.Div, dict | None]:
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
            return "Error: Please create the workflow first using the 'Create Workflow' button above.", True, False, True, False, None, None
    elif workflow_source_tab == "existing-workflow-tab":
        # Use selected workflow
        if selected_workflow and "id" in selected_workflow:
            workflow_id = selected_workflow["id"]
        else:
            return "Error: No workflow selected. Please select a workflow from the 'View Resources' tab first.", True, False, True, False, None, None
    else:
        return "Error: Unknown workflow source", True, False, True, False, None, None

    try:
        if execution_mode == "run":
            # Check if workflow needs initialization first
            init_check = cli_wrapper.check_workflow_needs_initialization(workflow_id, config.get("url"))

            if init_check.get("needs_init"):
                check_data = init_check.get("check_data")

                # Check for missing input files (always fail)
                if not check_data.get("safe"):
                    missing_files = check_data.get("missing_input_files", [])
                    error_message = [
                        html.P(f"Cannot execute workflow {workflow_id}: "
                               f"{check_data.get('missing_input_file_count', len(missing_files))} required input file(s) are missing:"),
                        html.Ul([html.Li(f) for f in missing_files])
                    ]
                    return dbc.Alert(error_message, color="danger", dismissable=True), True, False, True, False, None, None

                # Check for existing output files (show modal)
                if check_data.get("existing_output_file_count", 0) > 0:
                    existing_files = check_data.get("existing_output_files", [])
                    modal_message = [
                        html.P(f"Workflow {workflow_id} needs initialization but found {len(existing_files)} existing output file(s):"),
                        html.Ul([html.Li(f, style={"font-size": "0.9em"}) for f in existing_files]),
                        html.P("Do you want to delete these files, initialize, and execute the workflow?",
                               className="text-danger fw-bold mt-3"),
                    ]
                    store_data = {
                        "workflow_id": workflow_id,
                        "check_data": check_data,
                        "api_url": config.get("url"),
                        "execution_mode": execution_mode
                    }
                    return "", True, False, True, True, modal_message, store_data

            # Start process (non-blocking) with real-time output
            if cli_wrapper.start_workflow_process(workflow_id, api_url=config.get("url")):
                return f"Starting workflow {workflow_id} execution...\n", False, True, False, False, None, None
            else:
                return f"✗ Failed to start workflow {workflow_id}", True, False, True, False, None, None
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

            return "\n".join(output_lines), True, False, True, False, None, None

    except Exception as e:
        return f"Error: {str(e)}", True, False, True, False, None, None


@callback(
    Output("execution-output", "children", allow_duplicate=True),
    Output("cancel-execution-button", "disabled", allow_duplicate=True),
    Input("cancel-execution-button", "n_clicks"),
    State("execution-output", "children"),
    prevent_initial_call=True,
)
def cancel_workflow_execution(n_clicks: int, current_output: str | None) -> tuple:
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
def poll_execution_output(n_intervals: int, current_output: str | None) -> tuple:
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
    Output("initialize-confirmation-modal", "is_open"),
    Output("initialize-modal-message", "children"),
    Output("initialize-check-store", "data"),
    Output("reinitialize-confirmation-modal", "is_open"),
    Output("reinitialize-modal-message", "children"),
    Output("reinitialize-check-store", "data"),
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
    selected_workflow: dict[str, Any] | None,
    config: dict[str, str],
) -> tuple[html.Div, bool, html.Div, dict | None, bool, html.Div, dict | None]:
    """Handle workflow management operations (initialize, reinitialize, reset)."""
    from dash import ctx

    if not ctx.triggered_id:
        raise PreventUpdate

    if not selected_workflow or "id" not in selected_workflow:
        return (
            dbc.Alert(
                "Please select a workflow from the 'View Details' tab first.",
                color="warning",
                dismissable=True,
            ),
            False,  # init modal closed
            None,   # no init modal message
            None,   # no init check data
            False,  # reinit modal closed
            None,   # no reinit modal message
            None,   # no reinit check data
        )

    workflow_id = selected_workflow["id"]
    cli_wrapper = TorcCliWrapper()

    try:
        button_id = ctx.triggered_id

        if button_id == "initialize-existing-workflow-button":
            # Run dry-run check first
            check_result = cli_wrapper._check_initialization(workflow_id, config.get("url"))

            if not check_result["success"]:
                return (
                    dbc.Alert(
                        f"Initialization check failed: {check_result.get('error', 'Unknown error')}",
                        color="danger",
                        dismissable=True,
                    ),
                    False, None, None, False, None, None,
                )

            check_data = check_result["data"]

            # Handle missing input files (always fail)
            if not check_data["safe"]:
                missing_files = check_data["missing_input_files"]
                error_message = [
                    html.P(f"Cannot initialize workflow {workflow_id}: "
                           f"{check_data['missing_input_file_count']} required input file(s) are missing:"),
                    html.Ul([html.Li(f) for f in missing_files])
                ]
                return (
                    dbc.Alert(error_message, color="danger", dismissable=True),
                    False, None, None, False, None, None,
                )

            # Handle existing output files (prompt user)
            if check_data["existing_output_file_count"] > 0:
                existing_files = check_data["existing_output_files"]
                modal_message = [
                    html.P(f"Found {check_data['existing_output_file_count']} existing output file(s):"),
                    html.Ul([html.Li(f, style={"font-size": "0.9em"}) for f in existing_files]),
                    html.P("Do you want to delete these files and proceed with initialization?",
                           className="text-danger fw-bold mt-3"),
                ]
                # Store check data and show modal
                return (
                    no_update,
                    True,  # Open init modal
                    modal_message,
                    {"workflow_id": workflow_id, "check_data": check_data, "api_url": config.get("url")},
                    False, None, None,  # Reinit modal closed
                )

            # No issues - proceed with initialization directly
            result = cli_wrapper.initialize_workflow_direct(workflow_id, config.get("url"), force=False)
            operation = "Initialize"

            if result["success"]:
                message = f"{operation} workflow {workflow_id} successful"
                if result.get("stdout"):
                    message += f"\n{result['stdout']}"
                return (
                    dbc.Alert(message, color="success", dismissable=True),
                    False, None, None, False, None, None,
                )
            else:
                error_msg = result.get("error", "Unknown error")
                stderr = result.get("stderr", "")
                message = f"{operation} workflow {workflow_id} failed: {error_msg}"
                if stderr:
                    message += f"\n{stderr}"
                return (
                    dbc.Alert(message, color="danger", dismissable=True),
                    False, None, None, False, None, None,
                )

        elif button_id == "reinitialize-workflow-button":
            # Run dry-run check first
            check_result = cli_wrapper._check_reinitialize(workflow_id, config.get("url"))

            if not check_result["success"]:
                return (
                    dbc.Alert(
                        f"Re-initialization check failed: {check_result.get('error', 'Unknown error')}",
                        color="danger",
                        dismissable=True,
                    ),
                    False, None, None, False, None, None,
                )

            check_data = check_result["data"]

            # Handle missing input files (always fail)
            if not check_data["safe"]:
                missing_files = check_data["missing_input_files"]
                error_message = [
                    html.P(f"Cannot re-initialize workflow {workflow_id}: "
                           f"{check_data['missing_input_file_count']} required input file(s) are missing:"),
                    html.Ul([html.Li(f) for f in missing_files])
                ]
                return (
                    dbc.Alert(error_message, color="danger", dismissable=True),
                    False, None, None, False, None, None,
                )

            # Handle existing output files (prompt user)
            if check_data["existing_output_file_count"] > 0:
                existing_files = check_data["existing_output_files"]
                modal_message = [
                    html.P(f"Found {check_data['existing_output_file_count']} existing output file(s):"),
                    html.Ul([html.Li(f, style={"font-size": "0.9em"}) for f in existing_files]),
                    html.P("Do you want to delete these files and proceed with re-initialization?",
                           className="text-danger fw-bold mt-3"),
                ]
                # Store check data and show reinit modal
                return (
                    no_update,
                    False, None, None,  # Init modal closed
                    True,  # Open reinit modal
                    modal_message,
                    {"workflow_id": workflow_id, "check_data": check_data, "api_url": config.get("url")},
                )

            # No issues - proceed with reinitialization directly
            result = cli_wrapper.reinitialize_workflow_direct(workflow_id, config.get("url"), force=False)
            operation = "Re-initialize"

            if result["success"]:
                message = f"{operation} workflow {workflow_id} successful"
                if result.get("stdout"):
                    message += f"\n{result['stdout']}"
                return (
                    dbc.Alert(message, color="success", dismissable=True),
                    False, None, None, False, None, None,
                )
            else:
                error_msg = result.get("error", "Unknown error")
                stderr = result.get("stderr", "")
                message = f"{operation} workflow {workflow_id} failed: {error_msg}"
                if stderr:
                    message += f"\n{stderr}"
                return (
                    dbc.Alert(message, color="danger", dismissable=True),
                    False, None, None, False, None, None,
                )

        elif button_id == "reset-workflow-button":
            result = cli_wrapper.reset_status_workflow(workflow_id, config.get("url"))
            operation = "Reset"

            if result["success"]:
                message = f"{operation} workflow {workflow_id} successful"
                if result.get("stdout"):
                    message += f"\n{result['stdout']}"
                return (
                    dbc.Alert(message, color="success", dismissable=True),
                    False, None, None, False, None, None,
                )
            else:
                error_msg = result.get("error", "Unknown error")
                stderr = result.get("stderr", "")
                message = f"{operation} workflow {workflow_id} failed: {error_msg}"
                if stderr:
                    message += f"\n{stderr}"
                return (
                    dbc.Alert(message, color="danger", dismissable=True),
                    False, None, None, False, None, None,
                )
        else:
            return (
                dbc.Alert("Unknown operation", color="danger", dismissable=True),
                False, None, None, False, None, None,
            )

    except Exception as e:
        return (
            dbc.Alert(f"Error: {str(e)}", color="danger", dismissable=True),
            False, None, None, False, None, None,
        )


@callback(
    Output("workflow-management-status", "children", allow_duplicate=True),
    Output("initialize-confirmation-modal", "is_open", allow_duplicate=True),
    Input("initialize-modal-confirm", "n_clicks"),
    Input("initialize-modal-cancel", "n_clicks"),
    State("initialize-check-store", "data"),
    prevent_initial_call=True,
)
def handle_initialize_modal(
    confirm_clicks: int,
    cancel_clicks: int,
    check_store_data: dict | None,
) -> tuple[html.Div, bool]:
    """Handle confirmation or cancellation of initialization with file deletion."""
    from dash import ctx

    if not ctx.triggered_id:
        raise PreventUpdate

    # User cancelled
    if ctx.triggered_id == "initialize-modal-cancel":
        return (
            dbc.Alert("Initialization cancelled by user", color="info", dismissable=True),
            False,  # Close modal
        )

    # User confirmed - proceed with deletion and initialization
    if not check_store_data:
        return (
            dbc.Alert("Error: No workflow data found", color="danger", dismissable=True),
            False,
        )

    workflow_id = check_store_data["workflow_id"]
    check_data = check_store_data["check_data"]
    api_url = check_store_data.get("api_url")

    import os
    cli_wrapper = TorcCliWrapper()

    # Delete existing output files
    existing_files = check_data["existing_output_files"]
    warnings = []
    warnings.append(f"Deleted {len(existing_files)} existing output file(s):")

    deleted_count = 0
    failed_deletions = []
    for file_path in existing_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_count += 1
                warnings.append(f"  ✓ {file_path}")
        except Exception as e:
            failed_deletions.append(f"  ✗ {file_path}: {str(e)}")

    if failed_deletions:
        warnings.append(f"\nFailed to delete {len(failed_deletions)} file(s):")
        warnings.extend(failed_deletions)
        return (
            dbc.Alert("\n".join(warnings), color="danger", dismissable=True),
            False,
        )

    # Proceed with initialization using --force flag
    result = cli_wrapper.initialize_workflow_direct(workflow_id, api_url, force=True)

    if result["success"]:
        success_message = "\n".join(warnings) + "\n\n" + result.get("stdout", "")
        return (
            dbc.Alert(
                [html.Pre(success_message, style={"white-space": "pre-wrap"})],
                color="success",
                dismissable=True
            ),
            False,
        )
    else:
        error_msg = result.get("error", "Unknown error")
        stderr = result.get("stderr", "")
        message = f"Initialization failed: {error_msg}"
        if stderr:
            message += f"\n{stderr}"
        return (
            dbc.Alert(message, color="danger", dismissable=True),
            False,
        )


@callback(
    Output("workflow-management-status", "children", allow_duplicate=True),
    Output("reinitialize-confirmation-modal", "is_open", allow_duplicate=True),
    Input("reinitialize-modal-confirm", "n_clicks"),
    Input("reinitialize-modal-cancel", "n_clicks"),
    State("reinitialize-check-store", "data"),
    prevent_initial_call=True,
)
def handle_reinitialize_modal(
    confirm_clicks: int,
    cancel_clicks: int,
    check_store_data: dict | None,
) -> tuple[html.Div, bool]:
    """Handle confirmation or cancellation of re-initialization with file deletion."""
    from dash import ctx

    if not ctx.triggered_id:
        raise PreventUpdate

    # User cancelled
    if ctx.triggered_id == "reinitialize-modal-cancel":
        return (
            dbc.Alert("Re-initialization cancelled by user", color="info", dismissable=True),
            False,  # Close modal
        )

    # User confirmed - proceed with deletion and reinitialization
    if not check_store_data:
        return (
            dbc.Alert("Error: No workflow data found", color="danger", dismissable=True),
            False,
        )

    workflow_id = check_store_data["workflow_id"]
    check_data = check_store_data["check_data"]
    api_url = check_store_data.get("api_url")

    cli_wrapper = TorcCliWrapper()

    # Delete existing output files
    delete_result = cli_wrapper.check_and_delete_files(workflow_id, check_data["existing_output_files"])

    if not delete_result["success"]:
        warnings = [f"Failed to delete {len(delete_result['failed_deletions'])} file(s):"]
        for file_path, error in delete_result['failed_deletions']:
            warnings.append(f"  ✗ {file_path}: {error}")
        return (
            dbc.Alert("\n".join(warnings), color="danger", dismissable=True),
            False,
        )

    # Build success message
    warnings = [f"Deleted {len(delete_result['deleted_files'])} existing output file(s):"]
    for file_path in delete_result['deleted_files']:
        warnings.append(f"  ✓ {file_path}")

    # Proceed with reinitialization using --force flag
    result = cli_wrapper.reinitialize_workflow_direct(workflow_id, api_url, force=True)

    if result["success"]:
        success_message = "\n".join(warnings) + "\n\n" + result.get("stdout", "")
        return (
            dbc.Alert(
                [html.Pre(success_message, style={"white-space": "pre-wrap"})],
                color="success",
                dismissable=True
            ),
            False,
        )
    else:
        error_msg = result.get("error", "Unknown error")
        stderr = result.get("stderr", "")
        message = f"Re-initialization failed: {error_msg}"
        if stderr:
            message += f"\n{stderr}"
        return (
            dbc.Alert(message, color="danger", dismissable=True),
            False,
        )


@callback(
    Output("execution-output", "children", allow_duplicate=True),
    Output("cancel-execution-button", "disabled", allow_duplicate=True),
    Output("execute-workflow-button", "disabled", allow_duplicate=True),
    Output("execution-poll-interval", "disabled", allow_duplicate=True),
    Output("execute-confirmation-modal", "is_open", allow_duplicate=True),
    Input("execute-modal-confirm", "n_clicks"),
    Input("execute-modal-cancel", "n_clicks"),
    State("execute-check-store", "data"),
    prevent_initial_call=True,
)
def handle_execute_modal(
    confirm_clicks: int,
    cancel_clicks: int,
    check_store_data: dict | None,
) -> tuple[str, bool, bool, bool, bool]:
    """Handle confirmation or cancellation of execution with file deletion and initialization."""
    from dash import ctx

    if not ctx.triggered_id:
        raise PreventUpdate

    # User cancelled
    if ctx.triggered_id == "execute-modal-cancel":
        return (
            "⚠ Execution cancelled by user\n",
            True,  # cancel button disabled
            False, # execute button enabled
            True,  # poll interval disabled
            False, # Close modal
        )

    # User confirmed - proceed with deletion, initialization, and execution
    if not check_store_data:
        return (
            "Error: No workflow data found\n",
            True,
            False,
            True,
            False,
        )

    workflow_id = check_store_data["workflow_id"]
    check_data = check_store_data["check_data"]
    api_url = check_store_data.get("api_url")

    cli_wrapper = TorcCliWrapper()

    # Delete existing output files
    delete_result = cli_wrapper.check_and_delete_files(workflow_id, check_data["existing_output_files"])

    if not delete_result["success"]:
        warnings = [f"Failed to delete {len(delete_result['failed_deletions'])} file(s):"]
        for file_path, error in delete_result['failed_deletions']:
            warnings.append(f"  ✗ {file_path}: {error}")
        return (
            "\n".join(warnings) + "\n",
            True,
            False,
            True,
            False,
        )

    # Build deletion success message
    output_lines = [f"Deleted {len(delete_result['deleted_files'])} existing output file(s):"]
    for file_path in delete_result['deleted_files']:
        output_lines.append(f"  ✓ {file_path}")

    # Initialize workflow using --force flag
    init_result = cli_wrapper.initialize_workflow_direct(workflow_id, api_url, force=True)

    if not init_result["success"]:
        error_msg = init_result.get("error", "Unknown error")
        stderr = init_result.get("stderr", "")
        output_lines.append(f"\n✗ Initialization failed: {error_msg}")
        if stderr:
            output_lines.append(f"Stderr: {stderr}")
        return (
            "\n".join(output_lines) + "\n",
            True,
            False,
            True,
            False,
        )

    output_lines.append(f"\n✓ Workflow {workflow_id} initialized successfully")

    # Start workflow execution
    if cli_wrapper.start_workflow_process(workflow_id, api_url=api_url):
        output_lines.append(f"\nStarting workflow {workflow_id} execution...\n")
        return (
            "\n".join(output_lines) + "\n",
            False, # cancel button enabled
            True,  # execute button disabled
            False, # poll interval enabled
            False, # Close modal
        )
    else:
        output_lines.append(f"\n✗ Failed to start workflow {workflow_id}")
        return (
            "\n".join(output_lines) + "\n",
            True,
            False,
            True,
            False,
        )


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
def show_dag_tab(n_clicks: int, uploaded_spec: dict | None, selected_workflow: dict | None) -> tuple[str, int | None]:
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
    Output("dag-load-status", "children"),
    Input("selected-workflow-store", "data"),
    Input("main-tabs", "active_tab"),
    Input("dag-graph-tabs", "active_tab"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def load_job_deps_graph(
    workflow_data: dict[str, Any] | None,
    main_tab: str,
    dag_tab: str,
    config: dict[str, str]
) -> tuple[html.Div, html.Div]:
    """Load job dependencies graph when its tab is visible."""
    if workflow_data is None:
        raise PreventUpdate

    # Only render when DAG tab is active AND job-deps sub-tab is active
    if main_tab != "dag-tab" or dag_tab != "job-deps-graph-tab":
        raise PreventUpdate

    workflow_id = workflow_data.get("id")
    if workflow_id is None:
        raise PreventUpdate

    try:
        api_wrapper = TorcApiWrapper(config.get("url", ""), config.get("username", ""))
        result = api_wrapper.list_job_dependencies(workflow_id, limit=1000)

        if not result["success"]:
            error_msg = result.get("error", "Unknown error")
            return (
                html.Div(f"Error: {error_msg}"),
                dbc.Alert(f"Failed to load job dependencies: {error_msg}", color="danger")
            )

        graph = create_job_deps_graph(result["data"])
        status = dbc.Alert(
            f"Loaded {len(result['data'])} job dependencies",
            color="success", dismissable=True, duration=3000
        )
        return graph, status

    except Exception as e:
        return html.Div(f"Error: {e}"), dbc.Alert(str(e), color="danger")


@callback(
    Output("file-rels-graph-container", "children"),
    Input("selected-workflow-store", "data"),
    Input("main-tabs", "active_tab"),
    Input("dag-graph-tabs", "active_tab"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def load_file_rels_graph(
    workflow_data: dict[str, Any] | None,
    main_tab: str,
    dag_tab: str,
    config: dict[str, str]
) -> html.Div:
    """Load file relationships graph when its tab is visible."""
    if workflow_data is None:
        raise PreventUpdate

    # Only render when DAG tab is active AND file-rels sub-tab is active
    if main_tab != "dag-tab" or dag_tab != "file-rels-graph-tab":
        raise PreventUpdate

    workflow_id = workflow_data.get("id")
    if workflow_id is None:
        raise PreventUpdate

    try:
        api_wrapper = TorcApiWrapper(config.get("url", ""), config.get("username", ""))
        result = api_wrapper.list_job_file_relationships(workflow_id, limit=1000)

        if not result["success"]:
            error_msg = result.get("error", "Unknown error")
            return html.Div(f"Error: {error_msg}")

        return create_file_rels_graph(result["data"])

    except Exception as e:
        return html.Div(f"Error: {e}")


@callback(
    Output("user-data-rels-graph-container", "children"),
    Input("selected-workflow-store", "data"),
    Input("main-tabs", "active_tab"),
    Input("dag-graph-tabs", "active_tab"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def load_user_data_rels_graph(
    workflow_data: dict[str, Any] | None,
    main_tab: str,
    dag_tab: str,
    config: dict[str, str]
) -> html.Div:
    """Load user data relationships graph when its tab is visible."""
    if workflow_data is None:
        raise PreventUpdate

    # Only render when DAG tab is active AND user-data-rels sub-tab is active
    if main_tab != "dag-tab" or dag_tab != "user-data-rels-graph-tab":
        raise PreventUpdate

    workflow_id = workflow_data.get("id")
    if workflow_id is None:
        raise PreventUpdate

    try:
        api_wrapper = TorcApiWrapper(config.get("url", ""), config.get("username", ""))
        result = api_wrapper.list_job_user_data_relationships(workflow_id, limit=1000)

        if not result["success"]:
            error_msg = result.get("error", "Unknown error")
            return html.Div(f"Error: {error_msg}")

        return create_user_data_rels_graph(result["data"])

    except Exception as e:
        return html.Div(f"Error: {e}")


def create_job_deps_graph(dependencies: list[dict[str, Any]]) -> html.Div:
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
        depends_on_id = dep.get("depends_on_job_id")
        depends_on_name = dep.get("depends_on_job_name", f"Job {depends_on_id}")

        nodes.add((job_id, job_name))
        nodes.add((depends_on_id, depends_on_name))

        edges.append({
            "data": {
                "source": str(depends_on_id),
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
        layout={
            "name": "breadthfirst",
            "directed": True,
            "fit": True,
            "padding": 200,
            "spacingFactor": 1.0,
        },
        style={"width": "100%", "height": "600px"},
        zoom=0.3,
        pan={"x": 0, "y": -100},
        minZoom=0.1,
        maxZoom=3,
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


def create_file_rels_graph(relationships: list[dict[str, Any]]) -> html.Div:
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
        layout={
            "name": "breadthfirst",
            "directed": True,
            "fit": True,
            "padding": 200,
            "spacingFactor": 1.0,
        },
        style={"width": "100%", "height": "600px"},
        zoom=0.3,
        pan={"x": 0, "y": -100},
        minZoom=0.1,
        maxZoom=3,
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


def create_user_data_rels_graph(relationships: list[dict[str, Any]]) -> html.Div:
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
        layout={
            "name": "breadthfirst",
            "directed": True,
            "fit": True,
            "padding": 200,
            "spacingFactor": 1.0,
        },
        style={"width": "100%", "height": "600px"},
        zoom=0.3,
        pan={"x": 0, "y": -100},
        minZoom=0.1,
        maxZoom=3,
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
    selected_workflow: dict | None,
    uploaded_spec: dict | None,
    spec_path: str | None,
    config: dict[str, str]
) -> tuple[bool, html.Div]:
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
    config: dict[str, str],
) -> list[dict[str, Any]]:
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
    use_selected: list[str],
    selected_workflow: dict[str, Any] | None,
) -> tuple[str, bool]:
    """Display the selected workflow from View Details tab."""
    if "use_selected" in use_selected:
        if selected_workflow and "id" in selected_workflow:
            workflow_name = selected_workflow.get("name", "Unknown")
            workflow_id = selected_workflow["id"]
            return f"Using workflow: {workflow_name} (ID: {workflow_id})", True
        else:
            return "No workflow selected in View Details tab", True
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
    use_selected: list[str],
    selected_workflow: dict[str, Any] | None,
    dropdown_workflow_id: int | None,
    poll_interval: int,
) -> tuple[bool, bool, bool, bool, int]:
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
    use_selected: list[str],
    selected_workflow: dict[str, Any] | None,
    dropdown_workflow_id: int | None,
    is_active: bool,
    last_event_id: int | None,
    current_content: str,
    config: dict[str, str],
) -> tuple[str, str, int | None]:
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
def refresh_database_list(n_clicks: int | None, active_tab: str) -> list[dict[str, str]]:
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
def enable_generate_button(db_path: str | None) -> bool:
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
def generate_plots(n_clicks: int | None, db_path: str | None) -> tuple:
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
def display_selected_plot(plot_file: str | None) -> dict[str, Any]:
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


# ============================================================================
# Debugging Tab Callbacks
# ============================================================================

@callback(
    Output("debug-report-store", "data"),
    Output("debug-report-status", "children"),
    Output("debug-jobs-table-container", "children"),
    Output("debug-job-count-badge", "children"),
    Input("debug-generate-report-btn", "n_clicks"),
    State("selected-workflow-store", "data"),
    State("debug-output-dir", "value"),
    State("debug-report-options", "value"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def generate_debug_report(
    n_clicks: int,
    selected_workflow: dict[str, Any] | None,
    output_dir: str,
    options: list[str],
    config: dict[str, str],
) -> tuple[dict | None, html.Div | None, html.Div, str]:
    """Generate the job results report and display in table."""
    if not n_clicks:
        raise PreventUpdate

    if not selected_workflow or "id" not in selected_workflow:
        return (
            None,
            dbc.Alert(
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Please select a workflow from the Workflow Selection panel first."
                ],
                color="warning",
                dismissable=True,
            ),
            html.Div("No workflow selected", className="text-muted text-center p-3"),
            "0",
        )

    workflow_id = selected_workflow["id"]
    all_runs = "all_runs" in (options or [])
    failed_only = "failed_only" in (options or [])

    cli_wrapper = TorcCliWrapper()
    result = cli_wrapper.get_job_results_report(
        workflow_id,
        api_url=config.get("url"),
        output_dir=output_dir or "output",
        all_runs=all_runs,
    )

    if not result["success"]:
        error_msg = result.get("error", "Unknown error")
        return (
            None,
            dbc.Alert(
                [
                    html.I(className="fas fa-exclamation-circle me-2"),
                    f"Failed to generate report: {error_msg}"
                ],
                color="danger",
                dismissable=True,
            ),
            html.Div("Error generating report", className="text-muted text-center p-3"),
            "0",
        )

    report_data = result["data"]

    # Filter for failed jobs if requested
    # Note: CLI returns "results" not "jobs"
    jobs = report_data.get("results", [])
    if failed_only:
        jobs = [j for j in jobs if j.get("return_code") != 0]

    # Create table data
    # Note: CLI uses "job_stdout"/"job_stderr" not "stdout_path"/"stderr_path"
    table_data = []
    for job in jobs:
        return_code = job.get("return_code")

        table_data.append({
            "job_id": job.get("job_id", ""),
            "job_name": job.get("job_name", ""),
            "status": job.get("status", ""),
            "return_code": return_code if return_code is not None else "N/A",
            "run_id": job.get("run_id", ""),
            "stdout_path": job.get("job_stdout", ""),
            "stderr_path": job.get("job_stderr", ""),
        })

    if not table_data:
        return (
            report_data,
            dbc.Alert(
                [
                    html.I(className="fas fa-info-circle me-2"),
                    "Report generated but no matching jobs found."
                ],
                color="info",
                dismissable=True,
            ),
            html.Div("No jobs match the filter criteria", className="text-muted text-center p-3"),
            "0",
        )

    # Create the DataTable
    from dash import dash_table

    columns = [
        {"name": "Job ID", "id": "job_id"},
        {"name": "Job Name", "id": "job_name"},
        {"name": "Status", "id": "status"},
        {"name": "Return Code", "id": "return_code"},
        {"name": "Run ID", "id": "run_id"},
    ]

    table = dash_table.DataTable(
        id="debug-jobs-table",
        columns=columns,
        data=table_data,
        row_selectable="single",
        selected_rows=[],
        page_size=15,
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "10px",
            "fontSize": "13px",
        },
        style_header={
            "backgroundColor": "#f8f9fa",
            "fontWeight": "bold",
            "borderBottom": "2px solid #dee2e6",
        },
        style_data_conditional=[
            {
                "if": {"filter_query": "{return_code} != 0"},
                "backgroundColor": "#f8d7da",
                "color": "#721c24",
            },
            {
                "if": {"filter_query": "{return_code} = 0"},
                "backgroundColor": "#d4edda",
                "color": "#155724",
            },
            {
                "if": {"state": "selected"},
                "backgroundColor": "#cce5ff",
                "border": "1px solid #004085",
            },
        ],
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
    )

    job_count = len(table_data)
    failed_count = len([j for j in table_data if j["return_code"] != 0 and j["return_code"] != "N/A"])

    status_msg = f"Found {job_count} job(s)"
    if failed_count > 0:
        status_msg += f" ({failed_count} failed)"

    return (
        {"jobs": table_data, "raw": report_data},
        dbc.Alert(
            [
                html.I(className="fas fa-check-circle me-2"),
                status_msg
            ],
            color="success",
            dismissable=True,
        ),
        table,
        str(job_count),
    )


@callback(
    Output("debug-selected-job-store", "data"),
    Output("debug-selected-job-info", "children"),
    Output("debug-stdout-path", "children"),
    Output("debug-stderr-path", "children"),
    Output("debug-stdout-content", "children"),
    Output("debug-stderr-content", "children"),
    Input("debug-jobs-table", "selected_rows"),
    State("debug-report-store", "data"),
    prevent_initial_call=True,
)
def select_debug_job(
    selected_rows: list[int],
    report_data: dict | None,
) -> tuple[dict | None, str, str, str, str, str]:
    """Handle job selection and load log file contents."""
    if not selected_rows or not report_data:
        return (
            None,
            "No job selected. Click on a row in the table above.",
            "",
            "",
            "No stdout file loaded",
            "No stderr file loaded",
        )

    jobs = report_data.get("jobs", [])
    if not jobs or selected_rows[0] >= len(jobs):
        return (
            None,
            "Invalid selection",
            "",
            "",
            "No stdout file loaded",
            "No stderr file loaded",
        )

    job = jobs[selected_rows[0]]
    job_name = job.get("job_name", "Unknown")
    job_id = job.get("job_id", "")
    return_code = job.get("return_code", "N/A")
    status = job.get("status", "")

    # Build job info display
    return_code_class = "text-success" if return_code == 0 else "text-danger"
    job_info = html.Div([
        html.Strong(f"{job_name}"),
        html.Span(f" (ID: {job_id})", className="text-muted"),
        html.Span(" | ", className="mx-2"),
        html.Span(f"Status: {status}", className="me-2"),
        html.Span(" | ", className="mx-2"),
        html.Span(f"Return Code: ", className="me-1"),
        html.Span(str(return_code), className=return_code_class + " fw-bold"),
    ])

    # Get file paths
    stdout_path = job.get("stdout_path", "")
    stderr_path = job.get("stderr_path", "")

    # Load stdout content
    stdout_content = "No stdout file available"
    if stdout_path:
        stdout_file = Path(stdout_path)
        if stdout_file.exists():
            try:
                content = stdout_file.read_text()
                if content.strip():
                    stdout_content = content
                else:
                    stdout_content = "(empty file)"
            except Exception as e:
                stdout_content = f"Error reading file: {e}"
        else:
            stdout_content = f"File not found: {stdout_path}"

    # Load stderr content
    stderr_content = "No stderr file available"
    if stderr_path:
        stderr_file = Path(stderr_path)
        if stderr_file.exists():
            try:
                content = stderr_file.read_text()
                if content.strip():
                    stderr_content = content
                else:
                    stderr_content = "(empty file)"
            except Exception as e:
                stderr_content = f"Error reading file: {e}"
        else:
            stderr_content = f"File not found: {stderr_path}"

    return (
        job,
        job_info,
        stdout_path or "N/A",
        stderr_path or "N/A",
        stdout_content,
        stderr_content,
    )
