"""Merge multiple .env files into a unified baseline with conflict tracking."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class MergeConflict:
    key: str
    values: Dict[str, str]  # source_label -> value

    def __str__(self) -> str:
        parts = ", ".join(f"{src}={val!r}" for src, val in self.values.items())
        return f"Conflict on '{self.key}': {parts}"


@dataclass
class MergeResult:
    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: List[MergeConflict] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def conflict_keys(self) -> List[str]:
        return [c.key for c in self.conflicts]


class EnvMerger:
    """Merges multiple parsed env dicts into a single unified dict."""

    def __init__(self, strategy: str = "first"):
        """
        strategy:
          'first'  — keep the first value seen for a key (default)
          'last'   — keep the last value seen for a key
        """
        if strategy not in ("first", "last"):
            raise ValueError(f"Unknown merge strategy: {strategy!r}")
        self.strategy = strategy

    def merge(self, envs: List[Tuple[str, Dict[str, str]]]) -> MergeResult:
        """Merge a list of (label, env_dict) pairs."""
        result = MergeResult(sources=[label for label, _ in envs])
        seen: Dict[str, Dict[str, str]] = {}  # key -> {label: value}

        for label, env in envs:
            for key, value in env.items():
                if key not in seen:
                    seen[key] = {}
                seen[key][label] = value

        for key, source_map in seen.items():
            unique_values = list(dict.fromkeys(source_map.values()))
            if len(unique_values) > 1:
                result.conflicts.append(MergeConflict(key=key, values=source_map))

            if self.strategy == "first":
                result.merged[key] = next(iter(source_map.values()))
            else:
                result.merged[key] = list(source_map.values())[-1]

        return result
