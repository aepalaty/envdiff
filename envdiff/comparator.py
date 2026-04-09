"""Compare parsed environment files and identify differences."""

from typing import Dict, Set, List
from dataclasses import dataclass


@dataclass
class EnvDifference:
    """Represents a difference between environment files."""
    key: str
    difference_type: str  # 'missing', 'value_mismatch', 'extra'
    source_value: str = None
    target_value: str = None

    def __str__(self) -> str:
        if self.difference_type == 'missing':
            return f"Missing key: {self.key} (expected: {self.source_value})"
        elif self.difference_type == 'extra':
            return f"Extra key: {self.key} = {self.target_value}"
        elif self.difference_type == 'value_mismatch':
            return f"Value mismatch: {self.key}\n  Source: {self.source_value}\n  Target: {self.target_value}"
        return f"Unknown difference for {self.key}"


class EnvComparator:
    """Compare two parsed environment dictionaries."""

    def __init__(self, source: Dict[str, str], target: Dict[str, str]):
        """Initialize comparator with source and target environments.
        
        Args:
            source: The reference/baseline environment dict
            target: The environment dict to compare against source
        """
        self.source = source
        self.target = target
        self._differences: List[EnvDifference] = []

    def compare(self) -> List[EnvDifference]:
        """Compare source and target environments.
        
        Returns:
            List of EnvDifference objects describing all differences
        """
        self._differences = []
        source_keys = set(self.source.keys())
        target_keys = set(self.target.keys())

        # Find missing keys (in source but not in target)
        missing_keys = source_keys - target_keys
        for key in sorted(missing_keys):
            self._differences.append(
                EnvDifference(
                    key=key,
                    difference_type='missing',
                    source_value=self.source[key]
                )
            )

        # Find extra keys (in target but not in source)
        extra_keys = target_keys - source_keys
        for key in sorted(extra_keys):
            self._differences.append(
                EnvDifference(
                    key=key,
                    difference_type='extra',
                    target_value=self.target[key]
                )
            )

        # Find value mismatches (in both but different values)
        common_keys = source_keys & target_keys
        for key in sorted(common_keys):
            if self.source[key] != self.target[key]:
                self._differences.append(
                    EnvDifference(
                        key=key,
                        difference_type='value_mismatch',
                        source_value=self.source[key],
                        target_value=self.target[key]
                    )
                )

        return self._differences

    def get_differences(self) -> List[EnvDifference]:
        """Get the list of differences from the last comparison."""
        return self._differences

    def has_differences(self) -> bool:
        """Check if any differences were found."""
        return len(self._differences) > 0
