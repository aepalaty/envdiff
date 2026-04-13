"""Detect value drift for keys across multiple snapshots over time."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DriftEntry:
    key: str
    values: List[str] = field(default_factory=list)
    env_names: List[str] = field(default_factory=list)

    @property
    def unique_values(self) -> int:
        return len(set(self.values))

    @property
    def has_drift(self) -> bool:
        return self.unique_values > 1

    def __str__(self) -> str:
        if not self.has_drift:
            return f"{self.key}: stable across {len(self.env_names)} env(s)"
        pairs = ", ".join(
            f"{env}={val}" for env, val in zip(self.env_names, self.values)
        )
        return f"{self.key}: {self.unique_values} distinct values [{pairs}]"


@dataclass
class DriftReport:
    entries: List[DriftEntry] = field(default_factory=list)

    @property
    def drifted_keys(self) -> List[DriftEntry]:
        return [e for e in self.entries if e.has_drift]

    @property
    def stable_keys(self) -> List[DriftEntry]:
        return [e for e in self.entries if not e.has_drift]

    @property
    def has_drift(self) -> bool:
        return len(self.drifted_keys) > 0

    @property
    def summary(self) -> str:
        total = len(self.entries)
        drifted = len(self.drifted_keys)
        return f"{drifted}/{total} key(s) have value drift"


class KeyDriftCalculator:
    """Compare key values across multiple named environments to detect drift."""

    def calculate(self, envs: Dict[str, Dict[str, str]]) -> DriftReport:
        """Accepts a mapping of env_name -> {key: value} dicts."""
        all_keys: set = set()
        for env_dict in envs.values():
            all_keys.update(env_dict.keys())

        entries: List[DriftEntry] = []
        for key in sorted(all_keys):
            values: List[str] = []
            env_names: List[str] = []
            for env_name, env_dict in envs.items():
                if key in env_dict:
                    values.append(env_dict[key])
                    env_names.append(env_name)
            entries.append(DriftEntry(key=key, values=values, env_names=env_names))

        return DriftReport(entries=entries)
