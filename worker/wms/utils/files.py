"""File utility functions"""

import hashlib
import json
import logging
import os
import stat
from pathlib import Path

import json5


logger = logging.getLogger(__name__)


def create_script(filename, text, executable=True):
    """Creates a script with the given text.

    Parameters
    ----------
    text : str
        body of script
    filename : str
        file to create
    executable : bool
        if True, set as executable
    """
    # Permissions issues occur when trying to overwrite and then make
    # executable another user's file.
    path = Path(filename)
    if path.exists():
        path.unlink()

    path.write_text(text)
    if executable:
        curstat = path.stat()
        path.chmod(curstat.st_mode | stat.S_IEXEC)


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


def dump_data(data, filename, **kwargs):
    """Dump data to the filename.
    Supports JSON, JSON5, or custom via kwargs.

    Parameters
    ----------
    data : dict
        data to dump
    filename : str
        file to create or overwrite
    """
    mod = _get_module_from_extension(filename, **kwargs)
    with open(filename, "w") as f_out:
        mod.dump(data, f_out, **kwargs)

    logger.debug("Dumped data to %s", filename)


def load_data(filename, **kwargs):
    """Load data from the file.
    Supports JSON, JSON5, or custom via kwargs.

    Parameters
    ----------
    filename : str

    Returns
    -------
    dict
    """
    mod = _get_module_from_extension(filename, **kwargs)
    with open(filename) as f_in:
        try:
            data = mod.load(f_in)
        except Exception:
            logger.exception("Failed to load data from %s", filename)
            raise

    logger.debug("Loaded data from %s", filename)
    return data


def _get_module_from_extension(filename, **kwargs):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".json":
        mod = json
    elif ext == ".json5":
        mod = json5
    elif "mod" in kwargs:
        mod = kwargs["mod"]
    else:
        raise Exception(f"Unsupported extension {filename}")

    return mod


def dump_line_delimited_json(data, filename):
    """Dump a list of objects to the file as line-delimited JSON.

    Parameters
    ----------
    data : list
    filename : str
    """
    with open(filename, "w") as f_out:
        for obj in data:
            f_out.write(json.dumps(obj))
            f_out.write("\n")

    logger.debug("Dumped data to %s", filename)


def load_line_delimited_json(filename):
    """Load data from the file that is stored as line-delimited JSON.

    Parameters
    ----------
    filename : str

    Returns
    -------
    dict
    """
    objects = []
    with open(filename) as f_in:
        for i, line in enumerate(f_in):
            text = line.strip()
            if not text:
                continue
            try:
                objects.append(json.loads(text))
            except Exception:
                logger.exception("Failed to decode line number %s in %s", i, filename)
                raise

    logger.debug("Loaded data from %s", filename)
    return objects
