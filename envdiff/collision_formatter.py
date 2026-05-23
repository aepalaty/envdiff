"""Formatter for key collision reports."""
from typing import Optional

from .key_collisions import CollisionReport


class CollisionFormatter:
    def __init__(self, color: bool = True):
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def format_report(self, report: CollisionReport) -> str:
        lines = []
        header = self._c("Key Collision Report", "1;35")
        lines.append(header)
        lines.append(
            self._c(f"Environments: {', '.join(report.env_names)}", "2")
        )
        lines.append("")

        if not report.has_collisions:
            lines.append(self._c("  No key collisions detected.", "32"))
            return "\n".join(lines)

        lines.append(
            self._c(
                f"  {len(report.entries)} collision(s) found:", "1;31"
            )
        )
        lines.append("")

        for entry in report.entries:
            canonical_label = self._c(entry.canonical, "1")
            lines.append(f"  {canonical_label}")
            variants_str = ", ".join(
                self._c(v, "33") for v in entry.variants
            )
            lines.append(f"    Variants : {variants_str}")
            envs_str = ", ".join(
                self._c(e, "36") for e in entry.envs
            )
            lines.append(f"    In envs  : {envs_str}")
            lines.append("")

        return "\n".join(lines).rstrip()

    def format_summary(self, report: CollisionReport) -> str:
        count = len(report.entries)
        if count == 0:
            return self._c("collisions: none", "32")
        return self._c(f"collisions: {count} key(s) affected", "1;31")
