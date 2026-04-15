"""Detect encoding issues in .env file values (non-ASCII, null bytes, mixed line endings)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EncodingIssue:
    key: str
    env_name: str
    issue_type: str  # 'non_ascii', 'null_byte', 'control_char', 'mixed_line_ending'
    detail: str

    def __str__(self) -> str:
        return f"[{self.env_name}] {self.key}: {self.issue_type} — {self.detail}"


@dataclass
class EncodingReport:
    env_names: List[str]
    issues: List[EncodingIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def issues_for_env(self, env_name: str) -> List[EncodingIssue]:
        return [i for i in self.issues if i.env_name == env_name]

    def issues_for_key(self, key: str) -> List[EncodingIssue]:
        return [i for i in self.issues if i.key == key]


class EncodingChecker:
    """Check .env values for encoding anomalies."""

    def check(self, envs: Dict[str, Dict[str, str]]) -> EncodingReport:
        env_names = list(envs.keys())
        report = EncodingReport(env_names=env_names)

        for env_name, env in envs.items():
            for key, value in env.items():
                issues = self._check_value(key, env_name, value)
                report.issues.extend(issues)

        return report

    def _check_value(
        self, key: str, env_name: str, value: str
    ) -> List[EncodingIssue]:
        found: List[EncodingIssue] = []

        if "\x00" in value:
            found.append(
                EncodingIssue(key, env_name, "null_byte", "value contains null byte")
            )

        non_ascii = [c for c in value if ord(c) > 127]
        if non_ascii:
            sample = "".join(non_ascii[:5])
            found.append(
                EncodingIssue(
                    key,
                    env_name,
                    "non_ascii",
                    f"non-ASCII characters detected: {repr(sample)}",
                )
            )

        control_chars = [
            c for c in value if ord(c) < 32 and c not in ("\t", "\n", "\r")
        ]
        if control_chars:
            found.append(
                EncodingIssue(
                    key,
                    env_name,
                    "control_char",
                    f"{len(control_chars)} control character(s) found",
                )
            )

        if "\r\n" in value or ("\r" in value and "\n" in value):
            found.append(
                EncodingIssue(
                    key, env_name, "mixed_line_ending", "mixed CRLF/LF line endings"
                )
            )

        return found
