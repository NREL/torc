"""Tests database export functionality."""

import shlex
import subprocess

from torc.utils.files import load_line_delimited_json


def test_export(tmp_path, completed_workflow):
    """Tests the CLI commands that export data from the database."""
    db, _, output_dir = completed_workflow
    output_dir = tmp_path / "exports"
    cmd = f"torc -k {db.workflow.key} -u {db.url} export json -d {output_dir} --force"
    subprocess.run(shlex.split(cmd), check=True)
    jobs_file = output_dir / "jobs.json"
    assert jobs_file.exists()
    jobs = load_line_delimited_json(jobs_file)
    assert len(jobs) == 4
    assert (output_dir / "edges" / "blocks.json").exists()

    filename = tmp_path / "db.sqlite"
    cmd = f"torc -k {db.workflow.key} -u {db.url} export sqlite -F {filename} --force"
    subprocess.run(shlex.split(cmd), check=True)
    assert filename.exists()
