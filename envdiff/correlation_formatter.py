"""Formatter for key correlation reports."""
from typing import Optional
from envdiff.key_correlation import CorrelationReport, CorrelationEntry


class CorrelationFormatter:
    def __init__(self, color: bool = True) -> None:
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_entry(self, entry: CorrelationEntry) -> str:
        pct = int(entry.score * 100)
        bar_len = pct // 5
        bar = self._c("█" * bar_len, "36") + self._c("░" * (20 - bar_len), "90")
        score_str = self._c(f"{pct:>3}%", "32" if pct == 100 else "33" if pct >= 70 else "37")
        pair = self._c(entry.key_a, "97") + self._c(" <-> ", "90") + self._c(entry.key_b, "97")
        return f"  {score_str} {bar}  {pair}  ({entry.co_occurrences}/{entry.total_envs})"

    def format_report(
        self,
        report: CorrelationReport,
        top: Optional[int] = None,
        show_partial: bool = True,
    ) -> str:
        lines = []
        header = self._c("Key Correlation Report", "1;97")
        env_list = ", ".join(report.env_names) or "(none)"
        lines.append(f"{header}  [{self._c(env_list, '90')}]")
        lines.append("")

        entries = report.top(top) if top else report.entries
        if not entries:
            lines.append(self._c("  No correlated key pairs found.", "90"))
            return "\n".join(lines)

        strong = [e for e in entries if e.score == 1.0]
        partial = [e for e in entries if 0.0 < e.score < 1.0]

        if strong:
            lines.append(self._c("Always together (100%):", "1;32"))
            for entry in strong:
                lines.append(self._format_entry(entry))
            lines.append("")

        if show_partial and partial:
            lines.append(self._c("Partially correlated:", "1;33"))
            for entry in partial:
                lines.append(self._format_entry(entry))
            lines.append("")

        total_pairs = len(entries)
        strong_count = len(strong)
        lines.append(
            self._c(f"Total pairs: {total_pairs}", "90")
            + "  "
            + self._c(f"Always together: {strong_count}", "32")
        )
        return "\n".join(lines)
