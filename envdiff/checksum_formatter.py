"""Formatter for ChecksumReport output."""
from __future__ import annotations

from typing import Optional

from envdiff.key_checksum import ChecksumReport, ChecksumMismatch


class ChecksumFormatter:
    def __init__(self, use_color: bool = True) -> None:
        self._use_color = use_color

    def _c(self, text: str, code: str) -> str:
        if not self._use_color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_mismatch(self, mismatch: ChecksumMismatch) -> str:
        lines = []
        label = self._c(mismatch.key, "1;33")
        hashes = mismatch.unique_hashes()
        lines.append(f"  {label}  ({len(hashes)} distinct checksums)")
        for entry in mismatch.entries:
            short = entry.value_hash[:16]
            env_label = self._c(entry.env_name, "36")
            lines.append(f"    {env_label}: {short}... (len={entry.value_length})")
        return "\n".join(lines)

    def format_report(
        self,
        report: ChecksumReport,
        show_clean: bool = False,
    ) -> str:
        lines = []
        header = self._c("Checksum Comparison", "1;34")
        envs = ", ".join(report.env_names)
        lines.append(f"{header}  [{envs}]")
        lines.append("")

        mismatches = report.mismatches()
        if not mismatches:
            lines.append(self._c("  All checksums match across environments.", "32"))
        else:
            lines.append(
                self._c(f"  {len(mismatches)} key(s) with checksum mismatches:", "1;31")
            )
            lines.append("")
            for m in mismatches:
                lines.append(self._format_mismatch(m))
                lines.append("")

        if show_clean:
            clean_keys = [
                k for k, ents in report.entries.items()
                if len({e.value_hash for e in ents}) == 1
            ]
            if clean_keys:
                lines.append(self._c(f"  {len(clean_keys)} key(s) with matching checksums.", "32"))

        return "\n".join(lines)
