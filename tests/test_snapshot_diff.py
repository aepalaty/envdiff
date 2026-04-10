"""Tests for SnapshotDiffer."""

from __future__ import annotations

import pytest

from envdiff.snapshot import Snapshot, SnapshotManager
from envdiff.snapshot_diff import SnapshotDiffer


@pytest.fixture
def differ():
    return SnapshotDiffer()


@pytest.fixture
def baseline_snap():
    return Snapshot(
        source=".env.production",
        captured_at="2024-01-01T00:00:00+00:00",
        env={"DB_HOST": "prod-db", "DEBUG": "false", "ONLY_IN_BASE": "yes"},
        label="production",
    )


@pytest.fixture
def other_snap():
    return Snapshot(
        source=".env.staging",
        captured_at="2024-06-01T00:00:00+00:00",
        env={"DB_HOST": "staging-db", "DEBUG": "true", "ONLY_IN_OTHER": "yes"},
        label="staging",
    )


def test_diff_detects_missing_keys(differ, baseline_snap, other_snap):
    result = differ.diff(baseline_snap, other_snap)
    assert "ONLY_IN_BASE" in result.missing_keys


def test_diff_detects_extra_keys(differ, baseline_snap, other_snap):
    result = differ.diff(baseline_snap, other_snap)
    assert "ONLY_IN_OTHER" in result.extra_keys


def test_diff_detects_value_mismatch(differ, baseline_snap, other_snap):
    mismatched = {k for k, _, _ in result.mismatched_keys
                  for result in [differ.diff(baseline_snap, other_snap)]}
    result = differ.diff(baseline_snap, other_snap)
    keys = {k for k, _, _ in result.mismatched_keys}
    assert "DB_HOST" in keys
    assert "DEBUG" in keys


def test_diff_identical_snapshots_no_issues(differ):
    env = {"KEY": "value", "FOO": "bar"}
    snap_a = Snapshot(source="a", captured_at="t", env=env)
    snap_b = Snapshot(source="b", captured_at="t", env=env)
    result = differ.diff(snap_a, snap_b)
    assert not result.missing_keys
    assert not result.extra_keys
    assert not result.mismatched_keys


def test_diff_uses_labels(differ, baseline_snap, other_snap):
    result = differ.diff(baseline_snap, other_snap)
    assert result.label_a == "production"
    assert result.label_b == "staging"


def test_diff_falls_back_to_source_when_no_label(differ):
    snap_a = Snapshot(source=".env.a", captured_at="t", env={"X": "1"})
    snap_b = Snapshot(source=".env.b", captured_at="t", env={"X": "2"})
    result = differ.diff(snap_a, snap_b)
    assert result.label_a == ".env.a"
    assert result.label_b == ".env.b"


def test_diff_from_files(differ, tmp_path):
    mgr = SnapshotManager(snapshot_dir=str(tmp_path / "snaps"))
    env_a = {"KEY": "old", "ONLY_A": "yes"}
    env_b = {"KEY": "new", "ONLY_B": "yes"}
    snap_a = mgr.capture(env_a, source=".env.a")
    snap_b = mgr.capture(env_b, source=".env.b")
    path_a = mgr.save(snap_a, filename="snap_a.json")
    path_b = mgr.save(snap_b, filename="snap_b.json")
    result = differ.diff_from_files(str(path_a), str(path_b), manager=mgr)
    assert "ONLY_A" in result.missing_keys
    assert "ONLY_B" in result.extra_keys
