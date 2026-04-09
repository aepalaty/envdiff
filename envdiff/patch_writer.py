"""Writes patch files that can be applied to bring one .env in sync with another."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from envdiff.comparator import EnvDifference


class PatchWriter:
    """Generates and writes a patch script to reconcile environment differences."""

    def __init__(self, difference: EnvDifference, target_name: str = "target") -> None:
        self.difference = difference
        self.target_name = target_name

    def render(self) -> str:
        """Return the patch content as a shell-compatible export block."""
        lines: list[str] = [
            f"# envdiff patch — add/update keys in: {self.target_name}",
            "",
        ]

        if self.difference.missing_keys:
            lines.append("# Keys missing from target (present in baseline)")
            for key in sorted(self.difference.missing_keys):
                value = self.difference.baseline_values.get(key, "")
                lines.append(f"export {key}={self._quote(value)}")
            lines.append("")

        if self.difference.mismatched_keys:
            lines.append("# Keys with differing values (baseline value used)")
            for key in sorted(self.difference.mismatched_keys):
                value = self.difference.baseline_values.get(key, "")
                lines.append(f"export {key}={self._quote(value)}")
            lines.append("")

        if not self.difference.missing_keys and not self.difference.mismatched_keys:
            lines.append("# No changes required — environments are in sync.")

        return "\n".join(lines)

    def write(self, path: Optional[str] = None) -> Path:
        """Write the patch to *path*, defaulting to a generated filename."""
        out = Path(path) if path else Path(self.default_filename())
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.render(), encoding="utf-8")
        return out

    def default_filename(self) -> str:
        safe = self.target_name.replace(os.sep, "_").replace(" ", "_")
        return f"envdiff_patch_{safe}.sh"

    @staticmethod
    def _quote(value: str) -> str:
        """Wrap *value* in double quotes, escaping embedded double quotes."""
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
