"""Test CPU utility functions"""

import pytest

from torc.exceptions import InvalidParameter
from torc.utils.cpu_affinity_mask_tracker import (
    _compute_cpu_indexes,
    _get_max_parallel_jobs,
    CpuAffinityMaskTracker,
)


# Copied from a Kestrel compute node.
PY_LIBNUMA_HARDWARE_INFO: dict[str, dict[int, list[int]]] = {
    "node_cpu_info": {
        0: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        1: [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
        2: [26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38],
        3: [39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51],
        4: [52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64],
        5: [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77],
        6: [78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90],
        7: [91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103],
    },
}

ACTUAL_0 = PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"][0]
ACTUAL_1 = PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"][1]
ACTUAL_2 = PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"][2]
ACTUAL_3 = PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"][3]
ACTUAL_4 = PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"][4]
ACTUAL_5 = PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"][5]
ACTUAL_6 = PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"][6]
ACTUAL_7 = PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"][7]


def test_get_max_parallel_jobs():
    assert _get_max_parallel_jobs(PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"], 10) == sum(
        [len(x) // 10 for x in PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"].values()]
    )


def test_compute_cpu_indexes():
    """Test CPU masks"""
    assert _compute_cpu_indexes(PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"], 13) == [
        tuple(ACTUAL_0),
        tuple(ACTUAL_1),
        tuple(ACTUAL_2),
        tuple(ACTUAL_3),
        tuple(ACTUAL_4),
        tuple(ACTUAL_5),
        tuple(ACTUAL_6),
        tuple(ACTUAL_7),
    ]
    assert _compute_cpu_indexes(PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"], 5)[:4] == [
        tuple(ACTUAL_0[0:5]),
        tuple(ACTUAL_0[5:10]),
        tuple(ACTUAL_1[0:5]),
        tuple(ACTUAL_1[5:10]),
    ]


def test_cpu_affinity_mask_tracker():
    """Test CPU affinitity mask tracker."""
    masks = _compute_cpu_indexes(PY_LIBNUMA_HARDWARE_INFO["node_cpu_info"], 10)
    tracker = CpuAffinityMaskTracker(10, masks)
    assert tracker.acquire_mask() == (0, tuple(ACTUAL_0[0:10]))
    assert tracker.acquire_mask() == (1, tuple(ACTUAL_1[0:10]))
    assert tracker.acquire_mask() == (2, tuple(ACTUAL_2[0:10]))
    assert tracker.acquire_mask() == (3, tuple(ACTUAL_3[0:10]))
    assert tracker.acquire_mask() == (4, tuple(ACTUAL_4[0:10]))
    assert tracker.acquire_mask() == (5, tuple(ACTUAL_5[0:10]))
    assert tracker.acquire_mask() == (6, tuple(ACTUAL_6[0:10]))
    assert tracker.acquire_mask() == (7, tuple(ACTUAL_7[0:10]))
    with pytest.raises(InvalidParameter):
        tracker.acquire_mask()
    tracker.release_mask(2)
    assert tracker.acquire_mask() == (2, tuple(ACTUAL_2[0:10]))
