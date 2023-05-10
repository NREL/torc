"""Test script to use an ephemeral resource."""

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
    result = api.get_workflows_workflow_jobs_key_user_data_consumes(workflow_key, job_key)
    resource_ud = None
    for item in result.items:
        if item.name == "resource":
            resource_ud = item
            break

    assert resource_ud is not None
    assert "url" in resource_ud.data


if __name__ == "__main__":
    main()
