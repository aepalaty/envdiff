"""Tests for rotation report formatter."""
import pytest
from envdiff.key_rotation import RotationEntry, RotationReport
from envdiff.rotation_formatter import RotationFormatter


@pytest.fixture
def formatter():
    return RotationFormatter(use_color=False)


def _make_entry(key, env, days, tier, max_days):
    return RotationEntry(
        key=key,
        env_name=env,
        days_since_change=days,
        sensitivity_tier=tier,
        recommended_max_days=max_days,
    )


@pytest.fixture
def sample_report():
    return RotationReport(
        entries=[
            _make_entry("DB_PASSWORD", "prod", 45, "critical", 30),
            _make_entry("APP_NAME", "prod", 10, "low", 180),
            _make_entry("API_SECRET", "staging", 100, "high", 60),
        ],
        env_names=["prod", "staging"],
    )


def test_format_report_includes_header(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "Rotation" in output


def test_format_report_includes_overdue_key(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "DB_PASSWORD" in output


def test_format_report_includes_ok_key(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "APP_NAME" in output


def test_format_report_shows_overdue_section(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "Overdue" in output


def test_format_report_shows_up_to_date_section(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "Up to date" in output


def test_format_summary_contains_counts(formatter, sample_report):
    summary = formatter.format_summary(sample_report)
    assert "Total:" in summary
    assert "Overdue:" in summary


def test_empty_report_returns_no_data_message(formatter):
    report = RotationReport(entries=[], env_names=[])
    output = formatter.format_report(report)
    assert "No rotation data" in output


def test_format_entry_shows_days_and_tier(formatter):
    entry = _make_entry("SECRET", "prod", 70, "high", 60)
    output = formatter._format_entry(entry)
    assert "70d" in output
    assert "high" in output
    assert "SECRET" in output


def test_overdue_entry_shows_overdue_note(formatter):
    entry = _make_entry("TOKEN", "prod", 90, "critical", 30)
    output = formatter._format_entry(entry)
    assert "overdue" in output
