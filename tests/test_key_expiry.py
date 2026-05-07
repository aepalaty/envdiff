from datetime import date, timedelta

import pytest

from envdiff.key_expiry import ExpiryCalculator, ExpiryEntry, ExpiryReport


@pytest.fixture
def calculator():
    return ExpiryCalculator(expiry_days=90)


@pytest.fixture
def three_envs():
    return {
        "production": {"DB_PASSWORD": "secret", "API_KEY": "abc123", "APP_DEBUG": "false"},
        "staging": {"DB_PASSWORD": "staging_secret", "API_KEY": "xyz789"},
        "development": {"DB_PASSWORD": "devpass", "APP_DEBUG": "true"},
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, ExpiryReport)


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"production", "staging", "development"}


def test_entries_created_for_all_keys(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert len(report.entries) == 7  # 3 + 2 + 2


def test_no_rotation_dates_means_no_expiry(calculator, three_envs):
    report = calculator.calculate(three_envs)
    for entry in report.entries:
        assert entry.expires_on is None
        assert entry.days_until_expiry() is None


def test_expired_entry_detected(calculator, three_envs):
    old_date = date.today() - timedelta(days=100)
    rotation_dates = {"production": {"DB_PASSWORD": old_date}}
    report = calculator.calculate(three_envs, rotation_dates=rotation_dates)
    expired = report.expired_entries()
    assert len(expired) == 1
    assert expired[0].key == "DB_PASSWORD"
    assert expired[0].env_name == "production"


def test_fresh_entry_not_expired(calculator, three_envs):
    recent_date = date.today() - timedelta(days=10)
    rotation_dates = {"production": {"DB_PASSWORD": recent_date}}
    report = calculator.calculate(three_envs, rotation_dates=rotation_dates)
    expired = report.expired_entries()
    assert len(expired) == 0


def test_expiring_soon_detected(calculator, three_envs):
    soon_date = date.today() - timedelta(days=82)  # 8 days left before 90-day expiry
    rotation_dates = {"staging": {"API_KEY": soon_date}}
    report = calculator.calculate(three_envs, rotation_dates=rotation_dates)
    soon = report.expiring_soon(within_days=14)
    assert any(e.key == "API_KEY" and e.env_name == "staging" for e in soon)


def test_has_issues_false_when_all_fresh(calculator, three_envs):
    recent = date.today() - timedelta(days=5)
    rotation_dates = {
        "production": {"DB_PASSWORD": recent, "API_KEY": recent},
    }
    report = calculator.calculate(three_envs, rotation_dates=rotation_dates)
    assert not report.has_issues()


def test_has_issues_true_when_expired(calculator, three_envs):
    old = date.today() - timedelta(days=200)
    rotation_dates = {"development": {"DB_PASSWORD": old}}
    report = calculator.calculate(three_envs, rotation_dates=rotation_dates)
    assert report.has_issues()


def test_entry_str_expired():
    entry = ExpiryEntry(
        key="SECRET",
        env_name="prod",
        last_rotated=date.today() - timedelta(days=100),
        expiry_days=90,
        expires_on=date.today() - timedelta(days=10),
    )
    assert "EXPIRED" in str(entry)


def test_entry_str_no_expiry_date():
    entry = ExpiryEntry(
        key="SECRET",
        env_name="prod",
        last_rotated=None,
        expiry_days=90,
        expires_on=None,
    )
    assert "no expiry date" in str(entry)
