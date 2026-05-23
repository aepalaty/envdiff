from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class OwnershipEntry:
    key: str
    owner: Optional[str]
    team: Optional[str]
    contact: Optional[str]

    def __str__(self) -> str:
        parts = [self.key]
        if self.owner:
            parts.append(f"owner={self.owner}")
        if self.team:
            parts.append(f"team={self.team}")
        if self.contact:
            parts.append(f"contact={self.contact}")
        return "  ".join(parts)

    @property
    def is_unowned(self) -> bool:
        return self.owner is None and self.team is None


@dataclass
class OwnershipReport:
    entries: List[OwnershipEntry] = field(default_factory=list)

    @property
    def unowned_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_unowned]

    @property
    def has_unowned(self) -> bool:
        return len(self.unowned_keys) > 0

    @property
    def owned_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.is_unowned]


class OwnershipCalculator:
    """Maps env keys to their declared owners using a registry dict."""

    def __init__(self, registry: Dict[str, Dict[str, str]]) -> None:
        # registry: {key: {"owner": ..., "team": ..., "contact": ...}}
        self._registry = registry

    def calculate(self, env: Dict[str, str]) -> OwnershipReport:
        entries: List[OwnershipEntry] = []
        for key in sorted(env.keys()):
            meta = self._registry.get(key, {})
            entries.append(
                OwnershipEntry(
                    key=key,
                    owner=meta.get("owner"),
                    team=meta.get("team"),
                    contact=meta.get("contact"),
                )
            )
        return OwnershipReport(entries=entries)
