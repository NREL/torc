"""Callback functions for the Torc Dash app."""

import base64
import tempfile
import os
from concurrent.futures import Future
from typing import Any, Dict, List, Optional, Tuple

from dash import callback, Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from .layouts import create_view_tab_layout, create_run_tab_layout, create_data_table
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
# Tab Navigation Callbacks
# ============================================================================

@callback(
    Output("tab-content", "children"),
    Output("refresh-interval", "disabled"),
    Input("main-tabs", "active_tab"),
)
def render_tab_content(active_tab: str) -> Tuple[html.Div, bool]:
    """Render the content for the active tab."""
    if active_tab == "view-tab":
        return create_view_tab_layout(), False  # Enable auto-refresh
    elif active_tab == "run-tab":
        return create_run_tab_layout(), True  # Disable auto-refresh
    else:
        return html.Div("Tab content not implemented"), True


# ============================================================================
# View Tab Callbacks
# ============================================================================

@callback(
    Output("workflow-filter-select", "options"),
    Output("workflow-filter-select", "value"),
    Input("main-tabs", "active_tab"),
    Input("refresh-button", "n_clicks"),
    Input("refresh-interval", "n_intervals"),
    State("api-config-store", "data"),
    prevent_initial_call=False,
)
def update_workflow_filter_dropdown(
    active_tab: str,
    n_clicks: int,
    n_intervals: int,
    config: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], Optional[int]]:
    """Update workflow filter dropdown options."""
    # Only update if we're on the view tab
    if active_tab != "view-tab":
        raise PreventUpdate

    if not config:
        return [], None

    api_wrapper = TorcApiWrapper(config["url"], config.get("username"))
    result = api_wrapper.list_workflows(limit=1000)

    if not result["success"]:
        return [], None

    workflows = result["data"]
    options = [
        {"label": f"{w['name']} (ID: {w['id']})", "value": w["id"]}
        for w in workflows
    ]

    return options, None


@callback(
    Output("auto-refresh-toggle", "value"),
    Input("auto-refresh-toggle", "value"),
)
def update_auto_refresh(value: List[str]) -> List[str]:
    """Handle auto-refresh toggle."""
    return value


@callback(
    Output("selected-workflow-store", "data"),
    Input("workflows-table", "selected_rows"),
    State("workflows-table", "data"),
    prevent_initial_call=True,
)
def store_selected_workflow(
    selected_rows: List[int],
    table_data: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Store the selected workflow when a row is clicked."""
    if not selected_rows or not table_data:
        return None

    # Get the first selected row
    row_index = selected_rows[0]
    if row_index < len(table_data):
        return table_data[row_index]

    return None


@callback(
    Output("resource-table-container", "children"),
    Output("view-status-message", "children"),
    Input("refresh-button", "n_clicks"),
    Input("refresh-interval", "n_intervals"),
    Input("resource-type-select", "value"),
    Input("workflow-filter-select", "value"),
    State("api-config-store", "data"),
    State("auto-refresh-toggle", "value"),
    prevent_initial_call=False,
)
def update_resource_table(
    n_clicks: int,
    n_intervals: int,
    resource_type: str,
    workflow_id: Optional[int],
    config: Dict[str, str],
    auto_refresh: List[str],
) -> Tuple[html.Div, Optional[html.Div]]:
    """Update the resource table based on selected type and filters."""
    # Only update on interval if auto-refresh is enabled
    from dash import ctx
    if ctx.triggered_id == "refresh-interval" and "auto" not in auto_refresh:
        raise PreventUpdate

    if not config:
        return html.Div("Please configure the API URL first"), dbc.Alert(
            "Configuration required",
            color="warning",
        )

    api_wrapper = TorcApiWrapper(config["url"], config.get("username"))

    # Fetch data based on resource type
    try:
        if resource_type == "workflows":
            result = api_wrapper.list_workflows(limit=1000)
        elif resource_type in ["jobs", "results", "events", "files", "user_data", "compute_nodes", "resource_requirements"]:
            if not workflow_id:
                return html.Div("Please select a workflow to view these resources"), dbc.Alert(
                    "Workflow selection required for this resource type",
                    color="info",
                )

            method_map = {
                "jobs": api_wrapper.list_jobs,
                "results": api_wrapper.list_results,
                "events": api_wrapper.list_events,
                "files": api_wrapper.list_files,
                "user_data": api_wrapper.list_user_data,
                "compute_nodes": api_wrapper.list_compute_nodes,
                "resource_requirements": api_wrapper.list_resource_requirements,
            }
            result = method_map[resource_type](workflow_id, limit=1000)
        else:
            return html.Div(f"Unknown resource type: {resource_type}"), dbc.Alert(
                f"Unknown resource type: {resource_type}",
                color="danger",
            )

        if not result["success"]:
            error_msg = result.get("error", "Unknown error")
            return html.Div(f"Error: {error_msg}"), dbc.Alert(
                f"Error fetching data: {error_msg}",
                color="danger",
                dismissable=True,
            )

        data = result["data"]

        if not data:
            return html.Div(
                dbc.Alert(
                    f"No {resource_type} found",
                    color="info",
                )
            ), None

        # Format columns
        columns = format_table_columns(data)

        # Create table with selection enabled for workflows
        enable_selection = (resource_type == "workflows")
        table = create_data_table(data, columns, f"{resource_type}-table", enable_selection)

        selection_help = None
        if enable_selection:
            selection_help = dbc.Alert(
                [
                    html.I(className="fas fa-info-circle me-2"),
                    "Click on a row to select a workflow. Selected workflows can be run from the 'Run Workflows' tab."
                ],
                color="info",
                className="mb-2",
            )

        return html.Div(
            [
                html.P(f"Total {resource_type}: {result['total']}", className="text-muted mb-2"),
                selection_help,
                table,
            ]
        ), None

    except Exception as e:
        return html.Div(f"Error: {str(e)}"), dbc.Alert(
            f"Unexpected error: {str(e)}",
            color="danger",
            dismissable=True,
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
    Output("execution-options-info", "children"),
    Input("execution-mode-radio", "value"),
    Input("create-workflow-checkbox", "value"),
)
def update_execution_options_info(
    execution_mode: str,
    create_workflow: List[str],
) -> html.Div:
    """Update execution options information."""
    if execution_mode == "run":
        mode_desc = "Executes the workflow on the local computer using available resources."
    else:
        mode_desc = "Submits the workflow to an HPC/Slurm scheduler for execution."

    if "create" in create_workflow:
        process_desc = html.P(
            [
                html.Strong("Two-step process:"),
                html.Br(),
                "1. Create workflow from specification",
                html.Br(),
                "2. Then run/submit the created workflow",
            ],
            className="text-muted small mb-0"
        )
    else:
        process_desc = html.P(
            [
                html.Strong("One-step process:"),
                html.Br(),
                "Create and execute in a single command",
            ],
            className="text-muted small mb-0"
        )

    return html.Div(
        [
            dbc.Alert(mode_desc, color="info", className="mb-2"),
            process_desc,
        ]
    )


@callback(
    Output("execution-output", "children"),
    Output("cancel-execution-button", "disabled"),
    Output("execute-workflow-button", "disabled"),
    Input("execute-workflow-button", "n_clicks"),
    State("workflow-source-tabs", "active_tab"),
    State("uploaded-spec-store", "data"),
    State("workflow-spec-path-input", "value"),
    State("selected-workflow-store", "data"),
    State("execution-mode-radio", "value"),
    State("create-workflow-checkbox", "value"),
    State("api-config-store", "data"),
    prevent_initial_call=True,
)
def execute_workflow(
    n_clicks: int,
    workflow_source_tab: str,
    uploaded_spec: Optional[Dict[str, str]],
    spec_path: Optional[str],
    selected_workflow: Optional[Dict[str, Any]],
    execution_mode: str,
    create_workflow: List[str],
    config: Dict[str, str],
) -> Tuple[str, bool, bool]:
    """Execute or submit a workflow."""
    if not n_clicks:
        raise PreventUpdate

    cli_wrapper = TorcCliWrapper()

    # Determine the workflow source
    workflow_spec_path = None
    temp_file = None

    try:
        if workflow_source_tab == "new-workflow-tab":
            if uploaded_spec:
                # Save uploaded content to a temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".yaml",
                    delete=False
                )
                temp_file.write(uploaded_spec["content"])
                temp_file.close()
                workflow_spec_path = temp_file.name
            elif spec_path:
                workflow_spec_path = spec_path
            else:
                return "Error: No workflow specification provided", True, False
        elif workflow_source_tab == "existing-workflow-tab":
            if selected_workflow and "id" in selected_workflow:
                workflow_spec_path = str(selected_workflow["id"])
            else:
                return "Error: No workflow selected. Please select a workflow from the 'View Resources' tab first.", True, False
        else:
            return "Error: Unknown workflow source", True, False

        # Execute based on mode
        output_lines = []

        if "create" in create_workflow and workflow_source_tab == "new-workflow-tab":
            # Two-step process: create first
            output_lines.append("Creating workflow...\n")
            create_result = cli_wrapper.create_workflow(
                workflow_spec_path,
                api_url=config.get("url")
            )

            if not create_result["success"]:
                error_msg = create_result.get("error", "Unknown error")
                output_lines.append(f"\nError creating workflow: {error_msg}\n")
                output_lines.append(f"\nStderr:\n{create_result.get('stderr', '')}")
                return "\n".join(output_lines), True, False

            output_lines.append(create_result["stdout"])

            # Extract workflow ID from output (assuming it's in the output)
            # This is a simplified extraction - may need adjustment based on actual output
            try:
                import re
                match = re.search(r"Workflow ID:\s*(\d+)", create_result["stdout"])
                if match:
                    workflow_id = match.group(1)
                    output_lines.append(f"\nWorkflow created with ID: {workflow_id}\n")
                    workflow_spec_path = workflow_id
                else:
                    output_lines.append("\nWarning: Could not extract workflow ID from output")
            except Exception as e:
                output_lines.append(f"\nWarning: Error extracting workflow ID: {str(e)}")

        # Run or submit the workflow
        if execution_mode == "run":
            output_lines.append("\nRunning workflow locally...\n")
            result = cli_wrapper.run_workflow(
                workflow_spec_path,
                api_url=config.get("url")
            )
        else:
            output_lines.append("\nSubmitting workflow to HPC/Slurm...\n")
            result = cli_wrapper.submit_workflow(
                workflow_spec_path,
                api_url=config.get("url")
            )

        if result["success"]:
            output_lines.append(result["stdout"])
            if result["stderr"]:
                output_lines.append(f"\nWarnings/Info:\n{result['stderr']}")
            output_lines.append("\n✓ Execution completed successfully")
        else:
            error_msg = result.get("error", "Unknown error")
            output_lines.append(f"\n✗ Execution failed: {error_msg}\n")
            output_lines.append(f"\nStdout:\n{result.get('stdout', '')}")
            output_lines.append(f"\nStderr:\n{result.get('stderr', '')}")

        return "\n".join(output_lines), True, False

    except Exception as e:
        return f"Error: {str(e)}", True, False

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass


# Note: Cancel execution is a placeholder - actual implementation would require
# process management and is left for future enhancement
@callback(
    Output("execution-output", "children", allow_duplicate=True),
    Input("cancel-execution-button", "n_clicks"),
    prevent_initial_call=True,
)
def cancel_workflow_execution(n_clicks: int) -> str:
    """Cancel workflow execution (placeholder)."""
    if not n_clicks:
        raise PreventUpdate

    return "Cancellation not yet implemented. Close the terminal or use Ctrl+C if running in foreground."
