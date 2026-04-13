"""Detect low-entropy (potentially weak or placeholder) values in env files."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List


def _shannon_entropy(value: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum(
        (c / length) * math.log2(c / length) for c in counts.values()
    )


@dataclass
class EntropyEntry:
    key: str
    value: str
    entropy: float
    is_weak: bool

    def __str__(self) -> str:
        status = "WEAK" if self.is_weak else "ok"
        return f"{self.key}: entropy={self.entropy:.2f} [{status}]"


@dataclass
class EntropyReport:
    env_name: str
    entries: List[EntropyEntry] = field(default_factory=list)

    @property
    def weak_keys(self) -> List[EntropyEntry]:
        return [e for e in self.entries if e.is_weak]

    @property
    def has_weak_values(self) -> bool:
        return bool(self.weak_keys)

    def summary(self) -> str:
        total = len(self.entries)
        weak = len(self.weak_keys)
        return f"{self.env_name}: {weak}/{total} weak values"


class EntropyCalculator:
    """Analyse env values for low entropy (e.g. 'changeme', '1234', placeholder text)."""

    DEFAULT_THRESHOLD = 2.5

    def __init__(self, threshold: float = DEFAULT_THRESHOLD) -> None:
        self.threshold = threshold

    def calculate(self, env: Dict[str, str], env_name: str = "env") -> EntropyReport:
        report = EntropyReport(env_name=env_name)
        for key, value in env.items():
            entropy = _shannon_entropy(value)
            is_weak = bool(value) and entropy < self.threshold
            report.entries.append(
                EntropyEntry(key=key, value=value, entropy=entropy, is_weak=is_weak)
            )
        return report

    def calculate_all(
        self, envs: Dict[str, Dict[str, str]]
    ) -> Dict[str, EntropyReport]:
        return {name: self.calculate(env, name) for name, env in envs.items()}
