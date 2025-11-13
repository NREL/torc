"""Test script to use an ephemeral resource."""

import os
import sys

from torc.api import make_api
from torc.openapi_client.models.user_data_model import UserDataModel
from torc.config import torc_settings


def main():
    """Entry point"""
    workflow_key = os.environ["TORC_WORKFLOW_KEY"]
    job_key = os.environ["TORC_JOB_KEY"]
    if not torc_settings.database_url:
        print("The database_url must be set in the torc config file.", file=sys.stderr)
        sys.exit(1)

    api = make_api(torc_settings.database_url)
    result = api.list_job_user_data_consumes(workflow_key, job_key)
    resource_ud: UserDataModel | None = None
    assert result.items is not None
    for item in result.items:
        if item.name == "resource":
            resource_ud = item
            break

    assert resource_ud is not None
    assert resource_ud.data is not None
    assert "url" in resource_ud.data


if __name__ == "__main__":
    main()
