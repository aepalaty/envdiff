"""Tests for envdiff.merger."""

import pytest
from envdiff.merger import EnvMerger, MergeConflict, MergeResult


@pytest.fixture
def merger():
    return EnvMerger(strategy="first")


def test_merge_no_conflicts(merger):
    envs = [
        ("dev", {"HOST": "localhost", "PORT": "5432"}),
        ("staging", {"HOST": "localhost", "PORT": "5432"}),
    ]
    result = merger.merge(envs)
    assert result.merged == {"HOST": "localhost", "PORT": "5432"}
    assert not result.has_conflicts
    assert result.conflict_keys() == []


def test_merge_detects_conflicts(merger):
    envs = [
        ("dev", {"HOST": "localhost", "DEBUG": "true"}),
        ("prod", {"HOST": "prod.example.com", "DEBUG": "false"}),
    ]
    result = merger.merge(envs)
    assert result.has_conflicts
    conflict_keys = result.conflict_keys()
    assert "HOST" in conflict_keys
    assert "DEBUG" in conflict_keys


def test_merge_strategy_first():
    merger = EnvMerger(strategy="first")
    envs = [
        ("a", {"KEY": "alpha"}),
        ("b", {"KEY": "beta"}),
    ]
    result = merger.merge(envs)
    assert result.merged["KEY"] == "alpha"


def test_merge_strategy_last():
    merger = EnvMerger(strategy="last")
    envs = [
        ("a", {"KEY": "alpha"}),
        ("b", {"KEY": "beta"}),
    ]
    result = merger.merge(envs)
    assert result.merged["KEY"] == "beta"


def test_merge_union_of_keys(merger):
    envs = [
        ("dev", {"A": "1", "B": "2"}),
        ("prod", {"B": "2", "C": "3"}),
    ]
    result = merger.merge(envs)
    assert set(result.merged.keys()) == {"A", "B", "C"}


def test_merge_sources_recorded(merger):
    envs = [("x", {}), ("y", {})]
    result = merger.merge(envs)
    assert result.sources == ["x", "y"]


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        EnvMerger(strategy="random")


def test_conflict_str():
    conflict = MergeConflict(key="DB_HOST", values={"dev": "localhost", "prod": "db.prod"})
    text = str(conflict)
    assert "DB_HOST" in text
    assert "localhost" in text
    assert "db.prod" in text


def test_merge_empty_envs(merger):
    result = merger.merge([])
    assert result.merged == {}
    assert not result.has_conflicts
    assert result.sources == []


def test_merge_single_env(merger):
    """Merging a single environment should produce no conflicts."""
    envs = [("dev", {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"})]
    result = merger.merge(envs)
    assert result.merged == {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    assert not result.has_conflicts
    assert result.sources == ["dev"]
