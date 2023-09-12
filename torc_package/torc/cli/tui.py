"""Starts a terminal-based management application."""

import click

from torc.apps.tui import TorcManagementConsole


@click.command()
def tui():
    """Starts a terminal-based management console."""
    app = TorcManagementConsole()
    app.run()
