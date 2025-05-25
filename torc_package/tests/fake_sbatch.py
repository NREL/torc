import multiprocessing
import os
import random
import subprocess
import sys
from pathlib import Path

import psutil

from slurm_cluster import SlurmCluster


def main():
    print(f"********** {sys.argv} ************")
    sbatch_file = Path(sys.argv[1])
    cmd: list[str] = []
    with open(sbatch_file, encoding="utf-8") as f:
        for line in f:
            if line.startswith("torc"):
                args = line.strip().split()
                # assert args[0] == "torc"
                # torc_exec = shutil.which(args[0])
                # coverage_file = str(uuid4()) + ".coverage"
                # cmd = ["coverage", "run", "--data-file", torc_exec, coverage_file] + args[1:]
                cmd += args
                break
    if not cmd:
        msg = f"Failed to find torc command in sbatch file {sbatch_file}"
        raise Exception(msg)

    job_id = str(random.randint(1, 1_000_000_000))
    output_dir: Path | None = None
    for i, arg in enumerate(cmd):
        if arg == "-o":
            output_dir = Path(cmd[i + 1])
    assert output_dir is not None
    stdout_file = output_dir / f"job_output_{job_id}.o"
    stderr_file = output_dir / f"job_output_{job_id}.e"

    env = os.environ.copy()
    env.update(
        {
            "SLURM_JOB_ID": job_id,
            "SLURM_NODEID": "1",
            "SLURM_TASK_PID": str(os.getpid()),
            "SLURM_CLUSTER_NAME": "local",
            "SLURM_MEM_PER_NODE": str(int(psutil.virtual_memory().total / (1024 * 1024))),
            "SLURM_JOB_NUM_NODES": "1",
            "SLURM_CPUS_ON_NODE": str(multiprocessing.cpu_count()),
            "SLURM_CPUS_PER_TASK": "1",
            "SLURM_JOB_GPUS": "0",
        }
    )
    cluster = SlurmCluster()
    cluster.add_active_node(job_id)
    try:
        print(f"Submitted batch job {job_id}")
        with open(stdout_file, "w") as f_out:
            with open(stderr_file, "w") as f_err:
                subprocess.run(cmd, check=True, env=env, stdout=f_out, stderr=f_err)
    except Exception:
        raise
    finally:
        cluster.remove_active_node(env["SLURM_JOB_ID"])


if __name__ == "__main__":
    main()
