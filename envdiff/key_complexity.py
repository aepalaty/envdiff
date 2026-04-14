"""Measures structural complexity of .env files based on key naming patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import re


@dataclass
class ComplexityEntry:
    key: str
    depth: int        # number of underscore-separated segments
    length: int       # character length of the key
    is_namespaced: bool  # has a recognisable PREFIX_ pattern
    score: float      # composite complexity score 0.0–1.0

    def __str__(self) -> str:
        return (
            f"{self.key}: depth={self.depth}, len={self.length}, "
            f"namespaced={self.is_namespaced}, score={self.score:.2f}"
        )


@dataclass
class ComplexityReport:
    env_name: str
    entries: List[ComplexityEntry] = field(default_factory=list)

    @property
    def average_score(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e.score for e in self.entries) / len(self.entries)

    @property
    def most_complex(self) -> List[ComplexityEntry]:
        return sorted(self.entries, key=lambda e: e.score, reverse=True)

    @property
    def deeply_nested(self) -> List[ComplexityEntry]:
        return [e for e in self.entries if e.depth >= 3]


class ComplexityCalculator:
    """Calculates per-key complexity metrics for one or more envs."""

    _NAMESPACE_RE = re.compile(r'^[A-Z][A-Z0-9]+_[A-Z]')

    def calculate(self, env_name: str, env: Dict[str, str]) -> ComplexityReport:
        entries: List[ComplexityEntry] = []
        for key in sorted(env):
            entry = self._analyse(key)
            entries.append(entry)
        return ComplexityReport(env_name=env_name, entries=entries)

    def calculate_all(
        self, envs: Dict[str, Dict[str, str]]
    ) -> Dict[str, ComplexityReport]:
        return {name: self.calculate(name, env) for name, env in envs.items()}

    def _analyse(self, key: str) -> ComplexityEntry:
        segments = key.split('_')
        depth = len(segments)
        length = len(key)
        is_namespaced = bool(self._NAMESPACE_RE.match(key))

        # Score components (each 0–1, weighted)
        depth_score = min((depth - 1) / 5.0, 1.0)      # weight 0.4
        length_score = min(length / 40.0, 1.0)          # weight 0.3
        namespace_score = 0.3 if is_namespaced else 0.0  # weight 0.3

        score = round(
            0.4 * depth_score + 0.3 * length_score + namespace_score, 4
        )
        return ComplexityEntry(
            key=key,
            depth=depth,
            length=length,
            is_namespaced=is_namespaced,
            score=score,
        )
