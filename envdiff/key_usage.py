"""Tracks key usage frequency and last-seen metadata across env snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class KeyUsageRecord:
    key: str
    seen_in: List[str] = field(default_factory=list)
    last_seen: Optional[str] = None  # ISO timestamp
    occurrence_count: int = 0

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "seen_in": self.seen_in,
            "last_seen": self.last_seen,
            "occurrence_count": self.occurrence_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KeyUsageRecord":
        return cls(
            key=data["key"],
            seen_in=data.get("seen_in", []),
            last_seen=data.get("last_seen"),
            occurrence_count=data.get("occurrence_count", 0),
        )


@dataclass
class KeyUsageReport:
    records: Dict[str, KeyUsageRecord] = field(default_factory=dict)

    @property
    def total_keys(self) -> int:
        return len(self.records)

    def most_common(self, n: int = 5) -> List[KeyUsageRecord]:
        sorted_records = sorted(
            self.records.values(), key=lambda r: r.occurrence_count, reverse=True
        )
        return sorted_records[:n]

    def least_common(self, n: int = 5) -> List[KeyUsageRecord]:
        sorted_records = sorted(
            self.records.values(), key=lambda r: r.occurrence_count
        )
        return sorted_records[:n]

    def keys_seen_in_all(self, env_names: List[str]) -> List[KeyUsageRecord]:
        """Return records for keys that appear in every one of the given env names."""
        env_set = set(env_names)
        return [
            record
            for record in self.records.values()
            if env_set.issubset(set(record.seen_in))
        ]


class KeyUsageTracker:
    """Builds a usage report from multiple named env dicts."""

    def track(self, envs: Dict[str, Dict[str, str]]) -> KeyUsageReport:
        report = KeyUsageReport()
        timestamp = datetime.utcnow().isoformat()

        for env_name, env in envs.items():
            for key in env:
                if key not in report.records:
                    report.records[key] = KeyUsageRecord(key=key)
                record = report.records[key]
                if env_name not in record.seen_in:
                    record.seen_in.append(env_name)
                record.occurrence_count += 1
                record.last_seen = timestamp

        return report
