"""Detect duplicate keys within a single .env file."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateEntry:
    key: str
    values: List[str]
    line_numbers: List[int]

    def __str__(self) -> str:
        lines = ", ".join(str(n) for n in self.line_numbers)
        vals = ", ".join(repr(v) for v in self.values)
        return f"{self.key} (lines {lines}): {vals}"


@dataclass
class DuplicateReport:
    source: str
    duplicates: List[DuplicateEntry] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return len(self.duplicates) > 0

    @property
    def duplicate_keys(self) -> List[str]:
        return [d.key for d in self.duplicates]

    def __str__(self) -> str:
        if not self.has_duplicates:
            return f"{self.source}: no duplicate keys found."
        lines = [f"{self.source}: {len(self.duplicates)} duplicate key(s) found:"]
        for entry in self.duplicates:
            lines.append(f"  {entry}")
        return "\n".join(lines)


class DuplicateDetector:
    """Scan a raw .env file for duplicate key definitions."""

    def detect(self, source: str, raw_lines: List[str]) -> DuplicateReport:
        """Return a DuplicateReport for the given raw file lines."""
        seen: Dict[str, List[int]] = {}
        seen_values: Dict[str, List[str]] = {}

        for lineno, line in enumerate(raw_lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            stripped = stripped.removeprefix("export ").strip()
            if "=" not in stripped:
                continue
            key, _, value = stripped.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if not key:
                continue
            seen.setdefault(key, []).append(lineno)
            seen_values.setdefault(key, []).append(value)

        duplicates = [
            DuplicateEntry(key=k, values=seen_values[k], line_numbers=v)
            for k, v in seen.items()
            if len(v) > 1
        ]
        return DuplicateReport(source=source, duplicates=duplicates)
