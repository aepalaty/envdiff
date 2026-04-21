"""Detect keys that are scoped to specific environments (e.g. only in prod, only in dev)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class ScopeEntry:
    key: str
    present_in: List[str]
    absent_from: List[str]

    @property
    def is_scoped(self) -> bool:
        return len(self.absent_from) > 0

    def __str__(self) -> str:
        present = ", ".join(self.present_in)
        absent = ", ".join(self.absent_from)
        return f"{self.key}: present in [{present}], absent from [{absent}]"


@dataclass
class ScopeReport:
    env_names: List[str]
    entries: List[ScopeEntry] = field(default_factory=list)

    @property
    def scoped_keys(self) -> List[ScopeEntry]:
        return [e for e in self.entries if e.is_scoped]

    @property
    def universal_keys(self) -> List[ScopeEntry]:
        return [e for e in self.entries if not e.is_scoped]

    @property
    def has_scoped_keys(self) -> bool:
        return len(self.scoped_keys) > 0

    def absent_from_env(self, env_name: str) -> List[ScopeEntry]:
        return [e for e in self.entries if env_name in e.absent_from]


class KeyScopeCalculator:
    def calculate(self, envs: Dict[str, Dict[str, str]]) -> ScopeReport:
        env_names = list(envs.keys())
        all_keys: Set[str] = set()
        for env in envs.values():
            all_keys.update(env.keys())

        entries: List[ScopeEntry] = []
        for key in sorted(all_keys):
            present_in = [name for name, env in envs.items() if key in env]
            absent_from = [name for name in env_names if name not in present_in]
            entries.append(ScopeEntry(
                key=key,
                present_in=present_in,
                absent_from=absent_from,
            ))

        return ScopeReport(env_names=env_names, entries=entries)
