"""Tests for key rotation detection."""
import pytest
from unittest.mock import MagicMock
from envdiff.key_rotation import (
    RotationCalculator,
    RotationEntry,
    RotationReport,
    _TIER_MAX_DAYS,
)


def _make_age_entry(key, days, envs=("prod",)):
    entry = MagicMock()
    entry.key = key
    entry.days_since_last_change = days
    entry.snapshots_seen = list(envs)
    return entry


def _make_sensitivity_entry(key, tier):
    entry = MagicMock()
    entry.key = key
    entry.tier = tier
    return entry


@pytest.fixture
def age_report():
    report = MagicMock()
    report.entries = [
        _make_age_entry("DB_PASSWORD", 45, ["prod"]),
        _make_age_entry("APP_NAME", 200, ["prod"]),
        _make_age_entry("API_TOKEN", 10, ["prod"]),
    ]
    return report


@pytest.fixture
def sensitivity_report():
    report = MagicMock()
    report.entries = [
        _make_sensitivity_entry("DB_PASSWORD", "critical"),
        _make_sensitivity_entry("APP_NAME", "low"),
        _make_sensitivity_entry("API_TOKEN", "critical"),
    ]
    return report


@pytest.fixture
def calculator():
    return RotationCalculator()


def test_calculate_returns_report(calculator, age_report, sensitivity_report):
    report = calculator.calculate(age_report, sensitivity_report)
    assert isinstance(report, RotationReport)


def test_all_keys_present(calculator, age_report, sensitivity_report):
    report = calculator.calculate(age_report, sensitivity_report)
    keys = {e.key for e in report.entries}
    assert "DB_PASSWORD" in keys
    assert "APP_NAME" in keys
    assert "API_TOKEN" in keys


def test_critical_key_overdue_when_over_30_days(calculator, age_report, sensitivity_report):
    report = calculator.calculate(age_report, sensitivity_report)
    db_entry = next(e for e in report.entries if e.key == "DB_PASSWORD")
    assert db_entry.sensitivity_tier == "critical"
    assert db_entry.is_overdue  # 45 > 30


def test_low_sensitivity_key_not_overdue_at_200_days(calculator, age_report, sensitivity_report):
    report = calculator.calculate(age_report, sensitivity_report)
    app_entry = next(e for e in report.entries if e.key == "APP_NAME")
    assert not app_entry.is_overdue  # 200 <= 180


def test_has_overdue_true_when_any_overdue(calculator, age_report, sensitivity_report):
    report = calculator.calculate(age_report, sensitivity_report)
    assert report.has_overdue


def test_urgency_critical_when_double_max(calculator, age_report, sensitivity_report):
    report = calculator.calculate(age_report, sensitivity_report)
    db_entry = next(e for e in report.entries if e.key == "DB_PASSWORD")
    # 45 days vs 30 max = ratio 1.5 => high
    assert db_entry.urgency in ("high", "critical", "medium")


def test_str_representation_contains_key():
    entry = RotationEntry(
        key="SECRET_KEY",
        env_name="staging",
        days_since_change=90,
        sensitivity_tier="critical",
        recommended_max_days=30,
    )
    result = str(entry)
    assert "SECRET_KEY" in result
    assert "staging" in result
    assert "overdue" in result


def test_tier_max_days_defined_for_all_tiers():
    for tier in ("critical", "high", "medium", "low"):
        assert tier in _TIER_MAX_DAYS
        assert _TIER_MAX_DAYS[tier] > 0


def test_ok_entry_has_ok_urgency():
    entry = RotationEntry(
        key="PORT",
        env_name="dev",
        days_since_change=5,
        sensitivity_tier="low",
        recommended_max_days=180,
    )
    assert entry.urgency == "ok"
    assert not entry.is_overdue
