import json
from pathlib import Path

from filelock import SoftFileLock


class SlurmCluster:
    cluster_file = Path("tests") / "slurm.json"
    lock_file = Path("tests") / "fake_slurm.lock"

    def __init__(self) -> None:
        self._timeout = 300

    @classmethod
    def initialize(cls) -> None:
        with open(cls.cluster_file, "w") as f:
            json.dump({"active_nodes": []}, f)

    @classmethod
    def delete(cls) -> None:
        if cls.cluster_file.exists():
            cls.cluster_file.unlink()
        if cls.lock_file.exists():
            cls.lock_file.unlink()

    def add_active_node(self, job_id: str) -> None:
        """Add an active node."""
        lock = SoftFileLock(self.lock_file)
        lock.acquire(timeout=self._timeout)
        try:
            with open(self.cluster_file, "r") as f:
                data = json.load(f)
                data["active_nodes"].append({"job_id": job_id})
            with open(self.cluster_file, "w") as f:
                json.dump(data, f, indent=2)
        finally:
            lock.release()

    def list_active_job_ids(self) -> list[str]:
        """Return all job IDs that are active."""
        lock = SoftFileLock(self.lock_file)
        lock.acquire(timeout=self._timeout)
        try:
            with open(self.cluster_file, "r") as f:
                data = json.load(f)
                return [x["job_id"] for x in data["active_nodes"]]
        finally:
            lock.release()

    def remove_active_node(self, job_id: str) -> None:
        """Remove the node with job_id."""
        lock = SoftFileLock(self.lock_file)
        lock.acquire(timeout=self._timeout)
        try:
            with open(self.cluster_file, "r") as f:
                data = json.load(f)
                node_index = -1
                for i, node in enumerate(data["active_nodes"]):
                    if node["job_id"] == job_id:
                        node_index = i
                        break
                assert node_index != -1
                data["active_nodes"].pop(node_index)
            with open(self.cluster_file, "w") as f:
                json.dump(data, f, indent=2)
        finally:
            lock.release()
