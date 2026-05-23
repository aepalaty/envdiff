from typing import Optional
from envdiff.key_lineage import LineageReport


class LineageFormatter:
    def __init__(self, color: bool = True):
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_entry(self, key: str, report: LineageReport) -> str:
        entry = report.get(key)
        if entry is None:
            return ""
        lines = []
        header = self._c(f"  {key}", "1;36")
        lines.append(header)
        lines.append(
            f"    introduced: {self._c(entry.introduced_in or 'unknown', '33')}  "
            f"changes: {self._c(str(entry.change_count), '35')}  "
            f"current: {self._c(repr(entry.current_value), '32')}"
        )
        for event in entry.events:
            if event.changed_from is not None:
                lines.append(
                    f"    {self._c(event.snapshot_label, '90')}: "
                    f"{self._c(repr(event.changed_from), '31')} -> "
                    f"{self._c(repr(event.value), '32')}"
                )
        return "\n".join(lines)

    def format_report(self, report: LineageReport) -> str:
        if not report.all_keys:
            return self._c("No lineage data available.", "90")

        lines = [self._c("Key Lineage Report", "1;34"), ""]
        for key in report.all_keys:
            block = self._format_entry(key, report)
            if block:
                lines.append(block)
        lines.append("")
        lines.append(
            self._c(f"Total keys tracked: {len(report.all_keys)}", "1")
        )
        return "\n".join(lines)
