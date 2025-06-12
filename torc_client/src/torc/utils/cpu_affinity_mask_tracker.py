"""Tracks active/inactive state of CPU affinity masks."""

import multiprocessing
from typing import Self

from loguru import logger

from torc.exceptions import InvalidParameter

NUMA_CPU_INFO: dict[int, list[int]]
try:
    from numa import info as numa_info

    NUMA_CPU_INFO = numa_info.numa_hardware_info()["node_cpu_info"]
except Exception:
    NUMA_CPU_INFO = {0: list(range(multiprocessing.cpu_count()))}


class CpuAffinityMaskTracker:
    """Tracks active/inactive state of CPU affinity masks."""

    def __init__(self, cpus_per_process: int, masks: list[tuple[int, ...]]) -> None:
        self._cpus_per_process = cpus_per_process
        self._masks = masks
        self._mask_indexes = [False] * len(self._masks)
        self._search_index = 0
        if len(NUMA_CPU_INFO) > 1 and cpus_per_process > len(NUMA_CPU_INFO[0]):
            logger.warning(
                "Disregarding NUMA because the cpus_per_process={} is greater than the "
                "number of CPUS per NUMA node: {}.",
                cpus_per_process,
                len(NUMA_CPU_INFO[0]),
            )
            # TODO: consider grouping NUMA nodes
            self._numa_cpu_info = {0: list(range(multiprocessing.cpu_count()))}

    @classmethod
    def load(cls, cpus_per_process: int) -> Self:
        masks = compute_cpu_indexes(cpus_per_process)
        return cls(cpus_per_process, masks)

    def acquire_mask(self) -> tuple[int, tuple[int, ...]]:
        """Find an inactive mask, make it active, and return its index and it."""
        for _ in range(len(self._masks)):
            if not self._mask_indexes[self._search_index]:
                self._mask_indexes[self._search_index] = True
                return (self._search_index, self._masks[self._search_index])
            self._search_index += 1
            if self._search_index == len(self._masks):
                self._search_index = 0

        msg = "No mask is available"
        raise InvalidParameter(msg)

    def release_mask(self, index: int):
        """Set a mask to inactive.

        Parameters
        ----------
        index : int
            Index of the mask returned by get_inactive_mask.
        """
        assert self._mask_indexes[index]
        self._mask_indexes[index] = False

    def get_num_masks(self) -> int:
        """Return the number of masks that are stored."""
        return len(self._masks)


def get_max_parallel_jobs(cpus_per_process: int) -> int:
    """Return the maximum number of parallel jobs that can be run."""
    return _get_max_parallel_jobs(NUMA_CPU_INFO, cpus_per_process)


def _get_max_parallel_jobs(node_cpu_info: dict[int, list[int]], cpus_per_process: int) -> int:
    total = 0
    for cpu_indexes in node_cpu_info.values():
        total += len(cpu_indexes) // cpus_per_process
    return total


def compute_cpu_indexes(cpus_per_process: int) -> list[tuple[int, ...]]:
    """Return tuples of CPU indexes that can be used to assign CPU affinity to processes.
    If num_cpus_in_node is not evenly divisible by cpus_per_process, not all CPUs will be assigned.
    """
    return _compute_cpu_indexes(numa_info.numa_hardware_info()["node_cpu_info"], cpus_per_process)  # type: ignore


def _compute_cpu_indexes(
    node_cpu_info: dict[int, list[int]], cpus_per_process: int
) -> list[tuple[int, ...]]:
    cpu_indexes: list[tuple[int, ...]] = []
    for node_index, node_cpu_indexes in node_cpu_info.items():
        for i in range(0, len(node_cpu_indexes), cpus_per_process):
            slice = node_cpu_indexes[i : i + cpus_per_process]
            if len(slice) == cpus_per_process:
                cpu_indexes.append(tuple(slice))
            else:
                # Users probably don't want us to assign CPUs from different nodes.
                logger.trace("Leaving {} CPUs idle on node {}", len(slice), node_index)

    return cpu_indexes
