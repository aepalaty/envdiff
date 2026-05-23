from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone


@dataclass
class FreshnessEntry:
    key: str
    last_seen: Optional[datetime]
    snapshot_count: int
    missing_in_latest: bool

    def __str__(self) -> str:
        status = "stale" if self.missing_in_latest else "fresh"
        last = self.last_seen.strftime("%Y-%m-%d") if self.last_seen else "never"
        return f"{self.key}: {status} (last seen {last}, {self.snapshot_count} snapshots)"


@dataclass
class FreshnessReport:
    env_names: List[str]
    entries: List[FreshnessEntry] = field(default_factory=list)

    @property
    def stale_keys(self) -> List[FreshnessEntry]:
        return [e for e in self.entries if e.missing_in_latest]

    @property
    def fresh_keys(self) -> List[FreshnessEntry]:
        return [e for e in self.entries if not e.missing_in_latest]

    @property
    def has_stale(self) -> bool:
        return len(self.stale_keys) > 0


class FreshnessCalculator:
    """Determine key freshness across a sequence of snapshots."""

    def calculate(self, snapshots: List[Dict[str, Dict[str, str]]]) -> FreshnessReport:
        """
        :param snapshots: ordered list of {env_name: {key: value}} dicts,
                          oldest first, newest last.
        """
        if not snapshots:
            return FreshnessReport(env_names=[])

        env_names = list(snapshots[-1].keys())
        all_keys: set = set()
        for snap in snapshots:
            for env_keys in snap.values():
                all_keys.update(env_keys.keys())

        latest_keys: set = set()
        for env_keys in snapshots[-1].values():
            latest_keys.update(env_keys.keys())

        entries: List[FreshnessEntry] = []
        for key in sorted(all_keys):
            count = sum(
                1 for snap in snapshots
                if any(key in env_keys for env_keys in snap.values())
            )
            last_seen: Optional[datetime] = None
            for i, snap in enumerate(snapshots):
                if any(key in env_keys for env_keys in snap.values()):
                    last_seen = datetime.fromtimestamp(
                        i * 86400, tz=timezone.utc
                    )
            missing = key not in latest_keys
            entries.append(FreshnessEntry(
                key=key,
                last_seen=last_seen,
                snapshot_count=count,
                missing_in_latest=missing,
            ))

        return FreshnessReport(env_names=env_names, entries=entries)
