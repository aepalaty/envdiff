"""Export diff results to various output formats (JSON, CSV, Markdown)."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from envdiff.comparator import EnvDifference


class DiffExporter:
    """Exports EnvDifference results to structured formats."""

    SUPPORTED_FORMATS = ("json", "csv", "markdown")

    def __init__(self, differences: List[EnvDifference]) -> None:
        self.differences = differences

    def to_json(self, indent: int = 2) -> str:
        """Serialize differences to a JSON string."""
        records = []
        for diff in self.differences:
            records.append({
                "baseline": diff.baseline_file,
                "other": diff.other_file,
                "missing_keys": sorted(diff.missing_keys),
                "extra_keys": sorted(diff.extra_keys),
                "mismatched_keys": sorted(diff.mismatched_keys),
            })
        return json.dumps(records, indent=indent)

    def to_csv(self) -> str:
        """Serialize differences to a CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["baseline", "other", "issue_type", "key"])
        for diff in self.differences:
            for key in sorted(diff.missing_keys):
                writer.writerow([diff.baseline_file, diff.other_file, "missing", key])
            for key in sorted(diff.extra_keys):
                writer.writerow([diff.baseline_file, diff.other_file, "extra", key])
            for key in sorted(diff.mismatched_keys):
                writer.writerow([diff.baseline_file, diff.other_file, "mismatch", key])
        return output.getvalue()

    def to_markdown(self) -> str:
        """Serialize differences to a Markdown table string."""
        lines = []
        for diff in self.differences:
            lines.append(f"## `{diff.baseline_file}` vs `{diff.other_file}`\n")
            lines.append("| Issue Type | Key |")
            lines.append("|------------|-----|")
            for key in sorted(diff.missing_keys):
                lines.append(f"| missing    | `{key}` |")
            for key in sorted(diff.extra_keys):
                lines.append(f"| extra      | `{key}` |")
            for key in sorted(diff.mismatched_keys):
                lines.append(f"| mismatch   | `{key}` |")
            lines.append("")
        return "\n".join(lines)

    def export(self, fmt: str) -> str:
        """Export to the given format name."""
        fmt = fmt.lower()
        if fmt == "json":
            return self.to_json()
        if fmt == "csv":
            return self.to_csv()
        if fmt == "markdown":
            return self.to_markdown()
        raise ValueError(
            f"Unsupported export format '{fmt}'. "
            f"Choose from: {', '.join(self.SUPPORTED_FORMATS)}"
        )
