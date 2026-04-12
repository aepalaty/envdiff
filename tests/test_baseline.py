"""Tests for BaselineManager and BaselineEntry."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envdiff.baseline import BaselineEntry, BaselineManager, DEFAULT_BASELINE_FILE


@pytest.fixture
def tmp_store(tmp_path):
    return str(tmp_path / "baseline.json")


@pytest.fixture
def manager(tmp_store):
    return BaselineManager(store_path=tmp_store)


def test_record_creates_entry(manager):
    entry = manager.record("prod.env", {"DB_HOST": "localhost", "PORT": "5432"})
    assert entry.path == "prod.env"
    assert entry.env["PORT"] == "5432"
    assert entry.recorded_at != ""


def test_record_persists_to_disk(manager, tmp_store):
    manager.record("prod.env", {"KEY": "val"})
    data = json.loads(Path(tmp_store).read_text())
    assert "prod.env" in data
    assert data["prod.env"]["env"]["KEY"] == "val"


def test_get_returns_entry(manager):
    manager.record("staging.env", {"FOO": "bar"}, label="v1")
    entry = manager.get("staging.env")
    assert entry is not None
    assert entry.label == "v1"
    assert entry.env["FOO"] == "bar"


def test_get_missing_returns_none(manager):
    assert manager.get("nonexistent.env") is None


def test_remove_existing_entry(manager):
    manager.record("dev.env", {"X": "1"})
    result = manager.remove("dev.env")
    assert result is True
    assert manager.get("dev.env") is None


def test_remove_nonexistent_returns_false(manager):
    assert manager.remove("ghost.env") is False


def test_list_all_returns_all_entries(manager):
    manager.record("a.env", {"A": "1"})
    manager.record("b.env", {"B": "2"})
    entries = manager.list_all()
    assert set(entries.keys()) == {"a.env", "b.env"}


def test_baseline_entry_roundtrip():
    original = BaselineEntry(path="x.env", env={"K": "V"}, label="test")
    restored = BaselineEntry.from_dict(original.to_dict())
    assert restored.path == original.path
    assert restored.env == original.env
    assert restored.label == original.label
    assert restored.recorded_at == original.recorded_at


def test_record_overwrites_existing_entry(manager):
    """Recording the same path twice should update the entry, not duplicate it."""
    manager.record("prod.env", {"KEY": "old_value"}, label="v1")
    manager.record("prod.env", {"KEY": "new_value"}, label="v2")

    entry = manager.get("prod.env")
    assert entry is not None
    assert entry.env["KEY"] == "new_value"
    assert entry.label == "v2"
    assert len(manager.list_all()) == 1
