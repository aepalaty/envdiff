"""Filter environment keys by glob patterns or prefix lists."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class KeyFilterConfig:
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    prefixes: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "KeyFilterConfig":
        return cls(
            include_patterns=data.get("include", []),
            exclude_patterns=data.get("exclude", []),
            prefixes=data.get("prefixes", []),
        )


class KeyFilter:
    """Filter a dict of env vars down to a matching subset."""

    def __init__(self, config: Optional[KeyFilterConfig] = None) -> None:
        self.config = config or KeyFilterConfig()

    def _matches_include(self, key: str) -> bool:
        if not self.config.include_patterns:
            return True
        return any(fnmatch.fnmatch(key, p) for p in self.config.include_patterns)

    def _matches_exclude(self, key: str) -> bool:
        return any(fnmatch.fnmatch(key, p) for p in self.config.exclude_patterns)

    def _matches_prefix(self, key: str) -> bool:
        if not self.config.prefixes:
            return True
        return any(key.startswith(pfx) for pfx in self.config.prefixes)

    def apply(self, env: Dict[str, str]) -> Dict[str, str]:
        """Return a filtered copy of *env* according to the configured rules."""
        result: Dict[str, str] = {}
        for key, value in env.items():
            if not self._matches_prefix(key):
                continue
            if not self._matches_include(key):
                continue
            if self._matches_exclude(key):
                continue
            result[key] = value
        return result

    def filter_keys(self, keys: List[str]) -> List[str]:
        """Return a filtered list of key names (no values needed)."""
        dummy = {k: "" for k in keys}
        return list(self.apply(dummy).keys())
