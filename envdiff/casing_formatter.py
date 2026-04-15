"""Format CasingReport for terminal output."""
from __future__ import annotations

from typing import Optional

from envdiff.key_casing import CasingReport


class CasingFormatter:
    def __init__(self, color: bool = True) -> None:
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def format_report(self, report: CasingReport) -> str:
        lines = []
        title = self._c("Key Casing Report", "1;34")
        lines.append(title)
        lines.append(
            f"Dominant convention: {self._c(report.dominant_convention or 'N/A', '36')}"
        )
        lines.append("")

        if not report.has_issues:
            lines.append(self._c("✔ All keys follow a consistent casing convention.", "32"))
            return "\n".join(lines)

        lines.append(
            self._c(f"{len(report.issues)} casing issue(s) found:", "33")
        )
        lines.append("")

        for env_name in report.env_names:
            env_issues = report.issues_for_env(env_name)
            if not env_issues:
                continue
            lines.append(self._c(f"  [{env_name}]", "1"))
            for issue in env_issues:
                key_str = self._c(issue.key, "33")
                detected_str = self._c(issue.detected, "31")
                expected_str = self._c(issue.expected, "32")
                lines.append(
                    f"    {key_str}: {detected_str} → expected {expected_str}"
                )
            lines.append("")

        return "\n".join(lines).rstrip()

    def format_summary(self, report: CasingReport) -> str:
        if not report.has_issues:
            return self._c("Casing: OK", "32")
        return self._c(
            f"Casing: {len(report.issues)} issue(s) across {len(report.env_names)} env(s)",
            "33",
        )
