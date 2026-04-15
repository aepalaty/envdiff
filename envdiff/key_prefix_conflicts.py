"""Detect keys that share a prefix but have conflicting naming conventions."""
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class PrefixConflict:
    prefix: str
    keys: List[str]
    envs_affected: Set[str]

    def __str__(self) -> str:
        keys_str = ", ".join(sorted(self.keys))
        envs_str = ", ".join(sorted(self.envs_affected))
        return f"[{self.prefix}*] keys: {keys_str} (in: {envs_str})"


@dataclass
class PrefixConflictReport:
    conflicts: List[PrefixConflict] = field(default_factory=list)
    env_names: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    @property
    def conflict_prefixes(self) -> List[str]:
        return [c.prefix for c in self.conflicts]


class PrefixConflictDetector:
    """Finds keys that share a prefix but differ across envs, suggesting naming drift."""

    def __init__(self, min_prefix_length: int = 3):
        self.min_prefix_length = min_prefix_length

    def detect(self, envs: Dict[str, Dict[str, str]]) -> PrefixConflictReport:
        env_names = list(envs.keys())
        all_keys: Set[str] = set()
        for env in envs.values():
            all_keys.update(env.keys())

        prefix_map: Dict[str, List[str]] = {}
        for key in all_keys:
            parts = key.split("_")
            for i in range(1, len(parts)):
                prefix = "_".join(parts[:i])
                if len(prefix) >= self.min_prefix_length:
                    prefix_map.setdefault(prefix, []).append(key)

        conflicts: List[PrefixConflict] = []
        seen_prefixes: Set[str] = set()

        for prefix, keys in prefix_map.items():
            if len(keys) < 2:
                continue
            if prefix in seen_prefixes:
                continue

            affected_envs: Set[str] = set()
            for env_name, env_data in envs.items():
                if any(k in env_data for k in keys):
                    affected_envs.add(env_name)

            if len(affected_envs) > 1:
                conflicts.append(PrefixConflict(
                    prefix=prefix,
                    keys=sorted(keys),
                    envs_affected=affected_envs,
                ))
                seen_prefixes.add(prefix)

        conflicts.sort(key=lambda c: c.prefix)
        return PrefixConflictReport(conflicts=conflicts, env_names=env_names)
