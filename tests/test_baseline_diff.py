"""Tests for BaselineDiffer."""

from __future__ import annotations

import pytest

from envdiff.baseline import BaselineManager
from envdiff.baseline_diff import BaselineDiffer


@pytest.fixture
def tmp_store(tmp_path):
    return str(tmp_path / "baseline.json")


@pytest.fixture
def manager(tmp_store):
    return BaselineManager(store_path=tmp_store)


@pytest.fixture
def differ(manager):
    return BaselineDiffer(manager=manager)


@pytest.fixture
def recorded(manager):
    manager.record("app.env", {"DB_HOST": "localhost", "PORT": "5432", "DEBUG": "true"})
    return "app.env"


def test_no_changes_when_env_identical(differ, recorded):
    current = {"DB_HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    result = differ.diff_env(recorded, current)
    assert not result.has_changes


def test_detects_missing_key(differ, recorded):
    current = {"DB_HOST": "localhost", "PORT": "5432"}
    result = differ.diff_env(recorded, current)
    assert result.has_changes
    assert "DEBUG" in result.difference.missing_keys


def test_detects_extra_key(differ, recorded):
    current = {"DB_HOST": "localhost", "PORT": "5432", "DEBUG": "true", "NEW_KEY": "x"}
    result = differ.diff_env(recorded, current)
    assert result.has_changes
    assert "NEW_KEY" in result.difference.extra_keys


def test_detects_mismatched_value(differ, recorded):
    current = {"DB_HOST": "remotehost", "PORT": "5432", "DEBUG": "true"}
    result = differ.diff_env(recorded, current)
    assert result.has_changes
    assert "DB_HOST" in result.difference.mismatched_keys


def test_summary_no_changes(differ, recorded):
    current = {"DB_HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    result = differ.diff_env(recorded, current)
    assert "No changes" in result.summary()


def test_summary_with_changes(differ, recorded):
    current = {"DB_HOST": "localhost"}
    result = differ.diff_env(recorded, current)
    summary = result.summary()
    assert "missing" in summary


def test_diff_env_raises_when_no_baseline(differ):
    with pytest.raises(ValueError, match="No baseline recorded"):
        differ.diff_env("untracked.env", {"K": "V"})


def test_baseline_entry_accessible_on_result(differ, recorded):
    current = {"DB_HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    result = differ.diff_env(recorded, current)
    assert result.baseline.path == recorded
    assert "DB_HOST" in result.baseline.env
