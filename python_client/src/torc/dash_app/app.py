"""Main Dash application for Torc workflow management."""

import os
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# Initialize the Dash app with Bootstrap theme
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title="Torc Workflow Manager",
)

# Default configuration
DEFAULT_API_URL = os.environ.get("TORC_API_URL", "http://localhost:8080/torc-service/v1")
DEFAULT_USERNAME = os.environ.get("USER", os.environ.get("USERNAME", ""))

# Main application layout
app.layout = dbc.Container(
    [
        # Store components for configuration
        dcc.Store(id="api-config-store", data={
            "url": DEFAULT_API_URL,
            "username": DEFAULT_USERNAME,
        }),
        dcc.Store(id="workflows-store"),
        dcc.Store(id="selected-workflow-store"),
        dcc.Store(id="dag-workflow-id-store"),
        dcc.Store(id="delete-workflow-id-store"),

        # Confirmation modal for workflow deletion
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Confirm Deletion")),
                dbc.ModalBody(id="delete-workflow-modal-body"),
                dbc.ModalFooter(
                    [
                        dbc.Button("Cancel", id="delete-workflow-cancel-btn", className="me-2", color="secondary"),
                        dbc.Button("Delete", id="delete-workflow-confirm-btn", color="danger"),
                    ]
                ),
            ],
            id="delete-workflow-modal",
            is_open=False,
        ),

        # Header
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H1(
                            [
                                html.I(className="fas fa-project-diagram me-3"),
                                "Torc Workflow Manager"
                            ],
                            className="text-primary mb-0"
                        ),
                        html.P(
                            "Distributed workflow orchestration and monitoring",
                            className="text-muted"
                        ),
                    ],
                    className="my-4"
                )
            )
        ),

        # Configuration panel (collapsible)
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            dbc.Button(
                                [
                                    html.I(className="fas fa-cog me-2"),
                                    "Configuration"
                                ],
                                id="config-collapse-button",
                                className="w-100 text-start",
                                color="light",
                                n_clicks=0,
                            )
                        ),
                        dbc.Collapse(
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Label("API URL", html_for="api-url-input"),
                                                    dbc.Input(
                                                        id="api-url-input",
                                                        type="text",
                                                        value=DEFAULT_API_URL,
                                                        placeholder="http://localhost:8080/torc-service/v1",
                                                    ),
                                                    dbc.FormText("The Torc server API endpoint"),
                                                ],
                                                md=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Label("Username", html_for="username-input"),
                                                    dbc.Input(
                                                        id="username-input",
                                                        type="text",
                                                        value=DEFAULT_USERNAME,
                                                        placeholder="Enter your username",
                                                    ),
                                                    dbc.FormText("Workflow owner username"),
                                                ],
                                                md=6,
                                            ),
                                        ],
                                        className="mb-3"
                                    ),
                                    # Password placeholder - commented out for now
                                    # dbc.Row(
                                    #     dbc.Col(
                                    #         [
                                    #             dbc.Label("Password", html_for="password-input"),
                                    #             dbc.Input(
                                    #                 id="password-input",
                                    #                 type="password",
                                    #                 placeholder="Enter password (optional)",
                                    #             ),
                                    #             dbc.FormText("Optional authentication password"),
                                    #         ],
                                    #         md=6,
                                    #     ),
                                    #     className="mb-3"
                                    # ),
                                    dbc.Row(
                                        dbc.Col(
                                            dbc.Button(
                                                [
                                                    html.I(className="fas fa-save me-2"),
                                                    "Save Configuration"
                                                ],
                                                id="save-config-button",
                                                color="primary",
                                                className="mt-2",
                                            ),
                                        )
                                    ),
                                    dbc.Row(
                                        dbc.Col(
                                            html.Div(id="config-status-message", className="mt-3")
                                        )
                                    ),
                                ]
                            ),
                            id="config-collapse",
                            is_open=False,
                        ),
                    ],
                    className="mb-4"
                )
            )
        ),

        # Workflow Selection panel (collapsible)
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            dbc.Button(
                                [
                                    html.I(className="fas fa-list me-2"),
                                    "Workflow Selection",
                                    html.Span(id="selected-workflow-badge", className="badge bg-primary ms-2"),
                                ],
                                id="workflow-selection-collapse-button",
                                className="w-100 text-start",
                                color="light",
                                n_clicks=0,
                            )
                        ),
                        dbc.Collapse(
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Button(
                                                        [html.I(className="fas fa-sync me-2"), "Refresh Workflows"],
                                                        id="global-refresh-workflows-button",
                                                        color="primary",
                                                        size="sm",
                                                        className="me-2",
                                                    ),
                                                    dbc.Checklist(
                                                        id="global-auto-refresh-toggle",
                                                        options=[
                                                            {"label": " Auto-refresh (every 30s)", "value": "auto"},
                                                        ],
                                                        value=[],
                                                        inline=True,
                                                        switch=True,
                                                    ),
                                                ],
                                                className="mb-3",
                                            ),
                                        ]
                                    ),
                                    dbc.Row(
                                        dbc.Col(
                                            html.Div(id="global-workflows-table-container"),
                                        )
                                    ),
                                ]
                            ),
                            id="workflow-selection-collapse",
                            is_open=True,
                        ),
                    ],
                    className="mb-4"
                )
            )
        ),

        # Hidden interval component for auto-refresh
        dcc.Interval(id="global-refresh-interval", interval=30000, disabled=True),

        # Main tabs
        dbc.Row(
            dbc.Col(
                dbc.Tabs(
                    [
                        dbc.Tab(
                            label="View Workflows",
                            tab_id="view-tab",
                            label_style={"cursor": "pointer"},
                            active_label_class_name="fw-bold",
                        ),
                        dbc.Tab(
                            label="Manage Workflows",
                            tab_id="run-tab",
                            label_style={"cursor": "pointer"},
                            active_label_class_name="fw-bold",
                        ),
                        dbc.Tab(
                            label="DAG Visualization",
                            tab_id="dag-tab",
                            label_style={"cursor": "pointer"},
                            active_label_class_name="fw-bold",
                        ),
                        dbc.Tab(
                            label="Monitor Events",
                            tab_id="monitor-tab",
                            label_style={"cursor": "pointer"},
                            active_label_class_name="fw-bold",
                        ),
                        dbc.Tab(
                            label="Resource Plots",
                            tab_id="plots-tab",
                            label_style={"cursor": "pointer"},
                            active_label_class_name="fw-bold",
                        ),
                    ],
                    id="main-tabs",
                    active_tab="view-tab",
                )
            )
        ),

        # Tab content - pre-render all tabs to preserve state when switching
        dbc.Row(
            dbc.Col(
                [
                    html.Div(id="view-tab-content", style={"display": "block", "marginTop": "1rem"}),
                    html.Div(id="run-tab-content", style={"display": "none"}),
                    html.Div(id="dag-tab-content", style={"display": "none"}),
                    html.Div(id="monitor-tab-content", style={"display": "none"}),
                    html.Div(id="plots-tab-content", style={"display": "none"}),
                ]
            )
        ),
    ],
    fluid=True,
    className="py-3"
)

# Import callbacks after layout is defined to avoid circular imports
from . import callbacks  # noqa: F401

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
