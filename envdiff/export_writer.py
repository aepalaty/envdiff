"""Write exported diff output to a file or stdout."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

from envdiff.comparator import EnvDifference
from envdiff.exporter import DiffExporter

_FORMAT_EXTENSIONS = {
    "json": ".json",
    "csv": ".csv",
    "markdown": ".md",
}


class ExportWriter:
    """Coordinates exporting diff results to a file or stdout."""

    def __init__(
        self,
        differences: List[EnvDifference],
        fmt: str,
        output_path: Optional[str] = None,
    ) -> None:
        if fmt not in DiffExporter.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unknown format '{fmt}'. "
                f"Supported: {', '.join(DiffExporter.SUPPORTED_FORMATS)}"
            )
        self.exporter = DiffExporter(differences)
        self.fmt = fmt
        self.output_path = Path(output_path) if output_path else None

    def write(self) -> None:
        """Render the export and write to the configured destination."""
        content = self.exporter.export(self.fmt)
        if self.output_path is None:
            sys.stdout.write(content)
            if not content.endswith("\n"):
                sys.stdout.write("\n")
        else:
            self._ensure_parent(self.output_path)
            self.output_path.write_text(content, encoding="utf-8")

    @staticmethod
    def _ensure_parent(path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default_filename(cls, fmt: str) -> str:
        """Return a sensible default output filename for the given format."""
        ext = _FORMAT_EXTENSIONS.get(fmt, ".txt")
        return f"envdiff_report{ext}"

    @classmethod
    def from_default_path(cls, differences: List[EnvDifference], fmt: str) -> "ExportWriter":
        """Create an ExportWriter using the default filename for the given format.

        This is a convenience constructor for cases where the caller wants to
        write to a file but has not specified an explicit output path.

        Args:
            differences: The list of env differences to export.
            fmt: The export format (e.g. 'json', 'csv', 'markdown').

        Returns:
            An ExportWriter configured to write to the default filename.
        """
        return cls(differences, fmt, output_path=cls.default_filename(fmt))
