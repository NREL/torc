"""Test CPU utility functions"""

import pytest

from torc.exceptions import InvalidParameter
from torc.utils.cpu_affinity_mask_tracker import compute_cpu_indexes, CpuAffinityMaskTracker


def test_compute_cpu_indexes():
    """Test CPU masks"""
    assert compute_cpu_indexes(36, 18) == [tuple(range(18)), tuple(range(18, 36))]
    assert compute_cpu_indexes(36, 9) == [
        tuple(range(0, 9)),
        tuple(range(9, 18)),
        tuple(range(18, 27)),
        tuple(range(27, 36)),
    ]


def test_cpu_affinity_mask_tracker():
    """Test CPU affinitity mask tracker."""
    tracker = CpuAffinityMaskTracker(36, 9)
    assert tracker.acquire_mask() == (0, tuple(range(0, 9)))
    assert tracker.acquire_mask() == (1, tuple(range(9, 18)))
    assert tracker.acquire_mask() == (2, tuple(range(18, 27)))
    assert tracker.acquire_mask() == (3, tuple(range(27, 36)))
    with pytest.raises(InvalidParameter):
        tracker.acquire_mask()
    tracker.release_mask(2)
    assert tracker.acquire_mask() == (2, tuple(range(18, 27)))
