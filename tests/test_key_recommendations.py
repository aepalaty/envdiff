"""Tests for RecommendationEngine and RecommendationsFormatter."""

import pytest

from envdiff.comparator import EnvDifference
from envdiff.key_recommendations import RecommendationEngine, RecommendationReport
from envdiff.recommendations_formatter import RecommendationsFormatter


@pytest.fixture
def engine():
    return RecommendationEngine()


@pytest.fixture
def formatter():
    return RecommendationsFormatter(color=False)


def _make_diff(
    missing=None, extra=None, mismatched=None,
    baseline="base.env", other="prod.env"
) -> EnvDifference:
    return EnvDifference(
        baseline_name=baseline,
        other_name=other,
        missing_keys=missing or [],
        extra_keys=extra or [],
        mismatched_keys=mismatched or {},
    )


def test_clean_diff_produces_no_recommendations(engine):
    diff = _make_diff()
    report = engine.generate(diff)
    assert not report.has_recommendations
    assert report.errors == []
    assert report.warnings == []


def test_missing_non_sensitive_key_is_warning(engine):
    diff = _make_diff(missing=["APP_ENV"])
    report = engine.generate(diff)
    assert len(report.warnings) == 1
    assert report.warnings[0].key == "APP_ENV"
    assert report.warnings[0].level == "warning"


def test_missing_sensitive_key_is_error(engine):
    diff = _make_diff(missing=["DB_PASSWORD"])
    report = engine.generate(diff)
    assert len(report.errors) == 1
    assert report.errors[0].key == "DB_PASSWORD"
    assert report.errors[0].level == "error"


def test_extra_key_is_info(engine):
    diff = _make_diff(extra=["EXTRA_KEY"])
    report = engine.generate(diff)
    assert len(report.infos) == 1
    assert report.infos[0].key == "EXTRA_KEY"


def test_mismatched_non_sensitive_key_is_info(engine):
    diff = _make_diff(mismatched={"LOG_LEVEL": ("debug", "info")})
    report = engine.generate(diff)
    assert len(report.infos) == 1
    assert report.infos[0].key == "LOG_LEVEL"


def test_mismatched_sensitive_key_is_error(engine):
    diff = _make_diff(mismatched={"API_SECRET": ("abc", "xyz")})
    report = engine.generate(diff)
    assert len(report.errors) == 1
    assert report.errors[0].key == "API_SECRET"


def test_generate_all_returns_one_report_per_diff(engine):
    diffs = [_make_diff(missing=["X"]), _make_diff(extra=["Y"], other="staging.env")]
    reports = engine.generate_all(diffs)
    assert len(reports) == 2


def test_summary_includes_counts(engine):
    diff = _make_diff(missing=["DB_PASSWORD"], extra=["EXTRA"])
    report = engine.generate(diff)
    summary = report.summary()
    assert "1 errors" in summary
    assert "1 info" in summary


def test_formatter_no_recommendations(formatter, engine):
    diff = _make_diff()
    report = engine.generate(diff)
    output = formatter.format_report(report)
    assert "No recommendations" in output


def test_formatter_includes_key_name(formatter, engine):
    diff = _make_diff(missing=["APP_ENV"])
    report = engine.generate(diff)
    output = formatter.format_report(report)
    assert "APP_ENV" in output
    assert "WARNING" in output


def test_format_all_empty_list(formatter):
    output = formatter.format_all([])
    assert "No recommendation" in output


def test_format_all_multiple_reports(formatter, engine):
    diffs = [_make_diff(missing=["A"]), _make_diff(extra=["B"], other="staging.env")]
    reports = engine.generate_all(diffs)
    output = formatter.format_all(reports)
    assert "prod.env" in output
    assert "staging.env" in output
