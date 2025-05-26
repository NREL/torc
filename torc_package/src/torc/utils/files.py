"""File utility functions"""

import hashlib
import json
import os
import stat
from pathlib import Path
from types import ModuleType
from typing import Any

import json5
from loguru import logger


def create_script(filename: str | Path, text: str, executable: bool = True) -> None:
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

    path.write_text(text, encoding="utf-8")
    if executable:
        curstat = path.stat()
        path.chmod(curstat.st_mode | stat.S_IEXEC)


def compute_file_hash(filename: str) -> str:
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


def compute_hash(text: bytes) -> str:
    """Compute a hash of the input string."""
    hash_obj = hashlib.sha256()
    hash_obj.update(text)
    return hash_obj.hexdigest()


def dump_json_file(data: dict[str, Any], filename: str | Path, **kwargs) -> None:
    """Dump data to the JSON or JSON5 filename."""
    mod = _get_module_from_extension(filename, **kwargs)
    with open(filename, "w", encoding="utf-8") as f_out:
        mod.dump(data, f_out, **kwargs)

    logger.trace("Dumped data to {}", filename)


def load_json_file(filename: str | Path, **kwargs) -> Any:
    """Load data from the JSON or JSON5 file."""
    mod = _get_module_from_extension(filename, **kwargs)
    with open(filename, encoding="utf-8") as f_in:
        try:
            data = mod.load(f_in)
        except Exception:
            logger.exception("Failed to load data from {}", filename)
            raise

    logger.trace("Loaded data from {}", filename)
    return data


def _get_module_from_extension(filename, **kwargs) -> ModuleType:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".json":
        mod = json
    elif ext == ".json5":
        mod = json5  # type: ignore
    elif "mod" in kwargs:
        mod = kwargs["mod"]  # type: ignore
    else:
        msg = f"Unsupported extension {filename}"
        raise Exception(msg)

    return mod


def dump_line_delimited_json(data: list[Any], filename: str | Path, mode: str = "w") -> None:
    """Dump a list of objects to the file as line-delimited JSON."""
    with open(filename, mode, encoding="utf-8") as f_out:
        for obj in data:
            f_out.write(json.dumps(obj))
            f_out.write("\n")

    logger.trace("Dumped data to {}", filename)


def load_line_delimited_json(filename: str | Path) -> list[Any]:
    """Load data from the file that is stored as line-delimited JSON."""
    objects = []
    with open(filename, encoding="utf-8") as f_in:
        for i, line in enumerate(f_in):
            text = line.strip()
            if not text:
                continue
            try:
                objects.append(json.loads(text))
            except Exception:
                logger.exception("Failed to decode line number {} in {}", i, filename)
                raise

    logger.trace("Loaded data from {}", filename)
    return objects
