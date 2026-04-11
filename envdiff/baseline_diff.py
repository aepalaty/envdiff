"""Compare a live env file against its recorded baseline."""

from __future__ import annotations

from typing import Dict, Optional

from envdiff.baseline import BaselineEntry, BaselineManager
from envdiff.comparator import EnvComparator, EnvDifference
from envdiff.parser import parse_file


class BaselineDiffResult:
    def __init__(self, baseline: BaselineEntry, difference: EnvDifference):
        self.baseline = baseline
        self.difference = difference

    @property
    def has_changes(self) -> bool:
        return (
            bool(self.difference.missing_keys)
            or bool(self.difference.extra_keys)
            or bool(self.difference.mismatched_keys)
        )

    def summary(self) -> str:
        d = self.difference
        parts = []
        if d.missing_keys:
            parts.append(f"{len(d.missing_keys)} missing")
        if d.extra_keys:
            parts.append(f"{len(d.extra_keys)} extra")
        if d.mismatched_keys:
            parts.append(f"{len(d.mismatched_keys)} mismatched")
        if not parts:
            return "No changes from baseline."
        return "Changes from baseline: " + ", ".join(parts) + "."


class BaselineDiffer:
    def __init__(self, manager: Optional[BaselineManager] = None):
        self.manager = manager or BaselineManager()

    def diff_file(self, env_path: str) -> BaselineDiffResult:
        entry = self.manager.get(env_path)
        if entry is None:
            raise ValueError(f"No baseline recorded for '{env_path}'. Run 'envdiff baseline record' first.")
        current_env = parse_file(env_path)
        return self._diff(entry, current_env)

    def diff_env(self, env_path: str, current_env: Dict[str, str]) -> BaselineDiffResult:
        entry = self.manager.get(env_path)
        if entry is None:
            raise ValueError(f"No baseline recorded for '{env_path}'.")
        return self._diff(entry, current_env)

    def _diff(self, entry: BaselineEntry, current_env: Dict[str, str]) -> BaselineDiffResult:
        comparator = EnvComparator(entry.env, current_env)
        difference = comparator.compare()
        return BaselineDiffResult(baseline=entry, difference=difference)
