from __future__ import annotations
from typing import Optional
from envdiff.key_ownership import OwnershipReport, OwnershipEntry


class OwnershipFormatter:
    def __init__(self, use_color: bool = True) -> None:
        self._use_color = use_color

    def _c(self, text: str, code: str) -> str:
        if not self._use_color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_entry_row(self, entry: OwnershipEntry) -> str:
        key_str = self._c(entry.key, "36")
        if entry.is_unowned:
            tag = self._c("UNOWNED", "31")
            return f"  {key_str}  [{tag}]"
        parts: list[str] = []
        if entry.owner:
            parts.append(f"owner: {self._c(entry.owner, '32')}")
        if entry.team:
            parts.append(f"team: {self._c(entry.team, '33')}")
        if entry.contact:
            parts.append(f"contact: {entry.contact}")
        return f"  {key_str}  " + "  ".join(parts)

    def format_report(self, report: OwnershipReport) -> str:
        lines: list[str] = []
        lines.append(self._c("Key Ownership", "1"))
        lines.append("-" * 40)
        if not report.entries:
            lines.append("  No keys found.")
            return "\n".join(lines)
        for entry in report.entries:
            lines.append(self._format_entry_row(entry))
        lines.append("")
        total = len(report.entries)
        owned = len(report.owned_keys)
        unowned = len(report.unowned_keys)
        lines.append(
            f"  Total: {total}  "
            + self._c(f"Owned: {owned}", "32")
            + "  "
            + (self._c(f"Unowned: {unowned}", "31") if unowned else f"Unowned: {unowned}")
        )
        return "\n".join(lines)
