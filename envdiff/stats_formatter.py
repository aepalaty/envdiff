"""Format EnvStatsReport for terminal or plain-text output."""

from envdiff.key_stats import EnvStatsReport, KeyStats


COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_GREEN = "\033[32m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"


class StatsFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"{code}{text}{COLOR_RESET}"

    def _format_key_row(self, stats: KeyStats) -> str:
        pct = f"{stats.coverage * 100:.0f}%".rjust(4)
        drift_marker = self._c(" ~", COLOR_YELLOW) if stats.has_value_drift else "  "
        if stats.coverage == 1.0:
            pct_colored = self._c(pct, COLOR_GREEN)
        elif stats.coverage == 0.0:
            pct_colored = self._c(pct, COLOR_RED)
        else:
            pct_colored = self._c(pct, COLOR_YELLOW)
        missing = ", ".join(stats.missing_from) if stats.missing_from else "-"
        return f"  {stats.key:<40} {pct_colored}{drift_marker}  missing: {missing}"

    def format_report(self, report: EnvStatsReport) -> str:
        lines = []
        header = self._c("Key Coverage Report", COLOR_BOLD)
        lines.append(header)
        lines.append(f"Environments: {', '.join(report.env_names)}")
        lines.append("")

        if not report.key_stats:
            lines.append("  (no keys found)")
            return "\n".join(lines)

        lines.append(f"  {'KEY':<40} {'COV':>4}    MISSING FROM")
        lines.append("  " + "-" * 70)
        for key, stats in report.key_stats.items():
            lines.append(self._format_key_row(stats))

        lines.append("")
        lines.append(self._c("Summary", COLOR_BOLD))
        lines.append(report.summary())
        return "\n".join(lines)

    def format_drifted(self, report: EnvStatsReport) -> str:
        drifted = report.drifted_keys
        if not drifted:
            return self._c("No value drift detected.", COLOR_GREEN)
        lines = [self._c(f"Value drift detected in {len(drifted)} key(s):", COLOR_YELLOW)]
        for key in drifted:
            stats = report.key_stats[key]
            vals = ", ".join(repr(v) for v in sorted(stats.unique_values))
            lines.append(f"  {key}: {vals}")
        return "\n".join(lines)
