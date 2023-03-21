"""Helper functions to access the API"""

import itertools

from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration

from wms.utils.timing import timer_stats_collector, Timer


def iter_documents(func, *args, batch_size=1000, **kwargs):
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
    skip = 0
    has_more = True
    while has_more:
        result = func(*args, skip=skip, limit=batch_size, **kwargs)
        for item in result.items:
            yield item
        skip += result.count
        has_more = result.has_more


def make_api(database_url) -> DefaultApi:
    """Instantiate a Swagger API object from a database URL."""
    configuration = Configuration()
    configuration.host = database_url
    return DefaultApi(ApiClient(configuration))


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
    """Sanitize a WorkflowModel dictionary in place so that it can be loaded into the database."""
    for item in itertools.chain([data["config"]], data["files"], data["resource_requirements"]):
        for key in _DATABASE_KEYS:
            item.pop(key, None)
    if "files" in data and not data["files"]:
        data.pop("files")
    for file in data.get("files", []):
        for field in ("file_hash", "st_mtime"):
            if file[field] is None:
                file.pop(field)
    for field in ("aws_schedulers", "local_schedulers", "slurm_schedulers"):
        if field in data["schedulers"] and not data["schedulers"][field]:
            data["schedulers"].pop(field)
    return data
