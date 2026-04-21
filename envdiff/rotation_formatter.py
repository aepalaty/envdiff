"""Formatter for key rotation reports."""
from envdiff.key_rotation import RotationReport, RotationEntry

_URGENCY_COLORS = {
    "critical": "\033[91m",
    "high": "\033[93m",
    "medium": "\033[33m",
    "ok": "\033[92m",
}
_RESET = "\033[0m"


class RotationFormatter:
    def __init__(self, use_color: bool = True):
        self._use_color = use_color

    def _c(self, text: str, color: str) -> str:
        if not self._use_color:
            return text
        return f"{color}{text}{_RESET}"

    def _urgency_label(self, urgency: str) -> str:
        color = _URGENCY_COLORS.get(urgency, "")
        label = urgency.upper()
        return self._c(f"[{label}]", color)

    def _format_entry(self, entry: RotationEntry) -> str:
        label = self._urgency_label(entry.urgency)
        overdue_note = ""
        if entry.is_overdue:
            overdue_by = entry.days_since_change - entry.recommended_max_days
            overdue_note = self._c(f" (+{overdue_by}d overdue)", "\033[91m")
        return (
            f"  {label} {entry.key} "
            f"[{entry.env_name}] "
            f"{entry.days_since_change}d / max {entry.recommended_max_days}d "
            f"(tier: {entry.sensitivity_tier}){overdue_note}"
        )

    def format_report(self, report: RotationReport) -> str:
        lines = [self._c("Key Rotation Status", "\033[1m"), ""]

        if not report.entries:
            lines.append("  No rotation data available.")
            return "\n".join(lines)

        overdue = report.overdue
        ok_entries = [e for e in report.entries if not e.is_overdue]

        if overdue:
            lines.append(self._c(f"Overdue ({len(overdue)} keys):", "\033[91m"))
            for entry in sorted(overdue, key=lambda e: e.days_since_change, reverse=True):
                lines.append(self._format_entry(entry))
            lines.append("")

        if ok_entries:
            lines.append(self._c(f"Up to date ({len(ok_entries)} keys):", "\033[92m"))
            for entry in sorted(ok_entries, key=lambda e: e.key):
                lines.append(self._format_entry(entry))

        lines.append("")
        lines.append(self.format_summary(report))
        return "\n".join(lines)

    def format_summary(self, report: RotationReport) -> str:
        total = len(report.entries)
        overdue = len(report.overdue)
        critical = len(report.by_urgency("critical"))
        ok = total - overdue
        summary = f"Total: {total}  OK: {ok}  Overdue: {overdue}"
        if critical:
            summary += self._c(f"  Critical: {critical}", "\033[91m")
        return summary
