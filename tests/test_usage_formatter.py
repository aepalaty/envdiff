"""Tests for UsageFormatter."""

import pytest
from envdiff.key_usage import KeyUsageTracker
from envdiff.usage_formatter import UsageFormatter


@pytest.fixture
def tracker():
    return KeyUsageTracker()


@pytest.fixture
def formatter():
    return UsageFormatter(color=False)


@pytest.fixture
def sample_report(tracker):
    envs = {
        "a": {"ALPHA": "1", "BETA": "2", "GAMMA": "3"},
        "b": {"ALPHA": "1", "DELTA": "4"},
        "c": {"ALPHA": "1", "BETA": "2"},
    }
    return tracker.track(envs)


def test_format_report_includes_total(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "4 unique keys" in output


def test_format_report_includes_most_used_header(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "Most used" in output


def test_format_report_includes_least_used_header(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "Least used" in output


def test_format_report_shows_alpha_as_most_common(formatter, sample_report):
    output = formatter.format_report(sample_report)
    lines = output.splitlines()
    most_section_start = next(i for i, l in enumerate(lines) if "Most used" in l)
    first_key_line = lines[most_section_start + 1]
    assert "ALPHA" in first_key_line


def test_format_summary_includes_total(formatter, sample_report):
    summary = formatter.format_summary(sample_report)
    assert "Total unique keys: 4" in summary


def test_format_summary_includes_most_common(formatter, sample_report):
    summary = formatter.format_summary(sample_report)
    assert "Most common: ALPHA" in summary


def test_format_report_top_n_limits_output(formatter, sample_report):
    output = formatter.format_report(sample_report, top_n=1)
    # Only one entry under each section
    most_lines = [l for l in output.splitlines() if "count=" in l]
    # top_n=1 means 1 most + 1 least = 2 lines with count
    assert len(most_lines) == 2


def test_color_disabled_no_escape_codes(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "\033[" not in output


def test_color_enabled_has_escape_codes(sample_report):
    colored_formatter = UsageFormatter(color=True)
    output = colored_formatter.format_report(sample_report)
    assert "\033[" in output
