"""Formatter for key age reports."""

from envdiff.key_age import AgeReport, AgeEntry


class AgeFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _staleness_color(self, entry: AgeEntry) -> str:
        if entry.days_since_change > 180:
            return "31"  # red
        if entry.days_since_change > 90:
            return "33"  # yellow
        return "32"  # green

    def _format_entry(self, entry: AgeEntry) -> str:
        days_str = self._c(
            f"{entry.days_since_change}d",
            self._staleness_color(entry)
        )
        stale_flag = self._c(" [STALE]", "31") if entry.is_stale else ""
        return (
            f"  {self._c(entry.key, '36'):<40} "
            f"last changed: {days_str} ago  "
            f"changes: {entry.change_count}{stale_flag}"
        )

    def format_report(self, report: AgeReport) -> str:
        if not report.entries:
            return self._c("No key age data available.", "90")

        lines = [self._c("Key Age Report", "1"), ""]

        stale = report.stale_keys
        if stale:
            lines.append(self._c(f"  {len(stale)} stale key(s) (unchanged > 90 days):", "33"))
        else:
            lines.append(self._c("  All keys are recently updated.", "32"))

        lines.append(f"  Avg days since change: {report.average_days_since_change:.1f}")
        lines.append("")
        lines.append(self._c("  Keys:", "1"))

        for entry in report.entries:
            lines.append(self._format_entry(entry))

        return "\n".join(lines)
