"""Tests for envdiff.key_redundancy."""
import pytest
from envdiff.key_redundancy import RedundancyDetector, RedundancyReport


@pytest.fixture
def detector():
    return RedundancyDetector()


@pytest.fixture
def three_envs():
    return {
        "dev": {
            "DB_URL": "postgres://localhost/dev",
            "APP_NAME": "myapp",
            "LOG_LEVEL": "debug",
            "SHARED_SECRET": "abc123",
        },
        "staging": {
            "DB_URL": "postgres://staging/db",
            "APP_NAME": "myapp",
            "LOG_LEVEL": "info",
            "SHARED_SECRET": "abc123",
        },
        "prod": {
            "DB_URL": "postgres://prod/db",
            "APP_NAME": "myapp",
            "LOG_LEVEL": "warn",
            "SHARED_SECRET": "abc123",
        },
    }


def test_calculate_returns_report(detector, three_envs):
    report = detector.calculate(three_envs)
    assert isinstance(report, RedundancyReport)


def test_env_names_captured(detector, three_envs):
    report = detector.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_detects_redundant_app_name(detector, three_envs):
    report = detector.calculate(three_envs)
    assert "APP_NAME" in report.redundant_keys


def test_detects_redundant_shared_secret(detector, three_envs):
    report = detector.calculate(three_envs)
    assert "SHARED_SECRET" in report.redundant_keys


def test_differing_values_not_flagged(detector, three_envs):
    report = detector.calculate(three_envs)
    assert "DB_URL" not in report.redundant_keys
    assert "LOG_LEVEL" not in report.redundant_keys


def test_has_redundant_true_when_entries_exist(detector, three_envs):
    report = detector.calculate(three_envs)
    assert report.has_redundant is True


def test_clean_envs_no_redundancy(detector):
    envs = {
        "dev": {"DB_URL": "postgres://dev", "SECRET": "devpass"},
        "prod": {"DB_URL": "postgres://prod", "SECRET": "prodpass"},
    }
    report = detector.calculate(envs)
    assert report.has_redundant is False
    assert len(report) == 0


def test_universally_empty_value_not_flagged(detector):
    envs = {
        "dev": {"OPTIONAL": ""},
        "prod": {"OPTIONAL": ""},
    }
    report = detector.calculate(envs)
    assert "OPTIONAL" not in report.redundant_keys


def test_single_env_returns_empty_report(detector):
    envs = {"dev": {"KEY": "value"}}
    report = detector.calculate(envs)
    assert report.has_redundant is False


def test_entry_str_contains_key_and_value(detector, three_envs):
    report = detector.calculate(three_envs)
    entry = next(e for e in report.entries if e.key == "APP_NAME")
    result = str(entry)
    assert "APP_NAME" in result
    assert "myapp" in result
