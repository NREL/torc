"""Updates the version in all torc files."""

import fileinput
import sys
from pathlib import Path


FILES = [
    {
        "filename": "torc_package/torc/__init__.py",
        "count": 1,
    },
    {
        "filename": "db_service/openapi.yaml",
        "count": 1,
    },
    {
        "filename": "db_service/src/api/workflows.js",
        "count": 1,
    },
    {
        "filename": "db_service/config.json",
        "count": 1,
    },
    {
        "filename": "docs/how_tos/getting_started/installation.rst",
        "count": 2,
    },
]


def main():
    """Entry point"""
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} NEW_VERSION")
        sys.exit(1)

    new_version = sys.argv[1]
    update_version(FILES, new_version)


def update_version(files, new_version):
    """Update the torc version in all files."""
    cur_version = _get_cur_version()
    _check_existing_counts(files, cur_version)
    _update_version(files, cur_version, new_version)


def _get_cur_version():
    lines = (
        Path("torc_package/torc/__init__.py").read_text(encoding="utf-8").splitlines()
    )
    for line in lines:
        if line.startswith("__version__"):
            return line.split("=")[1].strip().replace('"', "").replace("'", "")
    raise ValueError("Did not find the current version")


def _check_existing_counts(files, cur_version):
    for item in files:
        with open(item["filename"], encoding="utf-8") as f:
            count = len(list(filter(lambda x: cur_version in x, f)))
            if count != item["count"]:
                raise ValueError(
                    f"Found unexpected count of instances of {cur_version=}: {item}"
                )


def _update_version(files, cur_version, new_version):
    for item in files:
        filename = item["filename"]
        with fileinput.input([filename], inplace=True) as f:
            for line in f:
                if cur_version in line:
                    line = line.replace(cur_version, new_version)
                print(line, end="")
        print(f"Updated version in {filename} to {new_version}")


if __name__ == "__main__":
    main()
