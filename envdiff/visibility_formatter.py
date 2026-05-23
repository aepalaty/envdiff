from __future__ import annotations
from typing import Optional
from envdiff.key_visibility import VisibilityReport


VISIBILITY_COLORS = {
    "public": "\033[32m",
    "internal": "\033[33m",
    "private": "\033[31m",
}
RESET = "\033[0m"


class VisibilityFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        return f"{code}{text}{RESET}" if self.color else text

    def _label(self, visibility: str) -> str:
        color = VISIBILITY_COLORS.get(visibility, "")
        return self._c(f"[{visibility.upper():8}]", color)

    def format_report(self, report: VisibilityReport) -> str:
        if not report.entries:
            return "No keys found."

        lines = ["Key Visibility Report", "=" * 40]

        for section, getter in [
            ("Private", report.private_keys),
            ("Internal", report.internal_keys),
            ("Public", report.public_keys),
        ]:
            items = getter()
            if not items:
                continue
            lines.append(f"\n{section} ({len(items)})")
            for entry in items:
                label = self._label(entry.visibility)
                envs = ", ".join(entry.envs)
                lines.append(f"  {label} {entry.key}  ({envs})")

        lines.append("")
        lines.append(
            f"Total: {len(report.entries)} keys "
            f"| private={len(report.private_keys())} "
            f"| internal={len(report.internal_keys())} "
            f"| public={len(report.public_keys())}"
        )
        return "\n".join(lines)
