"""Format PatternReport results for CLI output."""
from __future__ import annotations

from typing import Dict

from envdiff.key_pattern import PatternReport


class PatternFormatter:
    def __init__(self, color: bool = True) -> None:
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def format_report(self, report: PatternReport) -> str:
        lines = []
        header = self._c(f"[{report.env_name}]", "1;34")
        lines.append(header)
        if not report.has_violations:
            lines.append(self._c("  ✔ All pattern checks passed.", "32"))
            return "\n".join(lines)
        for v in report.violations:
            label = self._c(v.key, "1;33")
            pattern = self._c(v.pattern_name, "36")
            value = self._c(repr(v.value), "31")
            lines.append(f"  ✘ {label}: expected {pattern}, got {value}")
        return "\n".join(lines)

    def format_all(self, reports: Dict[str, PatternReport]) -> str:
        if not reports:
            return self._c("No environments to check.", "33")
        sections = [self.format_report(r) for r in reports.values()]
        return "\n\n".join(sections)

    def format_summary(self, reports: Dict[str, PatternReport]) -> str:
        total = sum(len(r.violations) for r in reports.values())
        envs_affected = sum(1 for r in reports.values() if r.has_violations)
        if total == 0:
            return self._c("Pattern check summary: no violations found.", "32")
        return self._c(
            f"Pattern check summary: {total} violation(s) across {envs_affected} environment(s).",
            "31",
        )
