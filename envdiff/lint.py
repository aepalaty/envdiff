"""Linting rules for .env files — detect suspicious or invalid entries."""

from dataclasses import dataclass, field
from typing import List, Dict
import re


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str = "warning"  # "warning" or "error"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def __str__(self) -> str:
        if self.is_clean:
            return "No lint issues found."
        lines = [str(issue) for issue in self.issues]
        return "\n".join(lines)


class EnvLinter:
    """Applies a set of lint rules to a parsed env dictionary."""

    # Keys that should never be empty
    SENSITIVE_PATTERNS = re.compile(
        r"(password|secret|token|api_key|private_key)", re.IGNORECASE
    )
    VALID_KEY_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")

    def __init__(self, allow_lowercase: bool = False):
        self.allow_lowercase = allow_lowercase

    def lint(self, env: Dict[str, str]) -> LintResult:
        result = LintResult()
        for key, value in env.items():
            self._check_key_format(key, result)
            self._check_empty_sensitive(key, value, result)
            self._check_whitespace_value(key, value, result)
            self._check_placeholder_value(key, value, result)
        return result

    def _check_key_format(self, key: str, result: LintResult) -> None:
        if not self.allow_lowercase and not self.VALID_KEY_PATTERN.match(key):
            result.issues.append(
                LintIssue(key, "Key should be uppercase with underscores only.", "warning")
            )

    def _check_empty_sensitive(self, key: str, value: str, result: LintResult) -> None:
        if self.SENSITIVE_PATTERNS.search(key) and value.strip() == "":
            result.issues.append(
                LintIssue(key, "Sensitive key has an empty value.", "error")
            )

    def _check_whitespace_value(self, key: str, value: str, result: LintResult) -> None:
        if value != value.strip() and value.strip() != "":
            result.issues.append(
                LintIssue(key, "Value has leading or trailing whitespace.", "warning")
            )

    def _check_placeholder_value(self, key: str, value: str, result: LintResult) -> None:
        placeholders = {"TODO", "CHANGEME", "REPLACE_ME", "YOUR_VALUE_HERE", "<value>"}
        if value.upper() in {p.upper() for p in placeholders}:
            result.issues.append(
                LintIssue(key, f"Value appears to be a placeholder: '{value}'.", "warning")
            )
