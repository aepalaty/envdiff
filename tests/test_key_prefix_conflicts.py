"""Tests for the PrefixConflictDetector module."""
import pytest
from envdiff.key_prefix_conflicts import (
    PrefixConflictDetector,
    PrefixConflictReport,
    PrefixConflict,
)


@pytest.fixture
def detector():
    return PrefixConflictDetector(min_prefix_length=3)


@pytest.fixture
def three_envs():
    return {
        "prod": {
            "DB_HOST": "prod-db",
            "DB_PORT": "5432",
            "DB_PASS": "secret",
            "APP_NAME": "myapp",
        },
        "staging": {
            "DB_HOST": "staging-db",
            "DB_PORT": "5432",
            "APP_NAME": "myapp",
            "APP_DEBUG": "true",
        },
        "dev": {
            "DB_HOST": "localhost",
            "DB_PORT": "5433",
            "DB_PASS": "devpass",
            "APP_NAME": "myapp-dev",
            "APP_DEBUG": "true",
        },
    }


def test_calculate_returns_report(detector, three_envs):
    report = detector.detect(three_envs)
    assert isinstance(report, PrefixConflictReport)


def test_env_names_captured(detector, three_envs):
    report = detector.detect(three_envs)
    assert set(report.env_names) == {"prod", "staging", "dev"}


def test_detects_db_prefix_conflict(detector, three_envs):
    report = detector.detect(three_envs)
    assert report.has_conflicts
    assert "DB" in report.conflict_prefixes


def test_detects_app_prefix_conflict(detector, three_envs):
    report = detector.detect(three_envs)
    assert "APP" in report.conflict_prefixes


def test_conflict_contains_correct_keys(detector, three_envs):
    report = detector.detect(three_envs)
    db_conflict = next(c for c in report.conflicts if c.prefix == "DB")
    assert "DB_HOST" in db_conflict.keys
    assert "DB_PORT" in db_conflict.keys


def test_conflict_envs_affected(detector, three_envs):
    report = detector.detect(three_envs)
    db_conflict = next(c for c in report.conflicts if c.prefix == "DB")
    assert "prod" in db_conflict.envs_affected
    assert "dev" in db_conflict.envs_affected


def test_no_conflicts_for_unique_keys(detector):
    envs = {
        "a": {"ALPHA": "1"},
        "b": {"BETA": "2"},
    }
    report = detector.detect(envs)
    assert not report.has_conflicts


def test_str_representation(detector, three_envs):
    report = detector.detect(three_envs)
    db_conflict = next(c for c in report.conflicts if c.prefix == "DB")
    result = str(db_conflict)
    assert "DB*" in result
    assert "DB_HOST" in result


def test_min_prefix_length_filters_short_prefixes():
    detector_long = PrefixConflictDetector(min_prefix_length=10)
    envs = {
        "a": {"DB_HOST": "host-a", "DB_PORT": "5432"},
        "b": {"DB_HOST": "host-b", "DB_PORT": "5433"},
    }
    report = detector_long.detect(envs)
    assert not report.has_conflicts
