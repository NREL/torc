"""Contains logging configuration data."""

import logging
import logging.config


def setup_logging(
    name,
    filename=None,
    mode="w",
    console_level=logging.INFO,
    file_level=logging.INFO,
    packages=None,
):
    """Configures logging to file and console.

    Parameters
    ----------
    name : str
        logger name
    filename : str | None
        log filename
    mode : str
        Mode for how to open filename, if applicable.
    console_level : int, optional
        console log level. defaults to logging.INFO
    file_level : int, optional
        file log level. defaults to logging.INFO
    packages : list, optional
        enable logging for these package names. Always adds wms.
    """
    handler_names = ["console"]
    handler_configs = {
        "console": {
            "level": console_level,
            "formatter": "short",
            "class": "logging.StreamHandler",
        }
    }
    if filename is not None:
        handler_names.append("file")
        handler_configs["file"] = {
            "class": "logging.FileHandler",
            "level": file_level,
            "filename": filename,
            "mode": mode,
            "formatter": "detailed",
        }

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "basic": {"format": "%(message)s"},
            "short": {
                "format": "%(asctime)s - %(levelname)s [%(name)s "
                "%(filename)s:%(lineno)d] : %(message)s",
            },
            "detailed": {
                "format": "%(asctime)s - %(levelname)s [%(name)s "
                "%(filename)s:%(lineno)d] : %(message)s",
            },
        },
        "handlers": handler_configs,
        "loggers": {
            name: {"handlers": handler_names, "level": "DEBUG", "propagate": False},
        },
    }

    packages = set(packages or [])
    packages.add("wms")
    for package in packages:
        log_config["loggers"][package] = {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        }
        if filename is not None:
            log_config["loggers"][package]["handlers"].append("file")

    logging.config.dictConfig(log_config)
    logger = logging.getLogger(name)

    return logger
