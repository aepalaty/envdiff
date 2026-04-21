"""Formats VolatilityReport for terminal output."""
from __future__ import annotations
from envdiff.key_volatility import VolatilityReport, VolatilityEntry


class VolatilityFormatter:
    def __init__(self, color: bool = True):
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _ratio_color(self, entry: VolatilityEntry) -> str:
        ratio = entry.volatility_ratio
        if ratio >= 0.75:
            return "31"  # red
        if ratio >= 0.5:
            return "33"  # yellow
        return "32"  # green

    def _format_bar(self, ratio: float, width: int = 20) -> str:
        filled = round(ratio * width)
        bar = "#" * filled + "-" * (width - filled)
        return f"[{bar}]"

    def _format_entry(self, entry: VolatilityEntry) -> str:
        pct = f"{entry.volatility_ratio * 100:5.1f}%"
        bar = self._format_bar(entry.volatility_ratio)
        colored_pct = self._c(pct, self._ratio_color(entry))
        flag = self._c(" VOLATILE", "31;1") if entry.is_volatile else ""
        return f"  {entry.key:<40} {colored_pct} {bar} (changes: {entry.change_count}){flag}"

    def format_report(self, report: VolatilityReport) -> str:
        if not report.entries:
            return self._c("No volatility data available.", "90")

        lines = [self._c("Key Volatility Report", "1"), ""]
        lines.append(
            f"  {'KEY':<40} {'RATIO':>7}  {'BAR':<22} CHANGES"
        )
        lines.append("  " + "-" * 78)

        for entry in sorted(report.entries, key=lambda e: -e.volatility_ratio):
            lines.append(self._format_entry(entry))

        lines.append("")
        avg = report.average_volatility * 100
        lines.append(f"  Average volatility : {self._c(f'{avg:.1f}%', '36')}")
        lines.append(f"  Volatile keys      : {self._c(str(len(report.volatile_keys)), '33')}")
        lines.append(f"  Stable keys        : {self._c(str(len(report.stable_keys)), '32')}")
        return "\n".join(lines)
