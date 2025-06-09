"""Starts a terminal-based management application."""

import rich_click as click

from torc.apps.management_console import TorcManagementConsole


@click.command()
def tui():
    """Starts a terminal-based management console."""
    app = TorcManagementConsole()
    app.run()
