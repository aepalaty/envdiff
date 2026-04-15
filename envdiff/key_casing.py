"""Detect inconsistent casing conventions across env keys."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _detect_convention(key: str) -> str:
    """Return the casing convention of a key."""
    if re.match(r'^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$', key):
        return "SCREAMING_SNAKE"
    if re.match(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$', key):
        return "snake_case"
    if re.match(r'^[a-z][a-zA-Z0-9]*$', key):
        return "camelCase"
    if re.match(r'^[A-Z][a-zA-Z0-9]*$', key):
        return "PascalCase"
    if re.match(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$', key):
        return "kebab-case"
    return "mixed"


@dataclass
class CasingIssue:
    env_name: str
    key: str
    detected: str
    expected: str

    def __str__(self) -> str:
        return (
            f"[{self.env_name}] {self.key!r}: "
            f"expected {self.expected}, got {self.detected}"
        )


@dataclass
class CasingReport:
    env_names: List[str]
    issues: List[CasingIssue] = field(default_factory=list)
    dominant_convention: Optional[str] = None

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def issues_for_env(self, env_name: str) -> List[CasingIssue]:
        return [i for i in self.issues if i.env_name == env_name]


class CasingChecker:
    """Check env keys for consistent casing conventions."""

    def calculate(
        self,
        envs: Dict[str, Dict[str, str]],
        expected_convention: Optional[str] = None,
    ) -> CasingReport:
        env_names = list(envs.keys())
        all_keys = [k for env in envs.values() for k in env]

        if expected_convention is None:
            convention_counts: Dict[str, int] = {}
            for key in all_keys:
                c = _detect_convention(key)
                convention_counts[c] = convention_counts.get(c, 0) + 1
            dominant = max(convention_counts, key=convention_counts.get) if convention_counts else "SCREAMING_SNAKE"
        else:
            dominant = expected_convention

        issues: List[CasingIssue] = []
        for env_name, env in envs.items():
            for key in env:
                detected = _detect_convention(key)
                if detected != dominant:
                    issues.append(CasingIssue(
                        env_name=env_name,
                        key=key,
                        detected=detected,
                        expected=dominant,
                    ))

        return CasingReport(
            env_names=env_names,
            issues=issues,
            dominant_convention=dominant,
        )
