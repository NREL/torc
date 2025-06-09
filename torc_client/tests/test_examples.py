"""Test the workflow examples."""

import os
import subprocess
from pathlib import Path

import pytest


EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def test_manual_dependencies_python():
    """Test the manual-dependencies Python example."""
    subprocess.run(["python", str(EXAMPLES_DIR / "manual_job_dependencies.py")], check=True)


@pytest.mark.skipif("CI" in os.environ, reason="Skip Julia example in CI")
def test_manual_dependencies_julia():
    """Test the manual-dependencies Julia example."""
    project = Path(__file__).parents[2] / "julia" / "Torc"
    subprocess.run(
        [
            "julia",
            f"--project={project}",
            str(EXAMPLES_DIR / "manual_job_dependencies.jl"),
        ],
        check=True,
    )


def test_manual_dependencies_json5():
    """Test the manual-dependencies JSON5 example."""
    subprocess.run(
        [
            "torc",
            "workflows",
            "create-from-json-file",
            str(EXAMPLES_DIR / "manual_job_dependencies.json5"),
        ],
        check=True,
    )
