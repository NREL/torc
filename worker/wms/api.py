"""Helper functions to access the API"""

from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration

from wms.utils.timing import timer_stats_collector, Timer


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
