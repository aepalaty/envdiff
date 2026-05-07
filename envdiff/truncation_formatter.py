from __future__ import annotations
from typing import Optional
from envdiff.key_truncation import TruncationReport, TruncationIssue


class TruncationFormatter:
    def __init__(self, use_color: bool = True) -> None:
        self.use_color = use_color

    def _c(self, text: str, code: str) -> str:
        if not self.use_color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_issue(self, issue: TruncationIssue) -> str:
        key_part = self._c(issue.key, "33")
        env_part = self._c(issue.env_name, "36")
        length_part = self._c(str(issue.value_length), "31")
        max_part = self._c(str(issue.max_length), "32")
        return (
            f"  {key_part} [{env_part}]: "
            f"length {length_part} > max {max_part}"
        )

    def format_report(self, report: TruncationReport) -> str:
        lines = []
        header = self._c("Truncation Check", "1;34")
        lines.append(header)
        lines.append("-" * 40)

        if not report.has_issues():
            lines.append(self._c("  No truncation issues found.", "32"))
            return "\n".join(lines)

        for key in report.affected_keys():
            lines.append(self._c(f"  {key}", "1"))
            for issue in report.issues:
                if issue.key == key:
                    lines.append(self._format_issue(issue))

        lines.append("")
        total = self._c(str(len(report.issues)), "31")
        lines.append(f"Total issues: {total}")
        return "\n".join(lines)
