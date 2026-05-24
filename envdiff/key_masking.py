from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

_MASK = "***"

_SENSITIVE_PATTERNS = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "auth",
    "credential",
    "private_key",
    "access_key",
)


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in _SENSITIVE_PATTERNS)


@dataclass
class MaskingEntry:
    key: str
    original_value: str
    masked_value: str
    is_sensitive: bool

    def __str__(self) -> str:
        tag = "[sensitive]" if self.is_sensitive else "[plain]"
        return f"{self.key}={self.masked_value}  {tag}"


@dataclass
class MaskingReport:
    env_name: str
    entries: List[MaskingEntry] = field(default_factory=list)

    @property
    def masked_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_sensitive]

    @property
    def total_keys(self) -> int:
        return len(self.entries)

    def as_masked_env(self) -> Dict[str, str]:
        return {e.key: e.masked_value for e in self.entries}


class KeyMasker:
    """Produces a masked copy of an env dict, replacing sensitive values."""

    def __init__(self, extra_patterns: List[str] | None = None) -> None:
        self._patterns = list(_SENSITIVE_PATTERNS)
        if extra_patterns:
            self._patterns.extend(p.lower() for p in extra_patterns)

    def is_sensitive(self, key: str) -> bool:
        lower = key.lower()
        return any(pat in lower for pat in self._patterns)

    def mask_value(self, value: str) -> str:
        return _MASK if value else value

    def calculate(self, env_name: str, env: Dict[str, str]) -> MaskingReport:
        entries: List[MaskingEntry] = []
        for key, value in sorted(env.items()):
            sensitive = self.is_sensitive(key)
            masked = self.mask_value(value) if sensitive else value
            entries.append(
                MaskingEntry(
                    key=key,
                    original_value=value,
                    masked_value=masked,
                    is_sensitive=sensitive,
                )
            )
        return MaskingReport(env_name=env_name, entries=entries)
