"""Layout definitions for different tabs in the Torc Dash app."""

from typing import Optional
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto


def create_view_tab_layout():
    """Create the layout for the View Workflows tab."""
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
    """Create the layout for the Run Workflows tab."""
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("Manage Workflows", className="mb-3"),
                            html.P(
                                "Create, initialize, delete, and execute workflows locally or submit to HPC/Slurm",
                                className="text-muted"
                            ),
                        ]
                    )
                ]
            ),

            dbc.Row(
                [
                    # Left column: Workflow selection/upload
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Workflow Specification")),
                                    dbc.CardBody(
                                        [
                                            dbc.Tabs(
                                                [
                                                    dbc.Tab(
                                                        [
                                                            html.Div(
                                                                [
                                                                    dbc.Label("Upload Workflow Spec File", className="mt-3"),
                                                                    dcc.Upload(
                                                                        id="upload-workflow-spec",
                                                                        children=html.Div(
                                                                            [
                                                                                html.I(className="fas fa-cloud-upload-alt fa-3x mb-3"),
                                                                                html.Br(),
                                                                                "Drag and Drop or ",
                                                                                html.A("Select a File"),
                                                                            ],
                                                                            style={
                                                                                "textAlign": "center",
                                                                                "padding": "40px",
                                                                                "borderWidth": "2px",
                                                                                "borderStyle": "dashed",
                                                                                "borderRadius": "5px",
                                                                                "cursor": "pointer",
                                                                            }
                                                                        ),
                                                                        multiple=False,
                                                                    ),
                                                                    html.Div(id="upload-status", className="mt-3"),

                                                                    dbc.Label("Or enter file path", className="mt-3"),
                                                                    dbc.Input(
                                                                        id="workflow-spec-path-input",
                                                                        type="text",
                                                                        placeholder="/path/to/workflow.yaml",
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        label="New Workflow",
                                                        tab_id="new-workflow-tab",
                                                    ),
                                                    dbc.Tab(
                                                        [
                                                            html.Div(
                                                                [
                                                                    dbc.Alert(
                                                                        [
                                                                            html.I(className="fas fa-info-circle me-2"),
                                                                            "Select a workflow from the 'View Resources' tab to run it here."
                                                                        ],
                                                                        color="info",
                                                                        className="mt-3",
                                                                    ),
                                                                    html.Div(id="existing-workflow-info", className="mt-3"),
                                                                ]
                                                            )
                                                        ],
                                                        label="Selected Workflow",
                                                        tab_id="existing-workflow-tab",
                                                    ),
                                                ],
                                                id="workflow-source-tabs",
                                                active_tab="existing-workflow-tab",
                                            ),
                                        ]
                                    ),
                                ],
                                className="mb-4"
                            ),
                        ],
                        md=6,
                    ),

                    # Right column: Execution options
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Workflow Actions")),
                                    dbc.CardBody(
                                        [
                                            html.Div(id="workflow-creation-section", children=[
                                                dbc.Label("Step 1: Create Workflow", className="fw-bold mb-2"),
                                                dbc.Checklist(
                                                    id="initialize-workflow-checkbox",
                                                    options=[
                                                        {"label": " Initialize workflow after creation", "value": "initialize"},
                                                    ],
                                                    value=["initialize"],
                                                    className="mb-3",
                                                ),
                                                dbc.Button(
                                                    [html.I(className="fas fa-plus-circle me-2"), "Create Workflow"],
                                                    id="create-workflow-button",
                                                    color="primary",
                                                    size="lg",
                                                    className="w-100 mb-3",
                                                ),
                                                html.Div(id="workflow-creation-status", className="mb-3"),
                                            ]),

                                            html.Hr(),

                                            html.Div(id="workflow-management-section", children=[
                                                dbc.Label("Workflow Management", className="fw-bold mb-2"),
                                                dbc.Row([
                                                    dbc.Col(
                                                        dbc.Button(
                                                            [html.I(className="fas fa-sync me-2"), "Initialize"],
                                                            id="initialize-existing-workflow-button",
                                                            color="primary",
                                                            className="w-100",
                                                            disabled=False,
                                                        ),
                                                        width=4,
                                                    ),
                                                    dbc.Col(
                                                        dbc.Button(
                                                            [html.I(className="fas fa-redo me-2"), "Re-initialize"],
                                                            id="reinitialize-workflow-button",
                                                            color="warning",
                                                            className="w-100",
                                                            disabled=False,
                                                        ),
                                                        width=4,
                                                    ),
                                                    dbc.Col(
                                                        dbc.Button(
                                                            [html.I(className="fas fa-rotate-left me-2"), "Reset"],
                                                            id="reset-workflow-button",
                                                            color="info",
                                                            className="w-100",
                                                            disabled=False,
                                                        ),
                                                        width=4,
                                                    ),
                                                ], className="mb-3"),
                                                html.Div(id="workflow-management-status", className="mb-3"),
                                            ]),

                                            html.Hr(),

                                            html.Div(id="workflow-dag-section", children=[
                                                dbc.Label("Workflow Visualization", className="fw-bold mb-2"),
                                                dbc.Button(
                                                    [html.I(className="fas fa-project-diagram me-2"), "Show DAG"],
                                                    id="show-dag-button",
                                                    color="info",
                                                    size="lg",
                                                    className="w-100 mb-3",
                                                    disabled=False,
                                                ),
                                            ]),

                                            html.Hr(),

                                            html.Div(id="workflow-execution-section", children=[
                                                dbc.Label("Step 2: Execute Workflow", className="fw-bold mb-2"),
                                                dbc.RadioItems(
                                                    id="execution-mode-radio",
                                                    options=[
                                                        {"label": " Run Locally", "value": "run"},
                                                        {"label": " Submit to HPC/Slurm", "value": "submit"},
                                                    ],
                                                    value="run",
                                                    inline=False,
                                                    className="mb-3",
                                                ),
                                                dbc.Button(
                                                    [html.I(className="fas fa-play me-2"), "Execute Workflow"],
                                                    id="execute-workflow-button",
                                                    color="success",
                                                    size="lg",
                                                    className="w-100 mb-2",
                                                    disabled=False,
                                                ),
                                                dbc.Button(
                                                    [html.I(className="fas fa-stop me-2"), "Cancel Execution"],
                                                    id="cancel-execution-button",
                                                    color="danger",
                                                    size="lg",
                                                    className="w-100",
                                                    disabled=True,
                                                ),
                                            ]),
                                        ]
                                    ),
                                ],
                                className="mb-4"
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="mb-4"
            ),

            # Polling interval for real-time output
            dcc.Interval(id="execution-poll-interval", interval=1000, disabled=True),

            # Execution output
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.I(className="fas fa-terminal me-2"),
                                    "Execution Output"
                                ]
                            ),
                            dbc.CardBody(
                                [
                                    html.Div(
                                        id="execution-output",
                                        style={
                                            "fontFamily": "monospace",
                                            "whiteSpace": "pre-wrap",
                                            "backgroundColor": "#f8f9fa",
                                            "padding": "15px",
                                            "borderRadius": "5px",
                                            "minHeight": "200px",
                                            "maxHeight": "400px",
                                            "overflowY": "auto",
                                        }
                                    ),
                                ]
                            ),
                        ]
                    )
                )
            ),

            # Store for uploaded file content
            dcc.Store(id="uploaded-spec-store"),
        ],
        fluid=True
    )


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
                                                                    {"label": " Use selected workflow from View Workflows tab", "value": "use_selected"},
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


def create_dag_tab_layout(workflow_id: Optional[int] = None):
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
