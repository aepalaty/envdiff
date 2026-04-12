"""Formats KeyGrouper reports for terminal output."""

from typing import Optional

from envdiff.key_grouper import GroupReport


class GrouperFormatter:
    """Renders a GroupReport as human-readable text, with optional color."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    DIM = "\033[2m"

    def __init__(self, color: bool = True):
        self.color = color

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"{code}{text}{self.RESET}"

    def format_report(self, report: GroupReport, env_name: Optional[str] = None) -> str:
        lines = []

        header = "Key Groups"
        if env_name:
            header += f" — {env_name}"
        lines.append(self._c(header, self.BOLD))
        lines.append("")

        if not report.groups:
            lines.append(self._c("  No groups found.", self.DIM))
        else:
            for name in report.group_names:
                group = report.groups[name]
                label = self._c(f"[{name}]", self.CYAN)
                count = self._c(f"({len(group)} keys)", self.DIM)
                lines.append(f"  {label} {count}")
                for key in sorted(group.keys):
                    lines.append(f"    {self._c(key, self.YELLOW)}")

        if report.ungrouped:
            lines.append("")
            lines.append(self._c("  Ungrouped:", self.DIM))
            for key in sorted(report.ungrouped):
                lines.append(f"    {key}")

        lines.append("")
        lines.append(
            self._c(
                f"  {len(report.groups)} group(s), {report.total_grouped} grouped key(s), "
                f"{len(report.ungrouped)} ungrouped.",
                self.DIM,
            )
        )
        return "\n".join(lines)
