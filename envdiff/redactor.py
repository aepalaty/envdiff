"""Redaction utilities for masking sensitive values in .env output."""

from __future__ import annotations

import re
from typing import Dict, FrozenSet, Optional

# Common patterns that indicate a value is sensitive
_SENSITIVE_PATTERNS: list[re.Pattern] = [
    re.compile(r"(password|passwd|secret|token|api[_-]?key|private[_-]?key|auth|credential)", re.IGNORECASE),
]

DEFAULT_MASK = "***"


class Redactor:
    """Masks sensitive key values before display or output."""

    def __init__(
        self,
        sensitive_keys: Optional[FrozenSet[str]] = None,
        mask: str = DEFAULT_MASK,
        auto_detect: bool = True,
    ) -> None:
        self.sensitive_keys: FrozenSet[str] = sensitive_keys or frozenset()
        self.mask = mask
        self.auto_detect = auto_detect

    def is_sensitive(self, key: str) -> bool:
        """Return True if the key should be treated as sensitive."""
        if key in self.sensitive_keys:
            return True
        if self.auto_detect:
            return any(p.search(key) for p in _SENSITIVE_PATTERNS)
        return False

    def redact(self, key: str, value: str) -> str:
        """Return the value or the mask string if the key is sensitive."""
        return self.mask if self.is_sensitive(key) else value

    def redact_env(self, env: Dict[str, str]) -> Dict[str, str]:
        """Return a new dict with sensitive values replaced by the mask."""
        return {k: self.redact(k, v) for k, v in env.items()}
