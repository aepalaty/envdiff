"""Formatter for obsolete key reports."""
from typing import Optional

from .key_obsolete import ObsoleteReport


class ObsoleteFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_entry_row(self, entry) -> str:
        key_str = self._c(entry.key, "33")
        absent_str = self._c(", ".join(entry.absent_from), "31")
        present_str = self._c(", ".join(entry.present_in), "32")
        return f"  {key_str}\n    missing from : {absent_str}\n    present in   : {present_str}"

    def format_report(self, report: ObsoleteReport, max_entries: Optional[int] = None) -> str:
        lines = []
        header = self._c("Obsolete / Partial Keys", "1;36")
        lines.append(header)
        lines.append(self._c(f"Environments: {', '.join(report.env_names)}", "90"))
        lines.append("")

        if not report.has_obsolete:
            lines.append(self._c("  No obsolete keys detected.", "32"))
            return "\n".join(lines)

        entries = report.entries
        if max_entries is not None:
            entries = entries[:max_entries]

        for entry in entries:
            lines.append(self._format_entry_row(entry))

        truncated = len(report.entries) - len(entries)
        if truncated > 0:
            lines.append(self._c(f"  ... and {truncated} more", "90"))

        lines.append("")
        summary = self._c(f"{len(report.entries)} key(s) not present in all environments.", "33")
        lines.append(summary)
        return "\n".join(lines)
