import os
import sys
from pathlib import Path

from swagger_client import ApiClient, DefaultApi
from swagger_client.configuration import Configuration

from wms.job_runner import JobRunner
from wms.loggers import setup_logging


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} url output_dir time_limit")
        sys.exit(1)

    configuration = Configuration()
    configuration.host = sys.argv[1]
    time_limit = sys.argv[2]
    output_dir = Path(sys.argv[3])
    job_completion_poll_interval = 0.1
    setup_logging(__name__)  # , filename=output_dir / f"{os.getpid()}.log")
    api = DefaultApi(ApiClient(configuration))
    runner = JobRunner(
        api,
        output_dir,
        job_completion_poll_interval=job_completion_poll_interval,
        time_limit=time_limit,
    )
    runner.run_worker()
