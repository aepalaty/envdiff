"""Detect keys that conflict across environments due to type or format inconsistencies.

A conflict occurs when the same key exists in multiple environments but its
value appears to represent a fundamentally different type (e.g., integer vs
boolean string, URL vs plain string).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# Patterns used to classify value types
_BOOL_PATTERN = re.compile(r'^(true|false|yes|no|1|0)$', re.IGNORECASE)
_INT_PATTERN = re.compile(r'^-?\d+$')
_FLOAT_PATTERN = re.compile(r'^-?\d+\.\d+$')
_URL_PATTERN = re.compile(r'^https?://', re.IGNORECASE)
_JSON_PATTERN = re.compile(r'^[\[{]')


def _classify(value: str) -> str:
    """Return a simple type label for the given value string."""
    if not value:
        return "empty"
    if _BOOL_PATTERN.match(value):
        return "boolean"
    if _INT_PATTERN.match(value):
        return "integer"
    if _FLOAT_PATTERN.match(value):
        return "float"
    if _URL_PATTERN.match(value):
        return "url"
    if _JSON_PATTERN.match(value):
        return "json"
    return "string"


@dataclass
class ConflictEntry:
    """Represents a type-level conflict for a single key across environments."""

    key: str
    types_by_env: Dict[str, str] = field(default_factory=dict)  # env_name -> type label
    values_by_env: Dict[str, str] = field(default_factory=dict)  # env_name -> raw value

    @property
    def unique_types(self) -> List[str]:
        """Return the distinct type labels seen across environments."""
        return list(dict.fromkeys(self.types_by_env.values()))

    @property
    def has_conflict(self) -> bool:
        """True when more than one distinct type is present."""
        return len(self.unique_types) > 1

    def __str__(self) -> str:
        parts = ", ".join(
            f"{env}={t}" for env, t in self.types_by_env.items()
        )
        return f"{self.key}: [{parts}]"


@dataclass
class ConflictReport:
    """Aggregated conflict results across all environments."""

    env_names: List[str]
    entries: List[ConflictEntry] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return any(e.has_conflict for e in self.entries)

    @property
    def conflicting_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.has_conflict]

    @property
    def clean_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.has_conflict]

    def entry_for(self, key: str) -> Optional[ConflictEntry]:
        for e in self.entries:
            if e.key == key:
                return e
        return None


class KeyConflictDetector:
    """Detects type-level conflicts for keys shared across multiple environments."""

    def calculate(self, envs: Dict[str, Dict[str, str]]) -> ConflictReport:
        """Analyse *envs* (mapping of env-name -> key/value dict) for conflicts.

        Only keys that appear in **at least two** environments are evaluated;
        keys unique to a single environment are silently skipped because there
        is nothing to compare them against.
        """
        env_names = list(envs.keys())
        all_keys: List[str] = sorted(
            {k for env_data in envs.values() for k in env_data}
        )

        entries: List[ConflictEntry] = []
        for key in all_keys:
            envs_with_key = {
                name: data[key]
                for name, data in envs.items()
                if key in data
            }
            if len(envs_with_key) < 2:
                continue

            types_by_env = {name: _classify(val) for name, val in envs_with_key.items()}
            entry = ConflictEntry(
                key=key,
                types_by_env=types_by_env,
                values_by_env=dict(envs_with_key),
            )
            entries.append(entry)

        return ConflictReport(env_names=env_names, entries=entries)
