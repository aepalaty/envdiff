"""Detect correlated keys — pairs that tend to appear together across environments."""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from itertools import combinations


@dataclass
class CorrelationEntry:
    key_a: str
    key_b: str
    co_occurrences: int
    total_envs: int

    @property
    def score(self) -> float:
        """Ratio of envs where both keys appear together."""
        if self.total_envs == 0:
            return 0.0
        return self.co_occurrences / self.total_envs

    def __str__(self) -> str:
        pct = int(self.score * 100)
        return f"{self.key_a} <-> {self.key_b}: {pct}% co-occurrence ({self.co_occurrences}/{self.total_envs})"


@dataclass
class CorrelationReport:
    entries: List[CorrelationEntry] = field(default_factory=list)
    env_names: List[str] = field(default_factory=list)

    @property
    def strong_pairs(self) -> List[CorrelationEntry]:
        """Pairs that always appear together."""
        return [e for e in self.entries if e.score == 1.0]

    @property
    def partial_pairs(self) -> List[CorrelationEntry]:
        """Pairs that sometimes appear together."""
        return [e for e in self.entries if 0.0 < e.score < 1.0]

    def top(self, n: int = 10) -> List[CorrelationEntry]:
        return sorted(self.entries, key=lambda e: e.score, reverse=True)[:n]


class KeyCorrelationCalculator:
    def calculate(
        self,
        envs: Dict[str, Dict[str, str]],
        min_score: float = 0.5,
    ) -> CorrelationReport:
        env_names = list(envs.keys())
        total = len(env_names)
        if total == 0:
            return CorrelationReport(env_names=env_names)

        all_keys: List[str] = sorted(
            {k for env in envs.values() for k in env}
        )

        co_count: Dict[Tuple[str, str], int] = {}
        for env in envs.values():
            present = set(env.keys())
            for a, b in combinations(sorted(present), 2):
                pair = (a, b)
                co_count[pair] = co_count.get(pair, 0) + 1

        entries = []
        for (a, b), count in co_count.items():
            score = count / total
            if score >= min_score:
                entries.append(
                    CorrelationEntry(
                        key_a=a,
                        key_b=b,
                        co_occurrences=count,
                        total_envs=total,
                    )
                )

        entries.sort(key=lambda e: e.score, reverse=True)
        return CorrelationReport(entries=entries, env_names=env_names)
