from __future__ import annotations
from typing import List

from envdiff.key_tagging import TagReport


class TaggingFormatter:
    def __init__(self, color: bool = True) -> None:
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _tag_label(self, tag: str) -> str:
        colors = {
            "database": "34",
            "auth": "31",
            "cache": "33",
            "storage": "36",
            "email": "35",
            "observability": "32",
            "feature": "37",
        }
        code = colors.get(tag, "90")
        return self._c(f"[{tag}]", code)

    def format_report(self, report: TagReport) -> str:
        lines: List[str] = []
        header = f"Key Tags — {report.env_name}" if report.env_name else "Key Tags"
        lines.append(self._c(header, "1"))
        lines.append(self._c("-" * 40, "90"))

        if not report.entries:
            lines.append(self._c("  No keys found.", "90"))
            return "\n".join(lines)

        all_tags = sorted(report.all_tags())
        for tag in all_tags:
            keys = report.keys_for_tag(tag)
            lines.append(f"  {self._tag_label(tag)}")
            for k in sorted(keys):
                lines.append(f"    {self._c(k, '37')}")

        untagged = report.untagged_keys()
        if untagged:
            lines.append(f"  {self._c('[untagged]', '90')}")
            for k in sorted(untagged):
                lines.append(f"    {self._c(k, '90')}")

        lines.append("")
        lines.append(
            self._c(
                f"Total: {len(report.entries)} keys, "
                f"{len(all_tags)} tag(s), "
                f"{len(untagged)} untagged",
                "90",
            )
        )
        return "\n".join(lines)
