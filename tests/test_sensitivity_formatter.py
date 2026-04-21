"""Tests for sensitivity_formatter module."""
import pytest
from envdiff.key_sensitivity import SensitivityCalculator, SensitivityReport
from envdiff.sensitivity_formatter import SensitivityFormatter


@pytest.fixture
def calculator():
    return SensitivityCalculator()


@pytest.fixture
def formatter():
    return SensitivityFormatter(color=False)


@pytest.fixture
def sample_report(calculator):
    envs = {
        "prod": {
            "DB_PASSWORD": "realpass",
            "DB_HOST": "db.prod",
            "APP_NAME": "myapp",
            "SSL_CERT": "cert-data",
        },
        "dev": {
            "DB_PASSWORD": "CHANGEME",
            "DB_HOST": "localhost",
            "APP_NAME": "myapp",
        },
    }
    return calculator.calculate(envs)


def test_format_report_includes_tier_headers(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "CRITICAL" in output
    assert "HIGH" in output
    assert "MEDIUM" in output


def test_format_report_includes_key_names(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "DB_PASSWORD" in output
    assert "DB_HOST" in output
    assert "APP_NAME" in output


def test_format_report_flags_plain_value(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "plain value in" in output
    assert "prod" in output


def test_format_report_does_not_flag_placeholder(formatter, sample_report):
    output = formatter.format_report(sample_report)
    # dev has CHANGEME which is a placeholder — should not appear as plain
    lines = [l for l in output.splitlines() if "DB_PASSWORD" in l]
    assert lines
    combined = " ".join(lines)
    assert "dev" not in combined or "plain value in" not in combined


def test_format_report_includes_totals(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "Total keys" in output
    assert "Plain secrets detected" in output


def test_format_summary_with_issues(formatter, sample_report):
    summary = formatter.format_summary(sample_report)
    assert "CRITICAL" in summary or "plain-text" in summary


def test_format_summary_no_issues(formatter, calculator):
    envs = {"env": {"APP_NAME": "hello", "LOG_LEVEL": "debug"}}
    report = calculator.calculate(envs)
    summary = formatter.format_summary(report)
    assert "No high-sensitivity issues" in summary


def test_format_report_with_color():
    colored_formatter = SensitivityFormatter(color=True)
    calculator = SensitivityCalculator()
    envs = {"prod": {"DB_PASSWORD": "secret"}}
    report = calculator.calculate(envs)
    output = colored_formatter.format_report(report)
    assert "\033[" in output
