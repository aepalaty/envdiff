from typing import Optional
from envdiff.key_coverage import CoverageReport, CoverageEntry


class CoverageFormatter:
    def __init__(self, color: bool = True):
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _coverage_color(self, ratio: float) -> str:
        if ratio >= 1.0:
            return "32"  # green
        elif ratio >= 0.5:
            return "33"  # yellow
        return "31"  # red

    def _format_bar(self, ratio: float, width: int = 20) -> str:
        filled = int(ratio * width)
        bar = "█" * filled + "░" * (width - filled)
        color = self._coverage_color(ratio)
        return self._c(bar, color)

    def _format_entry(self, entry: CoverageEntry) -> str:
        pct = f"{int(entry.coverage_ratio * 100):>3}%"
        color = self._coverage_color(entry.coverage_ratio)
        pct_colored = self._c(pct, color)
        bar = self._format_bar(entry.coverage_ratio)
        absent = ""
        if entry.absent_from:
            absent = self._c(f"  missing: {', '.join(entry.absent_from)}", "90")
        return f"  {entry.key:<40} {pct_colored} {bar}{absent}"

    def format_report(self, report: CoverageReport) -> str:
        lines = []
        header = self._c("Key Coverage Report", "1;36")
        lines.append(header)
        lines.append(self._c(f"Environments: {', '.join(report.env_names)}", "90"))
        lines.append("")

        avg_pct = int(report.average_coverage * 100)
        avg_color = self._coverage_color(report.average_coverage)
        lines.append(f"  Average coverage: {self._c(str(avg_pct) + '%', avg_color)}")
        lines.append(f"  Universal keys:   {len(report.universal_keys)}/{report.total_keys}")
        lines.append("")

        if report.universal_keys:
            lines.append(self._c("  Universal (all envs):", "32"))
            for entry in report.universal_keys:
                lines.append(self._format_entry(entry))
            lines.append("")

        if report.partial_keys:
            lines.append(self._c("  Partial coverage:", "33"))
            for entry in sorted(report.partial_keys, key=lambda e: e.coverage_ratio):
                lines.append(self._format_entry(entry))

        return "\n".join(lines)
