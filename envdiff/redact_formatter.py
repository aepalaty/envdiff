"""Formatter wrapper that redacts sensitive values before display."""

from __future__ import annotations

from typing import Dict

from envdiff.comparator import EnvDifference
from envdiff.formatter import DiffFormatter
from envdiff.redactor import Redactor


class RedactingFormatter:
    """Wraps DiffFormatter and redacts sensitive values in diff output."""

    def __init__(self, formatter: DiffFormatter, redactor: Redactor) -> None:
        self._formatter = formatter
        self._redactor = redactor

    def _redact_diff(self, diff: EnvDifference) -> EnvDifference:
        """Return a copy of EnvDifference with sensitive values masked."""
        redacted_mismatches: Dict[str, tuple] = {}
        for key, (base_val, other_val) in diff.mismatches.items():
            redacted_mismatches[key] = (
                self._redactor.redact(key, base_val),
                self._redactor.redact(key, other_val),
            )

        new_diff = EnvDifference(
            base_name=diff.base_name,
            other_name=diff.other_name,
        )
        new_diff.missing_in_other = diff.missing_in_other
        new_diff.missing_in_base = diff.missing_in_base
        new_diff.mismatches = redacted_mismatches
        return new_diff

    def format_difference(self, diff: EnvDifference) -> str:
        """Format a diff with sensitive values redacted."""
        return self._formatter.format_difference(self._redact_diff(diff))

    def format_summary(self, diffs: list[EnvDifference]) -> str:
        """Format a summary with sensitive values redacted."""
        redacted = [self._redact_diff(d) for d in diffs]
        return self._formatter.format_summary(redacted)
