"""Test script to create an ephemeral resource."""

import os
import sys

from torc.api import make_api
from torc.torc_rc import TorcRuntimeConfig


def main():
    """Entry point"""
    workflow_key = os.environ["TORC_WORKFLOW_KEY"]
    job_key = os.environ["TORC_JOB_KEY"]
    config = TorcRuntimeConfig.load()
    if not config.database_url:
        print(f"The database_url must be set in {config.path()}.", file=sys.stderr)
        sys.exit(1)

    api = make_api(config.database_url)
    result = api.list_job_user_data_stores(workflow_key, job_key)
    resource_ud = None
    for item in result.items:
        if item.name == "resource":
            resource_ud = item
            break

    assert resource_ud is not None
    resource_ud.data = {"url": "http://localhost:8000"}
    res = api.modify_user_data(workflow_key, resource_ud.key, resource_ud)
    print(f"Added {res=} to the database")


if __name__ == "__main__":
    main()
