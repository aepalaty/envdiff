"""Sorts and groups env keys by prefix or alphabetically for organized output."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple


class KeyGroup:
    """A named group of key-value pairs sharing a common prefix."""

    def __init__(self, name: str, keys: Dict[str, Optional[str]]) -> None:
        self.name = name
        self.keys = keys

    def __repr__(self) -> str:  # pragma: no cover
        return f"KeyGroup(name={self.name!r}, keys={list(self.keys)!r})"


class KeySorter:
    """Groups and sorts env keys by prefix (e.g. DB_, AWS_) or alphabetically."""

    def __init__(self, separator: str = "_", ungrouped_label: str = "OTHER") -> None:
        self.separator = separator
        self.ungrouped_label = ungrouped_label

    def _extract_prefix(self, key: str) -> Optional[str]:
        """Return the prefix portion of a key, or None if no separator found."""
        if self.separator in key:
            return key.split(self.separator, 1)[0]
        return None

    def group_by_prefix(self, env: Dict[str, Optional[str]]) -> List[KeyGroup]:
        """Group keys by their prefix, sorting groups and keys alphabetically."""
        grouped: Dict[str, Dict[str, Optional[str]]] = defaultdict(dict)

        for key, value in env.items():
            prefix = self._extract_prefix(key)
            label = prefix if prefix else self.ungrouped_label
            grouped[label][key] = value

        result: List[KeyGroup] = []
        for group_name in sorted(grouped):
            sorted_keys = dict(sorted(grouped[group_name].items()))
            result.append(KeyGroup(name=group_name, keys=sorted_keys))

        return result

    def sort_flat(self, env: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
        """Return a new dict with keys sorted alphabetically."""
        return dict(sorted(env.items()))

    def sort_keys_list(self, keys: List[str]) -> List[str]:
        """Sort a plain list of key names alphabetically."""
        return sorted(keys)

    def split_by_prefix(
        self, keys: List[str]
    ) -> List[Tuple[str, List[str]]]:
        """Return (prefix, [keys]) tuples sorted by prefix for a flat key list."""
        grouped: Dict[str, List[str]] = defaultdict(list)
        for key in keys:
            prefix = self._extract_prefix(key) or self.ungrouped_label
            grouped[prefix].append(key)
        return [(p, sorted(grouped[p])) for p in sorted(grouped)]
