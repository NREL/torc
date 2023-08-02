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
    """Defines the runtime config that can be stored in users' home or working directories."""

    database_url: str | None = None
    workflow_key: str | None = None
    output_format: str = "text"
    filter_workflows_by_user: bool = False
    console_level: str = "info"
    file_level: str = "info"
    timings: bool = False

    @classmethod
    def load(cls, path=None):
        """Load the torc runtime config if it exists or one with default values."""
        if path is not None and not path.exists():
            raise FileNotFoundError(f"torc rc file {path} does not exist")

        rc_file = path or cls.path()
        if rc_file.exists():
            data = json5.loads(rc_file.read_text())
            return cls(**data)
        return cls()

    def dump(self, path=None):
        """Dump the config to path.

        Parameters
        ----------
        path : Path | None
            If not passed, dump to the user's home directory.

        """
        filename = path or Path.home() / RC_FILENAME
        dump_data(self.model_dump(), filename, indent=2)
        print(f"Wrote torc config to {filename.absolute()}", file=sys.stderr)

    @staticmethod
    def path() -> Path:
        """Return the path to the highest-priority config file."""
        local_file = Path(".") / RC_FILENAME
        if local_file.exists():
            logger.debug("Use config file in current directory.")
            return local_file
        return Path.home() / RC_FILENAME
