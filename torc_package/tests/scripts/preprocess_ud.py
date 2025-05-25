#!/usr/bin/env python

"""Test script to run a preprocess command."""

import os
import sys

from torc.api import make_api
from torc.config import torc_settings

if torc_settings.database_url is None:
    print(
        "This test requires that the database_url be set in the torc config file", file=sys.stderr
    )
    sys.exit(1)

api = make_api(torc_settings.database_url)

workflow_key = os.environ["TORC_WORKFLOW_KEY"]
job_key = os.environ["TORC_JOB_KEY"]
result = api.list_job_user_data_consumes(workflow_key, job_key)
assert result is not None
assert result.items is not None
assert len(result.items) == 1, result
inputs = result.items[0]
assert inputs is not None
assert inputs.data is not None

result2 = api.list_job_user_data_stores(workflow_key, job_key)
assert result2.items is not None
assert len(result2.items) == 2, result2
for item in result2.items:
    assert item is not None
    assert item.key is not None
    if item.name == "data1":
        item.data = {"val": inputs.data["val"] + 1}
    elif item.name == "data2":
        item.data = {"val": inputs.data["val"] + 2}
    api.modify_user_data(workflow_key, item.key, item)
