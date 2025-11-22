"""Entry point for running the Torc Dash application."""

import argparse
from .app import app


def main():
    """Run the Torc Dash application."""
    parser = argparse.ArgumentParser(
        description="Torc Workflow Manager - Web UI"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to run the server on (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8050,
        help="Port to run the server on (default: 8050)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    args = parser.parse_args()

    print(f"Starting Torc Dash application on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")

    app.run_server(
        debug=args.debug,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
