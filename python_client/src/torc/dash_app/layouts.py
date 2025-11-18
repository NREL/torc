"""Layout definitions for different tabs in the Torc Dash app."""

from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


def create_view_tab_layout():
    """Create the layout for the View Resources tab."""
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("View Resources", className="mb-3"),
                            html.P(
                                "Browse and monitor workflows, jobs, results, events, files, and user data",
                                className="text-muted"
                            ),
                        ]
                    )
                ]
            ),

            # Resource type selector
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Resource Type", html_for="resource-type-select"),
                            dcc.Dropdown(
                                id="resource-type-select",
                                options=[
                                    {"label": "Workflows", "value": "workflows"},
                                    {"label": "Jobs", "value": "jobs"},
                                    {"label": "Results", "value": "results"},
                                    {"label": "Events", "value": "events"},
                                    {"label": "Files", "value": "files"},
                                    {"label": "User Data", "value": "user_data"},
                                    {"label": "Compute Nodes", "value": "compute_nodes"},
                                    {"label": "Resource Requirements", "value": "resource_requirements"},
                                ],
                                value="workflows",
                                clearable=False,
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Select Workflow (for filtered resources)", html_for="workflow-filter-select"),
                            dcc.Dropdown(
                                id="workflow-filter-select",
                                placeholder="Select a workflow to filter resources...",
                                clearable=True,
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Actions", html_for="refresh-button"),
                            html.Div(
                                [
                                    dbc.Button(
                                        [html.I(className="fas fa-sync-alt me-2"), "Refresh"],
                                        id="refresh-button",
                                        color="primary",
                                        className="me-2",
                                    ),
                                    dbc.Checklist(
                                        options=[{"label": " Auto-refresh", "value": "auto"}],
                                        value=[],
                                        id="auto-refresh-toggle",
                                        inline=True,
                                        switch=True,
                                    ),
                                ]
                            ),
                        ],
                        md=2,
                    ),
                ],
                className="mb-4"
            ),

            # Loading indicator
            dbc.Row(
                dbc.Col(
                    dcc.Loading(
                        id="loading-resources",
                        type="default",
                        children=html.Div(id="resource-table-container"),
                    )
                )
            ),

            # Status message
            dbc.Row(
                dbc.Col(
                    html.Div(id="view-status-message", className="mt-3")
                )
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
                            html.H3("Run Workflows", className="mb-3"),
                            html.P(
                                "Create and execute workflows locally or submit to HPC/Slurm",
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
                                                active_tab="new-workflow-tab",
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
                                    dbc.CardHeader(html.H5("Execution Options")),
                                    dbc.CardBody(
                                        [
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

                                            html.Hr(),

                                            dbc.Label("Additional Options", className="fw-bold mb-2"),

                                            dbc.Checklist(
                                                id="create-workflow-checkbox",
                                                options=[
                                                    {"label": " Create workflow first (two-step process)", "value": "create"},
                                                ],
                                                value=[],
                                                className="mb-3",
                                            ),

                                            html.Div(id="execution-options-info", className="mb-3"),
                                        ]
                                    ),
                                ],
                                className="mb-4"
                            ),

                            # Action buttons
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Actions")),
                                    dbc.CardBody(
                                        [
                                            dbc.Button(
                                                [html.I(className="fas fa-play me-2"), "Execute Workflow"],
                                                id="execute-workflow-button",
                                                color="success",
                                                size="lg",
                                                className="w-100 mb-2",
                                            ),
                                            dbc.Button(
                                                [html.I(className="fas fa-stop me-2"), "Cancel Execution"],
                                                id="cancel-execution-button",
                                                color="danger",
                                                size="lg",
                                                className="w-100",
                                                disabled=True,
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="mb-4"
            ),

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
                                    dcc.Loading(
                                        id="loading-execution",
                                        type="default",
                                        children=html.Div(
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


def create_data_table(data, columns, table_id, enable_selection=False):
    """Create a Dash DataTable with common styling and features.

    Args:
        data: List of dictionaries containing table data
        columns: List of column definitions
        table_id: Unique ID for the table
        enable_selection: Enable row selection (default: False)

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

    return dash_table.DataTable(
        id=table_id,
        data=data,
        columns=columns,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=20,
        row_selectable="single" if enable_selection else False,
        selected_rows=[],
        style_table={
            "overflowX": "auto",
        },
        style_cell={
            "textAlign": "left",
            "padding": "10px",
            "minWidth": "100px",
            "maxWidth": "300px",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_header={
            "backgroundColor": "#f8f9fa",
            "fontWeight": "bold",
            "border": "1px solid #dee2e6",
        },
        style_data={
            "border": "1px solid #dee2e6",
        },
        style_data_conditional=style_data_conditional,
    )
