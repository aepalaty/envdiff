"""Measures how frequently keys change value across snapshots."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Sequence


@dataclass
class VolatilityEntry:
    key: str
    total_snapshots: int
    change_count: int
    values_seen: List[str] = field(default_factory=list)

    @property
    def volatility_ratio(self) -> float:
        if self.total_snapshots <= 1:
            return 0.0
        return self.change_count / (self.total_snapshots - 1)

    @property
    def is_volatile(self) -> bool:
        return self.volatility_ratio >= 0.5

    def __str__(self) -> str:
        pct = f"{self.volatility_ratio * 100:.0f}%"
        flag = " [volatile]" if self.is_volatile else ""
        return f"{self.key}: changed {self.change_count}/{self.total_snapshots - 1} transitions ({pct}){flag}"


@dataclass
class VolatilityReport:
    entries: List[VolatilityEntry] = field(default_factory=list)

    @property
    def volatile_keys(self) -> List[VolatilityEntry]:
        return [e for e in self.entries if e.is_volatile]

    @property
    def stable_keys(self) -> List[VolatilityEntry]:
        return [e for e in self.entries if not e.is_volatile]

    @property
    def has_volatile_keys(self) -> bool:
        return len(self.volatile_keys) > 0

    @property
    def average_volatility(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e.volatility_ratio for e in self.entries) / len(self.entries)


class VolatilityCalculator:
    """Calculates key volatility across a sequence of env snapshots."""

    def calculate(self, snapshots: Sequence[Dict[str, str]]) -> VolatilityReport:
        if not snapshots:
            return VolatilityReport()

        all_keys: set[str] = set()
        for snap in snapshots:
            all_keys.update(snap.keys())

        entries: List[VolatilityEntry] = []
        for key in sorted(all_keys):
            values = [snap.get(key, "") for snap in snapshots]
            changes = sum(1 for i in range(1, len(values)) if values[i] != values[i - 1])
            unique_vals = list(dict.fromkeys(values))
            entries.append(
                VolatilityEntry(
                    key=key,
                    total_snapshots=len(snapshots),
                    change_count=changes,
                    values_seen=unique_vals,
                )
            )

        return VolatilityReport(entries=entries)
