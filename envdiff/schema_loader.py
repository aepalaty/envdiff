"""Helpers to locate and load schema files for envdiff."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from envdiff.schema import EnvSchema

DEFAULT_SCHEMA_FILENAMES = [
    ".envschema.json",
    "envschema.json",
    ".env.schema.json",
]


def find_schema(directory: Optional[Path] = None) -> Optional[Path]:
    """Search for a schema file in the given directory (default: cwd)."""
    search_dir = directory or Path.cwd()
    for name in DEFAULT_SCHEMA_FILENAMES:
        candidate = search_dir / name
        if candidate.exists():
            return candidate
    return None


def load_schema_from_path(path: Optional[str]) -> Optional[EnvSchema]:
    """Load schema from an explicit path, or return None if not provided."""
    if path is None:
        return None
    schema_path = Path(path)
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    return EnvSchema.load(schema_path)


def load_schema_auto(explicit_path: Optional[str] = None) -> Optional[EnvSchema]:
    """Load schema from an explicit path or auto-discover in cwd.

    Returns None if no schema is found and no path is specified.
    """
    if explicit_path:
        return load_schema_from_path(explicit_path)
    discovered = find_schema()
    if discovered:
        return EnvSchema.load(discovered)
    return None
