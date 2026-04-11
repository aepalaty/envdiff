"""Formats KeyUsageReport for terminal output."""

from __future__ import annotations

from typing import Optional

from envdiff.key_usage import KeyUsageReport


class UsageFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def format_report(self, report: KeyUsageReport, top_n: int = 5) -> str:
        lines = []
        lines.append(self._c(f"Key Usage Report ({report.total_keys} unique keys)", "1"))
        lines.append("")

        lines.append(self._c("Most used keys:", "36"))
        for rec in report.most_common(top_n):
            envs = ", ".join(rec.seen_in)
            lines.append(
                f"  {self._c(rec.key, '32')}  (count={rec.occurrence_count}, envs=[{envs}])"
            )

        lines.append("")
        lines.append(self._c("Least used keys:", "33"))
        for rec in report.least_common(top_n):
            envs = ", ".join(rec.seen_in)
            lines.append(
                f"  {self._c(rec.key, '31')}  (count={rec.occurrence_count}, envs=[{envs}])"
            )

        return "\n".join(lines)

    def format_summary(self, report: KeyUsageReport) -> str:
        most = report.most_common(1)
        least = report.least_common(1)
        parts = [f"Total unique keys: {report.total_keys}"]
        if most:
            parts.append(f"Most common: {most[0].key} ({most[0].occurrence_count}x)")
        if least:
            parts.append(f"Least common: {least[0].key} ({least[0].occurrence_count}x)")
        return " | ".join(parts)
