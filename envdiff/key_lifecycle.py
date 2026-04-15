from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LifecycleEvent:
    snapshot_label: str
    status: str  # 'added', 'removed', 'modified', 'unchanged'
    value: Optional[str] = None

    def __str__(self) -> str:
        return f"[{self.snapshot_label}] {self.status}" + (
            f" = {self.value}" if self.value is not None else ""
        )


@dataclass
class LifecycleEntry:
    key: str
    events: List[LifecycleEvent] = field(default_factory=list)

    @property
    def first_seen(self) -> Optional[str]:
        for e in self.events:
            if e.status in ("added", "unchanged"):
                return e.snapshot_label
        return None

    @property
    def last_removed(self) -> Optional[str]:
        for e in reversed(self.events):
            if e.status == "removed":
                return e.snapshot_label
        return None

    @property
    def change_count(self) -> int:
        return sum(1 for e in self.events if e.status in ("added", "removed", "modified"))

    def __str__(self) -> str:
        return f"{self.key}: {len(self.events)} events, {self.change_count} changes"


@dataclass
class LifecycleReport:
    entries: List[LifecycleEntry] = field(default_factory=list)

    @property
    def all_keys(self) -> List[str]:
        return [e.key for e in self.entries]

    def entry_for(self, key: str) -> Optional[LifecycleEntry]:
        for e in self.entries:
            if e.key == key:
                return e
        return None


class LifecycleCalculator:
    def calculate(self, snapshots: List[Dict[str, Dict[str, str]]]) -> LifecycleReport:
        """snapshots: list of {label: str, env: dict} dicts in chronological order."""
        all_keys: set = set()
        for snap in snapshots:
            all_keys.update(snap["env"].keys())

        entries: List[LifecycleEntry] = []
        for key in sorted(all_keys):
            entry = LifecycleEntry(key=key)
            prev_value: Optional[str] = None
            prev_present: bool = False
            for snap in snapshots:
                label = snap["label"]
                env = snap["env"]
                if key in env:
                    current = env[key]
                    if not prev_present:
                        status = "added"
                    elif current != prev_value:
                        status = "modified"
                    else:
                        status = "unchanged"
                    entry.events.append(LifecycleEvent(label, status, current))
                    prev_value = current
                    prev_present = True
                else:
                    if prev_present:
                        entry.events.append(LifecycleEvent(label, "removed"))
                    prev_present = False
                    prev_value = None
            entries.append(entry)
        return LifecycleReport(entries=entries)
