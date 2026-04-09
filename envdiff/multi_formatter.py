"""Formatter for multi-file diff results."""

from typing import List

from envdiff.differ import MultiDiffResult, PairwiseDiff
from envdiff.formatter import DiffFormatter


class MultiDiffFormatter:
    """Formats a MultiDiffResult for terminal output."""

    HEADER = "\033[1;34m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def __init__(self, color: bool = True) -> None:
        self.color = color
        self._base_formatter = DiffFormatter(color=color)

    def _header(self, left: str, right: str) -> str:
        line = f"--- {left}  vs  {right} ---"
        if self.color:
            return f"{self.HEADER}{self.BOLD}{line}{self.RESET}"
        return line

    def format_all(self, result: MultiDiffResult) -> str:
        if not result.pairwise:
            return "No comparisons to display."

        sections: List[str] = []
        for pd in result.pairwise:
            header = self._header(pd.left_path, pd.right_path)
            body = self._base_formatter.format_difference(pd.difference)
            sections.append(f"{header}\n{body}")

        return "\n\n".join(sections)

    def format_summary(self, result: MultiDiffResult) -> str:
        total_pairs = len(result.pairwise)
        pairs_with_issues = sum(1 for pd in result.pairwise if pd.has_issues)

        lines = [
            f"Compared {len(result.paths)} file(s) across {total_pairs} pair(s).",
            f"Pairs with differences: {pairs_with_issues}/{total_pairs}",
        ]

        if result.has_issues:
            unique_keys = result.all_keys
            lines.append(f"Unique differing keys: {len(unique_keys)}")
        else:
            lines.append("All files are in sync.")

        return "\n".join(lines)
