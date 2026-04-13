"""Track how env key values change across multiple snapshots over time."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envdiff.snapshot import Snapshot


@dataclass
class TimelineEntry:
    label: str
    value: Optional[str]

    def __str__(self) -> str:
        val = self.value if self.value is not None else "<missing>"
        return f"[{self.label}] {val}"


@dataclass
class KeyTimeline:
    key: str
    entries: List[TimelineEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        values = [e.value for e in self.entries]
        return len(set(values)) > 1

    @property
    def change_count(self) -> int:
        changes = 0
        for i in range(1, len(self.entries)):
            if self.entries[i].value != self.entries[i - 1].value:
                changes += 1
        return changes

    def __str__(self) -> str:
        lines = [f"Key: {self.key}"]
        for entry in self.entries:
            lines.append(f"  {entry}")
        return "\n".join(lines)


@dataclass
class TimelineReport:
    timelines: Dict[str, KeyTimeline] = field(default_factory=dict)

    @property
    def changed_keys(self) -> List[str]:
        return [k for k, t in self.timelines.items() if t.has_changes]

    @property
    def stable_keys(self) -> List[str]:
        return [k for k, t in self.timelines.items() if not t.has_changes]

    @property
    def has_changes(self) -> bool:
        return bool(self.changed_keys)


class KeyTimelineCalculator:
    def calculate(self, snapshots: List[Snapshot]) -> TimelineReport:
        """Build a timeline report from an ordered list of snapshots."""
        report = TimelineReport()

        all_keys: set = set()
        for snap in snapshots:
            all_keys.update(snap.env.keys())

        for key in sorted(all_keys):
            timeline = KeyTimeline(key=key)
            for snap in snapshots:
                label = snap.label or snap.captured_at
                value = snap.env.get(key)
                timeline.entries.append(TimelineEntry(label=label, value=value))
            report.timelines[key] = timeline

        return report
