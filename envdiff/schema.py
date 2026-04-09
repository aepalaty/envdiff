"""Schema definition and loading for .env file validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class KeySchema:
    """Schema definition for a single environment key."""

    name: str
    required: bool = True
    description: str = ""
    allowed_values: List[str] = field(default_factory=list)
    pattern: Optional[str] = None

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "KeySchema":
        return cls(
            name=name,
            required=data.get("required", True),
            description=data.get("description", ""),
            allowed_values=data.get("allowed_values", []),
            pattern=data.get("pattern"),
        )


@dataclass
class EnvSchema:
    """Schema for an entire .env file."""

    keys: Dict[str, KeySchema] = field(default_factory=dict)
    allow_extra_keys: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnvSchema":
        keys = {
            name: KeySchema.from_dict(name, key_data)
            for name, key_data in data.get("keys", {}).items()
        }
        return cls(
            keys=keys,
            allow_extra_keys=data.get("allow_extra_keys", True),
        )

    @classmethod
    def load(cls, path: Path) -> "EnvSchema":
        """Load schema from a JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def required_keys(self) -> List[str]:
        return [k for k, v in self.keys.items() if v.required]

    def optional_keys(self) -> List[str]:
        return [k for k, v in self.keys.items() if not v.required]
