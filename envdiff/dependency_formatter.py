from __future__ import annotations
from typing import Optional
from envdiff.key_dependencies import DependencyReport


class DependencyFormatter:
    def __init__(self, color: bool = True) -> None:
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def format_report(self, report: DependencyReport) -> str:
        lines = []
        title = self._c("Key Dependency Check", "1;36")
        lines.append(f"\n{title}")
        lines.append(self._c("=" * 40, "36"))

        if not report.has_violations:
            lines.append(self._c("  No dependency violations found.", "32"))
            return "\n".join(lines)

        for env_name in report.env_names:
            env_violations = report.violations_for_env(env_name)
            if not env_violations:
                continue
            lines.append(self._c(f"  {env_name}", "1;33"))
            for v in env_violations:
                key_str = self._c(v.key, "33")
                req_str = self._c(v.requires, "31")
                lines.append(f"    {key_str} requires {req_str}")

        lines.append("")
        total = len(report.violations)
        summary = self._c(f"  {total} violation(s) detected.", "31")
        lines.append(summary)
        return "\n".join(lines)

    def format_summary(self, report: DependencyReport) -> str:
        if not report.has_violations:
            return self._c("dependencies: ok", "32")
        n = len(report.violations)
        return self._c(f"dependencies: {n} violation(s)", "31")
