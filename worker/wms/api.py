"""Helper functions to access the API"""

from wms.utils.timing import timer_stats_collector, Timer


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
