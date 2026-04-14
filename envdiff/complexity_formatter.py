"""Formats ComplexityReport objects for terminal output."""
from __future__ import annotations
from typing import Dict
from envdiff.key_complexity import ComplexityReport


class ComplexityFormatter:
    def __init__(self, color: bool = True) -> None:
        self._color = color

    def _c(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self._color else text

    def _score_color(self, score: float) -> str:
        if score >= 0.7:
            return self._c(f"{score:.2f}", "31")   # red
        if score >= 0.4:
            return self._c(f"{score:.2f}", "33")   # yellow
        return self._c(f"{score:.2f}", "32")        # green

    def _format_entry_row(self, key: str, depth: int, length: int,
                          namespaced: bool, score: float) -> str:
        ns = self._c("yes", "36") if namespaced else "no"
        score_str = self._score_color(score)
        return f"  {key:<40} depth={depth}  len={length:<3}  ns={ns:<3}  score={score_str}"

    def format_report(self, report: ComplexityReport) -> str:
        lines = [
            self._c(f"Complexity: {report.env_name}", "1"),
            f"  Average score : {self._score_color(report.average_score)}",
            f"  Total keys    : {len(report.entries)}",
            f"  Deeply nested : {len(report.deeply_nested)} (depth ≥ 3)",
            "",
            self._c("  Key                                      depth  len  ns   score", "2"),
        ]
        for e in report.most_complex:
            lines.append(
                self._format_entry_row(
                    e.key, e.depth, e.length, e.is_namespaced, e.score
                )
            )
        return "\n".join(lines)

    def format_all(self, reports: Dict[str, ComplexityReport]) -> str:
        if not reports:
            return self._c("No complexity data available.", "33")
        sections = [self.format_report(r) for r in reports.values()]
        return "\n\n".join(sections)
