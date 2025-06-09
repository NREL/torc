#!/usr/bin/env python

"""Test script to run post-processing."""

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
assert len(result.items) == 2, result
total = 0
for item in result.items:
    assert item.data is not None
    total += item.data["val"]

result2 = api.list_job_user_data_stores(workflow_key, job_key)
assert result2.items is not None
assert len(result2.items) == 1, result2
output_data = result2.items[0]
output_data.data = {"result": total}
assert output_data.key is not None
api.modify_user_data(workflow_key, output_data.key, output_data)
