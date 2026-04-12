"""Annotate env keys with metadata: source file, line number, and value presence."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class KeyAnnotation:
    key: str
    value: Optional[str]
    source: str
    line_number: int
    has_value: bool

    def __str__(self) -> str:
        status = "set" if self.has_value else "empty"
        return f"{self.key} [{status}] @ {self.source}:{self.line_number}"


@dataclass
class AnnotationReport:
    env_name: str
    annotations: List[KeyAnnotation] = field(default_factory=list)

    @property
    def total_keys(self) -> int:
        return len(self.annotations)

    @property
    def empty_keys(self) -> List[KeyAnnotation]:
        return [a for a in self.annotations if not a.has_value]

    @property
    def populated_keys(self) -> List[KeyAnnotation]:
        return [a for a in self.annotations if a.has_value]

    def by_key(self, key: str) -> Optional[KeyAnnotation]:
        for ann in self.annotations:
            if ann.key == key:
                return ann
        return None


class KeyAnnotator:
    """Annotate keys from a raw env file, capturing line numbers and value presence."""

    def annotate(self, source: str, raw_lines: List[str]) -> AnnotationReport:
        report = AnnotationReport(env_name=source)
        for lineno, line in enumerate(raw_lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("export "):
                stripped = stripped[len("export "):].strip()
            if "=" not in stripped:
                continue
            key, _, raw_value = stripped.partition("=")
            key = key.strip()
            raw_value = raw_value.strip().strip('"').strip("'")
            annotation = KeyAnnotation(
                key=key,
                value=raw_value if raw_value else None,
                source=source,
                line_number=lineno,
                has_value=bool(raw_value),
            )
            report.annotations.append(annotation)
        return report

    def annotate_file(self, path: str) -> AnnotationReport:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        return self.annotate(source=path, raw_lines=lines)
