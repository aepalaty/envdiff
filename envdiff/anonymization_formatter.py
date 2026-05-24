from __future__ import annotations
from typing import Dict
from envdiff.key_anonymization import AnonymizationReport


class AnonymizationFormatter:
    def __init__(self, color: bool = True) -> None:
        self.color = color

    def _c(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.color else text

    def _format_entry_row(self, key: str, value: str, sensitive: bool) -> str:
        label = self._c("[sensitive]", "33") if sensitive else self._c("[plain]", "90")
        key_str = self._c(key, "36")
        return f"  {key_str} {label} = {value}"

    def format_report(self, report: AnonymizationReport) -> str:
        lines = [
            self._c(f"Anonymization Report: {report.env_name}", "1"),
            f"  Sensitive keys : {len(report.sensitive_keys)}",
            f"  Plain keys     : {len(report.plain_keys)}",
            "",
        ]
        for entry in sorted(report.entries, key=lambda e: e.key):
            lines.append(self._format_entry_row(
                entry.key, entry.anonymized_value, entry.is_sensitive
            ))
        return "\n".join(lines)

    def format_all(self, reports: Dict[str, AnonymizationReport]) -> str:
        if not reports:
            return self._c("No environments to display.", "90")
        sections = [self.format_report(r) for r in reports.values()]
        return "\n\n".join(sections)

    def format_summary(self, reports: Dict[str, AnonymizationReport]) -> str:
        total_sensitive = sum(len(r.sensitive_keys) for r in reports.values())
        total_plain = sum(len(r.plain_keys) for r in reports.values())
        lines = [
            self._c("Anonymization Summary", "1"),
            f"  Environments   : {len(reports)}",
            f"  Sensitive keys : {self._c(str(total_sensitive), '33')}",
            f"  Plain keys     : {total_plain}",
        ]
        return "\n".join(lines)
