"""Format SensitivityReport for terminal output."""
from __future__ import annotations
from typing import Optional
from envdiff.key_sensitivity import SensitivityReport, SensitivityEntry

_TIER_COLORS = {
    "CRITICAL": "\033[91m",  # bright red
    "HIGH": "\033[93m",      # yellow
    "MEDIUM": "\033[94m",    # blue
    "LOW": "\033[37m",       # light grey
}
_RESET = "\033[0m"
_BOLD = "\033[1m"


class SensitivityFormatter:
    def __init__(self, color: bool = True) -> None:
        self.color = color

    def _c(self, text: str, code: str) -> str:
        return f"{code}{text}{_RESET}" if self.color else text

    def _tier_label(self, tier: str) -> str:
        color = _TIER_COLORS.get(tier, "")
        label = f"[{tier:<8}]"
        return self._c(label, color)

    def _format_entry(self, entry: SensitivityEntry) -> str:
        line = f"  {self._tier_label(entry.tier)} {entry.key}"
        if entry.envs_with_plain_value:
            envs_str = ", ".join(entry.envs_with_plain_value)
            warning = self._c(f" ⚠ plain value in: {envs_str}", _TIER_COLORS["CRITICAL"])
            line += warning
        return line

    def format_report(self, report: SensitivityReport) -> str:
        lines = [self._c("Key Sensitivity Report", _BOLD), ""]
        tiers = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        for tier in tiers:
            group = [e for e in report.entries if e.tier == tier]
            if not group:
                continue
            lines.append(self._c(f"{tier} ({len(group)})", _TIER_COLORS.get(tier, "")))
            for entry in group:
                lines.append(self._format_entry(entry))
            lines.append("")

        total = len(report.entries)
        plain_count = sum(1 for e in report.entries if e.envs_with_plain_value)
        lines.append(f"Total keys: {total}  |  Plain secrets detected: {plain_count}")
        return "\n".join(lines)

    def format_summary(self, report: SensitivityReport) -> str:
        critical = len(report.critical())
        high = len(report.high())
        plain = sum(1 for e in report.entries if e.envs_with_plain_value)
        parts = []
        if critical:
            parts.append(self._c(f"{critical} CRITICAL", _TIER_COLORS["CRITICAL"]))
        if high:
            parts.append(self._c(f"{high} HIGH", _TIER_COLORS["HIGH"]))
        if plain:
            parts.append(self._c(f"{plain} plain-text secrets", _TIER_COLORS["CRITICAL"]))
        if not parts:
            return self._c("No high-sensitivity issues found.", "\033[92m")
        return "Sensitivity: " + ", ".join(parts)
