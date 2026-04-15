"""Formatter for OutlierReport output."""

from typing import Optional
from envdiff.key_outliers import OutlierReport, OutlierEntry


class OutlierFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_entry(self, entry: OutlierEntry) -> str:
        lines = []
        key_label = self._c(entry.key, "1;33")  # bold yellow
        common_label = self._c(repr(entry.common_value), "32")  # green
        lines.append(f"  {key_label}  (majority value: {common_label})")
        for env, val in entry.outlier_envs.items():
            env_label = self._c(env, "36")  # cyan
            val_label = self._c(repr(val), "31")  # red
            lines.append(f"    {env_label}: {val_label}")
        return "\n".join(lines)

    def format_report(self, report: OutlierReport) -> str:
        lines = []
        header = self._c("Outlier Key Report", "1;37")
        envs_label = ", ".join(report.env_names)
        lines.append(f"{header}  [{envs_label}]")
        lines.append("")

        if not report.has_outliers:
            lines.append(
                self._c("  No outliers detected — all keys share consistent values.", "32")
            )
            return "\n".join(lines)

        lines.append(
            self._c(f"  {len(report.entries)} outlier(s) found:", "1;31")
        )
        lines.append("")
        for entry in report.entries:
            lines.append(self._format_entry(entry))
            lines.append("")

        return "\n".join(lines).rstrip()

    def format_summary(self, report: OutlierReport) -> str:
        count = len(report.entries)
        if count == 0:
            return self._c("outliers: none", "32")
        return self._c(f"outliers: {count} key(s) deviate from majority", "1;31")
