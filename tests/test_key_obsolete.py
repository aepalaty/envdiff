"""Tests for ObsoleteDetector and ObsoleteFormatter."""
import pytest

from envdiff.key_obsolete import ObsoleteDetector, ObsoleteEntry, ObsoleteReport
from envdiff.obsolete_formatter import ObsoleteFormatter


@pytest.fixture
def detector():
    return ObsoleteDetector()


@pytest.fixture
def three_envs():
    return {
        "production": {"DB_URL": "postgres://prod", "API_KEY": "abc", "LEGACY_FLAG": "1"},
        "staging": {"DB_URL": "postgres://staging", "API_KEY": "xyz"},
        "development": {"DB_URL": "postgres://dev", "DEBUG": "true"},
    }


def test_calculate_returns_report(detector, three_envs):
    report = detector.calculate(three_envs)
    assert isinstance(report, ObsoleteReport)


def test_env_names_captured(detector, three_envs):
    report = detector.calculate(three_envs)
    assert set(report.env_names) == {"production", "staging", "development"}


def test_universal_key_not_obsolete(detector, three_envs):
    report = detector.calculate(three_envs)
    assert "DB_URL" not in report.obsolete_keys


def test_partial_key_detected(detector, three_envs):
    report = detector.calculate(three_envs)
    assert "LEGACY_FLAG" in report.obsolete_keys
    assert "DEBUG" in report.obsolete_keys


def test_absent_from_correct_envs(detector, three_envs):
    report = detector.calculate(three_envs)
    entry = next(e for e in report.entries if e.key == "LEGACY_FLAG")
    assert "production" in entry.present_in
    assert "staging" in entry.absent_from
    assert "development" in entry.absent_from


def test_has_obsolete_true_when_partial(detector, three_envs):
    report = detector.calculate(three_envs)
    assert report.has_obsolete is True


def test_has_obsolete_false_when_all_match(detector):
    envs = {
        "a": {"X": "1"},
        "b": {"X": "2"},
    }
    report = detector.calculate(envs)
    assert report.has_obsolete is False


def test_for_env_returns_correct_entries(detector, three_envs):
    report = detector.calculate(three_envs)
    missing_in_dev = report.for_env("development")
    keys = [e.key for e in missing_in_dev]
    assert "API_KEY" in keys
    assert "LEGACY_FLAG" in keys


def test_format_report_no_issues():
    report = ObsoleteReport(env_names=["a", "b"], entries=[])
    fmt = ObsoleteFormatter(color=False)
    output = fmt.format_report(report)
    assert "No obsolete" in output


def test_format_report_includes_key_name(detector, three_envs):
    report = detector.calculate(three_envs)
    fmt = ObsoleteFormatter(color=False)
    output = fmt.format_report(report)
    assert "LEGACY_FLAG" in output
    assert "DEBUG" in output


def test_format_report_max_entries(detector, three_envs):
    report = detector.calculate(three_envs)
    fmt = ObsoleteFormatter(color=False)
    output = fmt.format_report(report, max_entries=1)
    assert "... and" in output
