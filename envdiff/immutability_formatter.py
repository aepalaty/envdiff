from typing import Optional
from envdiff.key_immutability import ImmutabilityReport


class ImmutabilityFormatter:
    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def format_report(self, report: ImmutabilityReport) -> str:
        lines = []
        header = self._c("Immutability Check", "1;36")
        lines.append(header)
        lines.append("-" * 40)

        if not report.has_issues():
            lines.append(self._c("  No immutability violations found.", "32"))
            return "\n".join(lines)

        for key in report.affected_keys():
            key_issues = report.issues_for_key(key)
            lines.append(self._c(f"  {key}", "1;33"))
            for issue in key_issues:
                env_label = self._c(issue.env_name, "36")
                snap_label = self._c(issue.snapshot_label, "35")
                old_val = self._c(repr(issue.old_value), "31")
                new_val = self._c(repr(issue.new_value), "33")
                lines.append(
                    f"    [{env_label}] @ {snap_label}: {old_val} -> {new_val}"
                )

        lines.append("")
        total = self._c(str(len(report.issues)), "1;31")
        lines.append(f"  Total violations: {total}")
        return "\n".join(lines)

    def format_summary(self, report: ImmutabilityReport) -> str:
        if not report.has_issues():
            return self._c("immutability: ok", "32")
        n = len(report.issues)
        return self._c(f"immutability: {n} violation(s)", "1;31")
