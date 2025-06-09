"""Test script that verifies correct CPU affinity."""

import multiprocessing
import os
import sys

from torc.openapi_client.models.user_data_model import (
    UserDataModel,
)

from torc.api import make_api
from torc.config import torc_settings

print(f"running {sys.argv}")

if torc_settings.database_url is None:
    print(
        "This test requires that the database_url be set in torc config file",
        file=sys.stderr,
    )
    sys.exit(1)

api = make_api(torc_settings.database_url)
workflow_key = os.environ["TORC_WORKFLOW_KEY"]
job_key = os.environ["TORC_JOB_KEY"]

affinity = os.sched_getaffinity(os.getpid())  # type: ignore
result = UserDataModel(
    name="result",
    data={"affinity": list(affinity), "num_cpus": multiprocessing.cpu_count()},
)
api.add_user_data(workflow_key, result)
