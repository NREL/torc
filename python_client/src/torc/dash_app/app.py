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

        # Main tabs
        dbc.Row(
            dbc.Col(
                dbc.Tabs(
                    [
                        dbc.Tab(
                            label="View Resources",
                            tab_id="view-tab",
                            label_style={"cursor": "pointer"},
                            active_label_class_name="fw-bold",
                        ),
                        dbc.Tab(
                            label="Run Workflows",
                            tab_id="run-tab",
                            label_style={"cursor": "pointer"},
                            active_label_class_name="fw-bold",
                        ),
                        # Placeholder for future tabs
                        # dbc.Tab(
                        #     label="Analytics",
                        #     tab_id="analytics-tab",
                        #     label_style={"cursor": "pointer"},
                        #     active_label_class_name="fw-bold",
                        #     disabled=True,
                        # ),
                    ],
                    id="main-tabs",
                    active_tab="view-tab",
                )
            )
        ),

        # Tab content
        dbc.Row(
            dbc.Col(
                html.Div(id="tab-content", className="mt-4")
            )
        ),

        # Interval components for auto-refresh
        dcc.Interval(
            id="refresh-interval",
            interval=5000,  # 5 seconds
            n_intervals=0,
            disabled=True,  # Start disabled, enable when viewing resources
        ),
    ],
    fluid=True,
    className="py-3"
)

# Import callbacks after layout is defined to avoid circular imports
from . import callbacks  # noqa: F401

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
