from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortedEnv:
    name: str
    keys: List[str]
    original_order: List[str]

    @property
    def is_sorted(self) -> bool:
        return self.keys == sorted(self.keys)

    @property
    def unsorted_keys(self) -> List[str]:
        sorted_keys = sorted(self.original_order)
        return [
            k for i, k in enumerate(self.original_order)
            if k != sorted_keys[i]
        ]

    def __str__(self) -> str:
        status = "sorted" if self.is_sorted else "unsorted"
        return f"{self.name}: {status} ({len(self.keys)} keys)"


@dataclass
class SortingReport:
    envs: List[SortedEnv] = field(default_factory=list)

    @property
    def unsorted_envs(self) -> List[SortedEnv]:
        return [e for e in self.envs if not e.is_sorted]

    @property
    def has_unsorted(self) -> bool:
        return len(self.unsorted_envs) > 0

    @property
    def env_names(self) -> List[str]:
        return [e.name for e in self.envs]


class KeySortingChecker:
    """Checks whether keys in each env file are in alphabetical order."""

    def calculate(self, envs: Dict[str, Dict[str, str]]) -> SortingReport:
        report = SortingReport()
        for name, env in envs.items():
            keys = list(env.keys())
            sorted_env = SortedEnv(
                name=name,
                keys=sorted(keys),
                original_order=keys,
            )
            report.envs.append(sorted_env)
        return report

    def suggest_sorted(self, env: Dict[str, str]) -> Dict[str, str]:
        """Return a new dict with keys sorted alphabetically."""
        return dict(sorted(env.items()))
