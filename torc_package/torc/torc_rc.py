"""Manages the torc runtime configuration file"""

import logging
import sys
from pathlib import Path

import json5

from torc.common import TorcBaseModel
from torc.utils.files import dump_data

RC_FILENAME = ".torc.json5"

logger = logging.getLogger(__name__)


class TorcRuntimeConfig(TorcBaseModel):
    """Defines the runtime config that can be stored in users' home directories."""

    database_url: str | None = None
    workflow_key: str | None = None
    output_format: str = "text"
    filter_workflows_by_user: bool = False
    console_level: str = "info"
    file_level: str = "info"
    timings: bool = False

    @classmethod
    def load(cls):
        """Load the torc runtime config if it exists or one with default values."""
        rc_file = cls.path()
        if rc_file.exists():
            data = json5.loads(rc_file.read_text())
            return cls(**data)
        return cls()

    def dump(self):
        """Dump the config to the user's home directory."""
        path = self.path()
        dump_data(self.dict(), path, indent=2)
        print(f"Wrote torc config to {path}", file=sys.stderr)

    @staticmethod
    def path() -> Path:
        """Return the path to the config file."""
        return Path.home() / RC_FILENAME
