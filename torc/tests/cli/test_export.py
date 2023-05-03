"""Tests database export functionality."""

from click.testing import CliRunner

from torc.cli.torc import cli


def test_export(tmp_path, completed_workflow):
    """Tests the CLI commands that export data from the database."""
    db = completed_workflow[0]
    filename = tmp_path / "db.sqlite"
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli, ["-u", db.url, "-k", db.workflow.key, "export", "sqlite", "-F", filename, "--force"]
    )
    assert result.exit_code == 0
    assert filename.exists()
