"""Formatter for key inheritance reports."""
from typing import Optional
from envdiff.key_inheritance import InheritanceReport


class InheritanceFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_entry_row(self, entry) -> str:
        key_str = self._c(entry.key, "36")
        if not entry.is_overridden:
            status = self._c("inherited", "32")
            base = entry.base_value if entry.base_value is not None else self._c("(missing)", "33")
            return f"  {key_str}: {status}  base={base}"
        else:
            status = self._c("overridden", "33")
            parts = [f"  {key_str}: {status}"]
            parts.append(f"    base ({entry.base_value!r})")
            for env_name, val in entry.overrides.items():
                marker = self._c("*", "31") if val != entry.base_value else " "
                parts.append(f"    {marker} {env_name}: {val!r}")
            return "\n".join(parts)

    def format_report(self, report: InheritanceReport) -> str:
        lines = [
            self._c(f"Inheritance Report (base: {report.base_name})", "1"),
            "",
        ]
        if not report.entries:
            lines.append("  No keys found.")
            return "\n".join(lines)

        for entry in report.entries:
            lines.append(self._format_entry_row(entry))

        lines.append("")
        total = len(report.entries)
        n_inherited = len(report.inherited_keys)
        n_overridden = len(report.overridden_keys)
        lines.append(
            self._c("Summary", "1") + f": {total} keys — "
            + self._c(f"{n_inherited} inherited", "32") + ", "
            + self._c(f"{n_overridden} overridden", "33")
        )
        return "\n".join(lines)
