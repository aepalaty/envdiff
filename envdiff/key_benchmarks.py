from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BenchmarkEntry:
    key: str
    env_name: str
    value_length: int
    is_sensitive: bool
    score: float  # 0.0 to 1.0, higher is better

    def __str__(self) -> str:
        rating = "good" if self.score >= 0.7 else ("fair" if self.score >= 0.4 else "poor")
        return f"{self.key} ({self.env_name}): score={self.score:.2f} [{rating}]"


@dataclass
class BenchmarkReport:
    env_names: List[str]
    entries: List[BenchmarkEntry] = field(default_factory=list)

    def average_score(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e.score for e in self.entries) / len(self.entries)

    def poor_keys(self) -> List[BenchmarkEntry]:
        return [e for e in self.entries if e.score < 0.4]

    def good_keys(self) -> List[BenchmarkEntry]:
        return [e for e in self.entries if e.score >= 0.7]

    def entries_for_env(self, env_name: str) -> List[BenchmarkEntry]:
        return [e for e in self.entries if e.env_name == env_name]


SENSITIVE_PATTERNS = ("password", "secret", "token", "key", "api", "auth", "private")


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(p in lower for p in SENSITIVE_PATTERNS)


def _score_entry(key: str, value: str) -> float:
    score = 1.0
    if not value:
        return 0.0
    sensitive = _is_sensitive(key)
    if sensitive and len(value) < 16:
        score -= 0.4
    if value.lower() in ("true", "false", "yes", "no", "1", "0"):
        score -= 0.1
    if value == value.lower() and sensitive:
        score -= 0.2
    if len(value) > 64:
        score -= 0.05
    return max(0.0, min(1.0, score))


class BenchmarkCalculator:
    def calculate(self, envs: Dict[str, Dict[str, str]]) -> BenchmarkReport:
        env_names = list(envs.keys())
        report = BenchmarkReport(env_names=env_names)
        for env_name, env in envs.items():
            for key, value in env.items():
                sensitive = _is_sensitive(key)
                score = _score_entry(key, value)
                entry = BenchmarkEntry(
                    key=key,
                    env_name=env_name,
                    value_length=len(value),
                    is_sensitive=sensitive,
                    score=score,
                )
                report.entries.append(entry)
        return report
