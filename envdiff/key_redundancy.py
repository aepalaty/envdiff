"""Detect redundant keys — keys whose values are identical across all environments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RedundancyEntry:
    key: str
    value: str
    envs: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        env_list = ", ".join(self.envs)
        return f"{self.key} = '{self.value}'  [{env_list}]"


@dataclass
class RedundancyReport:
    env_names: List[str]
    entries: List[RedundancyEntry] = field(default_factory=list)

    @property
    def has_redundant(self) -> bool:
        return len(self.entries) > 0

    @property
    def redundant_keys(self) -> List[str]:
        return [e.key for e in self.entries]

    def __len__(self) -> int:
        return len(self.entries)


class RedundancyDetector:
    """Flag keys that carry the exact same non-empty value in every environment."""

    def calculate(
        self, envs: Dict[str, Dict[str, str]]
    ) -> RedundancyReport:
        env_names = list(envs.keys())
        if len(env_names) < 2:
            return RedundancyReport(env_names=env_names)

        all_keys: set = set()
        for env_data in envs.values():
            all_keys.update(env_data.keys())

        entries: List[RedundancyEntry] = []

        for key in sorted(all_keys):
            values = [
                envs[name].get(key)
                for name in env_names
                if key in envs[name]
            ]
            present_in = [
                name for name in env_names if key in envs[name]
            ]
            # Only redundant when present in ALL envs with the same non-empty value
            if len(present_in) == len(env_names) and len(set(values)) == 1:
                value = values[0]
                if value:  # skip keys that are universally empty
                    entries.append(
                        RedundancyEntry(key=key, value=value, envs=env_names)
                    )

        return RedundancyReport(env_names=env_names, entries=entries)
