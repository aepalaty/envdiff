"""Compute statistics and frequency analysis across multiple .env environments."""

from dataclasses import dataclass, field
from typing import Dict, List, Set
from collections import Counter


@dataclass
class KeyStats:
    """Statistics for a single key across all environments."""
    key: str
    present_in: List[str] = field(default_factory=list)
    missing_from: List[str] = field(default_factory=list)
    unique_values: Set[str] = field(default_factory=set)

    @property
    def coverage(self) -> float:
        total = len(self.present_in) + len(self.missing_from)
        if total == 0:
            return 0.0
        return len(self.present_in) / total

    @property
    def has_value_drift(self) -> bool:
        return len(self.unique_values) > 1

    def __str__(self) -> str:
        pct = f"{self.coverage * 100:.0f}%"
        drift = " [value drift]" if self.has_value_drift else ""
        return f"{self.key}: coverage={pct}, envs={len(self.present_in)}{drift}"


@dataclass
class EnvStatsReport:
    """Aggregated statistics across all compared environments."""
    env_names: List[str]
    key_stats: Dict[str, KeyStats] = field(default_factory=dict)

    @property
    def total_keys(self) -> int:
        return len(self.key_stats)

    @property
    def universal_keys(self) -> List[str]:
        return [k for k, s in self.key_stats.items() if s.coverage == 1.0]

    @property
    def partial_keys(self) -> List[str]:
        return [k for k, s in self.key_stats.items() if 0 < s.coverage < 1.0]

    @property
    def drifted_keys(self) -> List[str]:
        return [k for k, s in self.key_stats.items() if s.has_value_drift]

    def summary(self) -> str:
        lines = [
            f"Environments : {len(self.env_names)}",
            f"Total keys   : {self.total_keys}",
            f"Universal    : {len(self.universal_keys)}",
            f"Partial      : {len(self.partial_keys)}",
            f"Value drift  : {len(self.drifted_keys)}",
        ]
        return "\n".join(lines)


class EnvStatsCalculator:
    """Compute KeyStats across a collection of named environments."""

    def calculate(self, envs: Dict[str, Dict[str, str]]) -> EnvStatsReport:
        env_names = list(envs.keys())
        all_keys: Set[str] = set()
        for env in envs.values():
            all_keys.update(env.keys())

        report = EnvStatsReport(env_names=env_names)
        for key in sorted(all_keys):
            stats = KeyStats(key=key)
            for name, env in envs.items():
                if key in env:
                    stats.present_in.append(name)
                    stats.unique_values.add(env[key])
                else:
                    stats.missing_from.append(name)
            report.key_stats[key] = stats

        return report
