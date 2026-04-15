from typing import Optional
from envdiff.key_lifecycle import LifecycleReport, LifecycleEntry

_STATUS_SYMBOLS = {
    "added": "+",
    "removed": "-",
    "modified": "~",
    "unchanged": "=",
}

_STATUS_COLORS = {
    "added": "\033[32m",
    "removed": "\033[31m",
    "modified": "\033[33m",
    "unchanged": "\033[90m",
}

_RESET = "\033[0m"


class LifecycleFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        return f"{code}{text}{_RESET}" if self.color else text

    def _format_event_line(self, label: str, status: str, value: Optional[str]) -> str:
        symbol = _STATUS_SYMBOLS.get(status, "?")
        color = _STATUS_COLORS.get(status, "")
        parts = [f"  {self._c(symbol, color)} [{label}] {status}"]
        if value is not None and status != "removed":
            parts.append(f"= {value}")
        return " ".join(parts)

    def _format_entry(self, entry: LifecycleEntry) -> str:
        lines = [f"{entry.key}  ({entry.change_count} changes)"]
        for event in entry.events:
            lines.append(self._format_event_line(event.snapshot_label, event.status, event.value))
        return "\n".join(lines)

    def format_report(self, report: LifecycleReport) -> str:
        if not report.entries:
            return "No lifecycle data available."
        sections = [self._format_entry(e) for e in report.entries]
        return "\n\n".join(sections)

    def format_summary(self, report: LifecycleReport) -> str:
        total = len(report.entries)
        changed = sum(1 for e in report.entries if e.change_count > 0)
        stable = total - changed
        lines = [
            f"Total keys tracked : {total}",
            f"Keys with changes  : {self._c(str(changed), '\033[33m')}",
            f"Stable keys        : {self._c(str(stable), '\033[32m')}",
        ]
        return "\n".join(lines)
