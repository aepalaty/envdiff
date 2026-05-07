from __future__ import annotations
from typing import Optional
from envdiff.key_whitespace import WhitespaceReport, WhitespaceIssue


class WhitespaceFormatter:
    def __init__(self, color: bool = True):
        self._color = color

    def _c(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_issue(self, issue: WhitespaceIssue) -> str:
        kinds = []
        if issue.leading:
            kinds.append(self._c("leading", "33"))
        if issue.trailing:
            kinds.append(self._c("trailing", "33"))
        if issue.internal:
            kinds.append(self._c("internal", "35"))
        label = ", ".join(kinds)
        repr_val = repr(issue.value)
        return f"  {self._c(issue.key, '36')} ({issue.env_name}): {label} — {repr_val}"

    def format_report(self, report: WhitespaceReport) -> str:
        lines = []
        header = self._c("Whitespace Issues", "1")
        lines.append(header)
        lines.append("-" * 40)
        if not report.has_issues():
            lines.append(self._c("No whitespace issues found.", "32"))
            return "\n".join(lines)
        for env_name in report.env_names:
            env_issues = report.issues_for_env(env_name)
            if not env_issues:
                continue
            lines.append(self._c(f"[{env_name}]", "1;34"))
            for issue in env_issues:
                lines.append(self._format_issue(issue))
        lines.append("")
        total = len(report.issues)
        lines.append(self._c(f"Total issues: {total}", "33" if total > 0 else "32"))
        return "\n".join(lines)

    def format_summary(self, report: WhitespaceReport) -> str:
        total = len(report.issues)
        affected = len(report.affected_keys())
        if total == 0:
            return self._c("whitespace: clean", "32")
        return self._c(f"whitespace: {total} issue(s) across {affected} key(s)", "33")
