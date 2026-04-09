"""Report generation for envdiff comparisons."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from envdiff.comparator import EnvDifference


@dataclass
class Report:
    """Structured report of an env comparison."""

    baseline: str
    targets: List[str]
    missing_keys: Dict[str, List[str]]
    extra_keys: Dict[str, List[str]]
    mismatched_keys: Dict[str, List[str]]
    total_issues: int

    def has_issues(self) -> bool:
        return self.total_issues > 0


class ReportGenerator:
    """Generates reports from EnvDifference objects."""

    def __init__(self, baseline_path: str, target_paths: List[str]) -> None:
        self.baseline_path = baseline_path
        self.target_paths = target_paths

    def generate(self, differences: List[EnvDifference]) -> Report:
        """Build a Report from a list of EnvDifference results."""
        missing: Dict[str, List[str]] = {}
        extra: Dict[str, List[str]] = {}
        mismatched: Dict[str, List[str]] = {}
        total = 0

        for diff in differences:
            target = diff.target_name
            if diff.missing_keys:
                missing[target] = sorted(diff.missing_keys)
                total += len(diff.missing_keys)
            if diff.extra_keys:
                extra[target] = sorted(diff.extra_keys)
                total += len(diff.extra_keys)
            if diff.mismatched_keys:
                mismatched[target] = sorted(diff.mismatched_keys.keys())
                total += len(diff.mismatched_keys)

        return Report(
            baseline=self.baseline_path,
            targets=self.target_paths,
            missing_keys=missing,
            extra_keys=extra,
            mismatched_keys=mismatched,
            total_issues=total,
        )

    def to_json(self, report: Report, indent: int = 2) -> str:
        """Serialize a Report to a JSON string."""
        return json.dumps(asdict(report), indent=indent)

    def to_text(self, report: Report) -> str:
        """Serialize a Report to a human-readable text block."""
        lines: List[str] = []
        lines.append(f"Baseline: {report.baseline}")
        lines.append(f"Targets : {', '.join(report.targets)}")
        lines.append(f"Total issues: {report.total_issues}")
        lines.append("")

        for target in report.targets:
            issues: List[str] = []
            for key in report.missing_keys.get(target, []):
                issues.append(f"  MISSING   {key}")
            for key in report.extra_keys.get(target, []):
                issues.append(f"  EXTRA     {key}")
            for key in report.mismatched_keys.get(target, []):
                issues.append(f"  MISMATCH  {key}")
            if issues:
                lines.append(f"[{target}]")
                lines.extend(issues)
                lines.append("")

        return "\n".join(lines)
