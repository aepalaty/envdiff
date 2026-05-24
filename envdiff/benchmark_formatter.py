from __future__ import annotations
from typing import Optional
from envdiff.key_benchmarks import BenchmarkReport, BenchmarkEntry


class BenchmarkFormatter:
    def __init__(self, use_color: bool = True):
        self._use_color = use_color

    def _c(self, text: str, code: str) -> str:
        if not self._use_color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _score_color(self, score: float) -> str:
        if score >= 0.7:
            return self._c(f"{score:.2f}", "32")  # green
        if score >= 0.4:
            return self._c(f"{score:.2f}", "33")  # yellow
        return self._c(f"{score:.2f}", "31")  # red

    def _format_entry_row(self, entry: BenchmarkEntry) -> str:
        sensitive_flag = self._c("[sensitive]", "35") if entry.is_sensitive else ""
        score_str = self._score_color(entry.score)
        parts = [f"  {entry.key:<35} score={score_str}  len={entry.value_length}"]
        if sensitive_flag:
            parts.append(f"  {sensitive_flag}")
        return "".join(parts)

    def format_report(self, report: BenchmarkReport) -> str:
        lines = []
        header = self._c("Key Benchmark Report", "1;36")
        lines.append(header)
        lines.append("=" * 50)

        avg = report.average_score()
        avg_str = self._score_color(avg)
        lines.append(f"Average score: {avg_str}  ({len(report.entries)} entries across {len(report.env_names)} env(s))")
        lines.append("")

        for env_name in report.env_names:
            lines.append(self._c(f"[{env_name}]", "1;34"))
            entries = report.entries_for_env(env_name)
            if not entries:
                lines.append("  (no keys)")
            else:
                for entry in sorted(entries, key=lambda e: e.score):
                    lines.append(self._format_entry_row(entry))
            lines.append("")

        poor = report.poor_keys()
        if poor:
            lines.append(self._c(f"Poor keys ({len(poor)}):", "31"))
            for e in poor:
                lines.append(f"  {e.key} in {e.env_name}")

        return "\n".join(lines)
