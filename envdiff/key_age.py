"""Detect stale or potentially outdated keys based on snapshot history."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from envdiff.snapshot import Snapshot


@dataclass
class AgeEntry:
    key: str
    first_seen: datetime
    last_changed: datetime
    change_count: int
    days_since_change: int

    def __str__(self) -> str:
        return (
            f"{self.key}: last changed {self.days_since_change}d ago "
            f"(seen {self.change_count} change(s))"
        )

    @property
    def is_stale(self) -> bool:
        return self.days_since_change > 90


@dataclass
class AgeReport:
    entries: List[AgeEntry] = field(default_factory=list)

    @property
    def stale_keys(self) -> List[AgeEntry]:
        return [e for e in self.entries if e.is_stale]

    @property
    def has_stale(self) -> bool:
        return len(self.stale_keys) > 0

    @property
    def average_days_since_change(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e.days_since_change for e in self.entries) / len(self.entries)


class KeyAgeCalculator:
    def calculate(self, snapshots: List[Snapshot]) -> AgeReport:
        if not snapshots:
            return AgeReport()

        sorted_snaps = sorted(snapshots, key=lambda s: s.timestamp)
        now = datetime.now(timezone.utc)

        key_first_seen: Dict[str, datetime] = {}
        key_last_changed: Dict[str, datetime] = {}
        key_change_count: Dict[str, int] = {}
        key_last_value: Dict[str, Optional[str]] = {}

        for snap in sorted_snaps:
            ts = snap.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            for key, value in snap.env.items():
                if key not in key_first_seen:
                    key_first_seen[key] = ts
                    key_last_changed[key] = ts
                    key_change_count[key] = 0
                    key_last_value[key] = value
                elif value != key_last_value[key]:
                    key_last_changed[key] = ts
                    key_change_count[key] += 1
                    key_last_value[key] = value

        entries = []
        for key in key_first_seen:
            last_changed = key_last_changed[key]
            delta = now - last_changed
            entries.append(AgeEntry(
                key=key,
                first_seen=key_first_seen[key],
                last_changed=last_changed,
                change_count=key_change_count[key],
                days_since_change=delta.days,
            ))

        entries.sort(key=lambda e: e.days_since_change, reverse=True)
        return AgeReport(entries=entries)
