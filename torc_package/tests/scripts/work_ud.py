#!/usr/bin/env python

"""Test script to simulate doing work with input/output data stored in user_data collection."""

import os
import sys

from torc.api import make_api
from torc.torc_rc import TorcRuntimeConfig

config = TorcRuntimeConfig.load()
if config.database_url is None:
    print(f"This test requires that the database_url be set in {config.path()}", file=sys.stderr)
    sys.exit(1)

api = make_api(config.database_url)

workflow_key = os.environ["TORC_WORKFLOW_KEY"]
job_key = os.environ["TORC_JOB_KEY"]
result = api.get_jobs_key_user_data_consumes(workflow_key, job_key)
assert len(result.items) == 1, result
input_data = result.items[0]

result = api.get_jobs_key_user_data_stores(workflow_key, job_key)
assert len(result.items) == 1, result
output_data = result.items[0]
output_data.data = {"val": input_data.data["val"] + 1}
api.put_user_data_key(workflow_key, output_data.key, output_data)
