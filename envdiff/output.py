"""Output helpers — write reports to stdout or a file."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from envdiff.reporter import Report, ReportGenerator


SUPPORTED_FORMATS = ("text", "json")


class OutputWriter:
    """Renders and writes a Report in the requested format."""

    def __init__(
        self,
        generator: ReportGenerator,
        fmt: str = "text",
        output_path: Optional[str] = None,
    ) -> None:
        if fmt not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}"
            )
        self.generator = generator
        self.fmt = fmt
        self.output_path = Path(output_path) if output_path else None

    def render(self, report: Report) -> str:
        """Convert a Report to a string in the configured format."""
        if self.fmt == "json":
            return self.generator.to_json(report)
        return self.generator.to_text(report)

    def write(self, report: Report) -> None:
        """Write rendered report to a file or stdout."""
        content = self.render(report)
        if self.output_path is not None:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(content, encoding="utf-8")
        else:
            sys.stdout.write(content)
            if not content.endswith("\n"):
                sys.stdout.write("\n")

    @staticmethod
    def exit_code(report: Report) -> int:
        """Return shell exit code: 1 when issues found, 0 otherwise."""
        return 1 if report.has_issues() else 0
