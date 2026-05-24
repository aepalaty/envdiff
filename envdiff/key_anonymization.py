from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import hashlib
import re

_SENSITIVE_PATTERNS = [
    r"password", r"passwd", r"secret", r"token", r"api[_-]?key",
    r"private[_-]?key", r"auth", r"credential", r"cert", r"private",
]


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(re.search(p, lower) for p in _SENSITIVE_PATTERNS)


def _anonymize_value(value: str, method: str = "hash") -> str:
    if not value:
        return value
    if method == "hash":
        return hashlib.sha256(value.encode()).hexdigest()[:16]
    if method == "mask":
        return "*" * min(len(value), 8)
    if method == "redact":
        return "[REDACTED]"
    return value


@dataclass
class AnonymizationEntry:
    key: str
    original_value: str
    anonymized_value: str
    is_sensitive: bool

    def __str__(self) -> str:
        tag = "[sensitive]" if self.is_sensitive else "[plain]"
        return f"{self.key} {tag}: {self.anonymized_value}"


@dataclass
class AnonymizationReport:
    env_name: str
    entries: List[AnonymizationEntry] = field(default_factory=list)

    @property
    def sensitive_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_sensitive]

    @property
    def plain_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.is_sensitive]

    def anonymized_env(self) -> Dict[str, str]:
        return {e.key: e.anonymized_value for e in self.entries}


class KeyAnonymizer:
    def __init__(self, method: str = "hash") -> None:
        if method not in ("hash", "mask", "redact"):
            raise ValueError(f"Unknown anonymization method: {method}")
        self.method = method

    def anonymize(self, env_name: str, env: Dict[str, str]) -> AnonymizationReport:
        entries: List[AnonymizationEntry] = []
        for key, value in env.items():
            sensitive = _is_sensitive(key)
            anon_value = _anonymize_value(value, self.method) if sensitive else value
            entries.append(AnonymizationEntry(
                key=key,
                original_value=value,
                anonymized_value=anon_value,
                is_sensitive=sensitive,
            ))
        return AnonymizationReport(env_name=env_name, entries=entries)

    def anonymize_all(
        self, envs: Dict[str, Dict[str, str]]
    ) -> Dict[str, AnonymizationReport]:
        return {name: self.anonymize(name, env) for name, env in envs.items()}
