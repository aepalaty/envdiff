"""Tests for EnvStatsCalculator and EnvStatsReport."""

import pytest
from envdiff.key_stats import EnvStatsCalculator, KeyStats, EnvStatsReport


@pytest.fixture
def calculator():
    return EnvStatsCalculator()


@pytest.fixture
def three_envs():
    return {
        "prod": {"DB_URL": "postgres://prod", "SECRET": "abc", "PORT": "5432"},
        "staging": {"DB_URL": "postgres://staging", "SECRET": "abc", "DEBUG": "true"},
        "dev": {"DB_URL": "postgres://dev", "DEBUG": "true", "PORT": "3000"},
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, EnvStatsReport)
    assert report.env_names == ["prod", "staging", "dev"]


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.key_stats.keys()) == {"DB_URL", "SECRET", "PORT", "DEBUG"}


def test_universal_key_has_full_coverage(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert "DB_URL" in report.universal_keys
    assert report.key_stats["DB_URL"].coverage == 1.0


def test_partial_key_has_partial_coverage(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert "SECRET" in report.partial_keys
    stats = report.key_stats["SECRET"]
    assert 0 < stats.coverage < 1.0
    assert "dev" in stats.missing_from


def test_value_drift_detected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert "DB_URL" in report.drifted_keys


def test_no_value_drift_when_values_match(calculator):
    envs = {
        "prod": {"SECRET": "same"},
        "staging": {"SECRET": "same"},
    }
    report = calculator.calculate(envs)
    assert "SECRET" not in report.drifted_keys
    assert not report.key_stats["SECRET"].has_value_drift


def test_empty_envs_returns_empty_report(calculator):
    report = calculator.calculate({})
    assert report.total_keys == 0
    assert report.universal_keys == []


def test_summary_contains_expected_fields(calculator, three_envs):
    report = calculator.calculate(three_envs)
    summary = report.summary()
    assert "Total keys" in summary
    assert "Universal" in summary
    assert "Partial" in summary
    assert "Value drift" in summary


def test_key_stats_str(calculator):
    envs = {"a": {"X": "1"}, "b": {"X": "2"}}
    report = calculator.calculate(envs)
    s = str(report.key_stats["X"])
    assert "X" in s
    assert "drift" in s
