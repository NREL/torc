"""Functions to access the Torc Database API"""

import itertools

from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration

from torc.utils.timing import timer_stats_collector, Timer


DEFAULT_BATCH_SIZE = 1000


def make_api(database_url) -> DefaultApi:
    """Instantiate a Swagger API object from a database URL."""
    configuration = Configuration()
    configuration.host = database_url
    return DefaultApi(ApiClient(configuration))


def iter_documents(func, *args, skip=0, limit=DEFAULT_BATCH_SIZE, **kwargs):
    """Return a generator of documents where the API service employs batching.

    Parameters
    ----------
    func : function
        API function
    batch_size : int
        Max number of documents to fetch in each batch.

    Yields
    ------
    Swagger model or dict, depending on what the API function returns
    """
    has_more = True
    while has_more:
        result = func(*args, skip=skip, limit=limit, **kwargs)
        yield from result.items
        skip += result.count
        has_more = result.has_more


_DATABASE_KEYS = {"_id", "_key", "_rev", "id", "key", "rev"}


def remove_db_keys(data: dict):
    """Remove internal database keys from data."""
    return {x: data[x] for x in set(data) - _DATABASE_KEYS}


def send_api_command(func, *args, **kwargs):
    """Send an API command while tracking time, if timer_stats_collector is enabled.

    Parameters
    ----------
    func : function
        API function
    args : arguments to forward to func
    kwargs : keyword arguments to forward to func
    """
    with Timer(timer_stats_collector, func.__name__):
        return func(*args, **kwargs)


def sanitize_workflow(data: dict):
    """Sanitize a WorkflowSpecificationsModel dictionary in place so that it can be loaded into
    the database.
    """
    for item in itertools.chain([data["config"]], data["files"], data["resource_requirements"]):
        for key in _DATABASE_KEYS:
            item.pop(key, None)
    if "jobs" in data and not data["jobs"]:
        data.pop("jobs")
    if "resource_requirements" in data and not data["resource_requirements"]:
        data.pop("resource_requirements")
    if "files" in data and not data["files"]:
        data.pop("files")
    for file in data.get("files", []):
        for field in ("file_hash", "st_mtime"):
            if field in file and file[field] is None:
                file.pop(field)
    for field in ("aws_schedulers", "local_schedulers", "slurm_schedulers"):
        if field in data["schedulers"] and not data["schedulers"][field]:
            data["schedulers"].pop(field)
    return data
