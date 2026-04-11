"""Detect deprecated keys in .env files based on a deprecation registry."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DeprecationEntry:
    key: str
    reason: str
    replacement: Optional[str] = None

    def __str__(self) -> str:
        msg = f"{self.key}: {self.reason}"
        if self.replacement:
            msg += f" (use '{self.replacement}' instead)"
        return msg


@dataclass
class DeprecationReport:
    hits: List[DeprecationEntry] = field(default_factory=list)

    @property
    def has_deprecated(self) -> bool:
        return len(self.hits) > 0

    @property
    def deprecated_keys(self) -> List[str]:
        return [h.key for h in self.hits]

    def __str__(self) -> str:
        if not self.has_deprecated:
            return "No deprecated keys found."
        lines = ["Deprecated keys detected:"]
        for hit in self.hits:
            lines.append(f"  - {hit}")
        return "\n".join(lines)


class DeprecationRegistry:
    """Holds a set of known deprecated keys with reasons and optional replacements."""

    def __init__(self, entries: Optional[List[Dict]] = None) -> None:
        self._registry: Dict[str, DeprecationEntry] = {}
        for entry in entries or []:
            self.register(
                key=entry["key"],
                reason=entry.get("reason", "Deprecated"),
                replacement=entry.get("replacement"),
            )

    def register(self, key: str, reason: str, replacement: Optional[str] = None) -> None:
        self._registry[key] = DeprecationEntry(key=key, reason=reason, replacement=replacement)

    def check(self, env: Dict[str, str]) -> DeprecationReport:
        hits = [
            self._registry[key]
            for key in env
            if key in self._registry
        ]
        return DeprecationReport(hits=hits)

    @classmethod
    def from_dict(cls, data: Dict) -> "DeprecationRegistry":
        entries = data.get("deprecated", [])
        return cls(entries=entries)
