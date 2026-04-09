"""Load redaction configuration from a TOML or JSON config file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, FrozenSet, Optional

from envdiff.redactor import Redactor, DEFAULT_MASK

_CONFIG_FILENAMES = [".envdiff-redact.json", ".envdiff-redact.toml"]


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open() as fh:
        return json.load(fh)


def _load_toml(path: Path) -> Dict[str, Any]:
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]
    with path.open("rb") as fh:
        return tomllib.load(fh)


def load_redact_config(config_path: Optional[Path] = None) -> Redactor:
    """Load a Redactor from a config file, or return defaults."""
    if config_path is None:
        for name in _CONFIG_FILENAMES:
            candidate = Path.cwd() / name
            if candidate.exists():
                config_path = candidate
                break

    if config_path is None:
        return Redactor()

    if config_path.suffix == ".toml":
        data = _load_toml(config_path)
    else:
        data = _load_json(config_path)

    sensitive_keys: FrozenSet[str] = frozenset(data.get("sensitive_keys", []))
    mask: str = data.get("mask", DEFAULT_MASK)
    auto_detect: bool = data.get("auto_detect", True)

    return Redactor(sensitive_keys=sensitive_keys, mask=mask, auto_detect=auto_detect)
