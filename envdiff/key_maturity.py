from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envdiff.snapshot import Snapshot


MATURITY_THRESHOLDS = {
    "stable": 5,
    "established": 3,
    "emerging": 1,
}


@dataclass
class MaturityEntry:
    key: str
    appearances: int
    snapshot_count: int
    label: str

    def __str__(self) -> str:
        return f"{self.key}: {self.label} ({self.appearances}/{self.snapshot_count} snapshots)"

    @property
    def maturity_ratio(self) -> float:
        if self.snapshot_count == 0:
            return 0.0
        return self.appearances / self.snapshot_count


@dataclass
class MaturityReport:
    entries: List[MaturityEntry] = field(default_factory=list)
    env_names: List[str] = field(default_factory=list)

    @property
    def stable_keys(self) -> List[MaturityEntry]:
        return [e for e in self.entries if e.label == "stable"]

    @property
    def emerging_keys(self) -> List[MaturityEntry]:
        return [e for e in self.entries if e.label == "emerging"]

    @property
    def transient_keys(self) -> List[MaturityEntry]:
        return [e for e in self.entries if e.label == "transient"]


def _classify(appearances: int, total: int) -> str:
    if total == 0:
        return "transient"
    ratio = appearances / total
    if ratio >= 0.8:
        return "stable"
    if ratio >= 0.4:
        return "established"
    if ratio >= 0.1:
        return "emerging"
    return "transient"


class MaturityCalculator:
    def calculate(self, snapshots: List[Snapshot]) -> MaturityReport:
        if not snapshots:
            return MaturityReport()

        env_names = [s.label or s.path for s in snapshots]
        total = len(snapshots)
        key_counts: Dict[str, int] = {}

        for snap in snapshots:
            for key in snap.env.keys():
                key_counts[key] = key_counts.get(key, 0) + 1

        entries = []
        for key, count in sorted(key_counts.items()):
            label = _classify(count, total)
            entries.append(MaturityEntry(
                key=key,
                appearances=count,
                snapshot_count=total,
                label=label,
            ))

        return MaturityReport(entries=entries, env_names=env_names)
