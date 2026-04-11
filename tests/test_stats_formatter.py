"""Tests for StatsFormatter."""

import pytest
from envdiff.key_stats import EnvStatsCalculator
from envdiff.stats_formatter import StatsFormatter


@pytest.fixture
def calculator():
    return EnvStatsCalculator()


@pytest.fixture
def formatter():
    return StatsFormatter(color=False)


@pytest.fixture
def sample_report(calculator):
    envs = {
        "prod": {"DB_URL": "postgres://prod", "SECRET": "s3cr3t", "PORT": "5432"},
        "staging": {"DB_URL": "postgres://staging", "SECRET": "s3cr3t"},
        "dev": {"DB_URL": "postgres://dev", "PORT": "3000"},
    }
    return calculator.calculate(envs)


def test_format_report_includes_env_names(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "prod" in output
    assert "staging" in output
    assert "dev" in output


def test_format_report_includes_all_keys(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "DB_URL" in output
    assert "SECRET" in output
    assert "PORT" in output


def test_format_report_shows_missing_env(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "dev" in output  # SECRET missing from dev


def test_format_report_empty_envs(formatter, calculator):
    report = calculator.calculate({})
    output = formatter.format_report(report)
    assert "no keys found" in output


def test_format_drifted_lists_keys(formatter, sample_report):
    output = formatter.format_drifted(sample_report)
    assert "DB_URL" in output


def test_format_drifted_no_drift_message(formatter, calculator):
    envs = {"a": {"X": "same"}, "b": {"X": "same"}}
    report = calculator.calculate(envs)
    output = formatter.format_drifted(report)
    assert "No value drift" in output


def test_format_report_summary_section(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "Summary" in output
    assert "Total keys" in output


def test_color_disabled_has_no_escape_codes(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "\033[" not in output


def test_color_enabled_has_escape_codes(sample_report):
    colored_formatter = StatsFormatter(color=True)
    output = colored_formatter.format_report(sample_report)
    assert "\033[" in output
