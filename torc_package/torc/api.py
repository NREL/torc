"""Functions to access the Torc Database API"""

import itertools

from resource_monitor.timing.timer_stats import Timer
from torc.swagger_client import ApiClient, DefaultApi
from torc.swagger_client.configuration import Configuration

from torc.common import timer_stats_collector


def make_api(database_url) -> DefaultApi:
    """Instantiate a Swagger API object from a database URL."""
    configuration = Configuration()
    configuration.host = database_url
    return DefaultApi(ApiClient(configuration))


def iter_documents(func, *args, skip=0, **kwargs):
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
    if "limit" in kwargs and kwargs["limit"] is None:
        kwargs.pop("limit")
    limit = kwargs.get("limit")

    has_more = True
    docs_received = 0
    while has_more and (limit is None or docs_received < limit):
        result = func(*args, skip=skip, **kwargs)
        yield from result.items
        skip += result.count
        docs_received += result.count
        has_more = result.has_more


def map_job_keys_to_names(api: DefaultApi, workflow_key, filters=None) -> dict[str, str]:
    """Return a mapping of job key to name."""
    filters = filters or {}
    return {
        x.key: x.name
        for x in iter_documents(api.get_workflows_workflow_jobs, workflow_key, **filters)
    }


_DATABASE_KEYS = {"_id", "_key", "_rev", "_oldRev", "id", "key", "rev"}


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
    for item in itertools.chain(
        [data.get("config")],
        data.get("files", []),
        data.get("resource_requirements", []),
    ):
        if item is not None:
            for key in _DATABASE_KEYS:
                item.pop(key, None)
    for collection in ("jobs", "resource_requirements", "files", "schedulers"):
        if collection in data and not data[collection]:
            data.pop(collection)
    for collection in ("jobs", "resource_requirements", "files"):
        for item in data.get(collection, []):
            for field in [k for k, v in item.items() if v is None]:
                item.pop(field)
    for field in ("aws_schedulers", "local_schedulers", "slurm_schedulers"):
        schedulers = data.get("schedulers", {})
        if schedulers and field in schedulers and not schedulers[field]:
            data["schedulers"].pop(field)
    return data
