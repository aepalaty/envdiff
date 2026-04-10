"""Compare two snapshots and produce an EnvDifference."""

from __future__ import annotations

from typing import Optional

from envdiff.comparator import EnvComparator, EnvDifference
from envdiff.snapshot import Snapshot, SnapshotManager


class SnapshotDiffer:
    """Diff two Snapshot objects using the existing EnvComparator."""

    def __init__(self) -> None:
        self._comparator = EnvComparator()

    def diff(self, baseline: Snapshot, other: Snapshot) -> EnvDifference:
        """Return the EnvDifference between baseline and other snapshots."""
        return self._comparator.compare(
            baseline.env,
            other.env,
            label_a=baseline.label or baseline.source,
            label_b=other.label or other.source,
        )

    def diff_from_files(
        self,
        baseline_path: str,
        other_path: str,
        manager: Optional[SnapshotManager] = None,
    ) -> EnvDifference:
        """Load two snapshot files from disk and diff them."""
        mgr = manager or SnapshotManager()
        baseline = mgr.load(baseline_path)
        other = mgr.load(other_path)
        return self.diff(baseline, other)
