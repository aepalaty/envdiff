"""Tests for deprecation_loader module."""

import json
import pytest
from pathlib import Path

from envdiff.deprecation_loader import (
    find_registry,
    load_registry_auto,
    load_registry_from_path,
)


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write_json(path: Path, data: dict) -> Path:
    target = path / ".envdeprecations.json"
    target.write_text(json.dumps(data), encoding="utf-8")
    return target


def test_load_from_json(tmp_dir):
    data = {
        "deprecated": [
            {"key": "OLD_KEY", "reason": "Outdated", "replacement": "NEW_KEY"}
        ]
    }
    config_path = _write_json(tmp_dir, data)
    registry = load_registry_from_path(str(config_path))
    assert "OLD_KEY" in registry._registry


def test_load_missing_file_raises(tmp_dir):
    with pytest.raises(FileNotFoundError):
        load_registry_from_path(str(tmp_dir / "nonexistent.json"))


def test_find_registry_locates_json(tmp_dir):
    _write_json(tmp_dir, {"deprecated": []})
    found = find_registry(str(tmp_dir))
    assert found is not None
    assert found.name == ".envdeprecations.json"


def test_find_registry_returns_none_when_absent(tmp_dir):
    found = find_registry(str(tmp_dir))
    assert found is None


def test_load_auto_returns_empty_registry_when_no_config(tmp_dir):
    registry = load_registry_auto(str(tmp_dir))
    assert len(registry._registry) == 0


def test_load_auto_finds_and_loads_json(tmp_dir):
    data = {"deprecated": [{"key": "DEPRECATED_VAR", "reason": "Removed"}]}
    _write_json(tmp_dir, data)
    registry = load_registry_auto(str(tmp_dir))
    assert "DEPRECATED_VAR" in registry._registry


def test_unsupported_format_raises(tmp_dir):
    bad_file = tmp_dir / ".envdeprecations.yaml"
    bad_file.write_text("deprecated: []", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        load_registry_from_path(str(bad_file))
