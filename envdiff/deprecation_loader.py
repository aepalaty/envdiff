"""Load deprecation registry from JSON or TOML config files."""

import json
from pathlib import Path
from typing import Optional

from envdiff.key_deprecation import DeprecationRegistry

_DEFAULT_FILENAMES = [".envdeprecations.json", ".envdeprecations.toml"]


def load_registry_from_path(path: str) -> DeprecationRegistry:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Deprecation config not found: {path}")
    return _load(p)


def find_registry(search_dir: Optional[str] = None) -> Optional[Path]:
    base = Path(search_dir) if search_dir else Path.cwd()
    for name in _DEFAULT_FILENAMES:
        candidate = base / name
        if candidate.exists():
            return candidate
    return None


def load_registry_auto(search_dir: Optional[str] = None) -> DeprecationRegistry:
    path = find_registry(search_dir)
    if path is None:
        return DeprecationRegistry()
    return _load(path)


def _load(path: Path) -> DeprecationRegistry:
    if path.suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return DeprecationRegistry.from_dict(data)
    if path.suffix == ".toml":
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            import tomli as tomllib  # type: ignore
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return DeprecationRegistry.from_dict(data)
    raise ValueError(f"Unsupported deprecation config format: {path.suffix}")
