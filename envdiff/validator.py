"""Validator module for checking .env file keys against a required schema."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ValidationResult:
    """Result of validating an env file against a schema."""

    missing_required: List[str] = field(default_factory=list)
    unknown_keys: List[str] = field(default_factory=list)
    empty_values: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Return True if there are no validation errors."""
        return not self.missing_required

    def __str__(self) -> str:
        lines = []
        if self.missing_required:
            keys = ", ".join(self.missing_required)
            lines.append(f"Missing required keys: {keys}")
        if self.unknown_keys:
            keys = ", ".join(self.unknown_keys)
            lines.append(f"Unknown keys: {keys}")
        if self.empty_values:
            keys = ", ".join(self.empty_values)
            lines.append(f"Keys with empty values: {keys}")
        return "\n".join(lines) if lines else "Validation passed."


class EnvValidator:
    """Validates parsed env dictionaries against a required schema."""

    def __init__(
        self,
        required_keys: List[str],
        optional_keys: Optional[List[str]] = None,
        allow_unknown: bool = True,
        warn_empty: bool = True,
    ) -> None:
        self.required_keys: Set[str] = set(required_keys)
        self.optional_keys: Set[str] = set(optional_keys or [])
        self.allow_unknown = allow_unknown
        self.warn_empty = warn_empty

    def validate(self, env: Dict[str, Optional[str]]) -> ValidationResult:
        """Validate an env dict and return a ValidationResult."""
        result = ValidationResult()
        env_keys = set(env.keys())

        # Check for missing required keys
        result.missing_required = sorted(self.required_keys - env_keys)

        # Check for unknown keys (not in required or optional)
        if not self.allow_unknown:
            known_keys = self.required_keys | self.optional_keys
            result.unknown_keys = sorted(env_keys - known_keys)

        # Check for empty values
        if self.warn_empty:
            result.empty_values = sorted(
                key for key, value in env.items()
                if value is None or value.strip() == ""
            )

        return result
