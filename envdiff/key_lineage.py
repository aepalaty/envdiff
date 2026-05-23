from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LineageEvent:
    snapshot_label: str
    value: str
    changed_from: Optional[str] = None

    def __str__(self) -> str:
        if self.changed_from is None:
            return f"[{self.snapshot_label}] introduced as {self.value!r}"
        return f"[{self.snapshot_label}] changed {self.changed_from!r} -> {self.value!r}"


@dataclass
class LineageEntry:
    key: str
    events: List[LineageEvent] = field(default_factory=list)

    @property
    def introduced_in(self) -> Optional[str]:
        return self.events[0].snapshot_label if self.events else None

    @property
    def current_value(self) -> Optional[str]:
        return self.events[-1].value if self.events else None

    @property
    def change_count(self) -> int:
        return sum(1 for e in self.events if e.changed_from is not None)

    def __str__(self) -> str:
        return f"{self.key}: {len(self.events)} event(s), {self.change_count} change(s)"


@dataclass
class LineageReport:
    entries: Dict[str, LineageEntry] = field(default_factory=dict)

    @property
    def all_keys(self) -> List[str]:
        return sorted(self.entries.keys())

    def get(self, key: str) -> Optional[LineageEntry]:
        return self.entries.get(key)


class LineageCalculator:
    def calculate(self, snapshots: List[Dict[str, Dict[str, str]]]) -> LineageReport:
        """
        snapshots: list of {label: str, env: dict} dicts ordered oldest -> newest.
        Each item should be {"label": "v1", "env": {"KEY": "val", ...}}
        """
        report = LineageReport()
        prev: Dict[str, str] = {}

        for snap in snapshots:
            label = snap["label"]
            env: Dict[str, str] = snap["env"]

            for key, value in env.items():
                if key not in report.entries:
                    report.entries[key] = LineageEntry(key=key)

                entry = report.entries[key]
                if key not in prev:
                    entry.events.append(LineageEvent(snapshot_label=label, value=value))
                elif prev[key] != value:
                    entry.events.append(
                        LineageEvent(snapshot_label=label, value=value, changed_from=prev[key])
                    )

            prev = dict(env)

        return report
