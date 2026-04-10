"""Tests for SnapshotManager and Snapshot."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from envdiff.snapshot import Snapshot, SnapshotManager


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path / "snaps")


@pytest.fixture
def manager(tmp_dir):
    return SnapshotManager(snapshot_dir=tmp_dir)


@pytest.fixture
def sample_env():
    return {"DB_HOST": "localhost", "DEBUG": "true", "SECRET": "abc123"}


def test_capture_creates_snapshot(manager, sample_env):
    snap = manager.capture(sample_env, source=".env.production", label="prod")
    assert snap.env == sample_env
    assert snap.source == ".env.production"
    assert snap.label == "prod"
    assert snap.captured_at  # non-empty timestamp


def test_capture_without_label(manager, sample_env):
    snap = manager.capture(sample_env, source=".env")
    assert snap.label is None


def test_save_creates_file(manager, sample_env):
    snap = manager.capture(sample_env, source=".env")
    path = manager.save(snap, filename="test_snap.json")
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["env"] == sample_env
    assert data["source"] == ".env"


def test_save_auto_filename(manager, sample_env):
    snap = manager.capture(sample_env, source=".env.staging")
    path = manager.save(snap)
    assert path.exists()
    assert path.suffix == ".json"


def test_load_round_trips(manager, sample_env):
    snap = manager.capture(sample_env, source=".env", label="base")
    path = manager.save(snap, filename="roundtrip.json")
    loaded = manager.load(str(path))
    assert loaded.env == sample_env
    assert loaded.label == "base"
    assert loaded.source == ".env"


def test_list_snapshots_empty(manager):
    assert manager.list_snapshots() == []


def test_list_snapshots_returns_all(manager, sample_env):
    for name in ["a.json", "b.json", "c.json"]:
        snap = manager.capture(sample_env, source=".env")
        manager.save(snap, filename=name)
    snaps = manager.list_snapshots()
    assert len(snaps) == 3
    assert all(p.suffix == ".json" for p in snaps)


def test_snapshot_to_dict_and_from_dict(sample_env):
    snap = Snapshot(source=".env", captured_at="2024-01-01T00:00:00+00:00", env=sample_env, label="x")
    d = snap.to_dict()
    restored = Snapshot.from_dict(d)
    assert restored.env == sample_env
    assert restored.label == "x"
    assert restored.source == ".env"
