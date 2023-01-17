"""File utility functions"""

import hashlib
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def compute_file_hash(filename):
    """Compute a hash of the contents of a file.

    Parameters
    ----------
    filename : str

    Returns
    -------
    str
        hash in the form of a hex number converted to a string

    """
    return compute_hash(Path(filename).read_bytes())


def compute_hash(text: str):
    hash_obj = hashlib.sha256()
    hash_obj.update(text)
    return hash_obj.hexdigest()
