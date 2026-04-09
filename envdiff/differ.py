"""Multi-file diff orchestrator for comparing more than two .env files."""

from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Tuple

from envdiff.comparator import EnvComparator, EnvDifference
from envdiff.parser import parse_file


@dataclass
class PairwiseDiff:
    """Holds the diff result between a pair of env files."""

    left_path: str
    right_path: str
    difference: EnvDifference

    @property
    def has_issues(self) -> bool:
        return (
            bool(self.difference.missing_keys)
            or bool(self.difference.extra_keys)
            or bool(self.difference.mismatched_values)
        )


@dataclass
class MultiDiffResult:
    """Aggregated result of comparing multiple .env files."""

    paths: List[str]
    pairwise: List[PairwiseDiff] = field(default_factory=list)

    @property
    def all_keys(self) -> List[str]:
        seen = set()
        for pd in self.pairwise:
            seen.update(pd.difference.missing_keys)
            seen.update(pd.difference.extra_keys)
            seen.update(pd.difference.mismatched_values.keys())
        return sorted(seen)

    @property
    def has_issues(self) -> bool:
        return any(pd.has_issues for pd in self.pairwise)


class MultiFileDiffer:
    """Compares multiple .env files pairwise against a baseline."""

    def __init__(self, baseline_path: str, other_paths: List[str]) -> None:
        self.baseline_path = baseline_path
        self.other_paths = other_paths

    def diff_all(self) -> MultiDiffResult:
        baseline_env = parse_file(self.baseline_path)
        all_paths = [self.baseline_path] + self.other_paths
        result = MultiDiffResult(paths=all_paths)

        for other_path in self.other_paths:
            other_env = parse_file(other_path)
            comparator = EnvComparator(baseline_env, other_env)
            difference = comparator.compare()
            result.pairwise.append(
                PairwiseDiff(
                    left_path=self.baseline_path,
                    right_path=other_path,
                    difference=difference,
                )
            )

        return result

    def diff_all_pairs(self) -> MultiDiffResult:
        """Compare every combination of files, not just against a baseline."""
        all_paths = [self.baseline_path] + self.other_paths
        envs: Dict[str, dict] = {p: parse_file(p) for p in all_paths}
        result = MultiDiffResult(paths=all_paths)

        for left, right in combinations(all_paths, 2):
            comparator = EnvComparator(envs[left], envs[right])
            difference = comparator.compare()
            result.pairwise.append(
                PairwiseDiff(left_path=left, right_path=right, difference=difference)
            )

        return result
