"""Filter and query utilities for MultiDiffResult and PairwiseDiff objects."""

from typing import List, Optional, Set
from envdiff.differ import MultiDiffResult, PairwiseDiff


class DiffFilter:
    """Applies filters to a MultiDiffResult to narrow down relevant diffs."""

    def __init__(self, result: MultiDiffResult):
        self._result = result

    def only_missing(self) -> List[PairwiseDiff]:
        """Return only diffs that have missing keys."""
        return [
            d for d in self._result.diffs
            if d.difference.missing_keys
        ]

    def only_mismatched(self) -> List[PairwiseDiff]:
        """Return only diffs that have value mismatches."""
        return [
            d for d in self._result.diffs
            if d.difference.mismatched_keys
        ]

    def only_extra(self) -> List[PairwiseDiff]:
        """Return only diffs that have extra keys not in baseline."""
        return [
            d for d in self._result.diffs
            if d.difference.extra_keys
        ]

    def with_issues(self) -> List[PairwiseDiff]:
        """Return only diffs that have any kind of issue."""
        return [d for d in self._result.diffs if d.has_issues]

    def for_key(self, key: str) -> List[PairwiseDiff]:
        """Return diffs where the given key appears in any issue category."""
        matches = []
        for d in self._result.diffs:
            diff = d.difference
            if (
                key in diff.missing_keys
                or key in diff.extra_keys
                or key in diff.mismatched_keys
            ):
                matches.append(d)
        return matches

    def keys_always_missing(self) -> Set[str]:
        """Return keys that are missing in every diff (universal gaps)."""
        if not self._result.diffs:
            return set()
        missing_sets = [
            set(d.difference.missing_keys) for d in self._result.diffs
        ]
        return missing_sets[0].intersection(*missing_sets[1:])

    def keys_sometimes_missing(self) -> Set[str]:
        """Return keys missing in at least one diff but not all."""
        all_missing: Set[str] = set()
        for d in self._result.diffs:
            all_missing.update(d.difference.missing_keys)
        return all_missing - self.keys_always_missing()

    def summary_by_file(self) -> dict:
        """Return a summary dict mapping each 'other' file to its issue counts."""
        summary = {}
        for d in self._result.diffs:
            summary[d.other_path] = {
                "missing": len(d.difference.missing_keys),
                "extra": len(d.difference.extra_keys),
                "mismatched": len(d.difference.mismatched_keys),
                "has_issues": d.has_issues,
            }
        return summary
