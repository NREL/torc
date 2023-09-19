"""Functions to access the Torc Database API"""

import itertools
import logging
import time

from resource_monitor.timing.timer_stats import Timer

from torc.openapi_client import ApiClient, DefaultApi
from torc.openapi_client.configuration import Configuration
from torc.openapi_client.rest import ApiException
from torc.openapi_client.models.workflow_bulk_jobs_model import WorkflowBulkJobsModel
from torc.common import timer_stats_collector
from torc.exceptions import DatabaseOffline


logger = logging.getLogger(__name__)


def make_api(database_url) -> DefaultApi:
    """Instantiate an OpenAPI client object from a database URL."""
    configuration = Configuration()
    configuration.host = database_url
    return DefaultApi(ApiClient(configuration))


def wait_for_healthy_database(api: DefaultApi, timeout_minutes=20, poll_seconds=60):
    """Ping the database until it's responding or timeout_minutes is exceeded.

    Parameters
    ----------
    api : DefaultApi
    timeout_minutes : float
        Number of minutes to wait for the database to become healthy.
    poll_seconds : float
        Number of seconds to wait in between each poll.

    Raises
    ------
    DatabaseOffline
        Raised if the timeout is exceeded.
    """
    logger.info(
        "Wait for the database to become healthy: timeout_minutes=%s, poll_seconds=%s",
        timeout_minutes,
        poll_seconds,
    )
    end = time.time() + timeout_minutes * 60
    while time.time() < end:
        try:
            send_api_command(api.get_ping)
            logger.info("The database is healthy again.")
            return
        except DatabaseOffline:
            logger.exception("Database is still offline")
        time.sleep(poll_seconds)

    raise DatabaseOffline("Timed out waiting for database to become healthy")


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
    OpenAPI [pydantic] model or dict, depending on what the API function returns
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


def send_api_command(func, *args, raise_on_error=True, **kwargs):
    """Send an API command while tracking time, if timer_stats_collector is enabled.

    Parameters
    ----------
    func : function
        API function
    args : arguments to forward to func
    raise_on_error : bool
        Raise an exception if there is an error, defaults to True.
    kwargs : keyword arguments to forward to func

    Raises
    ------
    ApiException
        Raised for errors detected by the server.
    DatabaseOffline
        Raised for all connection errors.
    """
    with Timer(timer_stats_collector, func.__name__):
        try:
            return func(*args, **kwargs)
        except ApiException:
            # This covers all errors reported by the server.
            logger.exception("Failed to send API command %s", func.__name__)
            if raise_on_error:
                raise
            logger.info("Exception is ignored.")
            return None
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # This covers all connection errors. It is likely too risky to try to catch
            # all possible errors from the underlying libraries (OS, urllib3, etc).
            logger.exception("Failed to send API command %s", func.__name__)
            if raise_on_error:
                raise DatabaseOffline(f"Received exception from API client: {exc=}") from exc
            logger.info("Exception is ignored.")
            return None


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


def list_model_fields(cls):
    """Return a list of the model's fields."""
    return list(cls.model_json_schema()["properties"].keys())


def add_jobs(
    api: DefaultApi,
    workflow_key: str,
    jobs: list[WorkflowBulkJobsModel],
) -> dict:
    """Add jobs in bulk to the workflow.
    Recommended maximum size is 10,000 jobs for ideal performance. The hard limit is tied to the
    memory size of the client handler in the torc-service (512 MiB).

    Returns
    -------
    dict
        Dictionary containing the created job keys.
    """
    api.post_workflows_workflow_bulk_jobs(workflow_key, jobs)


# def add_job(
#    api: DefaultApi,
#    workflow_key: str,
#    job: WorkflowJobsModel,
#    resource_requirements: str | None = None,
#    scheduler: str | None = None,
#    input_files: list[str] | None = None,
#    output_files: list[str] | None = None,
#    input_user_data: list[str] | None = None,
#    output_user_data: list[str] | None = None,
#    blocked_by: list[str] | None = None,
# ) -> WorkflowJobsModel:
#    """Add a job to the workflow.
#
#    Returns
#    -------
#    WorkflowJobsModel
#        The job document that is now stored in the database.
#    """
#    job = send_api_command(
#        api.post_workflows_workflow_jobs,
#        workflow_key,
#        job,
#    )
#    if resource_requirements is not None:
#        send_api_command(
#            api.post_workflows_workflow_edges_name,
#            workflow_key,
#            "requires",
#            EdgesNameModel(_from=job.id, to=resource_requirements),
#        )
#    if scheduler is not None:
#        send_api_command(
#            api.post_workflows_workflow_edges_name,
#            workflow_key,
#            "scheduled_bys",
#            EdgesNameModel(_from=job.id, to=scheduler),
#        )
#    for key in input_files or []:
#        send_api_command(
#            api.post_workflows_workflow_edges_name,
#            workflow_key,
#            "needs",
#            EdgesNameModel(_from=job.id, to=key),
#        )
#    for key in output_files or []:
#        send_api_command(
#            api.post_workflows_workflow_edges_name,
#            workflow_key,
#            "produces",
#            EdgesNameModel(_from=job.id, to=key),
#        )
#    for key in input_user_data or []:
#        send_api_command(
#            api.post_workflows_workflow_edges_name,
#            workflow_key,
#            "consumes",
#            EdgesNameModel(_from=job.id, to=key),
#        )
#    for key in output_user_data or []:
#        send_api_command(
#            api.post_workflows_workflow_edges_name,
#            workflow_key,
#            "stores",
#            EdgesNameModel(_from=job.id, to=key),
#        )
#    for key in blocked_by or []:
#        send_api_command(
#            api.post_workflows_workflow_edges_name,
#            workflow_key,
#            "blocks",
#            EdgesNameModel(_from=key, to=job.id),
#        )
#    return job
