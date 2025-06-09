"""Tracks active/inactive state of CPU affinity masks."""

from torc.exceptions import InvalidParameter


class CpuAffinityMaskTracker:
    """Tracks active/inactive state of CPU affinity masks."""

    def __init__(self, num_cpus: int, cpus_per_process: int) -> None:
        self._num_parallel_processes = num_cpus // cpus_per_process
        self._cpus_per_process = cpus_per_process
        self._masks = compute_cpu_indexes(num_cpus, self._cpus_per_process)
        self._mask_indexes = [False] * len(self._masks)
        self._search_index = 0

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


def compute_cpu_indexes(num_cpus_in_node, cpus_per_process) -> list[tuple[int, ...]]:
    """Return tuples of CPU indexes that can be used to assign CPU affinity to processes.
    If num_cpus_in_node is not evenly divisible by cpus_per_process, not all CPUs will be assigned.
    """
    # TODO: be NUMA aware
    return [
        tuple(range(i, i + cpus_per_process)) for i in range(0, num_cpus_in_node, cpus_per_process)
    ]
