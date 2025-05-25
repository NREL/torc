import sys

from slurm_cluster import SlurmCluster


def main():
    cluster = SlurmCluster()

    job_id: str | None = None
    for i, arg in enumerate(sys.argv):
        if arg == "-j":
            job_id = sys.argv[i + 1]
    assert job_id is not None
    name = job_id  # not technically correct, but we don't have that here and it is unused.
    if job_id in cluster.list_active_job_ids():
        print(f"{job_id} {name} RUNNING")
    else:
        print(f"{job_id} {name} COMPLETED")


if __name__ == "__main__":
    main()
