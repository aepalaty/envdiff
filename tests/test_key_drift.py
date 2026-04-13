"""Tests for key_drift and drift_formatter modules."""
import pytest
from envdiff.key_drift import KeyDriftCalculator, DriftEntry, DriftReport
from envdiff.drift_formatter import DriftFormatter


@pytest.fixture
def calculator():
    return KeyDriftCalculator()


@pytest.fixture
def three_envs():
    return {
        "dev": {"DB_URL": "postgres://localhost/dev", "DEBUG": "true", "PORT": "8000"},
        "staging": {"DB_URL": "postgres://staging/app", "DEBUG": "false", "PORT": "8000"},
        "prod": {"DB_URL": "postgres://prod/app", "DEBUG": "false", "PORT": "8000"},
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, DriftReport)


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys = {e.key for e in report.entries}
    assert keys == {"DB_URL", "DEBUG", "PORT"}


def test_db_url_has_drift(calculator, three_envs):
    report = calculator.calculate(three_envs)
    db_entry = next(e for e in report.entries if e.key == "DB_URL")
    assert db_entry.has_drift
    assert db_entry.unique_values == 3


def test_port_is_stable(calculator, three_envs):
    report = calculator.calculate(three_envs)
    port_entry = next(e for e in report.entries if e.key == "PORT")
    assert not port_entry.has_drift
    assert port_entry.unique_values == 1


def test_drifted_keys_list(calculator, three_envs):
    report = calculator.calculate(three_envs)
    drifted = {e.key for e in report.drifted_keys}
    assert "DB_URL" in drifted
    assert "DEBUG" in drifted
    assert "PORT" not in drifted


def test_stable_keys_list(calculator, three_envs):
    report = calculator.calculate(three_envs)
    stable = {e.key for e in report.stable_keys}
    assert "PORT" in stable


def test_has_drift_true(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.has_drift


def test_has_drift_false_when_identical(calculator):
    envs = {
        "dev": {"KEY": "value"},
        "prod": {"KEY": "value"},
    }
    report = calculator.calculate(envs)
    assert not report.has_drift


def test_summary_string(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert "drift" in report.summary
    assert "3" in report.summary


def test_drift_entry_str_stable():
    entry = DriftEntry(key="PORT", values=["8000", "8000"], env_names=["dev", "prod"])
    assert "stable" in str(entry)


def test_drift_entry_str_drifted():
    entry = DriftEntry(key="DB_URL", values=["local", "remote"], env_names=["dev", "prod"])
    assert "2 distinct" in str(entry)


def test_formatter_no_color(calculator, three_envs):
    report = calculator.calculate(three_envs)
    formatter = DriftFormatter(color=False)
    output = formatter.format_report(report)
    assert "Key Drift Report" in output
    assert "DRIFT" in output


def test_formatter_shows_stable_when_requested(calculator, three_envs):
    report = calculator.calculate(three_envs)
    formatter = DriftFormatter(color=False)
    output = formatter.format_report(report, show_stable=True)
    assert "Stable Keys" in output
    assert "PORT" in output


def test_formatter_empty_envs(calculator):
    report = calculator.calculate({})
    formatter = DriftFormatter(color=False)
    output = formatter.format_report(report)
    assert "No keys found" in output
