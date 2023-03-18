"""Tests database export functionality."""

import shlex
import subprocess

from wms.utils.files import load_line_delimited_json


def test_export(tmp_path, completed_workflow):  # pylint: disable=unused-argument
    """Tests the CLI commands that export data from the database."""
    output_dir = tmp_path / "exports"
    cmd = f"wms export json -d {output_dir} --force"
    subprocess.run(shlex.split(cmd), check=True)
    jobs_file = output_dir / "jobs.json"
    assert jobs_file.exists()
    jobs = load_line_delimited_json(jobs_file)
    assert len(jobs) == 4
    assert (output_dir / "edges" / "blocks.json").exists()

    filename = tmp_path / "db.sqlite"
    cmd = f"wms export sqlite -F {filename} --force"
    subprocess.run(shlex.split(cmd), check=True)
    assert filename.exists()
