from wms.utils.timing import timer_stats_collector, Timer


def send_api_command(func, *args, **kwargs):
    with Timer(timer_stats_collector, func.__name__):
        return func(*args, **kwargs)
