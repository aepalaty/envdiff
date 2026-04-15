"""Detect keys whose values match or violate expected patterns (e.g. URLs, UUIDs, ports)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Built-in named patterns
BUILTIN_PATTERNS: Dict[str, str] = {
    "url": r"^https?://[^\s]+$",
    "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    "port": r"^\d{1,5}$",
    "email": r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    "semver": r"^\d+\.\d+\.\d+$",
    "boolean": r"^(true|false|1|0|yes|no)$",
}


@dataclass
class PatternViolation:
    key: str
    value: str
    expected_pattern: str
    pattern_name: str

    def __str__(self) -> str:
        return (
            f"{self.key}: value {self.value!r} does not match "
            f"expected pattern '{self.pattern_name}' ({self.expected_pattern})"
        )


@dataclass
class PatternReport:
    env_name: str
    violations: List[PatternViolation] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return len(self.violations) > 0

    @property
    def violation_keys(self) -> List[str]:
        return [v.key for v in self.violations]


class KeyPatternChecker:
    """Check env values against named or custom regex patterns."""

    def __init__(
        self,
        rules: Optional[Dict[str, str]] = None,
        extra_patterns: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Args:
            rules: mapping of key -> pattern_name (e.g. {"PORT": "port"}).
            extra_patterns: additional named patterns beyond BUILTIN_PATTERNS.
        """
        self._rules: Dict[str, str] = rules or {}
        self._patterns: Dict[str, str] = {**BUILTIN_PATTERNS, **(extra_patterns or {})}

    def check(self, env: Dict[str, str], env_name: str = "env") -> PatternReport:
        report = PatternReport(env_name=env_name)
        for key, pattern_name in self._rules.items():
            if key not in env:
                continue
            value = env[key]
            regex = self._patterns.get(pattern_name)
            if regex is None:
                continue
            if not re.match(regex, value, re.IGNORECASE):
                report.violations.append(
                    PatternViolation(
                        key=key,
                        value=value,
                        expected_pattern=regex,
                        pattern_name=pattern_name,
                    )
                )
        return report

    def check_all(
        self, envs: Dict[str, Dict[str, str]]
    ) -> Dict[str, PatternReport]:
        return {name: self.check(env, env_name=name) for name, env in envs.items()}
