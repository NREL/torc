"""Layout definitions for different tabs in the Torc Dash app."""

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import dash_table, dcc, html


def create_view_tab_layout():
    """Create the layout for the View Details tab."""
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("Workflow Details", className="mb-3"),
                            html.P(
                                "View jobs, results, events, files, and other resources for the selected workflow",
                                className="text-muted"
                            ),
                        ],
                        width=10,
                    ),
                    dbc.Col(
                        [
                            dbc.Button(
                                [html.I(className="fas fa-sync-alt me-2"), "Refresh"],
                                id="refresh-workflow-details-button",
                                color="primary",
                                className="mt-2",
                            ),
                        ],
                        width=2,
                        className="d-flex justify-content-end",
                    ),
                ]
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(id="workflow-details-panel"),
                        ],
                        className="mb-3"
                    ),
                ],
                className="mb-4"
            ),
        ],
        fluid=True
    )


def create_run_tab_layout():
    """Create the layout for the unified Workflows tab.

    This is a workflow-centric design where:
    1. Workflow list is always visible with inline status and actions
    2. "Create New Workflow" opens a modal
    3. Selecting a row shows the detail panel with contextual actions
    """
    return dbc.Container(
        [
            # Header row with title and Create button
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("Workflows", className="mb-1"),
                            html.P(
                                "Create, manage, and execute workflows",
                                className="text-muted mb-0"
                            ),
                        ],
                        width=8,
                    ),
                    dbc.Col(
                        [
                            dbc.Button(
                                [html.I(className="fas fa-plus me-2"), "Create New Workflow"],
                                id="open-create-workflow-modal-btn",
                                color="primary",
                                size="lg",
                                className="float-end",
                            ),
                        ],
                        width=4,
                        className="d-flex align-items-center justify-content-end",
                    ),
                ],
                className="mb-3"
            ),

            # Workflow list card
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.I(className="fas fa-list me-2"),
                                                "All Workflows",
                                            ],
                                            width="auto",
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.InputGroup(
                                                    [
                                                        dbc.InputGroupText(
                                                            html.I(className="fas fa-search"),
                                                        ),
                                                        dbc.Input(
                                                            id="workflow-filter-input",
                                                            type="text",
                                                            placeholder="Filter workflows...",
                                                            size="sm",
                                                        ),
                                                    ],
                                                    size="sm",
                                                ),
                                            ],
                                            width=3,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    [html.I(className="fas fa-sync-alt me-1"), "Refresh"],
                                                    id="workflows-refresh-btn",
                                                    color="secondary",
                                                    size="sm",
                                                    outline=True,
                                                    className="me-2",
                                                ),
                                                dbc.Checklist(
                                                    id="workflows-auto-refresh-toggle",
                                                    options=[{"label": " Auto", "value": "auto"}],
                                                    value=[],
                                                    inline=True,
                                                    switch=True,
                                                    style={"display": "inline-block"},
                                                ),
                                            ],
                                            width="auto",
                                            className="ms-auto d-flex align-items-center",
                                        ),
                                    ],
                                    align="center",
                                    className="g-2",
                                ),
                            ),
                            dbc.CardBody(
                                [
                                    html.Div(id="unified-workflows-table-container"),
                                ],
                                style={"padding": "0"},
                            ),
                        ],
                        className="mb-3"
                    ),
                ),
            ),

            # Hidden interval for auto-refresh (reuses existing interval)
            dcc.Interval(id="workflows-auto-refresh-interval", interval=30000, disabled=True),

            # Selected workflow detail panel (static layout, dynamically shown/hidden)
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                html.H5(
                                    [
                                        html.I(className="fas fa-cog me-2"),
                                        html.Span(id="detail-panel-workflow-name"),
                                        html.Small(id="detail-panel-workflow-id", className="text-muted ms-2"),
                                    ],
                                    className="mb-0"
                                ),
                            ),
                            # Hidden element to keep callback working
                            html.Span(id="detail-panel-status-badge", style={"display": "none"}),
                            dbc.CardBody(
                                [
                                    # Workflow info
                                    dbc.Row(
                                        [
                                            dbc.Col([html.Strong("User: "), html.Span(id="detail-panel-user")], md=3),
                                            dbc.Col([html.Strong("Created: "), html.Span(id="detail-panel-timestamp")], md=3),
                                            dbc.Col([html.Strong("Description: "), html.Span(id="detail-panel-description")], md=6),
                                        ],
                                        className="mb-3"
                                    ),

                                    html.Hr(),

                                    # Action buttons
                                    dbc.Row(
                                        [
                                            # Management actions
                                            dbc.Col(
                                                [
                                                    html.Label("Management", className="fw-bold text-muted small mb-2"),
                                                    html.Div(
                                                        [
                                                            dbc.Button(
                                                                [html.I(className="fas fa-sync me-1"), "Initialize"],
                                                                id="initialize-existing-workflow-button",
                                                                color="primary",
                                                                size="sm",
                                                                className="me-2",
                                                            ),
                                                            dbc.Button(
                                                                [html.I(className="fas fa-redo me-1"), "Re-init"],
                                                                id="reinitialize-workflow-button",
                                                                color="warning",
                                                                size="sm",
                                                                className="me-2",
                                                            ),
                                                            dbc.Button(
                                                                [html.I(className="fas fa-rotate-left me-1"), "Reset"],
                                                                id="reset-workflow-button",
                                                                color="info",
                                                                size="sm",
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                md=4,
                                            ),
                                            # Execution actions
                                            dbc.Col(
                                                [
                                                    html.Label("Execution", className="fw-bold text-muted small mb-2"),
                                                    html.Div(
                                                        [
                                                            dbc.Button(
                                                                [html.I(className="fas fa-play me-1"), "Run Locally"],
                                                                id="run-workflow-button",
                                                                color="success",
                                                                size="sm",
                                                                className="me-2",
                                                            ),
                                                            dbc.Button(
                                                                [html.I(className="fas fa-paper-plane me-1"), "Submit to HPC"],
                                                                id="submit-workflow-button",
                                                                color="success",
                                                                outline=True,
                                                                size="sm",
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                md=4,
                                            ),
                                            # Visualization actions
                                            dbc.Col(
                                                [
                                                    html.Label("Visualize", className="fw-bold text-muted small mb-2"),
                                                    html.Div(
                                                        [
                                                            dbc.Button(
                                                                [html.I(className="fas fa-project-diagram me-1"), "DAG"],
                                                                id="show-dag-button",
                                                                color="info",
                                                                outline=True,
                                                                size="sm",
                                                                className="me-2",
                                                            ),
                                                            dbc.Button(
                                                                [html.I(className="fas fa-list-ol me-1"), "Plan"],
                                                                id="show-execution-plan-button",
                                                                color="info",
                                                                outline=True,
                                                                size="sm",
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                md=4,
                                            ),
                                        ],
                                        className="mb-2"
                                    ),

                                    # Status message area
                                    html.Div(id="workflow-management-status", className="mt-3"),
                                ],
                            ),
                        ],
                        id="workflow-detail-card",
                        className="border-primary",
                        style={"display": "none"},  # Hidden by default
                    ),
                ),
            ),

            # Placeholder for when no workflow is selected
            dbc.Row(
                dbc.Col(
                    dbc.Alert(
                        [
                            html.I(className="fas fa-hand-pointer me-2"),
                            "Click on a workflow row above to view details and actions"
                        ],
                        id="no-workflow-selected-alert",
                        color="light",
                        className="text-center",
                    ),
                ),
            ),

            # Create Workflow Modal
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle([
                        html.I(className="fas fa-plus-circle me-2"),
                        "Create New Workflow"
                    ])),
                    dbc.ModalBody([
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    [
                                        html.Div(
                                            [
                                                dbc.Label("Upload Workflow Spec File", className="mt-3 fw-bold"),
                                                dcc.Upload(
                                                    id="upload-workflow-spec",
                                                    children=html.Div(
                                                        [
                                                            html.I(className="fas fa-cloud-upload-alt fa-2x mb-2"),
                                                            html.Br(),
                                                            "Drag and Drop or ",
                                                            html.A("Select a File", className="text-primary"),
                                                        ],
                                                        style={
                                                            "textAlign": "center",
                                                            "padding": "30px",
                                                            "borderWidth": "2px",
                                                            "borderStyle": "dashed",
                                                            "borderRadius": "5px",
                                                            "cursor": "pointer",
                                                            "backgroundColor": "#f8f9fa",
                                                        }
                                                    ),
                                                    multiple=False,
                                                ),
                                                html.Div(id="upload-status", className="mt-2"),
                                            ]
                                        )
                                    ],
                                    label="Upload File",
                                    tab_id="upload-tab",
                                ),
                                dbc.Tab(
                                    [
                                        html.Div(
                                            [
                                                dbc.Label("Workflow Spec File Path", className="mt-3 fw-bold"),
                                                dbc.Input(
                                                    id="workflow-spec-path-input",
                                                    type="text",
                                                    placeholder="/path/to/workflow.yaml",
                                                ),
                                                dbc.FormText("Enter the full path to a YAML, JSON, or JSON5 workflow spec file."),
                                            ]
                                        )
                                    ],
                                    label="File Path",
                                    tab_id="path-tab",
                                ),
                            ],
                            id="create-workflow-source-tabs",
                            active_tab="upload-tab",
                        ),
                        html.Hr(),
                        dbc.Checklist(
                            id="create-workflow-options",
                            options=[
                                {"label": " Initialize workflow after creation", "value": "initialize"},
                                {"label": " Run workflow immediately after creation", "value": "run"},
                            ],
                            value=["initialize"],
                            className="mb-3",
                        ),
                        html.Div(id="create-workflow-status"),
                    ]),
                    dbc.ModalFooter([
                        dbc.Button(
                            "Cancel",
                            id="create-workflow-cancel-btn",
                            color="secondary",
                            className="me-2",
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-plus me-2"), "Create"],
                            id="create-workflow-confirm-btn",
                            color="primary",
                        ),
                    ]),
                ],
                id="create-workflow-modal",
                is_open=False,
                size="lg",
                backdrop="static",
            ),

            # Store for uploaded file content
            dcc.Store(id="uploaded-spec-store"),

            # Store for the workflow being created (temp)
            dcc.Store(id="workflows-store"),

            # Hidden elements for backward compatibility with old callbacks
            html.Div(id="existing-workflow-info", style={"display": "none"}),
            html.Div(id="workflow-creation-status", style={"display": "none"}),
            dcc.Store(id="workflow-source-tabs", data="existing-workflow-tab"),
            html.Div(id="create-workflow-button", style={"display": "none"}),
            dcc.Checklist(id="initialize-workflow-checkbox", options=[], value=[], style={"display": "none"}),
            html.Div(id="execute-workflow-button", style={"display": "none"}),
            dcc.RadioItems(id="execution-mode-radio", options=[], value="run", style={"display": "none"}),

            # Modals for workflow management actions (initialization, reinitialize, execute)
            # Modal for confirming file deletion during initialization
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Confirm Initialization")),
                    dbc.ModalBody([
                        html.Div(id="initialize-modal-message"),
                    ]),
                    dbc.ModalFooter([
                        dbc.Button(
                            "Cancel",
                            id="initialize-modal-cancel",
                            className="me-2",
                            color="secondary",
                        ),
                        dbc.Button(
                            "Delete Files and Initialize",
                            id="initialize-modal-confirm",
                            color="danger",
                        ),
                    ]),
                ],
                id="initialize-confirmation-modal",
                is_open=False,
                backdrop="static",
            ),

            # Store for initialization check data
            dcc.Store(id="initialize-check-store"),

            # Modal for confirming file deletion during reinitialize
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Confirm Re-initialization")),
                    dbc.ModalBody([
                        html.Div(id="reinitialize-modal-message"),
                    ]),
                    dbc.ModalFooter([
                        dbc.Button(
                            "Cancel",
                            id="reinitialize-modal-cancel",
                            className="me-2",
                            color="secondary",
                        ),
                        dbc.Button(
                            "Delete Files and Re-initialize",
                            id="reinitialize-modal-confirm",
                            color="danger",
                        ),
                    ]),
                ],
                id="reinitialize-confirmation-modal",
                is_open=False,
                backdrop="static",
            ),

            # Store for reinitialize check data
            dcc.Store(id="reinitialize-check-store"),

            # Modal for confirming file deletion during execute
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Confirm Workflow Execution")),
                    dbc.ModalBody([
                        html.Div(id="execute-modal-message"),
                    ]),
                    dbc.ModalFooter([
                        dbc.Button(
                            "Cancel",
                            id="execute-modal-cancel",
                            className="me-2",
                            color="secondary",
                        ),
                        dbc.Button(
                            "Delete Files and Execute",
                            id="execute-modal-confirm",
                            color="danger",
                        ),
                    ]),
                ],
                id="execute-confirmation-modal",
                is_open=False,
                backdrop="static",
            ),

            # Store for execute check data
            dcc.Store(id="execute-check-store"),

            # Modal for execution plan
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle([
                        html.I(className="fas fa-list-ol me-2"),
                        "Workflow Execution Plan"
                    ])),
                    dbc.ModalBody(id="execution-plan-modal-body"),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="execution-plan-close-btn", className="ms-auto", color="secondary")
                    ),
                ],
                id="execution-plan-modal",
                is_open=False,
                size="xl",
                scrollable=True,
            ),

            # Polling interval for real-time output
            dcc.Interval(id="execution-poll-interval", interval=1000, disabled=True),

            # Execution output panel (shown when running)
            dbc.Row(
                dbc.Col(
                    dbc.Collapse(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.I(className="fas fa-terminal me-2"),
                                                    "Execution Output"
                                                ],
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                dbc.Button(
                                                    [html.I(className="fas fa-stop me-2"), "Cancel"],
                                                    id="cancel-execution-button",
                                                    color="danger",
                                                    size="sm",
                                                ),
                                                width="auto",
                                                className="ms-auto",
                                            ),
                                        ],
                                        align="center",
                                    ),
                                ),
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            id="execution-output",
                                            style={
                                                "fontFamily": "monospace",
                                                "whiteSpace": "pre-wrap",
                                                "backgroundColor": "#1e1e1e",
                                                "color": "#d4d4d4",
                                                "padding": "15px",
                                                "borderRadius": "5px",
                                                "minHeight": "200px",
                                                "maxHeight": "400px",
                                                "overflowY": "auto",
                                            }
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-3"
                        ),
                        id="execution-output-collapse",
                        is_open=False,
                    ),
                ),
            ),
        ],
        fluid=True
    )


def _get_status_color(status: str | None) -> str:
    """Get Bootstrap color for workflow status."""
    status_colors = {
        "uninitialized": "secondary",
        "ready": "primary",
        "running": "warning",
        "completed": "success",
        "failed": "danger",
        "canceled": "dark",
    }
    return status_colors.get(status or "", "secondary")


def create_data_table(data, columns, table_id, enable_selection=False, tooltip_data=None):
    """Create a Dash DataTable with common styling and features.

    Args:
        data: List of dictionaries containing table data
        columns: List of column definitions
        table_id: Unique ID for the table
        enable_selection: Enable row selection (default: False)
        tooltip_data: Optional list of dictionaries mapping column IDs to tooltip text

    Returns:
        dash_table.DataTable component
    """
    style_data_conditional = [
        {
            "if": {"row_index": "odd"},
            "backgroundColor": "#f8f9fa",
        }
    ]

    # Add selection highlighting
    if enable_selection:
        style_data_conditional.append({
            "if": {"state": "selected"},
            "backgroundColor": "#0d6efd",
            "color": "white",
            "border": "1px solid #0d6efd",
        })

    table_props = {
        "id": table_id,
        "data": data,
        "columns": columns,
        "filter_action": "native",
        "sort_action": "native",
        "sort_mode": "multi",
        "page_action": "native",
        "page_current": 0,
        "page_size": 20,
        "row_selectable": "single" if enable_selection else False,
        "selected_rows": [],
        "style_table": {
            "overflowX": "auto",
        },
        "style_cell": {
            "textAlign": "left",
            "padding": "10px",
            "minWidth": "100px",
            "maxWidth": "300px",
            "whiteSpace": "normal",
            "height": "auto",
        },
        "style_header": {
            "backgroundColor": "#f8f9fa",
            "fontWeight": "bold",
            "border": "1px solid #dee2e6",
        },
        "style_data": {
            "border": "1px solid #dee2e6",
        },
        "style_data_conditional": style_data_conditional,
    }

    # Add tooltip data if provided
    if tooltip_data:
        table_props["tooltip_data"] = tooltip_data
        table_props["tooltip_delay"] = 0
        table_props["tooltip_duration"] = None

    return dash_table.DataTable(**table_props)


def create_monitor_tab_layout():
    """Create the layout for the Monitor Events tab."""
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("Monitor Events", className="mb-3"),
                            html.P(
                                "Monitor workflow events in real-time",
                                className="text-muted"
                            ),
                        ]
                    )
                ]
            ),

            # Controls
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Monitor Configuration")),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Label("Workflow", html_for="monitor-workflow-select"),
                                                            dbc.Checklist(
                                                                id="monitor-use-selected-workflow",
                                                                options=[
                                                                    {"label": " Use selected workflow from View Details tab", "value": "use_selected"},
                                                                ],
                                                                value=[],
                                                                className="mb-2",
                                                            ),
                                                            dcc.Dropdown(
                                                                id="monitor-workflow-select",
                                                                placeholder="Or select a workflow to monitor",
                                                                clearable=True,
                                                                searchable=True,
                                                            ),
                                                            html.Div(id="monitor-selected-workflow-display", className="mt-2 text-muted"),
                                                        ],
                                                        md=6,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Label("Poll Interval (seconds)", html_for="monitor-poll-interval"),
                                                            dbc.Input(
                                                                id="monitor-poll-interval",
                                                                type="number",
                                                                value=10,
                                                                min=10,
                                                                step=1,
                                                            ),
                                                            dbc.FormText("Minimum: 10 seconds"),
                                                        ],
                                                        md=3,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Label("Controls", html_for="monitor-start-button"),
                                                            dbc.Button(
                                                                [html.I(className="fas fa-play me-2"), "Start Monitoring"],
                                                                id="monitor-start-button",
                                                                color="success",
                                                                className="w-100 mb-2",
                                                            ),
                                                            dbc.Button(
                                                                [html.I(className="fas fa-stop me-2"), "Stop Monitoring"],
                                                                id="monitor-stop-button",
                                                                color="danger",
                                                                className="w-100 mb-2",
                                                                disabled=True,
                                                            ),
                                                            dbc.Button(
                                                                [html.I(className="fas fa-eraser me-2"), "Clear Events"],
                                                                id="monitor-clear-button",
                                                                color="secondary",
                                                                className="w-100",
                                                            ),
                                                        ],
                                                        md=3,
                                                    ),
                                                ],
                                                className="mb-3"
                                            ),
                                        ]
                                    ),
                                ],
                                className="mb-4"
                            ),
                        ]
                    )
                ]
            ),

            # Events display
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(className="fas fa-list me-2"),
                                            "Events",
                                            html.Span(id="monitor-event-count", className="badge bg-primary ms-2"),
                                        ]
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Loading(
                                                id="loading-events",
                                                type="default",
                                                children=html.Div(
                                                    id="monitor-events-container",
                                                    style={
                                                        "fontFamily": "monospace",
                                                        "whiteSpace": "pre-wrap",
                                                        "backgroundColor": "#f8f9fa",
                                                        "padding": "15px",
                                                        "borderRadius": "5px",
                                                        "minHeight": "400px",
                                                        "maxHeight": "600px",
                                                        "overflowY": "auto",
                                                    },
                                                    children="Select a workflow and click 'Start Monitoring' to begin"
                                                ),
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ]
                    )
                ]
            ),

            # Hidden stores
            dcc.Store(id="monitor-is-active", data=False),
            dcc.Store(id="monitor-last-event-id", data=None),
            dcc.Interval(id="monitor-interval", interval=10000, disabled=True),
        ],
        fluid=True
    )


def create_dag_tab_layout(workflow_id: int | None = None):
    """Create the layout for the DAG visualization tab.

    Args:
        workflow_id: The workflow ID to visualize (optional)

    Returns:
        Layout for the DAG tab
    """
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("Workflow DAG Visualization", className="mb-3"),
                            html.P(
                                "Visual representation of job dependencies, file relationships, and user data relationships",
                                className="text-muted"
                            ),
                        ]
                    )
                ]
            ),

            # DAG visualizations
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(id="dag-load-status", className="mb-3"),
                            dbc.Tabs(
                                [
                                    dbc.Tab(
                                        label="Job Dependencies",
                                        tab_id="job-deps-graph-tab",
                                        children=[
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        [
                                                            html.I(className="fas fa-sitemap me-2"),
                                                            "Job-Job Dependencies"
                                                        ]
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            dcc.Loading(
                                                                id="loading-job-deps-graph",
                                                                type="default",
                                                                children=html.Div(id="job-deps-graph-container"),
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                className="mt-3"
                                            ),
                                        ],
                                    ),
                                    dbc.Tab(
                                        label="File Relationships",
                                        tab_id="file-rels-graph-tab",
                                        children=[
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        [
                                                            html.I(className="fas fa-file me-2"),
                                                            "Job-File Relationships"
                                                        ]
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            dcc.Loading(
                                                                id="loading-file-rels-graph",
                                                                type="default",
                                                                children=html.Div(id="file-rels-graph-container"),
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                className="mt-3"
                                            ),
                                        ],
                                    ),
                                    dbc.Tab(
                                        label="User Data Relationships",
                                        tab_id="user-data-rels-graph-tab",
                                        children=[
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        [
                                                            html.I(className="fas fa-database me-2"),
                                                            "Job-User Data Relationships"
                                                        ]
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            dcc.Loading(
                                                                id="loading-user-data-rels-graph",
                                                                type="default",
                                                                children=html.Div(id="user-data-rels-graph-container"),
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                className="mt-3"
                                            ),
                                        ],
                                    ),
                                ],
                                id="dag-graph-tabs",
                                active_tab="job-deps-graph-tab",
                            ),
                        ],
                    ),
                ],
                className="mb-4"
            ),
        ],
        fluid=True
    )


def create_resource_plots_tab_layout():
    """Create the layout for the Resource Plots tab."""
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.I(className="fas fa-chart-line me-2"),
                                    "Resource Utilization Plots"
                                ]
                            ),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Label("Select Database", html_for="db-select"),
                                                    dcc.Dropdown(
                                                        id="db-select",
                                                        placeholder="Select a resource monitoring database...",
                                                        clearable=True,
                                                    ),
                                                ],
                                                md=8,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Label("\u00A0"),  # Spacer
                                                    dbc.Button(
                                                        [html.I(className="fas fa-sync me-2"), "Refresh DBs"],
                                                        id="refresh-dbs-button",
                                                        color="secondary",
                                                        className="w-100",
                                                    ),
                                                ],
                                                md=2,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Label("\u00A0"),  # Spacer
                                                    dbc.Button(
                                                        [html.I(className="fas fa-chart-area me-2"), "Generate Plots"],
                                                        id="generate-plots-button",
                                                        color="primary",
                                                        className="w-100",
                                                        disabled=True,
                                                    ),
                                                ],
                                                md=2,
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    dbc.Row(
                                        dbc.Col(
                                            html.Div(id="plot-status-message")
                                        )
                                    ),
                                ]
                            ),
                        ],
                        className="mb-4"
                    )
                )
            ),

            # Plot selection and display
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.I(className="fas fa-chart-bar me-2"),
                                    "Plot Viewer"
                                ]
                            ),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        dbc.Col(
                                            [
                                                dbc.Label("Select Plot", html_for="plot-select"),
                                                dcc.Dropdown(
                                                    id="plot-select",
                                                    placeholder="Generate plots first...",
                                                    clearable=True,
                                                ),
                                            ],
                                            md=12,
                                        ),
                                        className="mb-3",
                                    ),
                                    dbc.Row(
                                        dbc.Col(
                                            dcc.Graph(
                                                id="resource-plot-graph",
                                                style={"height": "600px"},
                                            )
                                        )
                                    ),
                                ]
                            ),
                        ],
                        className="mb-4"
                    )
                )
            ),

            # Store for generated plot files
            dcc.Store(id="plot-files-store"),
        ],
        fluid=True
    )


def create_debugging_tab_layout():
    """Create the layout for the Debugging tab.

    Returns
    -------
    dbc.Container
        Layout component for the debugging tab.
    """
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("Job Debugging", className="mb-3"),
                            html.P(
                                "View stdout/stderr files and debug job execution issues",
                                className="text-muted"
                            ),
                        ]
                    )
                ]
            ),

            # Job Results Report section
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.I(className="fas fa-file-alt me-2"),
                                    "Job Results Report"
                                ]
                            ),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Label("Output Directory"),
                                                    dbc.Input(
                                                        id="debug-output-dir",
                                                        type="text",
                                                        value="output",
                                                        placeholder="output",
                                                    ),
                                                    dbc.FormText(
                                                        "Directory where job logs are stored"
                                                    ),
                                                ],
                                                md=4,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Label("Options"),
                                                    dbc.Checklist(
                                                        id="debug-report-options",
                                                        options=[
                                                            {
                                                                "label": " Include all runs (not just latest)",
                                                                "value": "all_runs"
                                                            },
                                                            {
                                                                "label": " Show only failed jobs (return code != 0)",
                                                                "value": "failed_only"
                                                            },
                                                        ],
                                                        value=["failed_only"],
                                                        inline=False,
                                                    ),
                                                ],
                                                md=4,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Label("\u00a0"),  # Non-breaking space for alignment
                                                    html.Div(
                                                        dbc.Button(
                                                            [
                                                                html.I(className="fas fa-search me-2"),
                                                                "Generate Report"
                                                            ],
                                                            id="debug-generate-report-btn",
                                                            color="primary",
                                                            className="w-100",
                                                        ),
                                                    ),
                                                ],
                                                md=4,
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    html.Div(id="debug-report-status"),
                                ]
                            ),
                        ],
                        className="mb-4"
                    )
                )
            ),

            # Job Results Table
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.I(className="fas fa-list me-2"),
                                    "Job Results",
                                    html.Span(
                                        id="debug-job-count-badge",
                                        className="badge bg-secondary ms-2"
                                    ),
                                ]
                            ),
                            dbc.CardBody(
                                [
                                    html.Div(id="debug-jobs-table-container"),
                                ]
                            ),
                        ],
                        className="mb-4"
                    )
                )
            ),

            # Log File Viewer
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.I(className="fas fa-terminal me-2"),
                                    "Log File Viewer"
                                ]
                            ),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Label("Selected Job"),
                                                    html.Div(
                                                        id="debug-selected-job-info",
                                                        children="No job selected. Click on a row in the table above.",
                                                        className="text-muted"
                                                    ),
                                                ],
                                                md=12,
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    dbc.Tabs(
                                        [
                                            dbc.Tab(
                                                label="stdout",
                                                tab_id="stdout-tab",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Button(
                                                                [
                                                                    html.I(className="fas fa-copy me-2"),
                                                                    "Copy Path"
                                                                ],
                                                                id="debug-copy-stdout-path-btn",
                                                                color="secondary",
                                                                size="sm",
                                                                className="mb-2",
                                                            ),
                                                            html.Small(
                                                                id="debug-stdout-path",
                                                                className="text-muted ms-2"
                                                            ),
                                                        ]
                                                    ),
                                                    dcc.Loading(
                                                        html.Pre(
                                                            id="debug-stdout-content",
                                                            style={
                                                                "backgroundColor": "#1e1e1e",
                                                                "color": "#d4d4d4",
                                                                "padding": "1rem",
                                                                "borderRadius": "4px",
                                                                "maxHeight": "500px",
                                                                "overflow": "auto",
                                                                "whiteSpace": "pre-wrap",
                                                                "wordWrap": "break-word",
                                                                "fontFamily": "monospace",
                                                                "fontSize": "12px",
                                                            },
                                                            children="No stdout file loaded",
                                                        ),
                                                    ),
                                                ],
                                            ),
                                            dbc.Tab(
                                                label="stderr",
                                                tab_id="stderr-tab",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Button(
                                                                [
                                                                    html.I(className="fas fa-copy me-2"),
                                                                    "Copy Path"
                                                                ],
                                                                id="debug-copy-stderr-path-btn",
                                                                color="secondary",
                                                                size="sm",
                                                                className="mb-2",
                                                            ),
                                                            html.Small(
                                                                id="debug-stderr-path",
                                                                className="text-muted ms-2"
                                                            ),
                                                        ]
                                                    ),
                                                    dcc.Loading(
                                                        html.Pre(
                                                            id="debug-stderr-content",
                                                            style={
                                                                "backgroundColor": "#1e1e1e",
                                                                "color": "#f48771",
                                                                "padding": "1rem",
                                                                "borderRadius": "4px",
                                                                "maxHeight": "500px",
                                                                "overflow": "auto",
                                                                "whiteSpace": "pre-wrap",
                                                                "wordWrap": "break-word",
                                                                "fontFamily": "monospace",
                                                                "fontSize": "12px",
                                                            },
                                                            children="No stderr file loaded",
                                                        ),
                                                    ),
                                                ],
                                            ),
                                        ],
                                        id="debug-log-tabs",
                                        active_tab="stdout-tab",
                                    ),
                                ]
                            ),
                        ],
                        className="mb-4"
                    )
                )
            ),

            # Store for report data
            dcc.Store(id="debug-report-store"),
            # Store for selected job
            dcc.Store(id="debug-selected-job-store"),
        ],
        fluid=True
    )


def create_execution_plan_view(plan_data: dict):
    """Create a visual representation of the execution plan.

    Args:
        plan_data: Dictionary containing execution plan data from the CLI

    Returns:
        Dash component displaying the execution plan
    """
    workflow_name = plan_data.get("workflow_name", "Unknown")
    total_stages = plan_data.get("total_stages", 0)
    total_jobs = plan_data.get("total_jobs", 0)
    stages = plan_data.get("stages", [])

    # Header with summary
    header = dbc.Alert(
        [
            html.H5(
                [
                    html.I(className="fas fa-project-diagram me-2"),
                    f"Execution Plan: {workflow_name}"
                ],
                className="mb-2"
            ),
            html.P(
                [
                    html.Strong(f"Total Stages: "), f"{total_stages}   |   ",
                    html.Strong(f"Total Jobs: "), f"{total_jobs}"
                ],
                className="mb-0"
            )
        ],
        color="info",
        className="mb-3"
    )

    # Create stage cards
    stage_cards = []
    for stage in stages:
        stage_number = stage.get("stage_number", 0)
        trigger = stage.get("trigger", "")
        scheduler_allocations = stage.get("scheduler_allocations", [])
        jobs_becoming_ready = stage.get("jobs_becoming_ready", [])

        # Stage icon based on stage number
        stage_icon = "fa-play-circle" if stage_number == 1 else "fa-arrow-circle-right"
        stage_color = "primary" if stage_number == 1 else "secondary"

        # Build stage content
        stage_content = []

        # Scheduler allocations
        if scheduler_allocations:
            alloc_items = []
            for alloc in scheduler_allocations:
                scheduler = alloc.get("scheduler", "")
                scheduler_type = alloc.get("scheduler_type", "")
                num_allocations = alloc.get("num_allocations", 0)
                job_names = alloc.get("job_names", [])

                # Format job names
                if len(job_names) <= 5:
                    jobs_str = ", ".join(job_names)
                else:
                    jobs_str = f"{', '.join(job_names[:5])}... ({len(job_names)} total)"

                alloc_items.append(
                    html.Li([
                        html.Strong(f"{scheduler} ({scheduler_type})"), " - ",
                        html.Span(f"{num_allocations} allocation(s)", className="badge bg-info me-2"),
                        html.Br(),
                        html.Small(f"For jobs: {jobs_str}", className="text-muted")
                    ], className="mb-2")
                )

            stage_content.append(html.Div([
                html.H6([
                    html.I(className="fas fa-server me-2"),
                    "Scheduler Allocations"
                ], className="mt-2"),
                html.Ul(alloc_items, className="mb-2")
            ]))

        # Jobs becoming ready
        if jobs_becoming_ready:
            # Format job names
            if len(jobs_becoming_ready) <= 10:
                jobs_display = html.Ul([html.Li(job) for job in jobs_becoming_ready])
            else:
                jobs_display = html.Div([
                    html.Ul([html.Li(job) for job in jobs_becoming_ready[:10]]),
                    html.P(f"... and {len(jobs_becoming_ready) - 10} more", className="text-muted mb-0")
                ])

            stage_content.append(html.Div([
                html.H6([
                    html.I(className="fas fa-tasks me-2"),
                    f"Jobs Becoming Ready ({len(jobs_becoming_ready)})"
                ], className="mt-2"),
                jobs_display
            ]))

        # No content message
        if not stage_content:
            stage_content.append(
                html.P("(No actions or jobs in this stage)", className="text-muted")
            )

        # Create stage card
        stage_card = dbc.Card(
            [
                dbc.CardHeader(
                    html.H5([
                        html.I(className=f"fas {stage_icon} me-2"),
                        f"Stage {stage_number}: {trigger}"
                    ], className="mb-0"),
                    className=f"bg-{stage_color} text-white"
                ),
                dbc.CardBody(stage_content)
            ],
            className="mb-3"
        )

        stage_cards.append(stage_card)

    return html.Div([header] + stage_cards)
