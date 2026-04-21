"""Tests for key scope detection."""
import pytest
from envdiff.key_scope import KeyScopeCalculator, ScopeEntry, ScopeReport


@pytest.fixture
def calculator():
    return KeyScopeCalculator()


@pytest.fixture
def three_envs():
    return {
        "dev": {
            "DB_URL": "postgres://localhost/dev",
            "DEBUG": "true",
            "DEV_ONLY_KEY": "dev_value",
        },
        "staging": {
            "DB_URL": "postgres://staging/db",
            "DEBUG": "false",
        },
        "prod": {
            "DB_URL": "postgres://prod/db",
            "PROD_ONLY_KEY": "secret",
        },
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, ScopeReport)


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys = {e.key for e in report.entries}
    assert keys == {"DB_URL", "DEBUG", "DEV_ONLY_KEY", "PROD_ONLY_KEY"}


def test_universal_key_is_not_scoped(calculator, three_envs):
    report = calculator.calculate(three_envs)
    db_url = next(e for e in report.entries if e.key == "DB_URL")
    assert not db_url.is_scoped
    assert db_url.absent_from == []


def test_dev_only_key_is_scoped(calculator, three_envs):
    report = calculator.calculate(three_envs)
    dev_key = next(e for e in report.entries if e.key == "DEV_ONLY_KEY")
    assert dev_key.is_scoped
    assert set(dev_key.absent_from) == {"staging", "prod"}
    assert dev_key.present_in == ["dev"]


def test_prod_only_key_absent_from_dev_and_staging(calculator, three_envs):
    report = calculator.calculate(three_envs)
    prod_key = next(e for e in report.entries if e.key == "PROD_ONLY_KEY")
    assert set(prod_key.absent_from) == {"dev", "staging"}


def test_scoped_keys_list(calculator, three_envs):
    report = calculator.calculate(three_envs)
    scoped = {e.key for e in report.scoped_keys}
    assert scoped == {"DEV_ONLY_KEY", "DEBUG", "PROD_ONLY_KEY"}


def test_universal_keys_list(calculator, three_envs):
    report = calculator.calculate(three_envs)
    universal = {e.key for e in report.universal_keys}
    assert universal == {"DB_URL"}


def test_has_scoped_keys_true(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.has_scoped_keys is True


def test_has_scoped_keys_false_when_identical(calculator):
    envs = {
        "dev": {"KEY": "val"},
        "prod": {"KEY": "val"},
    }
    report = calculator.calculate(envs)
    assert report.has_scoped_keys is False


def test_absent_from_env_filters_correctly(calculator, three_envs):
    report = calculator.calculate(three_envs)
    absent_from_prod = report.absent_from_env("prod")
    keys = {e.key for e in absent_from_prod}
    assert "DEV_ONLY_KEY" in keys
    assert "DEBUG" in keys
    assert "DB_URL" not in keys


def test_scope_entry_str(calculator, three_envs):
    report = calculator.calculate(three_envs)
    dev_key = next(e for e in report.entries if e.key == "DEV_ONLY_KEY")
    result = str(dev_key)
    assert "DEV_ONLY_KEY" in result
    assert "dev" in result
