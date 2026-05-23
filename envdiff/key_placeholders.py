"""Detect keys whose values are placeholder/stub values rather than real configuration."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

_PLACEHOLDER_PATTERNS: Set[str] = {
    "changeme",
    "placeholder",
    "your_value_here",
    "todo",
    "fixme",
    "example",
    "replace_me",
    "insert_here",
    "xxxx",
    "1234",
    "0000",
    "none",
    "null",
    "undefined",
    "n/a",
    "na",
    "tbd",
    "fill_in",
    "<your",
    "<replace",
    "<insert",
}


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    if not normalized:
        return False
    for pattern in _PLACEHOLDER_PATTERNS:
        if pattern in normalized:
            return True
    return False


@dataclass
class PlaceholderIssue:
    env_name: str
    key: str
    value: str

    def __str__(self) -> str:
        return f"{self.env_name}: {self.key}={self.value!r} looks like a placeholder"


@dataclass
class PlaceholderReport:
    env_names: List[str]
    issues: List[PlaceholderIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    def issues_for_env(self, env_name: str) -> List[PlaceholderIssue]:
        return [i for i in self.issues if i.env_name == env_name]

    @property
    def affected_keys(self) -> List[str]:
        return sorted({i.key for i in self.issues})


class PlaceholderChecker:
    """Scan one or more envs for keys that contain placeholder values."""

    def calculate(self, envs: Dict[str, Dict[str, str]]) -> PlaceholderReport:
        env_names = list(envs.keys())
        report = PlaceholderReport(env_names=env_names)
        for env_name, env in envs.items():
            for key, value in env.items():
                if _is_placeholder(value):
                    report.issues.append(
                        PlaceholderIssue(env_name=env_name, key=key, value=value)
                    )
        return report
