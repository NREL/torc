"""CLI commands to manage the torc runtime configuration"""

import toml
from pathlib import Path

import rich_click as click

from torc.config import DEFAULT_SETTINGS_FILENAME


@click.group()
def config():
    """Config commands"""


@click.command()
@click.option(
    "-F",
    "--output-format",
    default="text",
    type=click.Choice(["text", "json"]),
    show_default=True,
    help="Output format for get/list commands. Not all commands support all formats.",
)
@click.option(
    "-d",
    "--directory",
    default=Path.home(),
    show_default=True,
    help="Directory in which to store the config file.",
    callback=lambda *x: Path(x[2]),
)
@click.option(
    "-f",
    "--filter-workflows-by-user/--no-filter-workflows-by-user",
    is_flag=True,
    default=True,
    show_default=True,
    help="Whether to filter workflows by the current user",
)
@click.option(
    "-k",
    "--workflow-key",
    type=str,
    default=None,
    help="Workflow key. " "User will be prompted if it is missing unless --no-prompts is set.",
)
@click.option(
    "--timings/--no-timings",
    default=False,
    is_flag=True,
    show_default=True,
    help="Enable tracking of function timings.",
)
@click.option(
    "-u",
    "--database-url",
    type=str,
    default=None,
    help="Database URL. Note the database name in this example: "
    "http://localhost:8529/_db/database_name/torc-service",
)
@click.option(
    "--console-level",
    default="info",
    show_default=True,
    help="Console log level.",
)
@click.option(
    "--file-level",
    default="debug",
    show_default=True,
    help="File log level. Set to 'trace' for increased verbosity.",
)
def create(
    output_format,
    directory: Path,
    filter_workflows_by_user,
    workflow_key,
    timings,
    database_url,
    console_level,
    file_level,
):
    """Create a local torc runtime configuration file."""
    settings = {
        "output_format": output_format,
        "filter_workflows_by_user": filter_workflows_by_user,
        "workflow_key": workflow_key,
        "timings": timings,
        "database_url": database_url,
        "console_level": console_level,
        "file_level": file_level,
    }
    filename = directory / DEFAULT_SETTINGS_FILENAME
    with open(filename, "w") as f:
        toml.dump(settings, f)
        print(f"Wrote torc config to {filename}")


config.add_command(create)
