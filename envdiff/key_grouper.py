"""Groups environment keys by common prefix or naming convention."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class KeyGroup:
    prefix: str
    keys: List[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.keys)

    def __repr__(self) -> str:
        return f"KeyGroup(prefix={self.prefix!r}, keys={self.keys})"


@dataclass
class GroupReport:
    groups: Dict[str, KeyGroup]
    ungrouped: List[str] = field(default_factory=list)

    @property
    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    @property
    def total_grouped(self) -> int:
        return sum(len(g) for g in self.groups.values())

    def summary(self) -> str:
        lines = [f"Groups: {len(self.groups)}, Ungrouped: {len(self.ungrouped)}"]
        for name in self.group_names:
            group = self.groups[name]
            lines.append(f"  [{name}] ({len(group)} keys): {', '.join(sorted(group.keys))}")
        if self.ungrouped:
            lines.append(f"  [ungrouped]: {', '.join(sorted(self.ungrouped))}")
        return "\n".join(lines)


class KeyGrouper:
    """Groups keys from an env dict by shared prefix (e.g. DB_, AWS_, APP_)."""

    def __init__(self, min_group_size: int = 2, separator: str = "_"):
        self.min_group_size = min_group_size
        self.separator = separator

    def _extract_prefix(self, key: str) -> Optional[str]:
        parts = key.split(self.separator)
        if len(parts) >= 2:
            return parts[0]
        return None

    def group(self, env: Dict[str, str]) -> GroupReport:
        prefix_map: Dict[str, List[str]] = {}

        for key in env:
            prefix = self._extract_prefix(key)
            if prefix:
                prefix_map.setdefault(prefix, []).append(key)

        groups: Dict[str, KeyGroup] = {}
        ungrouped: List[str] = []

        assigned: set = set()
        for prefix, keys in prefix_map.items():
            if len(keys) >= self.min_group_size:
                groups[prefix] = KeyGroup(prefix=prefix, keys=keys)
                assigned.update(keys)

        for key in env:
            if key not in assigned:
                ungrouped.append(key)

        return GroupReport(groups=groups, ungrouped=ungrouped)
