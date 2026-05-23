from __future__ import annotations
from typing import List
from envdiff.key_freshness import FreshnessReport, FreshnessEntry


class FreshnessFormatter:
    def __init__(self, color: bool = True):
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_entry(self, entry: FreshnessEntry) -> str:
        status_label = self._c("STALE", "31") if entry.missing_in_latest else self._c("fresh", "32")
        last = entry.last_seen.strftime("%Y-%m-%d") if entry.last_seen else "never"
        return (
            f"  {self._c(entry.key, '36'):<40} "
            f"{status_label:<20} "
            f"seen in {entry.snapshot_count} snapshot(s), last: {last}"
        )

    def format_report(self, report: FreshnessReport) -> str:
        lines: List[str] = []
        lines.append(self._c("=== Key Freshness Report ===", "1"))
        lines.append(f"Environments: {', '.join(report.env_names)}")
        lines.append("")

        if not report.entries:
            lines.append("  No keys found.")
            return "\n".join(lines)

        stale = report.stale_keys
        fresh = report.fresh_keys

        if stale:
            lines.append(self._c(f"Stale keys ({len(stale)}):", "31"))
            for entry in stale:
                lines.append(self._format_entry(entry))
            lines.append("")

        if fresh:
            lines.append(self._c(f"Fresh keys ({len(fresh)}):", "32"))
            for entry in fresh:
                lines.append(self._format_entry(entry))
            lines.append("")

        summary = (
            f"Summary: {len(fresh)} fresh, "
            f"{self._c(str(len(stale)), '31' if stale else '32')} stale"
        )
        lines.append(summary)
        return "\n".join(lines)
