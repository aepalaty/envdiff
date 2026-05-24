from __future__ import annotations
from envdiff.key_maturity import MaturityReport, MaturityEntry

_LABEL_COLORS = {
    "stable": "\033[32m",
    "established": "\033[36m",
    "emerging": "\033[33m",
    "transient": "\033[31m",
}
_RESET = "\033[0m"


class MaturityFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if self.color:
            return f"{code}{text}{_RESET}"
        return text

    def _label_color(self, label: str) -> str:
        return _LABEL_COLORS.get(label, "")

    def _format_entry(self, entry: MaturityEntry) -> str:
        colored_label = self._c(entry.label.upper(), self._label_color(entry.label))
        ratio_pct = f"{entry.maturity_ratio * 100:.0f}%"
        return f"  {entry.key:<40} {colored_label:<20} {ratio_pct:>6}  ({entry.appearances}/{entry.snapshot_count})"

    def format_report(self, report: MaturityReport) -> str:
        if not report.entries:
            return "No maturity data available."

        lines = ["Key Maturity Report", "=" * 60]
        lines.append(f"  {'KEY':<40} {'MATURITY':<20} {'RATIO':>6}  APPEARANCES")
        lines.append("-" * 60)

        for entry in report.entries:
            lines.append(self._format_entry(entry))

        lines.append("")
        lines.append(f"Stable:      {len(report.stable_keys)}")
        lines.append(f"Established: {len([e for e in report.entries if e.label == 'established'])}")
        lines.append(f"Emerging:    {len(report.emerging_keys)}")
        lines.append(f"Transient:   {len(report.transient_keys)}")

        return "\n".join(lines)
