"""Detect keys that differ only by naming convention (e.g. FOO_BAR vs foo_bar vs FOO-BAR)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _normalize(key: str) -> str:
    """Return a canonical lowercase-underscore form of a key."""
    # Replace hyphens and dots with underscores, then lowercase
    return re.sub(r'[-.]', '_', key).lower()


@dataclass
class NormalizationGroup:
    canonical: str
    variants: List[str]

    def __len__(self) -> int:
        return len(self.variants)

    def __repr__(self) -> str:  # pragma: no cover
        return f"NormalizationGroup(canonical={self.canonical!r}, variants={self.variants})"


@dataclass
class NormalizationReport:
    groups: List[NormalizationGroup] = field(default_factory=list)
    env_names: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return any(len(g) > 1 for g in self.groups)

    @property
    def conflict_groups(self) -> List[NormalizationGroup]:
        return [g for g in self.groups if len(g) > 1]


class KeyNormalizationDetector:
    """Detect keys across environments that map to the same normalized form."""

    def detect(self, envs: Dict[str, Dict[str, str]]) -> NormalizationReport:
        """
        envs: mapping of env_name -> {KEY: value}
        Returns a NormalizationReport listing groups of keys that share a
        normalized form (potential naming-convention conflicts).
        """
        # Collect all unique keys across all envs
        all_keys: set[str] = set()
        for env_dict in envs.values():
            all_keys.update(env_dict.keys())

        # Group keys by their normalized form
        buckets: Dict[str, List[str]] = {}
        for key in sorted(all_keys):
            norm = _normalize(key)
            buckets.setdefault(norm, []).append(key)

        groups = [
            NormalizationGroup(canonical=norm, variants=variants)
            for norm, variants in sorted(buckets.items())
        ]

        return NormalizationReport(
            groups=groups,
            env_names=list(envs.keys()),
        )
