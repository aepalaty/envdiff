"""Validates parsed env data against an EnvSchema."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.schema import EnvSchema


@dataclass
class SchemaValidationResult:
    missing_required: List[str] = field(default_factory=list)
    disallowed_values: Dict[str, str] = field(default_factory=dict)
    pattern_violations: Dict[str, str] = field(default_factory=dict)
    extra_keys: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not (
            self.missing_required
            or self.disallowed_values
            or self.pattern_violations
            or self.extra_keys
        )

    def __str__(self) -> str:
        lines = []
        if self.missing_required:
            lines.append(f"Missing required keys: {', '.join(self.missing_required)}")
        for key, val in self.disallowed_values.items():
            lines.append(f"Disallowed value for '{key}': '{val}'")
        for key, val in self.pattern_violations.items():
            lines.append(f"Pattern violation for '{key}': '{val}'")
        if self.extra_keys:
            lines.append(f"Extra keys not allowed: {', '.join(self.extra_keys)}")
        return "\n".join(lines) if lines else "Schema validation passed."


class SchemaValidator:
    """Validates an env dict against a given EnvSchema."""

    def __init__(self, schema: EnvSchema) -> None:
        self.schema = schema

    def validate(self, env: Dict[str, str]) -> SchemaValidationResult:
        result = SchemaValidationResult()

        for key in self.schema.required_keys():
            if key not in env:
                result.missing_required.append(key)

        if not self.schema.allow_extra_keys:
            known = set(self.schema.keys.keys())
            for key in env:
                if key not in known:
                    result.extra_keys.append(key)

        for key, key_schema in self.schema.keys.items():
            if key not in env:
                continue
            value = env[key]
            if key_schema.allowed_values and value not in key_schema.allowed_values:
                result.disallowed_values[key] = value
            if key_schema.pattern and not re.fullmatch(key_schema.pattern, value):
                result.pattern_violations[key] = value

        return result
