from __future__ import annotations
from typing import Optional
from envdiff.key_balance import BalanceReport, BalanceEntry


class BalanceFormatter:
    def __init__(self, color: bool = True):
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _ratio_color(self, ratio: float) -> str:
        if ratio >= 1.0:
            return "32"   # green
        if ratio >= 0.5:
            return "33"   # yellow
        return "31"       # red

    def _format_bar(self, ratio: float, width: int = 20) -> str:
        filled = round(ratio * width)
        bar = "#" * filled + "-" * (width - filled)
        return f"[{bar}]"

    def _format_entry(self, entry: BalanceEntry) -> str:
        ratio = entry.balance_ratio
        color = self._ratio_color(ratio)
        bar = self._format_bar(ratio)
        label = self._c(f"{ratio:5.0%}", color)
        bar_colored = self._c(bar, color)
        absent = ""
        if entry.absent_from:
            absent = self._c(f"  missing: {', '.join(entry.absent_from)}", "90")
        return f"  {entry.key:<40} {label} {bar_colored}{absent}"

    def format_report(self, report: BalanceReport) -> str:
        lines = []
        header = self._c("Key Balance Report", "1;36")
        lines.append(header)
        lines.append(self._c(f"Environments: {', '.join(report.env_names)}", "90"))
        lines.append(self._c(f"Average balance: {report.average_balance:.0%}", "37"))
        lines.append("")

        if not report.entries:
            lines.append(self._c("  No keys found.", "90"))
            return "\n".join(lines)

        for entry in report.entries:
            lines.append(self._format_entry(entry))

        lines.append("")
        unbalanced = report.unbalanced_keys
        if unbalanced:
            msg = f"{len(unbalanced)} key(s) are not fully balanced across all environments."
            lines.append(self._c(msg, "33"))
        else:
            lines.append(self._c("All keys are balanced across all environments.", "32"))

        return "\n".join(lines)
