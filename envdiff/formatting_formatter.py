from typing import Optional
from envdiff.key_formatting import FormattingReport


class FormattingFormatter:
    def __init__(self, use_color: bool = True):
        self._use_color = use_color

    def _c(self, text: str, code: str) -> str:
        if not self._use_color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _type_color(self, issue_type: str) -> str:
        colors = {
            "trailing_whitespace": "33",
            "inconsistent_quotes": "31",
            "unnecessary_quotes": "36",
        }
        return colors.get(issue_type, "37")

    def _format_issue_row(self, issue) -> str:
        label = self._c(issue.issue_type, self._type_color(issue.issue_type))
        env = self._c(issue.env_name, "90")
        key = self._c(issue.key, "1")
        return f"  {env}  {key}  [{label}]  {issue.detail}"

    def format_report(self, report: FormattingReport) -> str:
        lines = []
        header = self._c("Formatting Issues", "1;34")
        lines.append(header)
        lines.append(self._c("-" * 50, "90"))

        if not report.has_issues():
            lines.append(self._c("  No formatting issues found.", "32"))
            return "\n".join(lines)

        by_type: dict = {}
        for issue in report.issues:
            by_type.setdefault(issue.issue_type, []).append(issue)

        for issue_type, issues in sorted(by_type.items()):
            lines.append(f"\n{self._c(issue_type.replace('_', ' ').title(), '1')} ({len(issues)}):")
            for issue in issues:
                lines.append(self._format_issue_row(issue))

        total = len(report.issues)
        lines.append("")
        lines.append(self._c(f"Total: {total} formatting issue(s) across {len(report.env_names)} env(s).", "33"))
        return "\n".join(lines)

    def format_summary(self, report: FormattingReport) -> str:
        if not report.has_issues():
            return self._c("formatting: OK", "32")
        return self._c(f"formatting: {len(report.issues)} issue(s)", "31")
