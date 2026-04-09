"""Format comparison results for display."""

from typing import List
from envdiff.comparator import EnvDifference


class DiffFormatter:
    """Format environment differences for console output."""

    # ANSI color codes
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def __init__(self, use_colors: bool = True):
        """Initialize formatter.
        
        Args:
            use_colors: Whether to use ANSI colors in output
        """
        self.use_colors = use_colors

    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled."""
        if not self.use_colors:
            return text
        return f"{color}{text}{self.RESET}"

    def format_difference(self, diff: EnvDifference) -> str:
        """Format a single difference for display.
        
        Args:
            diff: The EnvDifference to format
            
        Returns:
            Formatted string representation
        """
        if diff.difference_type == 'missing':
            key = self._colorize(diff.key, self.RED)
            value = self._colorize(diff.source_value, self.YELLOW)
            return f"  [-] {key} (expected: {value})"
        
        elif diff.difference_type == 'extra':
            key = self._colorize(diff.key, self.GREEN)
            value = self._colorize(diff.target_value, self.YELLOW)
            return f"  [+] {key} = {value}"
        
        elif diff.difference_type == 'value_mismatch':
            key = self._colorize(diff.key, self.YELLOW)
            source = self._colorize(diff.source_value, self.RED)
            target = self._colorize(diff.target_value, self.GREEN)
            return f"  [~] {key}\n      Source: {source}\n      Target: {target}"
        
        return str(diff)

    def format_summary(self, differences: List[EnvDifference]) -> str:
        """Format a summary of all differences.
        
        Args:
            differences: List of all differences found
            
        Returns:
            Formatted summary string
        """
        if not differences:
            success_msg = "✓ No differences found"
            return self._colorize(success_msg, self.GREEN)

        missing = [d for d in differences if d.difference_type == 'missing']
        extra = [d for d in differences if d.difference_type == 'extra']
        mismatched = [d for d in differences if d.difference_type == 'value_mismatch']

        summary_parts = []
        summary_parts.append(self._colorize(f"Found {len(differences)} difference(s):", self.BOLD))
        
        if missing:
            summary_parts.append(f"\n{self._colorize('Missing keys:', self.RED)}")
            for diff in missing:
                summary_parts.append(self.format_difference(diff))
        
        if extra:
            summary_parts.append(f"\n{self._colorize('Extra keys:', self.GREEN)}")
            for diff in extra:
                summary_parts.append(self.format_difference(diff))
        
        if mismatched:
            summary_parts.append(f"\n{self._colorize('Value mismatches:', self.YELLOW)}")
            for diff in mismatched:
                summary_parts.append(self.format_difference(diff))

        return "\n".join(summary_parts)
